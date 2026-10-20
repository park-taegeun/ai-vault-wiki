#!/usr/bin/env python3
"""LLM Wiki 결정론적 점검기.

LLM이 매번 파일을 다 읽어서 세면 느리고, 비싸고, 결과가 매번 달라진다.
세기·매칭·날짜 계산처럼 답이 하나로 정해지는 일은 이 스크립트가 하고,
Claude는 모순·중복 판단 같은 '의미'가 필요한 일만 맡는다.

사용법 (볼트 루트에서):
  python3 .tools/wiki_check.py lint            # 정비 리포트
  python3 .tools/wiki_check.py status          # 프로젝트·취업 대시보드
  python3 .tools/wiki_check.py pending         # 아직 넣지 않은 원본 목록 (본문 없는 목차 파일은 제외)
  python3 .tools/wiki_check.py pending --all   # 제외된 목차 파일 목록까지
  python3 .tools/wiki_check.py staged          # 공개 레포 커밋 게이트 (pre-commit)
  python3 .tools/wiki_check.py staged-private  # 비공개 레포 커밋 게이트 (_private pre-commit)
  python3 .tools/wiki_check.py public-gate     # 배포 직전 공개 파일 전수 검사 (GitHub Actions)
"""
import os
import re
import subprocess
import sys
from collections import defaultdict
from datetime import date, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from wiki_patterns import scan_text  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
PUBLIC = "wiki"
PRIV = "_private"
PRIVATE_WIKI = "_private/wiki"
RAW = "_private/raw"
LOG = "_private/log.md"
PUBLIC_DIRS = ("wiki", "eval")
INDEXES = {"wiki/index.md", "_private/wiki/private-index.md"}
PRIVATE_PATH_RE = re.compile(r"^(_private/|raw/|private/|\.obsidian/|99-Attachments/|log\.md$|\.env)")
LINK_RE = re.compile(r"\[\[([^\]|#]+)(?:#[^\]|]*)?(?:\|[^\]]*)?\]\]")
FENCE_RE = re.compile(r"```.*?```", re.S)
INLINE_CODE_RE = re.compile(r"`[^`\n]*`")
TODAY = date.today()
VELOG_LAST_OK = "_private/logs/velog-last-success"
VELOG_STALE_DAYS = 3
READINESS_WINDOW = 14     # 2단계 전환 판단 기간 (일)
READINESS_MIN_RUNS = 5    # 이 기간에 /velog-wiki를 최소 몇 번 돌려봤는지
READINESS_MAX_FIX = 1     # 사람이 고친 횟수가 이 이하이면 전환 검토 가능
ORDER = ["🚨 wiki → 비공개 링크", "🚨 공개 파일 안 비밀값·개인정보 의심", "📡 Velog 자동 수집 멈춤",
         "⚠️ 같은 이름 페이지 (링크 모호)", "⏰ 마감 지났는데 진행중/대기", "⚔️ 남아 있는 모순 표시", "🔗 끊긴 링크", "🏝 고아 페이지",
         "📇 목차에 없는 페이지", "🧾 프론트매터 누락 (type/modified)", "💤 30일 넘게 갱신 없는 진행중",
         "🧹 병합 안 된 초안 (drafts)", "📥 아직 넣지 않은 원본"]


# ── 파싱 ───────────────────────────────────────────
def read(path):
    with open(os.path.join(ROOT, path), encoding="utf-8", errors="replace") as f:
        return f.read()


def frontmatter(text):
    """--- 블록의 key: value만 읽는 최소 파서 (PyYAML 의존성 없이)."""
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    fm = {}
    for line in text[3:end].splitlines():
        if ":" in line and not line.startswith((" ", "\t", "#")):
            k, v = line.split(":", 1)
            fm[k.strip()] = v.split("#", 1)[0].strip().strip("'\"")
    return fm


def modified_of(fm):
    return to_date(fm.get("modified") or fm.get("updated") or "")


def to_date(s):
    try:
        y, m, d = map(int, s[:10].split("-"))
        return date(y, m, d)
    except Exception:
        return None


