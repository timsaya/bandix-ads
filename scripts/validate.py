#!/usr/bin/env python3

import json
import sys
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT / "ads.json"


def fail(message):
    print(f"error: {message}", file=sys.stderr)
    raise SystemExit(1)


def main():
    try:
        config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"cannot read ads.json: {exc}")

    if config.get("version") != 1:
        fail("version must be 1")

    interval = config.get("refresh_interval")
    if not isinstance(interval, int) or not 300 <= interval <= 86400:
        fail("refresh_interval must be an integer between 300 and 86400")

    try:
        datetime.fromisoformat(config["updated_at"].replace("Z", "+00:00"))
    except (KeyError, TypeError, ValueError):
        fail("updated_at must be an ISO 8601 date-time")

    ads = config.get("ads")
    if not isinstance(ads, list) or not 1 <= len(ads) <= 6:
        fail("ads must contain between 1 and 6 entries")

    seen_ids = set()
    required = {"id", "enabled", "title", "image", "href", "alt"}
    for index, ad in enumerate(ads, 1):
        if not isinstance(ad, dict):
            fail(f"ad #{index} must be an object")
        missing = required - ad.keys()
        if missing:
            fail(f"ad #{index} is missing: {', '.join(sorted(missing))}")
        if ad["id"] in seen_ids:
            fail(f"duplicate id: {ad['id']}")
        seen_ids.add(ad["id"])
        if not isinstance(ad["enabled"], bool):
            fail(f"{ad['id']}.enabled must be true or false")
        if not all(isinstance(ad[key], str) and ad[key] for key in ("title", "image", "alt")):
            fail(f"{ad['id']} requires non-empty title, image and alt")

        href = ad["href"]
        if href:
            parsed_href = urlparse(href)
            if parsed_href.scheme != "https" or not parsed_href.netloc:
                fail(f"{ad['id']}.href must be an HTTPS URL")
        elif ad["enabled"]:
            fail(f"{ad['id']} is enabled but href is empty")

        image = ad["image"]
        parsed_image = urlparse(image)
        if parsed_image.scheme:
            if parsed_image.scheme != "https" or not parsed_image.netloc:
                fail(f"{ad['id']}.image must be an HTTPS URL or repository-relative path")
        elif not (ROOT / image).is_file():
            fail(f"{ad['id']}.image does not exist: {image}")

    print(f"ok: validated {len(ads)} advertising slots")


if __name__ == "__main__":
    main()
