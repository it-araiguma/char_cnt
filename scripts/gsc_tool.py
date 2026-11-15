#!/usr/bin/env python3
"""Google Search Console の登録状況確認・サイトマップ送信・URL検査スクリプト。

使用法:
  python3 scripts/gsc_tool.py status
  python3 scripts/gsc_tool.py submit-sitemap [--sitemap-url <url>]
  python3 scripts/gsc_tool.py inspect <url>
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any, Dict, Optional

DEFAULT_SITE_URL = "https://count.it-araiguma.com/"
DEFAULT_SITEMAP_URL = "https://count.it-araiguma.com/sitemap.xml"
DEFAULT_SA_PATH = os.path.expanduser(
    os.getenv(
        "GOOGLE_SERVICE_ACCOUNT_FILE",
        "/home/aulani/develop/araiguma-blog/configs/service_accounts/search-console-service-account.json",
    )
)


def get_credentials(key_path: str):
    if not os.path.exists(key_path):
        raise FileNotFoundError(f"サービスアカウントファイルが見つかりません: {key_path}")
    from google.oauth2 import service_account

    scopes = [
        "https://www.googleapis.com/auth/webmasters",
        "https://www.googleapis.com/auth/webmasters.readonly",
    ]
    return service_account.Credentials.from_service_account_file(key_path, scopes=scopes)


def cmd_status(site_url: str, sa_path: str) -> int:
    """Search Console 上のサイト一覧および対象サイトの権限レベルを確認する。"""
    print(f"[gsc:status] サービスアカウント認証: {sa_path}")
    creds = get_credentials(sa_path)
    from googleapiclient.discovery import build

    service = build("searchconsole", "v1", credentials=creds)

    print("[gsc:status] 登録プロパティ一覧の取得:")
    sites = service.sites().list().execute()
    entries = sites.get("siteEntry", [])
    matched_entry = None
    for s in entries:
        url = s.get("siteUrl", "")
        perm = s.get("permissionLevel", "")
        print(f"  - {url} (permission: {perm})")
        if url.rstrip("/") == site_url.rstrip("/"):
            matched_entry = s

    if matched_entry:
        print(f"\n[gsc:status] 対象サイト '{site_url}' の状態:")
        print(f"  permissionLevel: {matched_entry.get('permissionLevel')}")
        if matched_entry.get("permissionLevel") in ("siteFullUser", "siteOwner"):
            print("  -> 所有者・フルユーザー権限が確認されました。")
            return 0
        else:
            print(f"  -> 警告: 権限が制限されています ({matched_entry.get('permissionLevel')})。")
            return 2
    else:
        print(f"\n[gsc:status] 対象サイト '{site_url}' はサービスアカウントに未共有または未登録です。")
        return 1


def cmd_submit_sitemap(site_url: str, sitemap_url: str, sa_path: str) -> int:
    """サイトマップを Search Console に送信する。"""
    print(f"[gsc:sitemap] サイトマップ送信: site={site_url}, sitemap={sitemap_url}")
    creds = get_credentials(sa_path)
    from googleapiclient.discovery import build

    service = build("searchconsole", "v1", credentials=creds)

    try:
        service.sitemaps().submit(siteUrl=site_url, feedpath=sitemap_url).execute()
        print("[gsc:sitemap] 送信成功")
        return 0
    except Exception as e:
        print(f"[gsc:sitemap] 送信エラー: {e}")
        return 1


def cmd_inspect(url: str, site_url: str, sa_path: str) -> int:
    """URL Inspection API でインデックス登録状況を照会する。"""
    print(f"[gsc:inspect] URL検査: url={url}, site={site_url}")
    creds = get_credentials(sa_path)
    from google.auth.transport.requests import AuthorizedSession

    session = AuthorizedSession(creds)
    endpoint = "https://searchconsole.googleapis.com/v1/urlInspection/index:inspect"
    payload = {
        "inspectionUrl": url,
        "siteUrl": site_url,
        "languageCode": "ja",
    }
    res = session.post(endpoint, json=payload)
    print(f"[gsc:inspect] HTTPステータス: {res.status_code}")
    try:
        data = res.json()
        print(json.dumps(data, indent=2, ensure_ascii=False))
    except Exception:
        print(res.text)

    return 0 if res.status_code == 200 else 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Search Console 管理ツール")
    parser.add_argument(
        "--sa",
        dest="sa_path",
        default=DEFAULT_SA_PATH,
        help="サービスアカウント JSON ファイルパス",
    )
    parser.add_argument(
        "--site-url",
        dest="site_url",
        default=DEFAULT_SITE_URL,
        help="Search Console サイトURL（例: https://count.it-araiguma.com/）",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # status
    subparsers.add_parser("status", help="プロパティ登録・権限状態の確認")

    # submit-sitemap
    p_sitemap = subparsers.add_parser("submit-sitemap", help="サイトマップの送信")
    p_sitemap.add_argument(
        "--sitemap-url",
        dest="sitemap_url",
        default=DEFAULT_SITEMAP_URL,
        help="送信するサイトマップURL",
    )

    # inspect
    p_inspect = subparsers.add_parser("inspect", help="URL Inspection API による検査")
    p_inspect.add_argument("url", help="検査対象のURL（例: https://count.it-araiguma.com/）")

    args = parser.parse_args()

    if args.command == "status":
        return cmd_status(args.site_url, args.sa_path)
    elif args.command == "submit-sitemap":
        return cmd_submit_sitemap(args.site_url, args.sitemap_url, args.sa_path)
    elif args.command == "inspect":
        return cmd_inspect(args.url, args.site_url, args.sa_path)

    return 0


if __name__ == "__main__":
    sys.exit(main())
