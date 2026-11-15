#!/usr/bin/env python3
"""GA4 Data API で文字数カウントの PV・セッション実測値を取得するスクリプト。

SEOクラスタ方針（docs/seo-cluster-strategy.md）の判定ゲートで使用する実測値を取得する。

使用法:
  python3 scripts/ga4_report.py pages [--start 28daysAgo] [--end today]
  python3 scripts/ga4_report.py channels [--start 28daysAgo] [--end today]
"""

from __future__ import annotations

import argparse
import os
import sys
from typing import Any, Dict, List

DEFAULT_PROPERTY_ID = "462068704"
DEFAULT_SA_PATH = os.path.expanduser(
    os.getenv(
        "GOOGLE_SERVICE_ACCOUNT_FILE",
        "/home/aulani/develop/araiguma-blog/configs/service_accounts/search-console-service-account.json",
    )
)


def get_session(key_path: str):
    if not os.path.exists(key_path):
        raise FileNotFoundError(f"サービスアカウントファイルが見つかりません: {key_path}")
    from google.auth.transport.requests import AuthorizedSession
    from google.oauth2 import service_account

    scopes = ["https://www.googleapis.com/auth/analytics.readonly"]
    creds = service_account.Credentials.from_service_account_file(key_path, scopes=scopes)
    return AuthorizedSession(creds)


def run_report(
    property_id: str, sa_path: str, dimension: str, start: str, end: str
) -> List[Dict[str, Any]]:
    """指定ディメンションごとの PV・セッションを取得する。"""
    session = get_session(sa_path)
    endpoint = f"https://analyticsdata.googleapis.com/v1beta/properties/{property_id}:runReport"
    payload = {
        "dateRanges": [{"startDate": start, "endDate": end}],
        "dimensions": [{"name": dimension}],
        "metrics": [{"name": "screenPageViews"}, {"name": "sessions"}],
        "orderBys": [{"metric": {"metricName": "screenPageViews"}, "desc": True}],
    }
    res = session.post(endpoint, json=payload)
    if res.status_code != 200:
        raise RuntimeError(f"GA4 Data API エラー: HTTP {res.status_code} {res.text[:500]}")
    rows = res.json().get("rows", [])
    return [
        {
            "key": r["dimensionValues"][0]["value"],
            "views": int(r["metricValues"][0]["value"]),
            "sessions": int(r["metricValues"][1]["value"]),
        }
        for r in rows
    ]


def cmd_report(args: argparse.Namespace, dimension: str, label: str) -> int:
    print(f"[ga4:{args.command}] property={args.property_id} 期間={args.start}〜{args.end}")
    try:
        rows = run_report(args.property_id, args.sa_path, dimension, args.start, args.end)
    except Exception as e:
        print(f"[ga4:{args.command}] 取得エラー: {e}")
        return 1

    total_views = sum(r["views"] for r in rows)
    total_sessions = sum(r["sessions"] for r in rows)
    print(f"  {label}\tPV\tセッション")
    for r in rows:
        print(f"  {r['key']}\t{r['views']}\t{r['sessions']}")
    print(f"  合計\t{total_views}\t{total_sessions}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="GA4 実測値取得ツール")
    parser.add_argument(
        "--sa",
        dest="sa_path",
        default=DEFAULT_SA_PATH,
        help="サービスアカウント JSON ファイルパス",
    )
    parser.add_argument(
        "--property-id",
        dest="property_id",
        default=DEFAULT_PROPERTY_ID,
        help="GA4 プロパティID（既定: 文字数カウント 462068704）",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)
    for name, help_text in (
        ("pages", "ページパス別の PV・セッション"),
        ("channels", "流入チャネル別の PV・セッション（Organic Search の確認用）"),
    ):
        p = subparsers.add_parser(name, help=help_text)
        p.add_argument("--start", default="28daysAgo", help="開始日（YYYY-MM-DD / NdaysAgo）")
        p.add_argument("--end", default="today", help="終了日（YYYY-MM-DD / today）")

    args = parser.parse_args()

    if args.command == "pages":
        return cmd_report(args, "pagePath", "ページ")
    elif args.command == "channels":
        return cmd_report(args, "sessionDefaultChannelGroup", "チャネル")

    return 0


if __name__ == "__main__":
    sys.exit(main())