def links_in(text):
    body = INLINE_CODE_RE.sub("", FENCE_RE.sub("", text))
    return {os.path.splitext(os.path.basename(t.strip()))[0] for t in LINK_RE.findall(body)}


def md_files(top):
    out = []
    for dp, _, fs in os.walk(os.path.join(ROOT, top)):
        for f in fs:
            if f.endswith(".md"):
                out.append(os.path.relpath(os.path.join(dp, f), ROOT))
    return out


def files_under(top):
    out = []
    for dp, _, fs in os.walk(os.path.join(ROOT, top)):
        for f in fs:
            if not f.startswith("."):
                out.append(os.path.relpath(os.path.join(dp, f), ROOT))
    return sorted(out)


def name_of(p):
    return os.path.splitext(os.path.basename(p))[0]


# ── 그래프 ─────────────────────────────────────────
class Vault:
    def __init__(self):
        self.pages = sorted(md_files(PUBLIC) + md_files(PRIVATE_WIKI))
        self.text = {p: read(p) for p in self.pages}
        self.fm = {p: frontmatter(t) for p, t in self.text.items()}
        self.by_name = defaultdict(list)
        for p in self.pages:
            self.by_name[name_of(p)].append(p)
        self.out = {p: links_in(t) for p, t in self.text.items()}

    @staticmethod
    def is_public(p):
        return p.startswith(PUBLIC + "/")

    def resolves_to(self, name):
        return self.by_name.get(name, [])

    def private_only(self, name):
        targets = self.resolves_to(name)
        return bool(targets) and all(not self.is_public(t) for t in targets)


# ── 점검 항목 ──────────────────────────────────────
def check_lint(v):
    r = defaultdict(list)
    content_pages = [p for p in v.pages if p not in INDEXES]

    # 공개 범위 위반 (가장 위험)
    for p in v.pages:
        if v.is_public(p):
            for n in sorted(v.out[p]):
                if v.private_only(n):
                    r["🚨 wiki → 비공개 링크"].append(f"{p} → [[{n}]]")
    for top in PUBLIC_DIRS:
        for p in sorted(md_files(top)):
            for kind, label, ln in scan_text(read(p)):
                r["🚨 공개 파일 안 비밀값·개인정보 의심"].append(f"{p}:{ln} ({label})")

    # 이름 충돌
    for n, ps in v.by_name.items():
        if len(ps) > 1:
            r["⚠️ 같은 이름 페이지 (링크 모호)"].append(f"{n}: {', '.join(ps)}")

    # 끊긴 링크
    for p in v.pages:
        for n in sorted(v.out[p]):
            if not v.resolves_to(n):
                r["🔗 끊긴 링크"].append(f"{p} → [[{n}]]")

    # 고아 페이지 (목차 제외, 본문 페이지끼리 연결이 0개)
    inbound = defaultdict(set)
    for p in content_pages:
        for n in v.out[p]:
            for t in v.resolves_to(n):
                if t != p:
                    inbound[t].add(p)
    for p in content_pages:
        outs = {t for n in v.out[p] for t in v.resolves_to(n) if t != p and t not in INDEXES}
        if not outs and not inbound[p]:
            r["🏝 고아 페이지"].append(p)

    # 목차 누락
    for p in content_pages:
        idx = "wiki/index.md" if v.is_public(p) else "_private/wiki/private-index.md"
        if idx in v.out and name_of(p) not in v.out[idx]:
            r["📇 목차에 없는 페이지"].append(f"{p} (→ {idx})")

    # 프론트매터
    for p in content_pages:
        if not v.fm[p].get("type") or not modified_of(v.fm[p]):
            r["🧾 프론트매터 누락 (type/modified)"].append(p)

    # 모순 콜아웃
    for p in v.pages:
        n = v.text[p].count("[!warning] 모순")
        if n:
            r["⚔️ 남아 있는 모순 표시"].append(f"{p} ({n}개)")

    # 프로젝트 상태
    for p in content_pages:
        fm = v.fm[p]
        if fm.get("type") not in ("project", "career"):
            continue
        st, dl, up = fm.get("status", ""), to_date(fm.get("deadline", "")), modified_of(fm)
        if dl and dl < TODAY and st in ("진행중", "대기"):
            r["⏰ 마감 지났는데 진행중/대기"].append(f"{p} (마감 {dl}, {st})")
        if st == "진행중" and up and (TODAY - up).days > 30:
            r["💤 30일 넘게 갱신 없는 진행중"].append(f"{p} (modified {up})")

    # 남은 초안
    drafts = files_under(f"{PRIV}/drafts")
    if drafts:
        r["🧹 병합 안 된 초안 (drafts)"].append(f"{len(drafts)}개 — /ingest-batch 병합 단계가 중간에 멈췄을 수 있음")

    # 미처리 원본
    pend = pending()
    if pend:
        r["📥 아직 넣지 않은 원본"].append(f"{len(pend)}개 — `python3 .tools/wiki_check.py pending`")

    # Velog 자동 수집이 멈췄는지 (예약을 설치한 경우에만 기록 파일이 생긴다)
    p = os.path.join(ROOT, VELOG_LAST_OK)
    if os.path.exists(p):
        last = to_date(read(VELOG_LAST_OK).strip())
        if last and (TODAY - last).days >= VELOG_STALE_DAYS:
            r["📡 Velog 자동 수집 멈춤"].append(
                f"마지막 성공 {last} ({(TODAY - last).days}일 전) — `bash .tools/velog_schedule.sh status`로 확인")
    return r


