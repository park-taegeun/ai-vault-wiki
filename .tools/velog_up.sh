#!/bin/bash
# velog-up — Velog에 새 글을 올린 뒤 한 번에 처리한다 (패치 6.11, 6.12)
#   1) /velog-sync   : 백업 레포·노션 대시보드·Memory 갱신 (볼트 밖, Claude Code를 대화 없이 실행)
#   2) velog_fetch   : 새 글을 원본 창고에 저장 (Claude 없이 직접 실행 — 샌드박스 밖이라 연결이 끊기지 않음)
#   3) /velog-wiki   : 위키 반영 → pending 0 확인 → publish-check → 공개·비공개 커밋 (볼트 안, 가드·샌드박스 그대로)
# push는 하지 않는다. 마지막에 출력되는 요약을 보고 사람이 push한다 (공개는 항상 사람).
#
# 사용: 터미널에서  velog-up                        (Claude Code 세션 안에서는 실행하지 않는다)
#       velog-up --no-sync                          1단계(백업·노션·Memory)를 건너뛴다
#       velog-up --resume "1, 2번 예시대로 승인"     직전 실행이 커밋 전에 멈췄을 때, 사람의 결정을 주고 이어서 마무리한다
set -uo pipefail

VAULT="${AI_VAULT:-$HOME/AI-Vault}"
SYNC=1
RESUME=""
while [ $# -gt 0 ]; do
  case "$1" in
    --no-sync) SYNC=0 ;;
    --resume)
      [ $# -ge 2 ] && [ -n "$2" ] || { echo "❌ --resume 뒤에 사람의 결정을 적어 주세요. 예: velog-up --resume \"1, 2번 예시 문장대로 승인\""; exit 2; }
      RESUME="$2"; shift ;;
    -h|--help) sed -n '2,11p' "$0"; exit 0 ;;
    *) echo "❌ 모르는 옵션: $1 (사용: velog-up [--no-sync] [--resume \"결정\"])"; exit 2 ;;
  esac
  shift
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
paths_of() { sed -e 's/^...//' -e 's/^"//' -e 's/"$//' -e 's/.* -> //'; }   # porcelain 줄 → 경로

# ── 사전 점검 ─────────────────────────────────────────
if [ -n "${CLAUDECODE:-}" ]; then
  echo "❌ Claude Code 세션 안에서는 실행할 수 없습니다. 일반 터미널에서 실행하세요."; exit 1
fi
command -v claude >/dev/null 2>&1 || { echo "❌ claude 명령을 찾을 수 없습니다."; exit 1; }
command -v python3 >/dev/null 2>&1 || { echo "❌ python3를 찾을 수 없습니다."; exit 1; }
cd "$VAULT" 2>/dev/null && [ -f CLAUDE.md ] && [ -d .claude ] && [ -d _private/.git ] \
  || { echo "❌ LLM Wiki 볼트가 아닙니다: $VAULT"; exit 1; }

PUB_DIRTY="$(git -c core.quotePath=false status --porcelain --untracked-files=all)"
PRIV_DIRTY="$(git -c core.quotePath=false -C _private status --porcelain --untracked-files=all)"
RAW_NEW="$(printf '%s\n' "$PRIV_DIRTY" | grep -E '^\?\? "?raw/velog/' || true)"
show_dirty() {
  echo "   [공개]";   printf '%s\n' "$PUB_DIRTY"  | sed '/^$/d; s/^/   /'
  echo "   [비공개]"; printf '%s\n' "$PRIV_DIRTY" | sed '/^$/d; s/^/   /'
}

