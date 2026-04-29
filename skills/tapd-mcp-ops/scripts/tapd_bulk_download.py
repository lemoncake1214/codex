#!/usr/bin/env python3
import argparse
import json
import os
import re
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen


def parse_version_text(text: str):
    if not text:
        return None
    m = re.search(r"v?(\d+)(?:\.(\d+))?", text.strip(), flags=re.IGNORECASE)
    if not m:
        return None
    major = int(m.group(1))
    minor = int(m.group(2) or 0)
    return major, minor


def parse_version_ranges(raw: str):
    if not raw.strip():
        return []
    ranges = []
    for part in [x.strip() for x in raw.split(",") if x.strip()]:
        if "-" not in part:
            raise ValueError(f"invalid range: {part}")
        left, right = [x.strip() for x in part.split("-", 1)]
        start = parse_version_text(left)
        end = parse_version_text(right)
        if not start or not end:
            raise ValueError(f"invalid version in range: {part}")
        if start > end:
            raise ValueError(f"range start > end: {part}")
        ranges.append((start, end))
    return ranges


def in_ranges(version_tuple, ranges):
    if version_tuple is None:
        return False
    for start, end in ranges:
        if start <= version_tuple <= end:
            return True
    return False


def pick_version_value(story_obj: dict, fields: list[str]):
    for key in fields:
        value = story_obj.get(key)
        if value:
            return str(value)
    return ""


def fetch_stories(base_url: str, token: str, workspace_id: str, page: int, limit: int):
    query = urlencode({"workspace_id": workspace_id, "page": page, "limit": limit})
    url = f"{base_url.rstrip('/')}/stories?{query}"
    req = Request(url, headers={"access_token": token})
    with urlopen(req, timeout=30) as resp:
        payload = json.loads(resp.read().decode("utf-8"))
    return payload.get("data", [])


def fetch_all_stories(base_url: str, token: str, workspace_id: str, limit: int = 200):
    page = 1
    all_items = []
    while True:
        items = fetch_stories(base_url, token, workspace_id, page=page, limit=limit)
        if not items:
            break
        all_items.extend(items)
        if len(items) < limit:
            break
        page += 1
    return all_items


def matches(story: dict, status: str, owner: str, updated_after: str, version_ranges, version_fields: list[str]):
    obj = story.get("Story", {})
    if status and str(obj.get("status", "")) != status:
        return False
    if owner and str(obj.get("owner", "")) != owner:
        return False
    if updated_after and str(obj.get("modified", "")) < updated_after:
        return False

    if version_ranges:
        v_raw = pick_version_value(obj, version_fields)
        if not in_ranges(parse_version_text(v_raw), version_ranges):
            return False

    return True


def render_markdown(story: dict, version_fields: list[str]):
    s = story.get("Story", {})
    ver = pick_version_value(s, version_fields)
    return f"""# {s.get('name','')}

- ID: {s.get('id','')}
- 状态: {s.get('status','')}
- 负责人: {s.get('owner','')}
- 版本: {ver}
- 更新时间: {s.get('modified','')}

## 描述

{s.get('description','')}
"""


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace-id", required=True)
    parser.add_argument("--status", default="")
    parser.add_argument("--owner", default="")
    parser.add_argument("--updated-after", default="")
    parser.add_argument("--version-ranges", default="", help='例如: "v1.0-v1.4,v1.8-v2.5"')
    parser.add_argument("--version-fields", default="version,release,iteration", help="从 Story 字段中依次取版本值")
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--format", choices=["json", "markdown"], default="markdown")
    parser.add_argument("--base-url", default="https://api.tapd.cn")
    args = parser.parse_args()

    token = os.getenv("TAPD_ACCESS_TOKEN", "")
    if not token:
        raise SystemExit("Missing TAPD_ACCESS_TOKEN env var")

    ranges = parse_version_ranges(args.version_ranges)
    version_fields = [x.strip() for x in args.version_fields.split(",") if x.strip()]

    items = fetch_all_stories(args.base_url, token, args.workspace_id)
    filtered = [x for x in items if matches(x, args.status, args.owner, args.updated_after, ranges, version_fields)]

    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)

    for story in filtered:
        sid = story.get("Story", {}).get("id", "unknown")
        if args.format == "json":
            (out / f"{sid}.json").write_text(json.dumps(story, ensure_ascii=False, indent=2), encoding="utf-8")
        else:
            (out / f"{sid}.md").write_text(render_markdown(story, version_fields), encoding="utf-8")

    print(f"exported {len(filtered)} stories to {out}")


if __name__ == "__main__":
    main()
