#!/bin/bash
# 매일 launchd가 실행하는 Velog 자동 수집 (1단계: 수집만, AI 사용 안 함)
#  - 새 글을 _private/raw/velog/ 에 저장 (velog_fetch.py)
#  - 새 글이 있으면 Mac 알림, 실패하면 실패 알림
#  - 성공 시각을 _private/logs/velog-last-success 에 기록 → 며칠째 멈추면 /lint 가 경고
# 직접 실행해도 됨: bash .tools/velog_daily.sh

set -u
VAULT="$(cd "$(dirname "$0")/.." && pwd)"
PY="${VELOG_PYTHON:-python3}"
LOGDIR="$VAULT/_private/logs"
LOG="$LOGDIR/velog-fetch.log"
mkdir -p "$LOGDIR"

notify() {  # notify <제목> <내용>  (macOS가 아니면 조용히 넘어감)
  command -v osascript >/dev/null 2>&1 || return 0
  osascript -e "display notification \"$2\" with title \"$1\"" >/dev/null 2>&1 || true
}

{
  echo "=== $(date '+%Y-%m-%d %H:%M:%S') ==="
  out="$(cd "$VAULT" && PYTHONIOENCODING=utf-8 "$PY" .tools/velog_fetch.py 2>&1)"
  rc=$?
  echo "$out"
  echo "(exit $rc)"
} >> "$LOG"

if [ "$rc" -eq 0 ]; then
  date '+%Y-%m-%dT%H:%M:%S' > "$LOGDIR/velog-last-success"
  n="$(printf '%s\n' "$out" | sed -n 's/^저장 \([0-9][0-9]*\)편.*/\1/p' | head -n 1)"
  if [ "${n:-0}" -gt 0 ]; then
    notify "AI-Vault" "Velog 새 글 ${n}편 수집됨. Claude Code에서 /velog-sync 로 정리하세요"
  fi
else
  notify "AI-Vault" "Velog 수집 실패. _private/logs/velog-fetch.log 를 확인하세요"
fi

# 로그가 끝없이 커지지 않게 최근 2000줄만 유지
tail -n 2000 "$LOG" > "$LOG.tmp" && mv "$LOG.tmp" "$LOG"
exit "$rc"
