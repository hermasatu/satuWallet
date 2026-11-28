// Harness uji lokal: index.html + backend KartuKu asli (handleKartuKu) di atas DB memori.
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
const APP = process.argv[2], PORT = +(process.argv[3] || 8787), DBF = process.argv[4] || new URL('./db.json', import.meta.url).pathname;
globalThis.Deno = { env: { get: k => process.env[k] } };
await import('./backend.mjs?' + Date.now());
let DB = fs.existsSync(DBF) ? JSON.parse(fs.readFileSync(DBF, 'utf8')) : { rid: 1, rows: [], kv: {}, files: {} };
const save = () => fs.writeFileSync(DBF, JSON.stringify(DB));
let chain = Promise.resolve();
const q = {
  async maybePrune() {},
  async loadBase() { return { rows: DB.rows.filter(r => r.tbl == 'Users' || r.tbl == 'Sessions').map(r => ({ tbl: r.tbl, rid: String(r.rid), data: r.data })), kv: JSON.parse(JSON.stringify(DB.kv)) }; },
  async loadTenant(uids) { return DB.rows.filter(r => uids.includes(r.user_id) && r.tbl != 'Users' && r.tbl != 'Sessions').map(r => ({ tbl: r.tbl, rid: String(r.rid), data: JSON.parse(JSON.stringify(r.data)) })); },
  async loadFiles(uid) { return Object.values(DB.files).filter(f => f.user_id == uid).map(f => ({ id: f.id, user_id: f.user_id, name: f.name, mime: f.mime, size: f.size, description: f.description, created: f.created })); },
  async loadFileData(ids) { const o = {}; ids.forEach(id => { o[id] = DB.files[id] ? Uint8Array.from(Buffer.from(DB.files[id].b64, 'base64')) : new Uint8Array(0); }); return o; },
  async applyChanges(ch) {
    const del = new Set(ch.deletes.map(String)); DB.rows = DB.rows.filter(r => !del.has(String(r.rid)));
    ch.updates.forEach(u => { const r = DB.rows.find(x => String(x.rid) == String(u.rid)); if (r) { r.data = JSON.parse(u.data); r.user_id = u.user_id; } });
    ch.inserts.forEach(i => DB.rows.push({ rid: DB.rid++, tbl: i.tbl, user_id: i.user_id, data: JSON.parse(i.data) }));
    ch.kvUp.forEach(e => DB.kv[e.k] = { v: e.v, exp: e.exp == null ? null : Number(e.exp) });
    ch.kvDel.forEach(k => delete DB.kv[k]);
    ch.filesNew.forEach(f => DB.files[f.id] = f);
    ch.filesMeta.forEach(f => { if (DB.files[f.id]) DB.files[f.id].description = f.description; });
    save();
  },
};
const MEM_DB = { tx: fn => (chain = chain.then(() => fn(q))).catch(e => { throw e; }) };
const MIME = { '.html': 'text/html; charset=utf-8', '.js': 'application/javascript', '.json': 'application/json', '.png': 'image/png', '.webmanifest': 'application/manifest+json', '.pdf': 'application/pdf' };
http.createServer(async (req, res) => {
  if (req.method == 'POST') {
    let b = ''; req.on('data', d => b += d); req.on('end', async () => {
      let out; try { const body = JSON.parse(b); body.__meta = {}; out = await globalThis.handleKartuKu(body, MEM_DB); } catch (e) { out = { ok: false, error: 'Server error: ' + e.message }; console.error(e); }
      res.writeHead(200, { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' }); res.end(JSON.stringify(out));
    }); return;
  }
  if (req.method == 'OPTIONS') { res.writeHead(204, { 'Access-Control-Allow-Origin': '*', 'Access-Control-Allow-Headers': '*' }); return res.end(); }
  let p = decodeURIComponent(req.url.split('?')[0]); if (p == '/') p = '/index.html';
  const f = path.join(APP, p);
  if (fs.existsSync(f) && fs.statSync(f).isFile()) { res.writeHead(200, { 'Content-Type': MIME[path.extname(f)] || 'application/octet-stream' }); return res.end(fs.readFileSync(f)); }
  res.writeHead(404); res.end('nf');
}).listen(PORT, () => console.log('ready ' + PORT));
