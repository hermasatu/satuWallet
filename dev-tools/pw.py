"""Helper Playwright: CDN -> file lokal, API Supabase -> server harness."""
import json, os, sys, time
from playwright.sync_api import sync_playwright
NM = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'node_modules')
VEND = {
    'cdn.tailwindcss.com': NM + '/@tailwindcss/browser/dist/index.global.js',
    'chart.umd.min.js': NM + '/chart.js/dist/chart.umd.js',
    'pdf.min.js': NM + '/pdfjs-dist/build/pdf.min.js',
    'pdf.worker.min.js': NM + '/pdfjs-dist/build/pdf.worker.min.js',
    'xlsx.full.min.js': NM + '/xlsx/dist/xlsx.full.min.js',
    'jszip.min.js': NM + '/jszip/dist/jszip.min.js',
}
PORT = int(os.environ.get('PORT', '8787'))

def route(r):
    u = r.request.url
    if 'supabase.co/functions' in u:
        import urllib.request
        if r.request.method == 'OPTIONS':
            return r.fulfill(status=204, headers={'Access-Control-Allow-Origin': '*', 'Access-Control-Allow-Headers': '*'})
        d = urllib.request.urlopen(urllib.request.Request(f'http://127.0.0.1:{PORT}/api', data=r.request.post_data_buffer), timeout=120).read()
        return r.fulfill(status=200, body=d, headers={'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'})
    if u.startswith(f'http://127.0.0.1:{PORT}'):
        return r.continue_()
    import re, os as _o
    m = re.match(r'https://cdn\.jsdelivr\.net/npm/((?:@[^/]+/)?[^@/]+)(?:@[^/]+)?/(.*)$', u.split('?')[0])
    if m:
        fp = NM + '/' + m.group(1) + '/' + m.group(2)
        if _o.path.isfile(fp):
            ct = 'application/wasm' if fp.endswith('.wasm') else ('application/gzip' if fp.endswith('.gz') else 'application/javascript')
            return r.fulfill(path=fp, content_type=ct, headers={'Access-Control-Allow-Origin': '*'})
    for k, f in VEND.items():
        if k in u:
            return r.fulfill(path=f, content_type='application/javascript')
    return r.abort()

def page(pw, w=1400, h=900, mobile=False):
    b = pw.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox'])
    ctx = b.new_context(viewport={'width': w, 'height': h}, is_mobile=mobile, has_touch=mobile, device_scale_factor=1)
    ctx.route('**/*', route)
    ctx.add_init_script("try{const d=new Date();localStorage.setItem('kk_m',d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0')+'-'+String(d.getDate()).padStart(2,'0'))}catch(e){}")
    pg = ctx.new_page()
    errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.on('console', lambda m: errs.append('console:' + m.text) if m.type == 'error' and 'Failed to load resource' not in m.text else None)
    return b, ctx, pg, errs

def login(pg, sess):
    pg.goto(f'http://127.0.0.1:{PORT}/')
    pg.evaluate("s=>{localStorage.setItem('SESSION_TOKEN',s)}", sess)
