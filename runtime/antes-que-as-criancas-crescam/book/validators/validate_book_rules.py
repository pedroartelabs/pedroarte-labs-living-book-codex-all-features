from __future__ import annotations
import argparse, re, sys
from pathlib import Path
import yaml
ROOT = Path(__file__).resolve().parents[2]
BOOK = ROOT / 'book'
MANUSCRIPT = ROOT / 'manuscript' / 'final' / 'MANUSCRIPT_FINAL_PTBR.md'
BRIEFS = ROOT / 'briefs' / 'chapters'

def spec(): return yaml.safe_load((BOOK/'BOOK_SPEC.yaml').read_text(encoding='utf-8'))

def counter_rules():
    seed = (BOOK/'seeds/COUNTER_RULES_SEED.md').read_text(encoding='utf-8').lower()
    required = ['crianças não veem', 'espont', 'morte', 'explicação definitiva']
    missing = [x for x in required if x not in seed]
    if missing:
        print('COUNTER_RULES INVALID:', missing); return 1
    print('COUNTER_RULES OK'); return 0

def counter_distribution():
    files = sorted(BRIEFS.glob('CHAPTER_*_BRIEF.md')) if BRIEFS.exists() else []
    if not files:
        print('COUNTER_DISTRIBUTION DEFERRED: chapter briefs not created'); return 0
    count=0
    for f in files:
        txt=f.read_text(encoding='utf-8',errors='ignore').lower()
        if 'contador' in txt and not re.search(r'contador\s*[:=-]\s*(nenhum|não|nao|none)',txt): count += 1
    if not 12 <= count <= 16:
        print(f'COUNTER_DISTRIBUTION INVALID: {count}, expected 12..16'); return 1
    print(f'COUNTER_DISTRIBUTION OK: {count}'); return 0

def final_line():
    if not MANUSCRIPT.exists():
        print('FINAL_LINE DEFERRED: manuscript not created'); return 0
    exact=spec()['spec']['final_sentence_exact']
    txt=MANUSCRIPT.read_text(encoding='utf-8').rstrip()
    if not txt.endswith(exact):
        print('FINAL_LINE INVALID'); return 1
    print('FINAL_LINE OK'); return 0

def main():
    p=argparse.ArgumentParser(); p.add_argument('check',choices=['counter-rules','counter-distribution','final-line']); a=p.parse_args()
    return {'counter-rules':counter_rules,'counter-distribution':counter_distribution,'final-line':final_line}[a.check]()
if __name__=='__main__': raise SystemExit(main())
