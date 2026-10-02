#!/usr/bin/env python3
"""Fetch problem statements, examples and constraints from LeetCode.

Writes content/leetcode.json, which build.py reads. The cache is committed so
the site build never needs the network; re-run this only when adding problems.

    python3 fetch_leetcode.py            # fetch anything missing
    python3 fetch_leetcode.py --force    # refetch everything

Paid-only problems return no content. They are recorded with premium=True and
the entry is expected to supply its own description.
"""
from __future__ import annotations

import html as htmllib
import json
import pathlib
import re
import sys
import time
import urllib.error
import urllib.request

ROOT = pathlib.Path(__file__).parent
CACHE = ROOT / "content" / "leetcode.json"
API = "https://leetcode.com/graphql/"

QUERY = """
query q($t: String!) {
  question(titleSlug: $t) {
    questionFrontendId
    title
    difficulty
    isPaidOnly
    content
    topicTags { name }
  }
}
"""

HEADERS = {
    "Content-Type": "application/json",
    "Referer": "https://leetcode.com",
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
    ),
}


def api(slug: str) -> dict | None:
    body = json.dumps({"query": QUERY, "variables": {"t": slug}}).encode()
    req = urllib.request.Request(API, data=body, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=30) as resp:
        payload = json.load(resp)
    if payload.get("errors"):
        raise SystemExit(f"{slug}: {payload['errors']}")
    return payload["data"]["question"]


# ---------------------------------------------------------------- parsing

def clean(fragment: str) -> str:
    """Strip images and tags we do not render, normalise whitespace."""
    fragment = re.sub(r"<img[^>]*>", "", fragment)
    fragment = re.sub(r"</?(?:div|span|font|p)[^>]*>", "", fragment)
    fragment = fragment.replace("&nbsp;", " ")
    fragment = re.sub(r"[ \t]+", " ", fragment)
    return fragment.strip()


def strip_tags(fragment: str) -> str:
    fragment = re.sub(r"<[^>]+>", "", fragment)
    return htmllib.unescape(fragment).replace("\xa0", " ").strip()


def parse(content: str) -> dict:
    """Split LeetCode's HTML into statement paragraphs, examples, constraints."""
    # --- constraints: the list following the Constraints heading
    constraints: list[str] = []
    cut = re.split(r"<strong>\s*Constraints:?\s*</strong>", content)
    body = cut[0]
    if len(cut) > 1:
        tail = cut[1]
        follow = re.search(r"<strong>\s*Follow[ -]?up", tail)
        if follow:
            tail = tail[: follow.start()]
        for li in re.findall(r"<li>(.*?)</li>", tail, re.S):
            text = clean(li)
            if text:
                constraints.append(text)

    # --- examples. LeetCode uses two formats: older problems put them in a
    # <pre>, newer ones in <div class="example-block"> with one <p> per field.
    examples: list[dict] = []

    def record(got: dict) -> None:
        if got.get("input") or got.get("output"):
            examples.append(got)

    for block in re.findall(r'<div class="example-block"[^>]*>(.*?)</div>', body, re.S):
        got = {}
        for label, key in (("Input", "input"), ("Output", "output"),
                           ("Explanation", "explanation")):
            m = re.search(
                rf"<strong>\s*{label}\s*:?\s*</strong>:?(.*?)(?=<strong>|\Z)", block, re.S)
            if m:
                value = " ".join(strip_tags(m.group(1)).split())
                if value:
                    got[key] = value
        record(got)

    for pre in re.findall(r"<pre>(.*?)</pre>", body, re.S):
        text = strip_tags(pre)
        got = {}
        for label, key in (("Input", "input"), ("Output", "output"),
                           ("Explanation", "explanation")):
            m = re.search(
                rf"{label}\s*:?\s*\n?(.*?)(?=\n\s*(?:Input|Output|Explanation)\s*:?\s*\n|\Z)",
                text, re.S)
            if m:
                value = " ".join(m.group(1).split())
                if value:
                    got[key] = value
        record(got)

    # --- statement: everything before the first example marker
    head = re.split(r"<strong class=\"example\">|<pre>", body)[0]
    head = re.sub(r"<strong>\s*Example[^<]*</strong>", "", head)
    paras = []
    for chunk in re.split(r"</p>|<br\s*/?>", head):
        text = clean(chunk)
        text = re.sub(r"^<p[^>]*>", "", text).strip()
        if strip_tags(text):
            paras.append(text)

    return {"statement": paras, "examples": examples, "constraints": constraints}


# ---------------------------------------------------------------- main

def main() -> None:
    force = "--force" in sys.argv
    sys.path.insert(0, str(ROOT / "content"))
    import dsa as content

    slugs = []
    for topic in content.TOPICS:
        for section in topic.get("sections", []):
            for prob in section["problems"]:
                if prob.get("slug"):
                    slugs.append(prob["slug"])

    cache = {}
    if CACHE.exists() and not force:
        cache = json.loads(CACHE.read_text(encoding="utf-8"))

    todo = [s for s in slugs if s not in cache]
    print(f"{len(slugs)} slugs referenced, {len(todo)} to fetch")

    for i, slug in enumerate(todo, 1):
        try:
            q = api(slug)
        except urllib.error.HTTPError as exc:
            print(f"  [{i}/{len(todo)}] {slug}: HTTP {exc.code}")
            continue
        if q is None:
            print(f"  [{i}/{len(todo)}] {slug}: NOT FOUND - check the slug")
            continue

        entry = {
            "lc": int(q["questionFrontendId"]),
            "title": q["title"],
            "difficulty": q["difficulty"].lower(),
            "premium": bool(q["isPaidOnly"]),
            "tags": [t["name"] for t in q["topicTags"]],
        }
        if q["content"]:
            entry.update(parse(q["content"]))
        else:
            entry.update({"statement": [], "examples": [], "constraints": []})

        cache[slug] = entry
        flag = " PREMIUM" if entry["premium"] else ""
        print(f"  [{i}/{len(todo)}] {slug} -> {entry['lc']} "
              f"{entry['difficulty']}{flag}, {len(entry['constraints'])} constraints, "
              f"{len(entry['examples'])} examples")
        time.sleep(0.4)

    CACHE.parent.mkdir(exist_ok=True)
    CACHE.write_text(json.dumps(cache, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"wrote {CACHE.relative_to(ROOT)} ({len(cache)} problems)")


if __name__ == "__main__":
    main()
