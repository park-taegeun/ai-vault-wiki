#!/bin/bash
# velog-up — Velog에 새 글을 올린 뒤 한 번에 처리한다 (패치 6.11)
#   1) /velog-sync   : 백업 레포·노션 대시보드·Memory 갱신 (볼트 밖, Claude Code를 대화 없이 실행)
#   2) velog_fetch   : 새 글을 원본 창고에 저장 (Claude 없이 직접 실행 — 샌드박스 밖이라 연결이 끊기지 않음)
#   3) /velog-wiki   : 위키 반영 → pending 0 확인 → publish-check → 공개·비공개 커밋 (볼트 안, 가드·샌드박스 그대로)
# push는 하지 않는다. 마지막에 출력되는 요약을 보고 사람이 push한다 (공개는 항상 사람).
#
# 사용: 터미널에서  velog-up      (Claude Code 세션 안에서는 실행하지 않는다)
#       velog-up --no-sync         1단계(백업·노션·Memory)를 건너뛴다
set -uo pipefail

VAULT="${AI_VAULT:-$HOME/AI-Vault}"
SYNC=1
for a in "$@"; do
  case "$a" in
    --no-sync) SYNC=0 ;;
    -h|--help) sed -n '2,10p' "$0"; exit 0 ;;
    *) echo "❌ 모르는 옵션: $a (사용: velog-up [--no-sync])"; exit 2 ;;
  esac
done

if [ -d "$HOME/Library/Logs" ]; then LOGDIR="$HOME/Library/Logs/ai-vault"; else LOGDIR="$HOME/.cache/ai-vault"; fi
mkdir -p "$LOGDIR"
TS="$(date +%Y%m%d-%H%M%S)"
LOG="$LOGDIR/velog-up-$TS.log"
SYNC_JSON="$LOGDIR/velog-up-$TS-sync.json"
WIKI_JSON="$LOGDIR/velog-up-$TS-wiki.json"

step() { printf '\n\033[1m▶ %s\033[0m\n' "$*"; }
result_of() {  # claude -p --output-format json 결과에서 마지막 보고 문장만 꺼낸다
  python3 - "$1" <<'PY'
import json, sys
try:
    d = json.load(open(sys.argv[1], encoding="utf-8"))
except Exception as e:
    print(f"(결과를 읽지 못했습니다: {type(e).__name__}. 로그 파일을 확인하세요)")
    sys.exit(0)
if d.get("is_error"):
    print("❗ 오류로 끝났습니다")
print((d.get("result") or "(보고 없음)").strip())
PY
}

# ── 사전 점검 ─────────────────────────────────────────
if [ -n "${CLAUDECODE:-}" ]; then
  echo "❌ Claude Code 세션 안에서는 실행할 수 없습니다. 일반 터미널에서 실행하세요."; exit 1
fi
command -v claude >/dev/null 2>&1 || { echo "❌ claude 명령을 찾을 수 없습니다."; exit 1; }
command -v python3 >/dev/null 2>&1 || { echo "❌ python3를 찾을 수 없습니다."; exit 1; }
cd "$VAULT" 2>/dev/null && [ -f CLAUDE.md ] && [ -d .claude ] && [ -d _private/.git ] \
  || { echo "❌ LLM Wiki 볼트가 아닙니다: $VAULT"; exit 1; }
if [ -n "$(git status --porcelain)" ] || [ -n "$(git -C _private status --porcelain)" ]; then
  echo "❌ 커밋 안 된 변경이 있어서 시작하지 않았습니다 (이번 실행의 커밋과 섞이지 않게)."
  echo "   [공개]";   git status --short | sed 's/^/   /'
  echo "   [비공개]"; git -C _private status --short | sed 's/^/   /'
  exit 1
fi
START_PUB="$(git rev-parse --short HEAD)"
START_PRIV="$(git -C _private rev-parse --short HEAD)"
fail=0
echo "로그: $LOG"

# ── 1) 백업 레포·노션·Memory ──────────────────────────
SYNC_PROMPT='/velog-sync
지금은 대화 없이 실행 중이라 질문할 수 없어. 스킬 절차대로 끝까지 진행해.
절차에 없는 판단이 필요한 이상한 점은 고치지 말고 보고에만 적어.
마지막 보고는 8줄 이내: 신규 편수와 제목, Velog 총 편수, posts/ 파일 수, GitHub 커밋 해시, 노션 행 추가 여부, Memory 갱신 여부, 실패하거나 다른 방법으로 우회한 단계.'
if [ "$SYNC" = 1 ]; then
  step "1/3 백업 레포·노션·Memory 동기화 (/velog-sync) — 1~3분"
  ( cd "$HOME" && claude -p "$SYNC_PROMPT" --dangerously-skip-permissions --output-format json ) \
    >"$SYNC_JSON" 2>>"$LOG"
  rc=$?
  result_of "$SYNC_JSON"
  [ $rc -eq 0 ] || { echo "⚠️  동기화가 종료 코드 $rc로 끝났습니다. 다음 단계는 계속합니다."; fail=1; }
