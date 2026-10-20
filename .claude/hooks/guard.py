#!/usr/bin/env python3
"""Claude Code PreToolUse 가드.

CLAUDE.md는 '부탁'이라 모델이 어길 수 있다. 어기면 안 되는 규칙은 여기서 강제한다.
  1) _private/raw/ 의 기존 파일 수정 금지 (새 파일 생성만 허용)
  2) 공개 구역(wiki/, eval/)에 비밀값·개인정보 쓰기 금지
  3) Bash로 원본 파일 삭제·이동·덮어쓰기 금지
  4) Bash로 위키(wiki/, eval/, _private/wiki/, _private/eval/) 파일 내용 쓰기 금지 (패치 6.10)
     — sed -i, 리다이렉트(>), tee, 밖에서 cp/mv로 들여오기. 2)의 검사를 건너뛰기 때문이다.
     한계: python -c 같은 스크립트 쓰기까지는 못 막는다. 그 뒤는 pre-commit·public-gate가 받친다.
exit 2 = 차단. stderr 메시지가 Claude에게 전달된다.
"""
import json
import os
import re
import shlex
import sys

ROOT = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
sys.path.insert(0, os.path.join(ROOT, ".tools"))
try:
    from wiki_patterns import scan_text
except Exception:  # 패턴 파일이 없으면 안전하게 막는다 (fail closed)
    scan_text = None

RAW = "_private/raw/"
PUBLIC_PREFIXES = ("wiki/", "eval/")
WIKI_PREFIXES = PUBLIC_PREFIXES + ("_private/wiki/", "_private/eval/")
COPY_PROGS = ("cp", "mv", "rsync", "ln", "install", "ditto")


def block(msg):
    print(f"[가드] {msg} — CLAUDE.md 9장. 우회하지 말고 사람에게 보고하세요.", file=sys.stderr)
    sys.exit(2)


def rel(path):
    return os.path.relpath(os.path.abspath(path), os.path.abspath(ROOT)).replace(os.sep, "/")


def in_wiki(path):
    if not path:
        return False
    r = rel(os.path.expanduser(path))
    return r.startswith(WIKI_PREFIXES) or r + "/" in WIKI_PREFIXES   # wiki/ 폴더 자체도 포함


def _commands(cmd):
    """명령줄을 단순 명령 단위 토큰 목록으로 나눈다. 따옴표 안은 한 토큰, >·>>·|·&& 등은 별도 토큰."""
    lex = shlex.shlex(cmd, posix=True, punctuation_chars=True)
    lex.whitespace_split = True
    cur = []
    for t in lex:
        if t in ("&&", "||", ";", "|", "&", ";;", "|&"):
            if cur:
                yield cur
            cur = []
        else:
            cur.append(t)
    if cur:
        yield cur


def writes_wiki(cmd):
    """Bash로 위키 파일 내용을 쓰는지 (상대·절대·~ 경로 모두). 위키 안에서 이름 바꾸기·복사는 허용."""
    try:
        cmds = list(_commands(cmd))
    except ValueError:      # 따옴표가 안 닫힌 명령 — 판단할 수 없으니 위키 경로가 보이면 막는다
        return bool(re.search(r"(?:^|[\s'\"=>])(?:\./)?(?:_private/)?(?:wiki|eval)/", cmd))
    for toks in cmds:
        words = []
        for i, t in enumerate(toks):
            if t in (">", ">>", ">|", "&>", "&>>") and i + 1 < len(toks) and in_wiki(toks[i + 1]):
                return True                                   # > 파일, >> 파일
            if not (i > 0 and toks[i - 1] in (">", ">>", ">|", "&>", "&>>", "<", "<<", ">&", "<&")):
                words.append(t)
        if not words:
            continue
        prog, args = os.path.basename(words[0]), words[1:]
        paths = [t for t in args if not t.startswith("-")]
        inplace = any(re.match(r"-[a-zA-Z]*i", t) or t.startswith("--in-place") for t in args)
        if prog in ("sed", "perl") and inplace and any(in_wiki(t) for t in paths):
            return True
        if prog == "tee" and any(in_wiki(t) for t in paths):
            return True
        if prog in COPY_PROGS and len(paths) >= 2 and in_wiki(paths[-1]) \
                and not all(in_wiki(a) for a in paths[:-1]):
            return True
    return False


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
    raw_ref = r"(\./)?(_private/)?raw/"
    destructive = re.search(r"\b(rm|mv|unlink|truncate|shred)\b[^|;&]*\braw/", cmd) \
        or re.search(r"\bsed\s+(-[a-zA-Z]*i|--in-place)[^|;&]*\braw/", cmd) \
        or re.search(r"(^|[^0-9&>])>>?\s*['\"]?" + raw_ref, cmd) \
        or re.search(r"\btee\b[^|;&]*\braw/", cmd)
    if destructive:
        block("Bash로 원본 파일을 삭제·이동·덮어쓸 수 없습니다")
    wiki_write = writes_wiki(cmd)
    if wiki_write:
        block("위키 파일은 Bash(sed -i, >, tee, 밖에서 cp/mv)로 쓸 수 없습니다. Write/Edit 도구로 쓰세요 "
              "(쓰는 순간 비밀값 검사를 받아야 합니다)")
    # settings.json deny는 명령어 앞부분만 보므로, 'cd _private && git push' 같은 형태도 여기서 막는다
    if re.search(r"\bgit\b[^|;&]*\s(push|config)\b", cmd) or re.search(r"--no-verify\b|\bcore\.hooksPath\b", cmd):
        block("git push / git config / --no-verify 는 사람이 직접 실행합니다")

sys.exit(0)
