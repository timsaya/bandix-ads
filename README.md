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

## 更新广告

1. 将广告图片放入 `images/`，建议使用 HTTPS 来源允许的 JPG、PNG、WebP 或 SVG 文件。
2. 编辑 `ads.json`：
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

- 宽高比：`3:1`
- 推荐尺寸：`600 × 200 px`
- 单张文件建议不超过 `200 KB`
- 不要提交京东联盟的 AppKey、AppSecret、Cookie 或访问令牌
