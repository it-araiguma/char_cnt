# Google Search Console 登録状態とサイトマップ管理方針

本書は、文字数カウント（`https://count.it-araiguma.com/`）における Google Search Console（GSC）の登録状態、インデックス登録状況、サイトマップ（`sitemap.xml`）および `robots.txt` の配置仕様、運用手順を記録するドキュメントです。

---

## 1. サイトマップおよびクロール制御の整備

### 1.1. `robots.txt` 仕様（`public/robots.txt`）
全検索エンジン・クローラーに対してサイト全体のアクセスを許可し、サイトマップの所在を明示します。
ビルド時に `dist/pwa/robots.txt` として本番公開されます。

```txt
User-agent: *
Allow: /

Sitemap: https://count.it-araiguma.com/sitemap.xml
```

### 1.2. `sitemap.xml` 仕様（`public/sitemap.xml`）
HTML5 History モード化（#11）後の正規 URL 構造に合わせた XML サイトマップです。
ビルド時に `dist/pwa/sitemap.xml` として本番公開されます。

```xml
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://count.it-araiguma.com/</loc>
    <lastmod>2026-11-15</lastmod>
    <changefreq>weekly</changefreq>
    <priority>1.0</priority>
  </url>
  <url>
    <loc>https://count.it-araiguma.com/privacy</loc>
    <lastmod>2026-11-15</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.5</priority>
  </url>
</urlset>
```

※用途別ページ（SEOクラスタ展開 #13 等）の追加時は、`public/sitemap.xml` に順次エントリを追加します。

### 1.3. 所有権確認メタタグおよび認証ファイル
- `index.html`: `<meta name="google-site-verification" content="SqRAhAwiGX0Dga6VFqFmURsaEm80emigFlRdWNt5kfQ">` を配置。
- `public/google08dee92ec25a3e48.html`: 親ドメインで確認済みの HTML 認証ファイルを配置。

---

## 2. Search Console 登録状態・インデックス状況（2026-11-15 実測）

### 2.1. インデックス状況
- Google 日本検索実測において「文字数カウント」「文字数カウンター」で 50 位圏外。
- インデックス登録済みページ数は 1 件（トップページ `https://count.it-araiguma.com/` のみ）。
- 旧ハッシュ形式（`/#/`）および初期表示時の英語上書き（#10）により、用途別ページや適切な日本語メタのインデックスが阻害されていた。
- #10（日本語UI・メタ恒久化）および #11（HTML5 History モード化）のマージ・デプロイにより、本番のクローラー向け環境は正常化済み。

### 2.2. API 連携およびサービスアカウント権限状態
- プロジェクト共通サービスアカウント: `blog-957@youtube-analytics-472912.iam.gserviceaccount.com`
- 調査結果:
  - `sites.add` により `https://count.it-araiguma.com/` をサイトリストに追加済み。
  - 現在の権限レベル: `permissionLevel: siteUnverifiedUser`（未検証）。
  - 所有権確認（Ownership Verification）または Search Console UI 上での権限共有（Full User / Owner）が未完了のため、API経由での Sitemaps 送信および URL Inspection は `403 Forbidden` となる。

---

## 3. Search Console 送信・再リクエスト手順

### 3.1. 所有権の確認・権限付与（Search Console Web UI）
1. Google Search Console（`https://search.google.com/search-console`）にログイン。
2. プロパティに `https://count.it-araiguma.com/` またはドメインプロパティ `sc-domain:it-araiguma.com` を選択。
3. 「設定」→「ユーザーと権限」を開く。
4. ユーザーを追加:
   - メールアドレス: `blog-957@youtube-analytics-472912.iam.gserviceaccount.com`
   - 権限: 「フル」または「オーナー」
5. または、HTML タグ方式 / HTML ファイル方式で所有権を確認（すでに `index.html` および `google08dee92ec25a3e48.html` がデプロイされているため、ワンクリックで検証完了可能）。

### 3.2. サイトマップ送信（手動 / CLI）
**Web UI からの送信**:
- Search Console の「インデックス作成」→「サイトマップ」を選択。
- 新しいサイトマップの追加に `sitemap.xml` を入力して「送信」。

**CLI（スクリプト）からの送信**:
サービスアカウントへの権限付与完了後、以下のコマンドで送信可能です。
```bash
python3 scripts/gsc_tool.py submit-sitemap
```

### 3.3. インデックス再リクエスト
UI・タイトルの日本語化（#10）および History モード（#11）反映後の最新ページを Googlebot にクロールさせるため、以下の URL に対してインデックス登録をリクエストします。

1. `https://count.it-araiguma.com/`
2. `https://count.it-araiguma.com/privacy`

**Web UI からの手順**:
1. Search Console 上部の検索バーに URL を入力（「URL を検査」）。
2. 「公開 URL をテスト」を実行し、レンダリングおよびステータスを確認。
3. 「インデックス登録をリクエスト」をクリック。
