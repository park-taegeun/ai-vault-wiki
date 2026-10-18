#!/usr/bin/env python3
"""Velog → _private/raw/velog/ 수집기 (LLM 없이 동작).

Velog 공개 GraphQL API에서 글 목록과 본문(마크다운)을 받아 원본 창고에 저장한다.
원본은 '추가만' 원칙이라 기존 파일은 절대 덮어쓰지 않는다.

사용법 (볼트 루트에서):
  python3 .tools/velog_fetch.py --list                 # 시리즈별 전체/저장됨/새 글 수만 보기
  python3 .tools/velog_fetch.py                        # 새 글만 저장
  python3 .tools/velog_fetch.py --series "LAB"         # 특정 시리즈만 (여러 번 지정 가능)
  python3 .tools/velog_fetch.py --limit 20             # 이번에 최대 20편만 (처음 대량 백필용)
  python3 .tools/velog_fetch.py --updates              # 저장 후 수정된 글도 새 버전 파일로 저장
  python3 .tools/velog_fetch.py --dry-run              # 저장하지 않고 무엇을 할지만 출력
"""
import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import date

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
OUT = os.path.join(ROOT, "_private", "raw", "velog")
API = "https://v2.velog.io/graphql"
DEFAULT_USER = os.environ.get("VELOG_USERNAME", "xorms")
PAGE = 50
POLITE_DELAY = 0.3  # 초. Velog 서버에 부담 주지 않게 요청 사이 간격


