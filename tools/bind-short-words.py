# -*- coding: utf-8 -*-
"""Bind short function words to the word after them with a non-breaking space,
so a line never ends on 'a', 'the', 'in', 'of' and friends at any width.
Runs over the built HTML, skipping script, style and tag interiors."""
import re, sys, glob

SHORT = {
    'a','an','the','and','or','but','of','in','on','at','to','for','from','with',
    'is','are','was','be','it','its','as','by','we','so','no','not','up','if','do',
    'my','me','our','per','via','off','out','one','two','into','over','than','that',
    'this','they','you','he','she','him','her','his','all','can','has','had','how',
    'why','who','what','when','only','also','just','both','each','every','their'
}
# words we never want to end a line on; longer ones stay breakable
BIND = {w for w in SHORT if len(w) <= 4}

SKIP = re.compile(r'(?is)(<script\b.*?</script>|<style\b.*?</style>)')
TAG = re.compile(r'(<[^>]*>)')

def bind(text):
    # &nbsp; after a short word, but never across punctuation
    def repl(m):
        word = m.group(1)
        return f'{word}&nbsp;' if word.lower().strip() in BIND else m.group(0)
    return re.sub(r'\b([A-Za-z]{1,4})\s+(?=[A-Za-z0-9“"\'])', repl, text)

def process(html):
    out = []
    for chunk in SKIP.split(html):
        if not chunk:
            continue
        if SKIP.fullmatch(chunk):
            out.append(chunk); continue
        parts = TAG.split(chunk)
        for i, p in enumerate(parts):
            if p and not p.startswith('<'):
                parts[i] = bind(p)
        out.append(''.join(parts))
    return ''.join(out)

if __name__ == '__main__':
    total = 0
    for f in sys.argv[1:]:
        s = open(f, encoding='utf-8').read()
        n = process(s)
        added = n.count('&nbsp;') - s.count('&nbsp;')
        if added:
            open(f, 'w', encoding='utf-8').write(n)
        total += added
        print(f'{f}: +{added} bindings')
    print('total', total)

# Usage, after any edit that rewrites the copy:
#   python3 tools/bind-short-words.py index.html games/game*/index.html
# It is idempotent — a space already turned into &nbsp; is left alone.