else
  step "1/3 동기화 건너뜀 (--no-sync)"
fi

# ── 2) 원본 수집 (Claude 없이) ────────────────────────
step "2/3 Velog 새 글을 원본 창고에 저장"
python3 .tools/velog_fetch.py 2>&1 | tee -a "$LOG"
rc=${PIPESTATUS[0]}
[ $rc -eq 0 ] || { echo "⚠️  수집이 종료 코드 $rc로 끝났습니다. 이미 저장된 원본만 반영합니다."; fail=1; }

PENDING_LINE="$(python3 .tools/wiki_check.py pending | head -1)"
N="$(printf '%s' "$PENDING_LINE" | sed -n 's/.*원본 \([0-9][0-9]*\)개.*/\1/p')"
N="${N:-0}"
echo "$PENDING_LINE"

# ── 3) 위키 반영·검사·커밋 (볼트 안, 가드·샌드박스 그대로) ──
WIKI_PROMPT='/velog-wiki
지금은 대화 없이 실행 중이라 질문할 수 없어. 아래 규칙을 지켜.
- Velog 가져오기(velog_fetch.py)는 방금 사람이 터미널에서 했어. 다시 하지 마.
- pending에 있는 velog 원본을 전부 반영하고, python3 .tools/wiki_check.py pending 으로 velog 원본이 0인지, lint 🚨가 0인지 확인해.
- 이어서 /publish-check 를 해. 🚨, 공개 기준으로 정할 수 없는 부분, 모순이 하나라도 나오면 커밋하지 말고 멈춰서 보고해. 사람이 확인한 뒤 다시 실행한다.
- 문제가 없으면 공개 레포와 비공개 레포를 각각 커밋해. 추적되지 않은 새 원본 파일은 비공개 커밋에 함께 넣어. 푸시는 절대 하지 마.
- Bash는 항상 볼트 루트에서 실행하고, 비공개 레포는 cd 대신 git -C _private 를 써.
- 막히면 우회하지 말고 보고해.
마지막 보고는 10줄 이내: pending 전/후, 신규·보강 페이지, publish-check 결론, 커밋 해시(공개/비공개), 멈췄다면 그 이유.'
ALLOWED='Read,Glob,Grep,Edit,Write,MultiEdit,Skill,Task,Bash(python3 .tools/wiki_check.py *),Bash(git status),Bash(git status *),Bash(git diff *),Bash(git log *),Bash(git add *),Bash(git commit *),Bash(git -C _private status),Bash(git -C _private status *),Bash(git -C _private diff *),Bash(git -C _private log *),Bash(git -C _private add *),Bash(git -C _private commit *)'

if [ "$N" -gt 0 ]; then
  step "3/3 위키 반영·검사·커밋 (/velog-wiki) — 2~5분"
  claude -p "$WIKI_PROMPT" --permission-mode acceptEdits --allowedTools "$ALLOWED" --output-format json \
    >"$WIKI_JSON" 2>>"$LOG"
  rc=$?
  result_of "$WIKI_JSON"
  [ $rc -eq 0 ] || { echo "⚠️  위키 반영이 종료 코드 $rc로 끝났습니다."; fail=1; }
else
  step "3/3 반영할 원본이 없어 건너뜀"
fi

# ── 요약 ─────────────────────────────────────────────
step "요약 — 확인 후 사람이 push"
python3 .tools/wiki_check.py pending | head -1
echo "[공개]   $START_PUB → $(git log --oneline -1)"
git status -sb | head -1
git status --short
echo "[비공개] $START_PRIV → $(git -C _private log --oneline -1)"
git -C _private status -sb | head -1
git -C _private status --short
if [ -n "$(git status --porcelain)" ] || [ -n "$(git -C _private status --porcelain)" ]; then
  echo "⚠️  커밋 안 된 변경이 남아 있습니다. 위 보고를 확인하세요 (push하지 마세요)."; fail=1
fi
echo
echo "보고가 괜찮으면:  git -C \"$VAULT\" push && git -C \"$VAULT/_private\" push"
echo "배포 확인:        gh run list -R park-taegeun/ai-vault-wiki -L 1"
echo "전체 로그:        $LOG"
exit $fail
