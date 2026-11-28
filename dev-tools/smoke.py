import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pw import *
S=open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'sess.txt')).read().strip()
W=int(sys.argv[1]) if len(sys.argv)>1 else 1400
js_steps=[
 ("tabs","(async()=>{for(const t of ['h','t','b','r','a','c','q','m','n']){go(t);await new Promise(r=>setTimeout(r,900))}return 'ok'})()"),
 ("form","(async()=>{go('t');await new Promise(r=>setTimeout(r,400));tf();await new Promise(r=>setTimeout(r,900));const ok=!!document.querySelector('#m .sh2.tf9 .wc26');cm();await new Promise(r=>setTimeout(r,400));return ok})()"),
 ("uploadGeneral","(async()=>{go('b');await new Promise(r=>setTimeout(r,500));upT9();await new Promise(r=>setTimeout(r,700));const t=document.querySelector('#m').innerText;cm();await new Promise(r=>setTimeout(r,400));return {kartuLain:t.includes('kartu lain'),rows:(t.match(/Tidak ada tagihan/g)||[]).length}})()"),
 ("billDetail","(async()=>{go('b');await new Promise(r=>setTimeout(r,500));const b=S.bills.find(x=>x.Statement_Amount>0);bqSel(b.ID);await new Promise(r=>setTimeout(r,1800));return !!document.querySelector('.rk26')||'mobile'})()"),
 ("reedit","(async()=>{const b=S.bills.find(x=>x.Statement_Amount>0);await billReedit(b.ID);await new Promise(r=>setTimeout(r,2000));const r=R.rows.find(x=>x.t!='Tagihan');document.getElementById('r'+r.id).querySelector('div').click();await new Promise(r=>setTimeout(r,800));const n=document.querySelectorAll('.vx-e .ai26').length;R=null;go('b');return n})()"),
 ("akun","(async()=>{akModal();await new Promise(r=>setTimeout(r,500));const n=document.querySelectorAll('#ak4 .akc[data-n]').length;cm2();return n})()"),
 ("boo","(async()=>{go('h');await new Promise(r=>setTimeout(r,400));booOpen26(1);await chSend21('APP','Tagihan mana dulu?');await new Promise(r=>setTimeout(r,800));const m=chS21('APP').msgs.slice(-1)[0];return m&&m.t.slice(0,60)})()"),
 ("search","(async()=>{go('t');Q.q='zus cofe';render();await new Promise(r=>setTimeout(r,500));const n=txF7().length;Q.q='';render();return n})()"),
]
with sync_playwright() as p:
    b,ctx,pg,errs=page(p,W,900 if W>800 else 844,W<800)
    login(pg,S);pg.goto(f'http://127.0.0.1:{PORT}/');pg.wait_for_timeout(3500)
    for name,js in js_steps:
        try: r=pg.evaluate(js)
        except Exception as e: r='EXC '+str(e)[:200]
        print(f'{name:14s}',r)
    print('JS ERRORS:',errs if errs else 'none')
    b.close()
