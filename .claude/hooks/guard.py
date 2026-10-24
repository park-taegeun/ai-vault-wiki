#!/usr/bin/env python3
"""Claude Code PreToolUse 가드.

CLAUDE.md는 '부탁'이라 모델이 어길 수 있다. 어기면 안 되는 규칙은 여기서 강제한다.
  1) _private/raw/ 의 기존 파일 수정 금지 (새 파일 생성만 허용)
  2) 공개 구역(wiki/, eval/)에 비밀값·개인정보 쓰기 금지
  3) 보호 경로를 언급하는 Bash 명령은 허용 목록에 있을 때만 통과 (패치 6.10의 차단 목록을 대체)
     보호 경로: wiki/ eval/ _private/wiki/ _private/eval/ _private/raw/ .claude/ .githooks/ _private/.githooks/ .tools/ .github/
     허용: 읽기·점검 명령, git 읽기·add·commit, .tools 점검 스크립트 2개, 같은 위키 구역 안의 rm/mv
     이유: Bash 쓰기는 2)의 검사를 건너뛰고, 안전장치 파일은 Bash로 고치면 settings.json deny(Edit 도구 전용)를 비켜 간다.
     한계: 경로를 글자로 드러내지 않는 쓰기(스크립트 파일 실행, 변수 조립, 글롭, 인코딩)는 못 본다.
           그 뒤는 pre-commit·public-gate(비밀값)와 사람의 diff 확인이 받친다.
exit 2 = 차단. stderr 메시지가 Claude에게 전달된다.
"""
import json
import os
import re
import shlex
import sys

ROOT = os.path.realpath(os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd())
sys.path.insert(0, os.path.join(ROOT, ".tools"))
try:
    from wiki_patterns import scan_text
except Exception:  # 패턴 파일이 없으면 안전하게 막는다 (fail closed)
    scan_text = None

RAW = "_private/raw/"
PUBLIC_PREFIXES = ("wiki/", "eval/")
PRIVATE_WIKI = ("_private/wiki/", "_private/eval/")
PROTECTED_DIRS = ("wiki", "eval", "_private/wiki", "_private/eval", "_private/raw",
                  ".claude", ".githooks", "_private/.githooks", ".tools", ".github")
# 명령줄에 보호 경로가 '글자로' 보이는지. wiki_check 같은 이름 일부는 제외, 앞에 / 가 붙은 절대경로는 포함.
PROTECTED_RE = re.compile(r"(?<![\w.-])(?:wiki|eval|raw|\.claude|\.githooks|\.tools|\.github)(?![\w.-])")
READ_PROGS = {"cat", "head", "tail", "wc", "ls", "grep", "rg", "find", "stat", "file", "du", "diff",
              "cut", "tr", "sort", "uniq", "echo", "printf", "pwd", "cd", "basename", "dirname", "true", "test", "["}
BAD_FLAGS = {"find": ("-delete", "-exec", "-execdir", "-ok", "-okdir", "-fprint", "-fls"),
             "rg": ("--pre",)}
TOOLS_SCRIPTS = {".tools/wiki_check.py", ".tools/velog_fetch.py"}
GIT_SUBS = {"status", "diff", "log", "show", "ls-files", "blame", "grep", "rev-parse", "check-ignore",
            "shortlog", "add", "commit", "restore", "mv", "rm"}
REDIR_OUT = {">", ">>", ">|", "&>", "&>>", "<>"}
REDIR_IN = {"<", "<<", "<<<", "<<-", "<&", ">&"}
PUNCT = set("();<>|&")


def block(msg):
    print(f"[가드] {msg} — CLAUDE.md 9장. 우회하지 말고 사람에게 보고하세요.", file=sys.stderr)
    sys.exit(2)


def rel(path):
    return os.path.relpath(os.path.realpath(path), ROOT).replace(os.sep, "/")


def in_protected(path):
    r = rel(path)
    return any(r == d or r.startswith(d + "/") for d in PROTECTED_DIRS)


def wiki_zone(path, base):
    r = rel(os.path.join(base, os.path.expanduser(path)))
    return "public" if r.startswith(PUBLIC_PREFIXES) else "private" if r.startswith(PRIVATE_WIKI) else None


def safe_target(t):
    """리다이렉트 대상이 보호 경로 밖인지. 상대경로는 cd에 따라 뜻이 바뀌므로 믿지 않는다."""
    p = os.path.expanduser(t)
    return t == "/dev/null" or (os.path.isabs(p) and not in_protected(p))


def move_problem(paths, base, moved):
    if moved:
        return "cd 뒤의 rm/mv"
    zones = {wiki_zone(p, base) for p in paths}
    if not paths or None in zones or len(zones) > 1:
        return "위키 구역 밖이거나 공개↔비공개를 넘나드는 rm/mv"
    return None