if [ -z "$RESUME" ]; then
  # 일반 실행: 자동 수집이 받아 둔 원본(raw/velog/ 새 파일)만 허용하고, 나머지 변경이 있으면 시작하지 않는다
  PRIV_OTHER="$(printf '%s\n' "$PRIV_DIRTY" | grep -vE '^\?\? "?raw/velog/' | sed '/^$/d' || true)"
  if [ -n "$PUB_DIRTY" ] || [ -n "$PRIV_OTHER" ]; then
    echo "❌ 커밋 안 된 변경이 있어서 시작하지 않았습니다 (이번 실행의 커밋과 섞이지 않게)."
    show_dirty
    echo "   직전 velog-up이 멈춘 상태라면:  velog-up --resume \"보고서 항목에 대한 결정\""
    exit 1
  fi
  [ -n "$RAW_NEW" ] && echo "📥 자동 수집이 받아 둔 원본 $(printf '%s\n' "$RAW_NEW" | wc -l | tr -d ' ')개는 이번 실행의 비공개 커밋에 함께 넣습니다."
else
  # 이어서 하기: 직전 실행이 남긴 변경(위키·평가, log.md, 새 원본)만 있어야 한다
  [ -n "$PUB_DIRTY$PRIV_DIRTY" ] || { echo "❌ 이어서 마무리할 변경이 없습니다 (두 레포 모두 깨끗함)."; exit 1; }
  BAD_PUB="$(printf '%s\n' "$PUB_DIRTY"  | sed '/^$/d' | paths_of | grep -vE '^(wiki|eval)/' || true)"
  BAD_PRIV="$(printf '%s\n' "$PRIV_DIRTY" | sed '/^$/d' | paths_of | grep -vE '^(log\.md|wiki/|eval/|raw/velog/)' || true)"
  if [ -n "$BAD_PUB$BAD_PRIV" ]; then
    echo "❌ velog-up이 만들 수 없는 변경이 섞여 있어 이어서 하지 않았습니다:"
    printf '%s\n' "$BAD_PUB" "$BAD_PRIV" | sed '/^$/d; s/^/   /'
    exit 1
  fi
  printf '%s\n' "$PRIV_DIRTY" | grep -E '^([MDR].|.[MD]) "?raw/' >/dev/null \
    && { echo "❌ 원본 창고의 기존 파일이 바뀌었습니다. 이어서 하지 않았습니다."; show_dirty; exit 1; }
  LAST_WIKI="$(ls -t "$LOGDIR"/velog-up-*-wiki.json 2>/dev/null | head -1)"
  [ -n "$LAST_WIKI" ] || { echo "❌ 직전 실행의 보고(velog-up-*-wiki.json)를 찾을 수 없습니다."; exit 1; }
  LAST_REPORT="$(result_of "$LAST_WIKI")"
fi

START_PUB="$(git rev-parse --short HEAD)"
START_PRIV="$(git -C _private rev-parse --short HEAD)"
fail=0
echo "로그: $LOG"

ALLOWED='Read,Glob,Grep,Edit,Write,MultiEdit,Skill,Task,Bash(python3 .tools/wiki_check.py *),Bash(git status),Bash(git status *),Bash(git diff *),Bash(git log *),Bash(git add *),Bash(git commit *),Bash(git -C _private status),Bash(git -C _private status *),Bash(git -C _private diff *),Bash(git -C _private log *),Bash(git -C _private add *),Bash(git -C _private commit *)'
COMMON_RULES='- 공개·비공개를 각각 커밋할 때, 추적되지 않은 새 원본 파일(_private/raw/velog/)은 비공개 커밋에 함께 넣어. 푸시는 절대 하지 마.
- Bash는 항상 볼트 루트에서 실행하고, 비공개 레포는 cd 대신 git -C _private 를 써.
- 막히면 우회하지 말고 보고해.'

if [ -z "$RESUME" ]; then
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
  WIKI_PROMPT="/velog-wiki
