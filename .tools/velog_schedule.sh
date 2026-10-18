#!/bin/bash
# Velog 자동 수집 예약 관리 (macOS launchd)
#
#   bash .tools/velog_schedule.sh install [HH:MM]   매일 정해진 시각에 수집 (기본 22:00)
#   bash .tools/velog_schedule.sh run-now           지금 한 번 실행 (설치 직후 시험용)
#   bash .tools/velog_schedule.sh status            예약 상태, 마지막 성공, 최근 로그
#   bash .tools/velog_schedule.sh uninstall         예약 해제
#   bash .tools/velog_schedule.sh plist [HH:MM]     설치하지 않고 설정 파일 내용만 보기
#
# Mac이 잠자는 동안 예약 시각이 지나면, 깨어났을 때 한 번 실행된다. 전원이 꺼져 있었으면 건너뛴다.

set -euo pipefail
VAULT="$(cd "$(dirname "$0")/.." && pwd)"
LABEL="com.ai-vault.velog-fetch"
PLIST="$HOME/Library/LaunchAgents/$LABEL.plist"
DOMAIN="gui/$(id -u)"

xml_escape() { printf '%s' "$1" | sed -e 's/&/\&amp;/g' -e 's/</\&lt;/g' -e 's/>/\&gt;/g'; }

parse_time() {
  local t="${1:-22:00}"
  if ! [[ "$t" =~ ^([01]?[0-9]|2[0-3]):([0-5][0-9])$ ]]; then
    echo "❌ 시각 형식은 HH:MM 입니다 (예: 22:00)" >&2; exit 1
  fi
  HOUR=$((10#${BASH_REMATCH[1]})); MINUTE=$((10#${BASH_REMATCH[2]}))
}

make_plist() {
  local py; py="$(command -v python3 || echo /usr/bin/python3)"
  local v; v="$(xml_escape "$VAULT")"
  cat <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>$LABEL</string>
  <key>ProgramArguments</key>
  <array>
    <string>/bin/bash</string>
    <string>$v/.tools/velog_daily.sh</string>
  </array>
  <key>EnvironmentVariables</key>
  <dict>
    <key>VELOG_PYTHON</key>
    <string>$(xml_escape "$py")</string>
    <key>PATH</key>
    <string>/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin</string>
    <key>LANG</key>
    <string>ko_KR.UTF-8</string>
  </dict>
  <key>StartCalendarInterval</key>
  <dict>
    <key>Hour</key>
    <integer>$HOUR</integer>
    <key>Minute</key>
    <integer>$MINUTE</integer>
  </dict>
  <key>StandardOutPath</key>
  <string>$v/_private/logs/launchd.out.log</string>
  <key>StandardErrorPath</key>
  <string>$v/_private/logs/launchd.err.log</string>
</dict>
</plist>
EOF
}

require_mac() { [ "$(uname)" = "Darwin" ] || { echo "❌ macOS 전용 명령입니다."; exit 1; }; }

case "${1:-}" in
  install)
    require_mac; parse_time "${2:-22:00}"
    mkdir -p "$HOME/Library/LaunchAgents" "$VAULT/_private/logs"
    make_plist > "$PLIST"
    plutil -lint "$PLIST" >/dev/null
    launchctl bootout "$DOMAIN" "$PLIST" 2>/dev/null || true
    launchctl bootstrap "$DOMAIN" "$PLIST"
    printf '✅ 매일 %02d:%02d 에 Velog 새 글을 수집합니다.\n' "$HOUR" "$MINUTE"
    echo "   설정 파일: $PLIST"
    echo "   지금 시험해보려면: bash .tools/velog_schedule.sh run-now"
    ;;
  run-now)
    require_mac
    [ -f "$PLIST" ] || { echo "❌ 아직 설치되지 않았습니다. 먼저 install 하세요."; exit 1; }
    launchctl kickstart "$DOMAIN/$LABEL"
    echo "▶️  실행했습니다. 몇 초 뒤 'status'로 결과를 확인하세요."
    ;;
  status)
    if [ -f "$PLIST" ] && [ "$(uname)" = "Darwin" ]; then
      echo "예약: 설치됨 ($PLIST)"
      launchctl print "$DOMAIN/$LABEL" 2>/dev/null | grep -E "^[[:space:]]*(state|last exit code|runs) =" | sed 's/^[[:space:]]*/   /' || echo "   (launchd에 등록되지 않음 — install 을 다시 실행하세요)"
    else
      echo "예약: 설치 안 됨"
    fi
    last="$VAULT/_private/logs/velog-last-success"
    echo "마지막 성공: $( [ -f "$last" ] && cat "$last" || echo '기록 없음')"
    log="$VAULT/_private/logs/velog-fetch.log"
    if [ -f "$log" ]; then echo "--- 최근 로그"; tail -n 12 "$log"; fi
    ;;
  uninstall)
    require_mac
    launchctl bootout "$DOMAIN" "$PLIST" 2>/dev/null || true
    rm -f "$PLIST"
    echo "✅ 예약을 해제했습니다. (이미 수집된 글과 로그는 그대로 둡니다)"
    ;;
  plist)
    parse_time "${2:-22:00}"; make_plist
    ;;
  *)
    sed -n '2,10p' "$0" | sed 's/^# \{0,1\}//'
    exit 1
    ;;
esac