# ── API ────────────────────────────────────────────
def gql(query):
    req = urllib.request.Request(
        API,
        data=json.dumps({"query": query}).encode(),
        headers={"Content-Type": "application/json", "User-Agent": "ai-vault-velog-wiki/1.0"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        res = json.load(r)
    if res.get("errors"):
        raise RuntimeError(f"Velog API 오류: {res['errors'][0].get('message')}")
    return res["data"]


def lit(s):
    """GraphQL 문자열 리터럴 (JSON 이스케이프와 호환)."""
    return json.dumps(s, ensure_ascii=False)


def list_posts(user):
    """전체 글 목록. 페이지 경계에서 같은 글이 두 번 와도 한 번만 돌려준다."""
    seen_ids = set()
    for p in _list_posts_raw(user):
        if p["id"] not in seen_ids:
            seen_ids.add(p["id"])
            yield p


def _list_posts_raw(user):
    cursor = None
    while True:
        args = f"username: {lit(user)}, limit: {PAGE}" + (f", cursor: {lit(cursor)}" if cursor else "")
        batch = gql(f"{{ posts({args}) {{ id title url_slug released_at updated_at series {{ name }} }} }}")["posts"] or []
        yield from batch
        if len(batch) < PAGE:
            return
        cursor = batch[-1]["id"]
        time.sleep(POLITE_DELAY)


def series_counts(user):
    """Velog가 알려주는 시리즈별 글 수. 목록 누락을 잡는 교차 확인용 (실패하면 None)."""
    try:
        rows = gql(f"{{ series_list(username: {lit(user)}) {{ name posts_count }} }}")["series_list"] or []
        return {(r.get("name") or "").strip(): r.get("posts_count") for r in rows}
    except Exception:
        return None


POST_FIELDS = "id title url_slug body tags is_private released_at updated_at series { name }"


def fetch_post(user, slug):
    return gql(f"{{ post(username: {lit(user)}, url_slug: {lit(slug)}) {{ {POST_FIELDS} }} }}")["post"]


def fetch_post_by_id(pid):
    """글 고유 id로 조회. 주소(slug)가 겹치거나 깨진 글도 정확히 가져온다. 실패하면 None."""
    try:
        return gql(f"{{ post(id: {lit(pid)}) {{ {POST_FIELDS} }} }}")["post"]
    except Exception:
        return None


def fetch_exact(user, p):
    """id 조회를 먼저 시도하고, 안 되면 주소 조회로 대신한다."""
    full = fetch_post_by_id(p["id"])
    if full and full.get("id") == p["id"]:
        return full
    return fetch_post(user, p["url_slug"])


# ── 저장소 ─────────────────────────────────────────
def safe(s, n=80):
    s = re.sub(r'[\\/:*?"<>|#^\[\]\s]+', "-", s or "").strip("-.")
    return s[:n] or "untitled"


def series_name(p):
    return ((p.get("series") or {}).get("name") or "").strip() or "_시리즈없음"  # Velog 시리즈 이름엔 앞뒤 공백이 섞여 있을 수 있음


def saved_versions():
    """저장된 원본에서 velog_id → 가장 최근 velog_updated_at."""
    seen = {}
    if not os.path.isdir(OUT):
        return seen
    for dp, _, fs in os.walk(OUT):
        for f in fs:
            if not f.endswith(".md"):
                continue
            with open(os.path.join(dp, f), encoding="utf-8") as fh:
                head = fh.read(2000)
            m_id = re.search(r"^velog_id:\s*(\S+)", head, re.M)
            m_up = re.search(r"^velog_updated_at:\s*(\S+)", head, re.M)
            if m_id:
                pid, up = m_id.group(1), (m_up.group(1) if m_up else "")
                if up >= seen.get(pid, ""):
                    seen[pid] = up
    return seen


def write_new(post, user, version=False):
    d = os.path.join(OUT, safe(series_name(post), 60))
    os.makedirs(d, exist_ok=True)
    stem = f"{post['released_at'][:10]}-{safe(post['url_slug'])}"
    if version:
        stem += f"@{post['updated_at'][:10]}"
    path, i = os.path.join(d, stem + ".md"), 2
    while os.path.exists(path):  # 원본은 절대 덮어쓰지 않는다
        path = os.path.join(d, f"{stem}-{i}.md")
        i += 1
    url = f"https://velog.io/@{user}/{urllib.parse.quote(post['url_slug'])}"
    fm = "\n".join([
        "---",
        f"source: {url}",
        f"velog_id: {post['id']}",
        f"title: {lit(post['title'])}",
        f"series: {lit(series_name(post))}",
        f"tags: {json.dumps(post.get('tags') or [], ensure_ascii=False)}",
        f"released_at: {post['released_at']}",
        f"velog_updated_at: {post['updated_at']}",
        f"fetched: {date.today()}",
        "---",
        "",
    ])
    with open(path, "x", encoding="utf-8") as fh:
        fh.write(fm + (post.get("body") or ""))
    return os.path.relpath(path, ROOT)


# ── 실행 ───────────────────────────────────────────
def main(argv=None):
    ap = argparse.ArgumentParser(description="Velog 글을 원본 창고로 가져오기")
    ap.add_argument("--user", default=DEFAULT_USER)
    ap.add_argument("--series", action="append", help="이 시리즈만 (여러 번 지정 가능)")
    ap.add_argument("--limit", type=int, default=0, help="이번 실행에서 최대 저장 편수 (0=제한 없음)")
    ap.add_argument("--updates", action="store_true", help="수정된 글도 새 버전 파일로 저장")
    ap.add_argument("--list", action="store_true", help="저장하지 않고 시리즈별 현황만 출력")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)

    seen = saved_versions()
    wanted = {s.strip() for s in a.series or []}
    posts = [p for p in list_posts(a.user) if not wanted or series_name(p) in wanted]

    todo = []
    for p in posts:
        if p["id"] not in seen:
            todo.append((p, False))
        elif a.updates and p["updated_at"] > seen[p["id"]]:
            todo.append((p, True))

    if a.list or a.dry_run:
        stats = {}
        for p in posts:
            s = stats.setdefault(series_name(p), [0, 0, 0])
            s[0] += 1
            s[1] += p["id"] in seen
            s[2] += p["id"] not in seen
        print(f"# Velog @{a.user} — 글 {len(posts)}편\n")
        print("| 시리즈 | 전체 | 저장됨 | 새 글 |\n|---|---|---|---|")
        for name, (t, s, n) in sorted(stats.items(), key=lambda kv: -kv[1][0]):
            print(f"| {name} | {t} | {s} | {n} |")
        counts = series_counts(a.user)
        if counts is not None:
            for name, (t, _, _) in stats.items():
                want = counts.get(name)
                if isinstance(want, int) and want != t:
                    print(f"⚠️  [{name}] Velog 기준 {want}편인데 목록에서 {t}편만 받았습니다 — 목록 누락 가능성")
        missing = [p for p in posts if p["id"] not in seen]
        if missing and len(missing) <= 20:
            print("\n아직 저장 안 된 글:")
            for p in missing:
                print(f"- [{series_name(p)}] {p['title']}")
        upd = sum(1 for _, v in todo if v)
        print(f"\n가져올 대상: 새 글 {len(todo) - upd}편" + (f", 수정본 {upd}편" if a.updates else ""))
        return 0

    todo.sort(key=lambda t: t[0]["released_at"])  # 오래된 글부터 → 위키에 시간 순서대로 쌓임
    if a.limit:
        todo = todo[: a.limit]
    saved, skipped = [], []
    for p, is_update in todo:
        try:
            full = fetch_exact(a.user, p)
        except Exception as e:  # 한 편이 실패해도 나머지는 계속
            skipped.append((p, f"오류: {e}"))
            continue
        if not full:
            skipped.append((p, "본문 조회 결과 없음 (주소가 바뀌었거나 삭제됨)"))
            continue
        if full.get("is_private"):
            skipped.append((p, "비공개 글"))
            continue
        if full.get("id") != p["id"]:  # 주소(slug)로 조회했는데 다른 글이 나옴 → 저장하면 엉뚱한 글이 중복 저장됨
            skipped.append((p, f"주소 '{p['url_slug']}'로 조회했더니 다른 글이 나옴: "
                               f"'{full.get('title')}' (id {str(full.get('id'))[:8]}, 주소 '{full.get('url_slug')}')"))
            continue
        saved.append(write_new(full, a.user, version=is_update))
        time.sleep(POLITE_DELAY)

    print(f"저장 {len(saved)}편 → _private/raw/velog/")
    for s in saved:
        print(f"- {s}")
    if skipped:
        print(f"\n건너뜀 {len(skipped)}편 (다음 실행 때 다시 시도합니다):")
        for p, why in skipped:
            print(f"- [{series_name(p)}] {p['title']} — {why}")
    remain = len([1 for p in posts if p["id"] not in seen]) - len([1 for _, u in todo if not u])
    if a.limit and remain > 0:
        print(f"\n아직 {remain}편 남음 — 같은 명령을 다시 실행하면 이어서 가져옵니다.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except urllib.error.URLError as e:
        print(f"❌ Velog에 연결할 수 없습니다: {e.reason}", file=sys.stderr)
        sys.exit(1)