지금은 대화 없이 실행 중이라 질문할 수 없어. 아래 규칙을 지켜.
- Velog 가져오기(velog_fetch.py)는 방금 사람이 터미널에서 했어. 다시 하지 마.
- pending에 있는 velog 원본을 전부 반영하고, python3 .tools/wiki_check.py pending 으로 velog 원본이 0인지, lint 🚨가 0인지 확인해.
- 이어서 /publish-check 를 해. 🚨, ✂️, 공개 기준으로 정할 수 없는 부분, 모순이 하나라도 나오면 커밋하지 말고 멈춰서 번호를 붙여 보고해. 사람이 결정한 뒤 velog-up --resume 으로 이어서 한다.
- 문제가 없으면 공개 레포와 비공개 레포를 각각 커밋해.
$COMMON_RULES
마지막 보고는 10줄 이내: pending 전/후, 신규·보강 페이지, publish-check 결론, 커밋 해시(공개/비공개), 멈췄다면 번호 붙인 결정 필요 항목."
  if [ "$N" -gt 0 ]; then
    step "3/3 위키 반영·검사·커밋 (/velog-wiki) — 2~5분"
    claude -p "$WIKI_PROMPT" --permission-mode acceptEdits --allowedTools "$ALLOWED" --output-format json \
      >"$WIKI_JSON" 2>>"$LOG"
    rc=$?
    result_of "$WIKI_JSON"
    [ $rc -eq 0 ] || { echo "⚠️  위키 반영이 종료 코드 $rc로 끝났습니다."; fail=1; }
  else
    step "3/3 반영할 원본이 없어 건너뜀"
    if [ -n "$RAW_NEW" ]; then
      echo "⚠️  받아 둔 원본이 있는데 미처리 원본이 0입니다. 이미 위키에 반영된 원본일 수 있으니 확인하세요:"
      printf '%s\n' "$RAW_NEW" | sed 's/^/   /'
      fail=1
    fi
  fi
else
  # ── 이어서 하기: 사람의 결정대로 고치고 마무리 ─────────
  step "이어서 하기 — 직전 보고: $(basename "$LAST_WIKI")"
  echo "사람의 결정: $RESUME"
  RESUME_PROMPT="지금은 대화 없이 실행 중이라 질문할 수 없어. 아래 규칙을 지켜.
직전 velog-up 실행이 커밋 전에 멈췄고, 바뀐 파일은 커밋되지 않은 채 남아 있어. 그때의 마지막 보고는 다음과 같아.
<<<직전 보고
$LAST_REPORT
직전 보고>>>
사람의 결정: $RESUME

- 사람의 결정에 적힌 것만 고쳐. 결정에 없는 항목은 고치지 말고 그대로 둬.
- 고친 뒤 python3 .tools/wiki_check.py pending 과 lint 로 🚨 0을 확인하고, /publish-check 를 다시 해.
- 새로운 🚨, ✂️, 공개 기준으로 정할 수 없는 부분, 모순이 하나라도 나오면 커밋하지 말고 멈춰서 번호를 붙여 보고해.
- 문제가 없으면 _private/log.md 맨 아래에 사람의 결정을 한 줄 남기고(기존 줄은 고치지 마), 공개 레포와 비공개 레포를 각각 커밋해.
- 직전 보고에서 네가 스스로 실수라고 밝힌 항목을 사람이 고치도록 결정했다면, log.md에 correction 줄도 남겨 (형식: - YYYY-MM-DD | correction | velog-wiki | 무엇을 어떻게 고쳤나).
$COMMON_RULES
마지막 보고는 10줄 이내: 고친 내용, publish-check 결론, 커밋 해시(공개/비공개), 멈췄다면 번호 붙인 결정 필요 항목."
  claude -p "$RESUME_PROMPT" --permission-mode acceptEdits --allowedTools "$ALLOWED" --output-format json \
    >"$WIKI_JSON" 2>>"$LOG"
  rc=$?
  result_of "$WIKI_JSON"
  [ $rc -eq 0 ] || { echo "⚠️  이어서 하기가 종료 코드 $rc로 끝났습니다."; fail=1; }
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
  echo "⚠️  커밋 안 된 변경이 남아 있습니다. push하지 마세요."
  echo "   위 보고의 번호별로 결정한 뒤:  velog-up --resume \"1번 승인, 2번은 원인 미확인으로\""
  fail=1
else
  echo
  echo "보고가 괜찮으면:  git -C \"$VAULT\" push && git -C \"$VAULT/_private\" push"
  echo "배포 확인:        gh run list -R park-taegeun/ai-vault-wiki -L 1"
fi
echo "전체 로그:        $LOG"
exit $fail
