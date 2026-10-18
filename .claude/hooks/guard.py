#!/usr/bin/env python3
"""Claude Code PreToolUse 가드.

CLAUDE.md는 '부탁'이라 모델이 어길 수 있다. 어기면 안 되는 규칙은 여기서 강제한다.
  1) _private/raw/ 의 기존 파일 수정 금지 (새 파일 생성만 허용)
  2) 공개 구역(wiki/, eval/)에 비밀값·개인정보 쓰기 금지
  3) Bash로 원본 파일 삭제·이동·덮어쓰기 금지
exit 2 = 차단. stderr 메시지가 Claude에게 전달된다.
"""
import json
import os
import re
import sys

ROOT = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
sys.path.insert(0, os.path.join(ROOT, ".tools"))
try:
    from wiki_patterns import scan_text
except Exception:  # 패턴 파일이 없으면 안전하게 막는다 (fail closed)
    scan_text = None

RAW = "_private/raw/"
PUBLIC_PREFIXES = ("wiki/", "eval/")


def block(msg):
    print(f"[가드] {msg} — CLAUDE.md 9장. 우회하지 말고 사람에게 보고하세요.", file=sys.stderr)
    sys.exit(2)


def rel(path):
    return os.path.relpath(os.path.abspath(path), os.path.abspath(ROOT)).replace(os.sep, "/")


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
    # settings.json deny는 명령어 앞부분만 보므로, 'cd _private && git push' 같은 형태도 여기서 막는다
    if re.search(r"\bgit\b[^|;&]*\s(push|config)\b", cmd) or re.search(r"--no-verify\b|\bcore\.hooksPath\b", cmd):
        block("git push / git config / --no-verify 는 사람이 직접 실행합니다")

sys.exit(0)