def readiness():
    """최근 기간의 /velog-wiki 실행 수와 사람이 결과를 고친 횟수 (log.md 기준)."""
    if not os.path.exists(os.path.join(ROOT, LOG)):
        return None
    runs = fixes = 0
    since = TODAY - timedelta(days=READINESS_WINDOW)
    ever = False
    for line in read(LOG).splitlines():
        m = re.match(r"^- (\d{4}-\d{2}-\d{2}) \| (\S+)\s*\|\s*(\S+)?", line)
        if not m:
            continue
        d, kind, target = to_date(m.group(1)), m.group(2), (m.group(3) or "")
        is_run = kind == "velog-wiki"
        is_fix = kind == "correction" and target.startswith("velog-wiki")
        ever |= is_run
        if d and d >= since:
            runs += is_run
            fixes += is_fix
    return (runs, fixes) if ever else None


def print_readiness():
    rd = readiness()
    if rd is None:
        return
    runs, fixes = rd
    ok = runs >= READINESS_MIN_RUNS and fixes <= READINESS_MAX_FIX
    print(f"## 🤖 자동화 2단계 준비도 (최근 {READINESS_WINDOW}일)")
    print(f"- /velog-wiki 실행 {runs}회, 사람이 결과를 고친 횟수 {fixes}회")
    print(f"- 기준: 실행 {READINESS_MIN_RUNS}회 이상이면서 고친 횟수 {READINESS_MAX_FIX}회 이하")
    print("- 판정: " + ("✅ 정리까지 자동화(2단계) 검토 가능" if ok else
                       ("⏳ 아직 표본이 적음 — 계속 1단계로" if runs < READINESS_MIN_RUNS else
                        "🔧 고칠 일이 아직 많음 — 반복되는 수정을 규칙(CLAUDE.md·스킬 시리즈 표)에 반영 후 재측정")))
    print()


# 본문 없이 제목·링크·URL·구분선만 있는 줄 (노션 목차 페이지, 빈 주차 페이지)
_TOC_LINE_RE = re.compile(
    r"^\s*(?:"
    r"#{1,6}\s.*"                                       # 제목
    r"|(?:[-*+]|\d+\.)?\s*(?:\[[^\]]*\]\([^)]*\)\s*)+"   # [이름](주소) 링크만 있는 줄
    r"|(?:[-*+]|\d+\.)?\s*<?https?://\S+>?"              # 주소만 있는 줄
    r"|[-*_]{3,}"                                       # 구분선
    r"|[-*+]"                                           # 빈 목록 기호
    r")?\s*$"
)


