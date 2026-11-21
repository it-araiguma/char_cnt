#!/usr/bin/env python3
"""Google Search Console の登録状況確認・サイトマップ送信・URL検査・検索パフォーマンス取得スクリプト。

使用法:
  python3 scripts/gsc_tool.py status
  python3 scripts/gsc_tool.py submit-sitemap [--sitemap-url <url>]
  python3 scripts/gsc_tool.py inspect <url>
  python3 scripts/gsc_tool.py analytics [--dimension query|page|both] [--days 28] [--start YYYY-MM-DD] [--end YYYY-MM-DD]
"""

from __future__ import annotations

import argparse
import datetime
import json
import os
import sys
from typing import Any, Dict, List, Optional

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


def _resolve_date_range(
    start: Optional[str], end: Optional[str], days: int
) -> tuple[str, str]:
    """開始日・終了日を YYYY-MM-DD 形式で解決する。"""
    if days <= 0:
        raise ValueError("--days は 1 以上を指定してください。")
    end_date = (
        datetime.date.fromisoformat(end) if end else datetime.date.today()
    )
    start_date = (
        datetime.date.fromisoformat(start)
        if start
        else end_date - datetime.timedelta(days=days)
    )
    if start_date > end_date:
        raise ValueError(f"開始日 ({start_date}) が終了日 ({end_date}) より後になっています。")
    return start_date.isoformat(), end_date.isoformat()


def _fetch_search_analytics(
    service: Any,
    site_url: str,
    start_date: str,
    end_date: str,
    dimension: str,
    row_limit: int,
) -> List[Dict[str, Any]]:
    """Search Analytics API から指定ディメンションの検索パフォーマンスを取得する。"""
    body = {
        "startDate": start_date,
        "endDate": end_date,
        "dimensions": [dimension],
        "rowLimit": row_limit,
    }
    res = service.searchanalytics().query(siteUrl=site_url, body=body).execute()
    return res.get("rows", [])


def cmd_analytics(
    site_url: str,
    sa_path: str,
    dimension: str,
    start: Optional[str],
    end: Optional[str],
    days: int,
    row_limit: int,
) -> int:
    """Search Analytics API でクエリ別・ページ別の表示回数・クリック・掲載順位を取得する。"""
    try:
        start_date, end_date = _resolve_date_range(start, end, days)
    except ValueError as e:
        print(f"[gsc:analytics] 引数エラー: {e}")
        return 2

    print(
        f"[gsc:analytics] 検索パフォーマンス取得: site={site_url}, 期間={start_date}〜{end_date}, dimension={dimension}"
    )
    creds = get_credentials(sa_path)
    from googleapiclient.discovery import build

    service = build("searchconsole", "v1", credentials=creds)
    target_dims = ["query", "page"] if dimension == "both" else [dimension]
    dim_labels = {"query": "クエリ", "page": "ページ"}

    try:
        for dim in target_dims:
            rows = _fetch_search_analytics(
                service, site_url, start_date, end_date, dim, row_limit
            )
            label = dim_labels[dim]
            print(f"\n[{label}別] ({len(rows)}件)")
            if not rows:
                print("  (データなし)")
                continue

            total_clicks = sum(int(r.get("clicks", 0)) for r in rows)
            total_impressions = sum(int(r.get("impressions", 0)) for r in rows)
            print(f"  {label}\tクリック\t表示回数\tCTR\t掲載順位")
            for r in rows:
                key = r.get("keys", ["-"])[0]
                clicks = int(r.get("clicks", 0))
                impressions = int(r.get("impressions", 0))
                ctr = float(r.get("ctr", 0.0)) * 100
                position = float(r.get("position", 0.0))
                print(
                    f"  {key}\t{clicks}\t{impressions}\t{ctr:.1f}%\t{position:.1f}"
                )
            print(f"  合計\t{total_clicks}\t{total_impressions}\t-\t-")
        return 0
    except Exception as e:
        print(f"[gsc:analytics] 取得エラー: {e}")
        return 1


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

    # analytics
    p_analytics = subparsers.add_parser(
        "analytics",
        aliases=["search-analytics"],
        help="Search Analytics API による検索パフォーマンス取得",
    )
    p_analytics.add_argument(
        "--dimension",
        "-d",
        choices=["query", "page", "both"],
        default="both",
        help="集計ディメンション（既定: both）",
    )
    p_analytics.add_argument(
        "--days",
        type=int,
        default=28,
        help="--start 未指定時の遡及日数（既定: 28）",
    )
    p_analytics.add_argument(
        "--start",
        default=None,
        help="開始日（YYYY-MM-DD、既定: 終了日の --days 日前）",
    )
    p_analytics.add_argument(
        "--end",
        default=None,
        help="終了日（YYYY-MM-DD、既定: 本日）",
    )
    p_analytics.add_argument(
        "--limit",
        type=int,
        default=100,
        help="取得件数上限（既定: 100）",
    )

    args = parser.parse_args()

    if args.command == "status":
        return cmd_status(args.site_url, args.sa_path)
    elif args.command == "submit-sitemap":
        return cmd_submit_sitemap(args.site_url, args.sitemap_url, args.sa_path)
    elif args.command == "inspect":
        return cmd_inspect(args.url, args.site_url, args.sa_path)
    elif args.command in ("analytics", "search-analytics"):
        return cmd_analytics(
            args.site_url,
            args.sa_path,
            args.dimension,
            args.start,
            args.end,
            args.days,
            args.limit,
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())
