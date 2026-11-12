#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError


APP_NAME = "小河狸合同助手"
DEFAULT_PORT_RANGE = range(8870, 8891)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SAMPLE_FILE = os.path.join(SCRIPT_DIR, "..", "references", "sample_data.json")


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")


def parse_ports(value: str | None) -> list[int]:
    if not value:
        return list(DEFAULT_PORT_RANGE)
    ports: list[int] = []
    for part in value.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            start, end = part.split("-", 1)
            ports.extend(range(int(start), int(end) + 1))
        else:
            ports.append(int(part))
    return sorted(dict.fromkeys(ports))


def http_json(url: str, timeout: float = 2.5, method: str = "GET") -> dict[str, Any]:
    req = Request(
        url,
        headers={"Accept": "application/json", "User-Agent": "LittleBeaverContractAssistantSkill/1.0.1"},
        method=method,
    )
    with urlopen(req, timeout=timeout) as resp:
        charset = resp.headers.get_content_charset() or "utf-8"
        return json.loads(resp.read().decode(charset))


def http_get_json(url: str, timeout: float = 2.5) -> dict[str, Any]:
    return http_json(url, timeout=timeout, method="GET")


def normalize_base_url(value: str) -> str:
    value = value.strip().rstrip("/")
    if not value:
        raise ValueError("base_url is empty")
    if not value.startswith(("http://", "https://")):
        value = "http://" + value
    return value


def discover_base_url(base_url: str | None = None, ports: list[int] | None = None) -> str:
    candidates: list[str] = []
    env_url = os.environ.get("CONTRACT_ASSISTANT_BASE_URL")
    if base_url:
        candidates.append(normalize_base_url(base_url))
    if env_url:
        candidates.append(normalize_base_url(env_url))
    for port in ports or parse_ports(os.environ.get("CONTRACT_ASSISTANT_PORTS")):
        candidates.append(f"http://127.0.0.1:{port}")

    seen = set()
    for candidate in candidates:
        if candidate in seen:
            continue
        seen.add(candidate)
        try:
            health = http_get_json(f"{candidate}/api/skill/health", timeout=0.6)
        except (OSError, URLError, HTTPError, TimeoutError, json.JSONDecodeError):
            continue
        if not health.get("success"):
            continue
        # 优先用 /api/metadata 的 app 字段确认身份；缺失时退回 /api/skill/info
        app_name = None
        try:
            meta = http_get_json(f"{candidate}/api/metadata", timeout=0.6)
            if meta.get("success"):
                app_name = meta.get("app")
        except (OSError, URLError, HTTPError, TimeoutError, json.JSONDecodeError):
            app_name = None
        if app_name is None:
            try:
                info = http_get_json(f"{candidate}/api/skill/info", timeout=0.6)
                if info.get("success"):
                    data = info.get("data") or {}
                    app_name = data.get("app") or data.get("name")
            except (OSError, URLError, HTTPError, TimeoutError, json.JSONDecodeError):
                app_name = None
        if app_name == APP_NAME:
            return candidate
    raise RuntimeError("未发现正在运行的小河狸合同助手。请先打开软件，再重试。")


def build_query(args: argparse.Namespace, fields: list[str]) -> str:
    pairs: list[tuple[str, str]] = []
    for field in fields:
        value = getattr(args, field.replace("-", "_"), None)
        if value is None or value == "":
            continue
        if isinstance(value, list):
            pairs.extend((field, str(item)) for item in value if item not in (None, ""))
        else:
            pairs.append((field, str(value)))
    return urlencode(pairs)


def request_skill(base_url: str, path: str, query: str = "", method: str = "GET") -> dict[str, Any]:
    url = f"{base_url}{path}"
    if query:
        url += "?" + query
    data = http_json(url, method=method)
    if not data.get("success"):
        raise RuntimeError(data.get("error") or f"API request failed: {path}")
    return data


def load_sample(command: str) -> dict[str, Any] | None:
    try:
        with open(SAMPLE_FILE, encoding="utf-8") as fh:
            samples = json.load(fh)
    except (OSError, json.JSONDecodeError):
        return None
    return samples.get(command)


def print_json(data: Any) -> None:
    print(json.dumps(data, ensure_ascii=False, indent=2))