def is_toc_only(f):
    """본문 없이 제목·링크만 있는 .md 원본인지 (패치 6.9). 이런 파일은 위키에 넣을 내용이 없다."""
    if not f.endswith(".md"):
        return False
    text = read(f)
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            text = text[end + 4:]
    return all(_TOC_LINE_RE.match(line) for line in text.splitlines())


def pending_split():
    """(넣어야 할 원본, 본문 없는 목차 원본) — 둘 다 아직 log에 없는 것만."""
    log = read(LOG) if os.path.exists(os.path.join(ROOT, LOG)) else ""
    todo = [f for f in files_under(RAW) if os.path.relpath(f, PRIV) not in log and f not in log]
    toc = [f for f in todo if is_toc_only(f)]
    return [f for f in todo if f not in toc], toc


def pending():
    return pending_split()[0]


def status_rows(v):
    rows = []
    for p in v.pages:
        fm = v.fm[p]
        if fm.get("type") not in ("project", "career"):
            continue
        m = re.search(r"^- \[ \] (.+)$", v.text[p], re.M)
        rows.append({
            "page": name_of(p), "status": fm.get("status", "?"), "priority": fm.get("priority", ""),
            "deadline": to_date(fm.get("deadline", "")), "modified": modified_of(fm),
            "next": m.group(1).strip() if m else "—",
        })
    return rows


def dday(d):
    if not d:
        return "—"
    n = (d - TODAY).days
    return f"{d} (D-{n})" if n > 0 else (f"{d} (D-DAY)" if n == 0 else f"{d} (D+{-n} 지남)")


def print_status(v):
    rows = status_rows(v)
    prio = {"높음": 0, "보통": 1, "낮음": 2}
    groups = [
        ("⏰ 마감 임박 (14일 이내·지남)", sorted([r for r in rows if r["deadline"] and r["deadline"] <= TODAY + timedelta(days=14) and r["status"] != "완료"], key=lambda r: r["deadline"])),
        ("🔥 진행중", sorted([r for r in rows if r["status"] == "진행중"], key=lambda r: prio.get(r["priority"], 9))),
        ("💤 14일 넘게 안 건드린 진행중", [r for r in rows if r["status"] == "진행중" and r["modified"] and (TODAY - r["modified"]).days > 14]),
        ("⏸ 보류 / 대기", [r for r in rows if r["status"] in ("보류", "대기")]),
    ]
    print(f"# 현황 대시보드 ({TODAY})\n")
    for title, rs in groups:
        print(f"## {title}")
        if not rs:
            print("- 없음\n")
            continue
        print("| 페이지 | 상태 | 마감 | 다음 할 일 |\n|---|---|---|---|")
        for r in rs:
            print(f"| [[{r['page']}]] | {r['status']} | {dday(r['deadline'])} | {r['next']} |")
        print()


# ── 커밋·배포 게이트 ───────────────────────────────
def git(cwd, *args):
    return subprocess.run(["git", "-c", "core.quotePath=false", *args], cwd=cwd,
                          capture_output=True, text=True).stdout


def staged_files(cwd):
    return [f for f in git(cwd, "diff", "--cached", "--name-only", "--diff-filter=ACMR", "-z").split("\0") if f]


def added_lines(cwd, f):
    return "\n".join(l[1:] for l in git(cwd, "diff", "--cached", "-U0", "--no-color", "--", f).splitlines()
                     if l.startswith("+") and not l.startswith("+++"))


def report(problems, hint):
    if not problems:
        return 0
    print("🚫 커밋 차단")
    for x in problems:
        print("  - " + x)
    print("\n" + hint)
    return 1


