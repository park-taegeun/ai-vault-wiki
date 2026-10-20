"""비밀값·개인정보 탐지 패턴 — 단일 원천(single source of truth).

pre-commit 훅, Claude Code 가드 훅, wiki_check.py가 모두 이 파일을 쓴다.
패턴을 바꿀 땐 여기만 고치면 된다. 탐지 결과에 값 자체는 절대 담지 않는다.
"""
import re

SECRET_PATTERNS = {
    "Firecrawl 키": r"fc-[A-Za-z0-9]{20,}",
    "Slack 토큰": r"xox[abprs]-[A-Za-z0-9-]{10,}",
    "Anthropic 키": r"sk-ant-[A-Za-z0-9_-]{20,}",
    "OpenAI 계열 키": r"sk-[A-Za-z0-9]{32,}",
    "GitHub 토큰": r"gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{20,}",
    "Notion 토큰": r"(?:ntn|secret)_[A-Za-z0-9]{30,}",
    "Google API 키": r"AIza[0-9A-Za-z_-]{35}",
    "AWS 키": r"AKIA[0-9A-Z]{16}",
    "Bearer 키": r"Bearer\s+[A-Za-z0-9._-]{20,}",
    "개인키": r"-----BEGIN [A-Z ]*PRIVATE KEY-----",
    # 값에 숫자가 섞여 있고(진짜 키는 거의 항상 그렇다) 함수 호출 "(" 로 끝나지 않을 때만.
    # access_token = refresh_access_token() / secret = settings.CLIENT_SECRET 같은 코드는 통과.
    "키=값 형태 비밀값": r"(?i)(?:api[_-]?key|access[_-]?token|secret|password|passwd)\s*[:=]\s*['\"]?(?=[A-Za-z0-9_\-./+]*\d)[A-Za-z0-9_\-./+]{16,}(?![A-Za-z0-9_\-./+]*\()",
    # ── 짧은 비밀번호 (패치 6.9) ─────────────────────────────
    # 위 규칙은 16자 이상만 잡아서 괄호 안에 적힌 짧은 비밀번호 같은 값을 놓쳤다.
    # 길이 대신 '비밀번호 문맥'을 본다. 값(v)에 숫자나 특수문자가 있어야 하고,
    # <REDACTED>·${ENV}·**** 같은 자리표시자와 코드 식별자는 _PW_ALLOW 로 통과시킨다.
    # 한계: 영문자만으로 된 비밀번호(예: qwerasdf)는 못 잡는다. 이런 건 의미 검토가 맡는다.
    "비밀번호 문맥": r"(?i)(?:비밀번호|비번|패스워드|password|passwd|pwd)['\"]?\s*(?:[가-힣]{1,4}\s*)?[:=(（]\s*['\"`]?(?P<v>[A-Za-z0-9!@#$%^&*_+\-=.?/~]{4,})",
    "MySQL -p 비밀번호": r"(?i)\b(?:mysql|mariadb|mysqldump|mysqladmin)\b[^\n]*?\s-p(?P<v>[^\s'\"]{4,})",
    "IDENTIFIED BY 비밀번호": r"(?i)\bidentified\s+by\s+['\"](?P<v>[^'\"\n]{4,})['\"]",
}

# 비밀번호 규칙의 값이 아래에 해당하면 실제 비밀번호가 아니라고 본다.
_PW_LABELS = {"비밀번호 문맥", "MySQL -p 비밀번호", "IDENTIFIED BY 비밀번호"}
_PW_HAS_DIGIT_OR_SYMBOL = re.compile(r"[0-9!@#$%^&*+\-=?/~]")
_PW_ALLOW = re.compile(
    r"^(?:"
    r"\$.*"                                   # $NEWPW, ${DB_PASSWORD} — 환경변수
    r"|[*xX.#]+"                              # ****, xxxx, ...., #### — 가린 값
    r"|[~.]?/.*"                              # /home/user, ./config — 경로
    r"|[A-Za-z_]\w*(?:\.[A-Za-z_]\w*)+"       # settings.DB_PASSWORD, os.environ — 코드 식별자
    r")$"
)


def _pw_is_real(value):
    value = value.rstrip(".,;:")
    return bool(_PW_HAS_DIGIT_OR_SYMBOL.search(value)) and not _PW_ALLOW.match(value)


PII_PATTERNS = {
    "휴대폰 번호": r"(?<!\d)01[016789][-. ]?\d{3,4}[-. ]?\d{4}(?!\d)",
    # 앞 6자리가 실제 생년월일(월 01~12, 일 01~31)이고, 소수점 숫자의 일부가 아닐 때만
    "주민등록번호": r"(?<![\d.])\d{2}(?:0[1-9]|1[0-2])(?:0[1-9]|[12]\d|3[01])[- ]?[1-4]\d{6}(?![\d.])",
    "이메일": r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
}

# 공개해도 되는 예시용 이메일과, 이메일처럼 생긴 Git SSH 주소(git@github.com:user/repo)
_EMAIL_ALLOW = re.compile(r"(@example\.(com|org|net)$|@users\.noreply\.github\.com$|^noreply@|^git@)", re.I)

_COMPILED = [(label, re.compile(p), "secret") for label, p in SECRET_PATTERNS.items()] + [
    (label, re.compile(p), "pii") for label, p in PII_PATTERNS.items()
]


def scan_text(text):
    """텍스트에서 탐지된 항목을 [(종류, 라벨, 줄번호)]로 돌려준다. 값은 담지 않는다."""
    hits = []
    for i, line in enumerate(text.splitlines(), 1):
        for label, rx, kind in _COMPILED:
            for m in rx.finditer(line):
                if label == "이메일" and _EMAIL_ALLOW.search(m.group(0)):
                    continue
                if label in _PW_LABELS and not _pw_is_real(m.group("v")):
                    continue
                hits.append((kind, label, i))
                break
    return hits