def segment_problem(words, cwd, moved):
    prog, args = words[0], words[1:]
    if prog in READ_PROGS:
        if any(a.startswith(BAD_FLAGS.get(prog, ())) for a in args) \
                or prog == "sort" and any(re.match(r"-[^-]*o|--o", a) for a in args) \
                or prog == "uniq" and len([a for a in args if not a.startswith("-")]) > 1:
            return f"{prog}의 쓰기·실행 옵션"
        return None
    if prog == "sed":
        ok = args[:1] == ["-n"] and len(args) >= 2 and re.fullmatch(r"[\d,$]+p", args[1])
        return None if ok else "sed (허용: sed -n '시작,끝p' 파일)"
    if prog in ("python3", "python"):
        ok = args and rel(os.path.join(cwd, args[0])) in TOOLS_SCRIPTS
        return None if ok else "python (허용: .tools/wiki_check.py, .tools/velog_fetch.py)"
    if prog in ("rm", "mv"):
        return move_problem([a for a in args if not a.startswith("-")], cwd, moved)
    if prog == "git":
        i, base = 0, cwd
        while i < len(args) and args[i].startswith("-"):
            if args[i] == "-C" and i + 1 < len(args):
                base, i = os.path.join(base, args[i + 1]), i + 2
            elif args[i] == "-c" and args[i + 1:i + 2] == ["core.quotePath=false"]:
                i += 2
            elif args[i] == "--no-pager":
                i += 1
            else:
                return f"git 옵션 {args[i]}"
        sub, rest = (args[i], args[i + 1:]) if i < len(args) else ("", [])
        if sub not in GIT_SUBS or any(a.startswith("--output") for a in rest):
            return f"git {sub}"
        if sub == "restore" and ("--staged" not in rest or any(re.match(r"--worktree|-[^-]*W", a) for a in rest)):
            return "git restore (작업 트리 덮어쓰기)"
        if sub in ("mv", "rm"):
            return move_problem([a for a in rest if not a.startswith("-")], base, moved)
        return None
    return f"허용 목록 밖 명령({prog})"


def bash_problem(cmd, cwd):
    """보호 경로를 언급하는(또는 보호 경로 안에서 도는) Bash 명령이 허용 목록 밖이면 이유를 돌려준다."""
    if not (PROTECTED_RE.search(cmd) or in_protected(cwd)):
        return None
    if re.search(r"`|\$\(|[<>]\(", cmd):
        return "명령 치환·프로세스 치환"
    lex = shlex.shlex(cmd.replace("\n", ";"), posix=True, punctuation_chars=True)
    lex.whitespace_split = True
    lex.commenters = ""                    # a#b 같은 단어를 주석으로 잘못 잘라 뒤의 > 를 놓치지 않게
    try:
        toks = list(lex)
    except ValueError:
        return "따옴표가 닫히지 않은 명령"
    segs, cur, i = [], [], 0
    while i < len(toks):
        t, nxt = toks[i], toks[i + 1] if i + 1 < len(toks) else ""
        if not set(t) <= PUNCT:
            cur.append(t)
        elif t in REDIR_OUT or t == ">&" and not re.fullmatch(r"\d+|-", nxt):
            if not safe_target(nxt):
                return f"파일로 리다이렉트({t} {nxt})"
            if cur and cur[-1].isdigit():
                cur.pop()                  # 2>/dev/null 의 2
            i += 1
        elif t in REDIR_IN:
            if t in (">&", "<&") and cur and cur[-1].isdigit():
                cur.pop()                  # 2>&1 의 2
            i += 1                         # 다음 토큰은 입력 파일·fd·heredoc 구분자
        elif "<" in t or ">" in t:
            return f"해석할 수 없는 리다이렉트({t})"
        elif cur:                          # ; && || | & ( ) 같은 명령 경계
            segs.append(cur)
            cur = []
        i += 1
    if cur:
        segs.append(cur)
    moved = any(s[0] in ("cd", "pushd", "popd") for s in segs)
    for s in segs:
        if "/" in s[0]:
            return f"경로로 부른 프로그램({s[0]})"
        why = segment_problem(s, cwd, moved)
        if why:
            return why
    return None


try:
    data = json.load(sys.stdin)
except Exception:
    sys.exit(0)

tool = data.get("tool_name", "")
ti = data.get("tool_input", {}) or {}

if tool in ("Write", "Edit", "MultiEdit", "NotebookEdit"):
    r = rel(ti.get("file_path") or ti.get("notebook_path") or "")

    # 1) 원본은 추가만
    if r.startswith(RAW) and os.path.exists(os.path.join(ROOT, r)):
        block(f"원본({RAW})의 기존 파일은 수정할 수 없습니다: {r}")

    # 2) 공개 구역에 비밀값·개인정보 금지
    if r.startswith(PUBLIC_PREFIXES):
        if scan_text is None:
            block(".tools/wiki_patterns.py 를 찾을 수 없어 공개 구역 쓰기를 막았습니다")
        new = ti.get("content") or ti.get("new_string") or ""
        for e in ti.get("edits", []) or []:
            new += "\n" + (e.get("new_string") or "")
        labels = sorted({label for _, label, _ in scan_text(new)})
        if labels:
            block(f"공개 파일({r})에 쓰려는 내용에 {', '.join(labels)} 의심 문자열이 있습니다. "
                  f"<REDACTED>로 바꾸거나 _private/wiki/ 로 옮기세요")

elif tool == "Bash":
    cmd = ti.get("command", "")
    # settings.json deny는 명령어 앞부분만 보므로, 'cd _private && git push' 같은 형태도 여기서 막는다
    if re.search(r"\bgit\b[^|;&]*\s(push|config)\b", cmd) or re.search(r"--no-verify\b|\bcore\.hooksPath\b", cmd):
        block("git push / git config / --no-verify 는 사람이 직접 실행합니다")
    # 3) 보호 경로를 건드리는 Bash는 허용 목록만
    why = bash_problem(cmd, data.get("cwd") or ROOT)
    if why:
        block(f"보호 경로(위키·원본·안전장치)를 언급하는 Bash 명령은 허용 목록만 통과합니다: {why}. "
              "위키는 Write/Edit 도구로 쓰고, 안전장치 파일은 사람이 고칩니다")

sys.exit(0)
