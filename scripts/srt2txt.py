import re, sys

def parse(path):
    blocks = re.split(r'\n\s*\n', open(path, encoding='utf-8').read().strip())
    out = []
    for b in blocks:
        lines = [l for l in b.strip().split('\n') if l.strip()]
        if len(lines) < 2:
            continue
        m = re.search(r'(\d+):(\d+):(\d+)[,.](\d+)\s*-->', lines[1] if lines[0].isdigit() else lines[0])
        if not m:
            continue
        secs = int(m.group(1))*3600 + int(m.group(2))*60 + int(m.group(3))
        text = ' '.join(lines[2:] if lines[0].isdigit() else lines[1:])
        out.append((secs, text.strip()))
    return out

def dedupe(cues):
    """YouTube ASR rolls text across cues; drop the repeated prefix."""
    words, stamps = [], []
    for secs, text in cues:
        new = text.split()
        # find largest overlap between tail of `words` and head of `new`
        best = 0
        for k in range(min(len(new), 20), 0, -1):
            if words[-k:] == new[:k]:
                best = k
                break
        stamps.append((secs, len(words)))
        words.extend(new[best:])
    return words, stamps

cues = parse(sys.argv[1])
words, stamps = dedupe(cues)

with open(sys.argv[2], 'w', encoding='utf-8') as f:
    si = 0
    line = []
    for i, w in enumerate(words):
        while si + 1 < len(stamps) and stamps[si+1][1] <= i:
            si += 1
        if not line:
            s = stamps[si][0]
            line.append(f'[{s//60:02d}:{s%60:02d}] ')
        line.append(w)
        if len(line) > 30:
            f.write(' '.join(line) + '\n')
            line = []
    if line:
        f.write(' '.join(line) + '\n')
print('words:', len(words))
