# CLAUDE.md

## 絶対ルール

### 問題対応の原則
- 修正時は根本原因を特定してから対応する。表面的な対症療法は禁止。
- エラーが出たら、まずエラーメッセージを正確に読み、原因を特定してから修正する。闇雲なリトライは禁止。
- テストコードや lint 設定は安易に変更せず、本体コード側を修正する。

### Git操作
- `main` ブランチへ直接コミットしない。すべての変更と Issue 対応は、専用ブランチ（原則として専用 worktree）で作業して PR を作る。
- コミット時は該当作業で変更したファイルだけを `git add` で個別指定する。`git add .` や `git add -A` は禁止。
- Issue は 1 件ずつ対応し、完了（PR マージ・本番デプロイ・外形確認・Status「完了」更新）を確認してから次に進む。まとめて対応しない。
- 作業の最後に複数の論理変更をまとめてコミットしない。1つの論理変更が完了し、検証できた時点で逐次コミットする。
- コミットは変更目的が 1 つにまとまり、単独でレビュー・検証・切り戻しできる粒度にする。実装と、その実装に直接対応するテスト・ドキュメントは同じコミットに含める。
- コミット前に `git diff --stat` で対象ファイルが正しいか確認する。

### サイト構成とデプロイ環境
- **サービス名**: 文字数カウント（`https://count.it-araiguma.com/`）
- **リポジトリ**: `it-araiguma/char_cnt`
- **GitHub Project**: `char_cnt`（Project 6 / ID: `PVT_kwHOAxJSE84Brsfe`）
  - `Status`: `やること` / `対応中` / `完了` / `検討中`
  - `重要度`: `高` / `中` / `低`
- **技術スタック**: Quasar v2 (`@quasar/app-vite`) + Vue 3 + TypeScript + Vue Router + vue-i18n (PWA モード)
- **本番サーバー**: VPS (`ssh vps` / `160.16.95.167`)
  - リポジトリパス: `/home/appuser/public_html/char_cnt`（実行ユーザー: `appuser`）
  - ドキュメントルート: `/home/appuser/public_html/char_cnt/dist/pwa`
  - Apache 設定: `/etc/httpd/conf.d/char_cnt.conf`
  - デプロイ方式: 手元で `quasar build -m pwa` を実行した成果物を VPS へ転送し、VPS 側は `flock` 排他制御下で git リポジトリ同期とアトミック配置を行う（メモリ 1GB の VPS 上ではビルドを実行しない）

### Issue対応フロー
Issue の選定から着手・実装・検証・PR・マージ・本番デプロイ・完了更新までを一気通貫で行う際は、`issue-work` Skill（`.claude/skills/issue-work/SKILL.md`）を使用する。
1. `select_candidates.py` で候補を取得し、重要度（高 > 中 > 低）と実用性で 1 件選定（指定がある場合は省略）
2. まず作業 Issue の Status を「対応中」へ更新する（ファイル調査や方針検討を先行させず、何よりもまず真っ先に `start.py` で専用 worktree を作成し Status を「対応中」にする）
3. 作成された worktree 内で Issue 本文・関連ファイルを確認し、方針整理・実装・検証（`npm run lint`、`npx --yes vue-tsc --noEmit`、`npx --yes quasar build -m pwa`）
4. PR 作成（`gh pr create`）とチェック確認（`wait_pr.py`）
5. `finish.py` で squash マージ、worktree・ローカルブランチ削除、本番 VPS デプロイ（手元 PWA ビルド成果物の転送・flock 排他制御による本番反映）と `https://count.it-araiguma.com/` 外形確認、Issue クローズ、Project 6 の Status を「完了」へ更新

### 完了報告
- ローカルでのコミットやテスト成功、PR 作成だけで作業を終えず、必ず PR マージ、本番デプロイ完了と外形確認、Project Status の「完了」更新まで自律的に完遂する。
- 完了報告に「確認していただきたい点」「ご確認ください」など、確認作業をユーザーへ戻す項目を付けない。

※単発の直接作業時も、破壊的変更以外はユーザー確認を挟まず自律的に完了まで進める。
