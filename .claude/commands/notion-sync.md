---
description: Notion MCP로 노션 페이지를 원본으로 가져오기
argument-hint: [노션 페이지 URL 또는 검색어]
---
1. Notion MCP로 "$ARGUMENTS" 페이지를 찾아 읽어. 후보가 여러 개면 목록을 보여주고 고르게 해.
2. `_private/raw/notion/YYYY-MM-DD-페이지제목.md`로 저장해. 맨 위에 아래 두 줄을 넣고, 그 아래는 원문 그대로.
   ```
   source: <노션 페이지 URL>
   fetched: YYYY-MM-DD
   ```
3. 같은 페이지를 예전에 가져온 파일이 있어도 덮어쓰지 마 (원본은 추가만). 날짜가 다른 새 파일로 저장해.
4. 저장이 끝나면 "/ingest로 위키에 반영할까?"라고 물어봐.
