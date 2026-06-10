# Claude project instructions

Work token-efficiently.

Rules:
- Do not summarize the whole project.
- Inspect only relevant files first. Prefer `rg` or `find` over broad reads.
- Make the smallest correct change.
- Do not refactor unrelated code.
- Do not modify `.DS_Store`, caches, generated files, dependency folders, or build outputs.
- Before editing, state the files you intend to touch in one short sentence.
- After editing, respond only with:
  1. Files changed
  2. Tests or checks run
  3. Blockers, if any

Project notes:
- This is a static portfolio site.
- Prefer narrow HTML/CSS edits.
- For UI changes, verify the relevant page visually in a browser.
