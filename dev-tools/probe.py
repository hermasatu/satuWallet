"""probe.py <w> <tab> <js-file-or-expr> [shot]  — muat app, buka tab, jalankan JS, cetak hasil."""
import sys, json, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pw import *
S = open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'sess.txt')).read().strip()
w = int(sys.argv[1]); t = sys.argv[2]; js = sys.argv[3]
if os.path.exists(js): js = open(js).read()
shot = sys.argv[4] if len(sys.argv) > 4 else ''
with sync_playwright() as p:
    b, ctx, pg, errs = page(p, w, 900 if w > 800 else 844, w < 800)
    login(pg, S)
    pg.goto(f'http://127.0.0.1:{PORT}/'); pg.wait_for_timeout(3500)
    if t != '-':
        pg.evaluate(f"go('{t}')"); pg.wait_for_timeout(1500)
    try:
        r = pg.evaluate(js)
        print(json.dumps(r, ensure_ascii=False, indent=1) if not isinstance(r, str) else r)
    except Exception as e:
        print('EVAL ERR', e)
    pg.wait_for_timeout(600)
    if shot: pg.screenshot(path=shot)
    print('ERRORS:', '\n'.join(errs[:15]) or 'none')
    b.close()
