# 本番サーバー設定（Apache）

本番環境（`https://count.it-araiguma.com/`）の Apache HTTP Server（AlmaLinux / Apache 2.4.37, `mpm_event`）に関する設定記録です。

## リポジトリ外のサーバー設定

### `/etc/httpd/conf.d/char_cnt.conf`

443 番ポートの `<VirtualHost *:443>` ブロックにて HTTP/2 を有効化するため、以下のディレクティブを設定しています（2026-11-21 反映）。

```apache
<VirtualHost *:443>
  SSLEngine on
  Protocols h2 http/1.1
  ServerName count.it-araiguma.com
  DocumentRoot /home/appuser/public_html/char_cnt/dist/pwa
  ...
```

反映手順：

```bash
sudo apachectl configtest
sudo systemctl reload httpd
```

## リポジトリ管理の設定（`public/.htaccess`）

`char_cnt.conf` で `AllowOverride All` が有効になっているため、圧縮・キャッシュ制御・SPA フォールバックは `public/.htaccess` で管理し、ビルド時に `dist/pwa/.htaccess` へ出力されます。

- **圧縮**: `mod_brotli`（`br`）および `mod_deflate`（`gzip`）により、`text/html`、`text/css`、`application/javascript`、`text/javascript`、`application/json`、`application/manifest+json`、`image/svg+xml`、`text/xml`、`text/plain` を圧縮配信します。
- **キャッシュ制御（`mod_headers`）**:
  - `/assets/*` および `workbox-*.js`（ハッシュ付き成果物）: `public, max-age=31536000, immutable`
  - `index.html`、`sw.js`、`manifest.json`、`sitemap.xml`、`robots.txt`: `no-cache`
  - `/icons/*`、`favicon.ico`: `public, max-age=604800`（1 週間）