def check_staged():
    problems = []
    v = Vault()
    for f in staged_files(ROOT):
        if PRIVATE_PATH_RE.search(f):
            problems.append(f"비공개 경로: {f}")
            continue
        added = added_lines(ROOT, f)
        labels = sorted({label for _, label, _ in scan_text(added)})
        if labels:
            problems.append(f"비밀값·개인정보 의심 ({', '.join(labels)}): {f}")
        if f.startswith(PUBLIC + "/") and f.endswith(".md"):
            for n in sorted(links_in(added)):
                if v.private_only(n):
                    problems.append(f"공개 페이지가 비공개 페이지를 링크: {f} → [[{n}]]")
    return report(problems, "→ 확인: git diff --cached -- <파일>   빼기: git restore --staged <파일>")


def check_staged_private():
    cwd = os.path.join(ROOT, PRIV)
    problems = []
    for f in staged_files(cwd):
        if f.startswith("drafts/") or re.search(r"(^|/)\.env", f):
            problems.append(f"올리면 안 되는 파일: {f}")
            continue
        labels = sorted({label for kind, label, _ in scan_text(added_lines(cwd, f)) if kind == "secret"})
        if labels:
            problems.append(f"API 키·토큰 의심 ({', '.join(labels)}): {f}")
    return report(problems,
                  "→ 아직 살아 있는 키라면 먼저 해당 서비스에서 폐기(rotate)하세요.\n"
                  "→ 이미 폐기된 키라는 걸 직접 확인했다면: git commit --no-verify")


def check_public_gate():
    """배포 직전: 공개될 파일 전체를 다시 훑는다 (커밋 훅을 우회한 커밋에 대한 마지막 방어선)."""
    problems = []
    for top in PUBLIC_DIRS:
        for p in sorted(md_files(top)):
            for kind, label, ln in scan_text(read(p)):
                problems.append(f"{p}:{ln} ({label})")
    # CI에는 _private/가 없으므로, 공개 페이지끼리 풀리지 않는 링크를 경고로 보여준다.
    # (끊긴 링크이거나 비공개 페이지 링크 — 후자면 페이지 '제목'이 사이트 설명문·검색 색인에 노출된다)
    public_names = {name_of(p) for p in md_files(PUBLIC)} | {name_of(p) for p in md_files("eval")}
    for p in sorted(md_files(PUBLIC)):
        for n in sorted(links_in(read(p))):
            if n not in public_names:
                print(f"⚠️  공개 사이트에서 풀리지 않는 링크: {p} → [[{n}]] (비공개 페이지라면 제목이 노출됨)")
    if problems:
        print("🚫 배포 중단 — 공개 파일에 비밀값·개인정보 의심")
        for x in problems:
            print("  - " + x)
        return 1
    print("✅ 공개 파일 검사 통과")
    return 0


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "lint"
    if mode == "staged":
        sys.exit(check_staged())
    if mode == "staged-private":
        sys.exit(check_staged_private())
    if mode == "public-gate":
        sys.exit(check_public_gate())
    if mode == "pending":
        p, toc = pending_split()
        show_toc = "--all" in sys.argv[2:]
        by_dir = defaultdict(list)
        for f in p:
            by_dir[os.path.dirname(f)].append(f)
        print(f"# 미처리 원본 {len(p)}개\n")
        for d in sorted(by_dir):
            print(f"## {d}/ ({len(by_dir[d])}개)")
            for f in by_dir[d]:
                print(f"- {f}")
        if toc:
            print(f"\n## 제외: 본문 없는 목차 파일 {len(toc)}개 (제목·링크만 있음 — 위키·log에 적을 필요 없음)")
            if show_toc:
                for f in toc:
                    print(f"- {f}")
            else:
                print("- 목록 보기: python3 .tools/wiki_check.py pending --all")
        return
    v = Vault()
    if mode == "status":
        print_status(v)
        return
    r = check_lint(v)
    print(f"# 위키 점검 리포트 ({TODAY}) — 페이지 {len(v.pages)}개\n")
    if not r:
        print("문제 없음 ✅\n")
    n = 0
    for title in sorted(r, key=lambda t: ORDER.index(t) if t in ORDER else 99):
        print(f"## {title}")
        for item in r[title]:
            n += 1
            print(f"{n}. {item}")
        print()
    print_readiness()


if __name__ == "__main__":
    main()
