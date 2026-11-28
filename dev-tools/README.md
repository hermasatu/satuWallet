# dev-tools — harness uji lokal booq.id KartuKu (untuk Claude / developer)
Tidak perlu diunggah ke GitHub Pages / Supabase.
1. `npm i pdfjs-dist@3.11.174 chart.js@4.4.1 xlsx@0.18.5 @tailwindcss/browser@4 tesseract.js@5.1.1 tesseract.js-core@5.1.1 @tesseract.js-data/eng @tesseract.js-data/ind jszip` dan `pip install playwright`.
2. `./build_backend.sh ../booq_edge_function_SATU_FILE.ts` → `backend.mjs` (Edge Function asli, Postgres diganti DB memori `db.json`).
3. `node server.mjs .. 8787` → daftar akun: `curl -X POST localhost:8787/api -d '{"action":"api_register","args":[{"email":"a@b.id","name":"Uji","password":"rahasia123"}]}'` → simpan sessionToken ke `sess.txt`.
4. `python3 seed.py` (data uji) · `python3 smoke.py 1400` & `python3 smoke.py 390` (semua halaman + error JS) · `python3 probe.py 1400 b "<js>" shot.png`.
