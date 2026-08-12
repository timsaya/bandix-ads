# Bandix Ads

Bandix LuCI 页面使用的远程广告配置仓库。仓库应保持为 **Public**，页面只读取公开的 `ads.json` 和图片，不需要保存 GitHub Token。

## 目录结构

```text
.
├── ads.json
├── images/
│   ├── slot-1.svg
│   └── ...
├── schema/
│   └── ads.schema.json
└── scripts/
    └── validate.py
```

## 多语言广告

广告按标准化语言代码存放在 `locales` 中。当前默认语言为简体中文：

```json
{
  "version": 2,
  "default_locale": "zh-hans",
  "locales": {
    "zh-hans": [],
    "zh-hant": [],
    "en": []
  }
}
```

LuCI 页面按“当前完整语言 → 基础语言 → `default_locale`”的顺序选择广告。例如 `en-us` 会先查找 `en-us`，再查找 `en`，最后回退到 `zh-hans`。常用中文代码会自动归一化：

- `zh-CN`、`zh-SG`、`zh-Hans` → `zh-hans`
- `zh-TW`、`zh-HK`、`zh-MO`、`zh-Hant` → `zh-hant`

要添加其他语言，可以复制一个完整广告数组并修改标题、图片和推广链接：

```json
"en": [
  {
    "id": "slot-1",
    "enabled": true,
    "title": "English advertisement",
    "image": "images/en/slot-1.jpg",
    "href": "https://example.com/promotion-link",
    "alt": "English advertisement"
  }
]
```

每个语言组最多包含 6 个广告；非默认语言可以使用空数组，此时页面显示 6 个空广告位。

## 更新广告

1. 将广告图片放入 `images/`，建议使用 HTTPS 来源允许的 JPG、PNG、WebP 或 SVG 文件。
2. 编辑 `ads.json` 中对应语言的广告数组：
   - `enabled` 改为 `true`；
   - `href` 填写京东联盟生成的推广链接，不能填写普通商品链接；
   - `image` 填写仓库内的相对路径，例如 `images/router.jpg`；
   - 更新 `title`、`alt` 和根节点的 `updated_at`。
3. 本地校验：

   ```sh
   python3 scripts/validate.py
   ```

4. 提交并推送。LuCI 页面将在下一次刷新周期读取新配置。

## 首次推送

在 GitHub 创建一个空的公开仓库后执行：

```sh
git remote add origin git@github.com:YOUR_GITHUB_USERNAME/bandix-ads.git
git push -u origin main
```

配置文件的 Raw 地址为：

```text
https://raw.githubusercontent.com/YOUR_GITHUB_USERNAME/bandix-ads/main/ads.json
```

## 建议图片规格

- 宽高比：`1:1`
- 推荐尺寸：`350 × 350 px` 或更高分辨率的正方形图片
- 单张文件建议不超过 `200 KB`
- 不要提交京东联盟的 AppKey、AppSecret、Cookie 或访问令牌
