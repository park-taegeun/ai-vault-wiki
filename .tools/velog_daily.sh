#!/bin/bash
# 매일 launchd가 실행하는 Velog 자동 수집 (수집만, AI 사용 안 함)
#  - 새 글을 _private/raw/velog/ 에 저장 (velog_fetch.py)
#  - 실패하면 5분 간격으로 두 번 더 시도 (잠자기에서 깨어난 직후 네트워크가 아직 없을 때 대비, 패치 6.12)
#  - 새 글이 있으면 Mac 알림, 끝내 실패하면 실패 알림
#  - 성공 시각을 _private/logs/velog-last-success 에 기록 → 며칠째 멈추면 /lint 가 경고
# 직접 실행해도 됨: bash .tools/velog_daily.sh

set -u
VAULT="$(cd "$(dirname "$0")/.." && pwd)"
PY="${VELOG_PYTHON:-python3}"
LOGDIR="$VAULT/_private/logs"
LOG="$LOGDIR/velog-fetch.log"
TRIES="${VELOG_TRIES:-3}"
WAIT="${VELOG_RETRY_WAIT:-300}"
mkdir -p "$LOGDIR"

notify() {  # notify <제목> <내용>  (macOS가 아니면 조용히 넘어감)
  command -v osascript >/dev/null 2>&1 || return 0
  osascript -e "display notification \"$2\" with title \"$1\"" >/dev/null 2>&1 || true
}

i=1
while :; do
  {
    echo "=== $(date '+%Y-%m-%d %H:%M:%S') === (시도 $i/$TRIES)"
    out="$(cd "$VAULT" && PYTHONIOENCODING=utf-8 "$PY" .tools/velog_fetch.py 2>&1)"
    rc=$?
    echo "$out"
    echo "(exit $rc)"
  } >> "$LOG"
  [ "$rc" -eq 0 ] && break
  [ "$i" -ge "$TRIES" ] && break
  i=$((i + 1))
  sleep "$WAIT"
done

if [ "$rc" -eq 0 ]; then
  date '+%Y-%m-%dT%H:%M:%S' > "$LOGDIR/velog-last-success"
  n="$(printf '%s\n' "$out" | sed -n 's/^저장 \([0-9][0-9]*\)편.*/\1/p' | head -n 1)"
  if [ "${n:-0}" -gt 0 ]; then
    notify "AI-Vault" "Velog 새 글 ${n}편 수집됨. 터미널에서 velog-up 을 실행하세요"
  fi
else
  notify "AI-Vault" "Velog 수집 실패(${TRIES}번 시도). _private/logs/velog-fetch.log 를 확인하세요"
fi

# 로그가 끝없이 커지지 않게 최근 2000줄만 유지
tail -n 2000 "$LOG" > "$LOG.tmp" && mv "$LOG.tmp" "$LOG"
exit "$rc"
