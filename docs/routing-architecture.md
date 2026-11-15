# ルーティングおよび配信方式の設計方針書

本書は、文字数カウント（`https://count.it-araiguma.com/`）におけるルーティング方式の選定、本番配信設定、および今後の用途別ページ（SEOクラスタ）展開に向けたアーキテクチャ方針を定義します。

---

## 1. 背景と課題

- **ハッシュ形式（`/#/`）の問題点**:
  - これまで `quasar.config.js` の `vueRouterMode: 'hash'` により、URLが `/#/` や `/#/privacy` となっていた。
  - URL のハッシュ（フラグメント識別子 `#`）以降は HTTP リクエストとしてサーバーに送信されず、Googlebot をはじめとする検索エンジンのクローラーもハッシュ以降のパスを個別の独立ページとして認識・インデックスしない。
  - 「文字数カウンターSEOクラスタ方針（#9）」において、用途別ページ（例: 原稿用紙文字数、レポート文字数、SNS投稿用文字数など）を個別の URL で公開し、検索エンジンに独立して評価・インデックスさせることが必須であるため、ハッシュ形式の廃止・独立 URL 化が最優先課題となっていた。

---

## 2. 方式の比較検討

| 方式 | 特徴 | メリット | デメリット / リスク | 判定 |
| :--- | :--- | :--- | :--- | :--- |
| **A. SPA + HTML5 History Mode + Apache mod_rewrite** | Quasar PWA のまま `vueRouterMode: 'history'` に変更し、Apache の `.htaccess` で未マッチのパスを `index.html` にフォールバック | ・構成がシンプルで安全<br>・PWA（Workbox）と完全互換<br>・Googlebot（Evergreen Chromium）によるレンダリング・インデックスが可能<br>・サーバーの運用負荷が増えない | ・SNSクローラー（OGP）は初期HTMLの静的メタを参照する（Google検索流入には影響なし） | **採用（第1段階・即時移行）** |
| **B. ビルド時プリレンダリング（SSG）** | ビルド時にヘッドレスブラウザ（Puppeteer等）で各ルートの静的HTMLを生成 | ・初期ロード高速<br>・完全静的HTMLでOGPクローラーにも即時応答 | ・Quasar v2 + Vite + PWAのパイプラインでの設定が複雑（Service Workerキャッシュとの衝突リスク）<br>・ビルド時間増大 | **将来の拡張候補（必要時に検討）** |
| **C. SSR（サーバーサイドレンダリング）** | Node.js サーバーでリクエストごとにHTMLを動的生成 | ・完全なサーバーレンダリング | ・VPS上で常駐Nodeプロセスのデーモン管理・リバースプロキシ設定が必要<br>・障害点・メモリ消費の増大 | **不採用（過剰）** |

### display.it-araiguma.com（実績構成）との比較
- 同ドメインで「画面サイズチェッカー」7位の実績がある `display.it-araiguma.com` は、Laravel（PHP）によるサーバーサイド生成を採用している。
- Apacheの設定（`AllowOverride All` ＋ フロントコントローラーへの `RewriteRule ^ index.php [L]`）によって全URLを独立ページとして配信している。
- `char_cnt` においても、Apacheの `mod_rewrite` により全URLを `index.html` にルーティングし、HTML5 History API で独立URLとして振る舞わせることで、Googlebot に対して `display` と同様にパスごとの独立URLとしてクロール・インデックスさせることが可能である。

---

## 3. 採用方式と実装仕様

### 3.1. ルーティング設定（`quasar.config.js`）
```javascript
build: {
  vueRouterMode: 'history', // HTML5 History Mode
}
```
- Vue Router が `createWebHistory()` を使用し、ブラウザの History API を通じてパス（`/`、`/privacy`、`/pages/...`）を直接管理する。

### 3.2. Apache フォールバック設定（`public/.htaccess`）
本番 VPS の DocumentRoot（`/home/appuser/public_html/char_cnt/dist/pwa`）は `AllowOverride All` が有効化されている。
リポジトリの `public/.htaccess` に以下のフォールバックルールを配置し、Quasar のビルド時に自動で `dist/pwa/.htaccess` へ出力する。

```apache
<IfModule mod_rewrite.c>
  RewriteEngine On
  RewriteBase /
  RewriteRule ^index\.html$ - [L]
  RewriteCond %{REQUEST_FILENAME} !-f
  RewriteCond %{REQUEST_FILENAME} !-d
  RewriteRule . /index.html [L]
</IfModule>
```
- 静的アセット（JS, CSS, 画像, manifest.json, sw.js 等）が存在する場合はそのまま返却。
- それ以外の全パス（例: `/privacy` や用途別ページ）への直接アクセス・リロード時は `index.html` を返却し、クライアント側の Vue Router が該当コンポーネントを描画する。

### 3.3. PWA（Workbox）との整合性
- Quasar PWA モードの Workbox（`generateSW`）は、SPA の History Mode と標準で整合している。
- ナビゲーションリクエストはキャッシュされた `index.html` にフォールバックするため、オフライン時やService Worker稼働時でもHistoryルーティングが正常に機能する。

### 3.4. SEOメタタグ（`src/utils/seo.ts`）の整合
- `canonical`、`og:url`、`og:type`、`og:site_name`、`og:image`、`twitter:card`、`twitter:image`、`hreflang` を動的に出力。
- `canonical` および `og:url` には `window.location.origin + router.currentRoute.value.path`（ハッシュ抜きの正規 URL）を設定。

---

## 4. 用途別ページ（SEOクラスタ）追加手順

今後、用途別ページ（#13 等）を追加・公開する際の手順は以下の通り。

1. **ページコンポーネントの作成**:
   - `src/pages/features/<PageName>.vue` を作成。
   - `useSeoMeta('<pageName>')` を呼び出し、各ページ固有のタイトル・説明文・キーワードを設定。
2. **多言語文言・SEOメタ定義の追加**:
   - `src/i18n/ja-JP/index.ts`（および他言語）の `seo.<pageName>` に `title`, `description`, `keywords` を定義。
3. **ルーティング定義の追加**:
   - `src/router/routes.ts` にパスとコンポーネントのマッピングを追加（例: `path: '/for-essay'`, `component: () => import('pages/features/EssayCountPage.vue')`）。
4. **サイトマップの更新（#12）**:
   - `public/sitemap.xml` に新ルートの URL を追加。
5. **検証とデプロイ**:
   - ローカル検証（Lint, TypeCheck, PWA Build）を実施後、PR を通じて本番 VPS にデプロイ。
   - 直接アクセス（例: `https://count.it-araiguma.com/for-essay`）およびリロードで HTTP 200 と正常描画を確認。
