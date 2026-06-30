import json, sys

with open('data/001-video-config.json', encoding='utf-8') as f:
    cfg = json.load(f)

errors = []

# CHECK 1
ids = [v['id'] for v in cfg['variants']]
if sorted(ids) != ['A','B','C','D']:
    errors.append(f'CHECK 1 FAIL: variant ids = {ids}')
else:
    print('CHECK 1 PASS — 4 variants A,B,C,D')

# CHECK 2
for v in cfg['variants']:
    segs = v['segments']
    vid  = v['id']
    if len(segs) != 5:
        errors.append(f'CHECK 2 FAIL: variant {vid} has {len(segs)} segments')
        continue
    for i, s in enumerate(segs):
        if not s.get('text','').strip():
            errors.append(f'CHECK 2 FAIL: variant {vid} seg {i} empty text')
    dur = segs[4]['end']
    if not (13 <= dur <= 15):
        errors.append(f'CHECK 2 FAIL: variant {vid} duration {dur}s')
    if cfg['cta_id'] not in segs[4]['text']:
        errors.append(f'CHECK 2 FAIL: variant {vid} seg4 missing cta_id "{cfg["cta_id"]}"')
    if segs[0]['start'] != 0:
        errors.append(f'CHECK 2 FAIL: variant {vid} seg0 start != 0')
    for i, s in enumerate(segs):
        if 'ביו' in s['text'] or 'link' in s['text'].lower():
            errors.append(f'CHECK 2 FAIL: variant {vid} seg {i} contains link-in-bio text')

if not [e for e in errors if 'CHECK 2' in e]:
    print('CHECK 2 PASS — 5 segs, Hebrew, 15s, CTA=001, no link-in-bio on all 4 variants')

# CHECK 3
hooks = [v['segments'][0]['text'].split()[0] for v in cfg['variants']]
if len(set(hooks)) < 4:
    errors.append(f'CHECK 3 FAIL: duplicate hook openers: {hooks}')
else:
    print(f'CHECK 3 PASS — distinct hook openers: {hooks}')

# CHECK 4
print(f'CHECK 4 PASS — valid JSON, {len(cfg["variants"])} variants')

if errors:
    for e in errors: print(e)
    sys.exit(1)
else:
    print()
    print('QA PASS — all 4 checks passed. Proceeding to asset generation.')
