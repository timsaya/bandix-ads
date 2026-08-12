#!/usr/bin/env python3

import json
import re
import sys
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT / "ads.json"
LOCALE_PATTERN = re.compile(r"^[a-z]{2,3}(?:-[a-z0-9]+)*$")


def fail(message):
    print(f"error: {message}", file=sys.stderr)
    raise SystemExit(1)


def validate_ads(locale, ads, require_entries=False):
    if not isinstance(ads, list) or len(ads) > 6 or (require_entries and not ads):
        requirement = "between 1 and 6" if require_entries else "between 0 and 6"
        fail(f"locales.{locale} must contain {requirement} entries")

    seen_ids = set()
    required = {"id", "enabled", "title", "image", "href", "alt"}
    for index, ad in enumerate(ads, 1):
        if not isinstance(ad, dict):
            fail(f"locales.{locale} ad #{index} must be an object")
        missing = required - ad.keys()
        if missing:
            fail(f"locales.{locale} ad #{index} is missing: {', '.join(sorted(missing))}")
        if ad["id"] in seen_ids:
            fail(f"duplicate id in locales.{locale}: {ad['id']}")
        seen_ids.add(ad["id"])
        if not isinstance(ad["enabled"], bool):
            fail(f"locales.{locale}.{ad['id']}.enabled must be true or false")
        if not all(isinstance(ad[key], str) and ad[key] for key in ("title", "image", "alt")):
            fail(f"locales.{locale}.{ad['id']} requires non-empty title, image and alt")

        href = ad["href"]
        if href:
            parsed_href = urlparse(href)
            if parsed_href.scheme != "https" or not parsed_href.netloc:
                fail(f"locales.{locale}.{ad['id']}.href must be an HTTPS URL")
        elif ad["enabled"]:
            fail(f"locales.{locale}.{ad['id']} is enabled but href is empty")

        image = ad["image"]
        parsed_image = urlparse(image)
        if parsed_image.scheme:
            if parsed_image.scheme != "https" or not parsed_image.netloc:
                fail(f"locales.{locale}.{ad['id']}.image must be an HTTPS URL or repository-relative path")
        elif not (ROOT / image).is_file():
            fail(f"locales.{locale}.{ad['id']}.image does not exist: {image}")


def main():
    try:
        config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"cannot read ads.json: {exc}")

    if config.get("version") != 2:
        fail("version must be 2")

    interval = config.get("refresh_interval")
    if not isinstance(interval, int) or not 300 <= interval <= 86400:
        fail("refresh_interval must be an integer between 300 and 86400")

    try:
        datetime.fromisoformat(config["updated_at"].replace("Z", "+00:00"))
    except (KeyError, TypeError, ValueError):
        fail("updated_at must be an ISO 8601 date-time")

    default_locale = config.get("default_locale")
    if not isinstance(default_locale, str) or not LOCALE_PATTERN.fullmatch(default_locale):
        fail("default_locale must be a normalized language code such as zh-hans or en")

    locales = config.get("locales")
    if not isinstance(locales, dict) or not locales:
        fail("locales must be a non-empty object")
    if default_locale not in locales:
        fail("default_locale must identify an entry in locales")

    total_ads = 0
    for locale, ads in locales.items():
        if not isinstance(locale, str) or not LOCALE_PATTERN.fullmatch(locale):
            fail(f"invalid locale key: {locale!r}")
        validate_ads(locale, ads, require_entries=locale == default_locale)
        total_ads += len(ads)

    print(f"ok: validated {total_ads} advertising slots across {len(locales)} locale(s)")


if __name__ == "__main__":
    main()