def add_common_filters(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--company-id", action="append", dest="company_id", help="公司 ID，可重复传入")
    parser.add_argument("--start", help="开始日期，格式 yyyy-mm-dd")
    parser.add_argument("--end", help="结束日期，格式 yyyy-mm-dd")


def main() -> int:
    root = argparse.ArgumentParser(description="读取本机小河狸合同助手数据")
    root.add_argument("--base-url", help="合同助手地址，例如 http://127.0.0.1:8870")
    root.add_argument("--ports", help="自动发现端口，例如 8870-8890,9000")
    root.add_argument("--demo", action="store_true", help="强制使用示例数据（演示/离线模式，不连接本机应用）")
    root.add_argument("--strict", action="store_true", help="检测不到本机应用时直接报错，不回退示例数据")
    sub = root.add_subparsers(dest="command", required=True)

    sub.add_parser("health")
    sub.add_parser("info")
    sub.add_parser("companies")

    summary = sub.add_parser("summary")
    add_common_filters(summary)

    contracts = sub.add_parser("contracts")
    add_common_filters(contracts)
    contracts.add_argument("--direction", choices=["销售", "采购"], help="合同方向")
    contracts.add_argument("--status", help="合同状态，如 active/terminated/voided")
    contracts.add_argument("--keyword")
    contracts.add_argument("--page", type=int, default=1)
    contracts.add_argument("--page-size", type=int, default=50)

    contract_nodes = sub.add_parser("contract-nodes")
    add_common_filters(contract_nodes)
    contract_nodes.add_argument("--page", type=int, default=1)
    contract_nodes.add_argument("--page-size", type=int, default=50)

    contract_links = sub.add_parser("contract-links")
    add_common_filters(contract_links)

    biz_entries = sub.add_parser("biz-entries")
    add_common_filters(biz_entries)
    biz_entries.add_argument("--keyword")

    projects = sub.add_parser("projects")
    add_common_filters(projects)

    coverage = sub.add_parser("coverage")
    add_common_filters(coverage)

    expiring = sub.add_parser("expiring")
    add_common_filters(expiring)
    expiring.add_argument("--days", type=int, default=90, help="到期窗口天数")

    parties = sub.add_parser("parties")
    add_common_filters(parties)
    parties.add_argument("--keyword")

    args = root.parse_args()
    try:
        if args.demo:
            sample = load_sample(args.command)
            if sample is None:
                raise RuntimeError(f"演示模式缺少 {args.command} 的示例数据")
            print("ℹ️ 演示/离线模式：以下为示例数据，未连接本机应用。", file=sys.stderr)
            print_json(sample)
            return 0
        try:
            base_url = discover_base_url(args.base_url, parse_ports(args.ports))
        except RuntimeError as exc:
            if args.strict:
                raise
            sample = load_sample(args.command)
            if sample is not None:
                print("⚠️ 未检测到本机小河狸合同助手，以下为示例数据（演示/离线模式）。打开软件后重试可获取真实数据。",
                      file=sys.stderr)
                print_json(sample)
                return 0
            raise
        if args.command == "health":
            print_json(request_skill(base_url, "/api/skill/health"))
        elif args.command == "info":
            print_json(request_skill(base_url, "/api/skill/info"))
        elif args.command == "companies":
            print_json(request_skill(base_url, "/api/skill/companies"))
        elif args.command == "summary":
            print_json(request_skill(base_url, "/api/skill/summary", build_query(args, ["company_id", "start", "end"])))
        elif args.command == "contracts":
            print_json(request_skill(base_url, "/api/skill/contracts", build_query(args, ["company_id", "start", "end", "direction", "status", "keyword", "page", "page_size"])))
        elif args.command == "contract-nodes":
            print_json(request_skill(base_url, "/api/skill/contract-nodes", build_query(args, ["company_id", "start", "end", "page", "page_size"])))
        elif args.command == "contract-links":
            print_json(request_skill(base_url, "/api/skill/contract-links", build_query(args, ["company_id", "start", "end"])))
        elif args.command == "biz-entries":
            print_json(request_skill(base_url, "/api/skill/biz-entries", build_query(args, ["company_id", "start", "end", "keyword"])))
        elif args.command == "projects":
            print_json(request_skill(base_url, "/api/skill/projects", build_query(args, ["company_id", "start", "end"])))
        elif args.command == "coverage":
            print_json(request_skill(base_url, "/api/skill/coverage", build_query(args, ["company_id", "start", "end"])))
        elif args.command == "expiring":
            print_json(request_skill(base_url, "/api/skill/expiring", build_query(args, ["company_id", "start", "end", "days"])))
        elif args.command == "parties":
            print_json(request_skill(base_url, "/api/skill/parties", build_query(args, ["company_id", "start", "end", "keyword"])))
        return 0
    except Exception as exc:
        print(json.dumps({"success": False, "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
