# -*- coding: utf-8 -*-
"""Google Search Console rejects a date-only dateModified in the ProfilePage
block ("недопустимое значение даты/времени") — it wants full ISO 8601 with a
timezone offset. This stamps it from the latest commit, so the value stays
truthful instead of drifting.

    python3 tools/stamp-modified.py
"""
import re, subprocess, sys

def last_commit_date():
    out = subprocess.run(['git', '--no-optional-locks', 'log', '-1',
                          '--date=iso-strict', '--format=%ad'],
                         capture_output=True, text=True, timeout=60)
    return out.stdout.strip()

def main():
    date = last_commit_date()
    if not re.fullmatch(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[+-]\d{2}:\d{2}', date):
        print('could not read a usable commit date:', repr(date)); return 1
    s = open('index.html', encoding='utf-8').read()
    new, n = re.subn(r'("dateModified":\s*")[^"]*(")', r'\g<1>' + date + r'\g<2>', s, count=1)
    if not n:
        print('no dateModified field found'); return 1
    if new != s:
        open('index.html', 'w', encoding='utf-8').write(new)
        print('dateModified ->', date)
    else:
        print('already current:', date)
    return 0

if __name__ == '__main__':
    sys.exit(main())
