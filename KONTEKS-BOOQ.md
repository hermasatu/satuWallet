# KONTEKS PROJECT — booq.id · KartuKu (myWallet)
_Lampirkan file ini setiap kali membuka chat Claude baru. Versi terakhir: **kartuku-sb 2026.11.27**. Untuk pekerjaan Separation of Concerns lampirkan juga **SOC-BOOQ.md**._

## 1. Ringkasan
- Pemilik: Hermawan (Waterground Coffee). Tidak paham coding → minta langkah sangat rinci & **file lengkap siap Replace-All**.
- Aplikasi pencatat kartu kredit & keuangan pribadi **KartuKu**, alur kerja sama dengan versi Google Apps Script.
- Menu: **Beranda** · **Transaksi** · **Tagihan** (upload PDF → rekonsiliasi → bayar dengan bukti) · **Rekap Tagihan** · **Kelola** (Kartu, Dompet, Kategori + Jenis/Tujuan buatan, **Poin & Miles**, Pintar, Pengaturan) · **Catatan Developer**.
- Tampilan (sejak 2026.11.18): **branding booq.id + maskot BOO** — palet Deep Teal `#064E50` · Mint Teal `#159B91` · Orange `#FF922E` · Soft Gold `#FFD16B` · Cream `#F5F0E8`, font Plus Jakarta Sans. (Sebelumnya navy `#14213d`.) **Sidebar** di layar ≥900px, menu bawah di HP. Ikon & logo **SVG vektor, bukan emoji**.
- Versi "rekap per pembayar" lama tidak dipakai (tabelnya dibiarkan). Data mulai dari kosong.

## 2. Arsitektur
| Bagian | Isi |
|---|---|
| Frontend | `index.html` di GitHub Pages + (sejak 2026.11.19) `manifest.webmanifest` & folder `icons/` di samping index.html untuk ikon "Tambahkan ke layar utama"; `API_URL`, `APP_VERSION` di bagian KONFIGURASI |
| Backend | Supabase Edge Function **`hyper-service`** → `https://vfryxascchrmfikjpoxd.supabase.co/functions/v1/hyper-service` (`booq_edge_function_SATU_FILE.ts`, Verify JWT **mati**) |
| Cara kerja backend | Code.gs KartuKu + **lapisan pengganti GAS** (SpreadsheetApp, Utilities, Cache/Properties, Lock, DriveApp, UrlFetchApp). Per permintaan: data pengguna dimuat → logika sinkron → hanya baris berubah ditulis. Fetch luar dijalankan async lalu logika diulang (waktu & UUID dibekukan). 1 advisory lock Postgres. Jam Asia/Jakarta. |
| Database | `kk_rows` (rid, tbl = nama sheet, user_id, data jsonb array sesuai SCHEMA) · `kk_kv` (cache `c:` & properti `p:`) · `kk_files` (PDF & bukti, bytea) · view `kk_v_<sheet>`. RLS aktif tanpa policy. |
| Login | Email + password app, sesi 7 hari. Akun pertama = pemilik; pendaftaran lalu tertutup (`ALLOW_REGISTER=1` / `REGISTRATION_CODE`). |
| Batas AI | **Tanpa batas bawaan** (selama Gemini mengizinkan). Batas hanya aktif bila secret `AI_LIMIT_PER_6H` diisi > 0. |
| AI | API key Gemini diisi di **Kelola → Pengaturan** (disimpan `p:APP_GEMINI_API_KEY`, hanya pemilik, divalidasi ke Google; format lama `AIza…` & baru `AQ.…` diterima) — diutamakan di atas secret `GEMINI_API_KEY`. |
| Memori AI | Sheet `AiMemory` (Kind PROFIL/PREFERENSI/ATURAN/FAKTA, Active) + pola otomatis dari transaksi 400 hari (merchant → kategori & tujuan, kebiasaan per kartu). Dikirim sebagai `systemInstruction` Gemini pada baca dokumen & saran kategori (`useMemory: true`). Rute `api_aiMemory`, `api_saveAiMemory`, `api_deleteAiMemory`. |
| Secret opsional | `GEMINI_API_KEY`, `GEMINI_MODEL`, `AI_LIMIT_PER_6H`, `AI_MAX_TOKENS`, `ALLOW_REGISTER`, `REGISTRATION_CODE`, `GOOGLE_CLIENT_ID`, `ALLOWED_ORIGINS` |

## 3. Tabel verifikasi tagihan (sejak 2026.10.29)
- Baris = kartu ringkas, **klik untuk edit**. Urutan kiri→kanan: grip seret (ubah urutan) · **Jenis** (kategori internal) · nama transaksi · **kategori belanja** (pil) · nominal · tombol Split. "hal N" kecil di pojok kanan bawah → lompat ke halaman PDF.
- Warna garis kiri: merah = perlu diisi, abu = belum dicek, biru = sudah kamu cek/edit (tombol **Selesai**), hijau = cocok catatan / sudah tersimpan. Legenda + jumlah di atas daftar.
- Jenis bawaan: Belanja, Cicilan, Iuran Tahunan, Cashback, Refund, Kredit, Pembayaran, **Tagihan** (tagihan bulan lalu → Previous_Balance, tidak jadi transaksi). Jenis buatan: Settings `Custom_Types` [{name, base}]. Disimpan di kolom transaksi `Tx_Type`.
- **Semua jenis boleh minus**: minus pada jenis debit = pengembalian di kategori yang sama (Credit_Type REFUND, kategori dipertahankan).
- Tagihan bulan lalu & total pembayaran otomatis jadi baris (jenis Tagihan / Pembayaran) untuk dikonfirmasi.
- Kategori belanja terisi otomatis dari **nama transaksi** yang diketik (riwayat nama → aturan/riwayat merchant → kata kunci; tombol "Tanya AI"). Sumber saran `LABEL`.
- Pilihan kategori punya "+ Kategori baru…" & "Kelola / hapus kategori…"; pilihan Tujuan punya "+ Tujuan baru…" (Settings `Custom_Purposes` [{name, personal}]).
- Header ringkasan lebih ramping + **pie chart kategori belanja** di kanan. Panel **Poin & Miles** dan **Baris ringkasan** (centang + aksi massal).
- Konfirmasi **Yakin / Tidak Jadi** (`askSure`) untuk: hapus baris/bagian split, batal split, batal input tagihan, baca ulang AI, aksi massal, simpan dengan baris ditolak, hapus transaksi/tagihan/kartu/kategori/dompet/aturan/memori/catatan/API key/jenis/tujuan/poin, gabung ulang split, ganti nama program.

## 3b. Poin & Miles
- Sheet `Rewards` (ID, Card_ID, Bill_ID, Period, Program, Unit, Opening, Earned, Redeemed, Adjusted, Balance, Expiring, Expiry_Date, Source STATEMENT/MANUAL, Notes, …). View `kk_v_rewards`.
- Nama program bebas; nama yang pernah dipakai dikirim ke AI agar konsisten. Rute `api_rewards`, `api_saveReward`, `api_deleteReward`, `api_renameProgram`; dari tagihan lewat `api_importStatement` (`rewards`). Rute daftar buatan: `api_saveLists`.

## 3c. Rekap Tagihan (1 halaman besar)
- Rentang **bulan cetak** (Dari–Sampai) → rute `api_rekap` (tagihan + transaksi tertaut + opsi transaksi kartu yang belum masuk tagihan).
- **Siapa bayar berapa** per tujuan: Pribadi / Bisnis (`Purpose`), Reimburse, Titip bayar, Belum ditentukan — klik = saring.
- Total per kategori (klik = saring) · kapsul kartu (Ctrl/⌘ = pilih beberapa; titik status lunas/sebagian/belum; `!` = selisih rekonsiliasi).
- Semua kartu → tabel tagihan per kartu; 1 kartu → panel tagihan (total, transaksi, dibayar, sisa, cek rekonsiliasi, Bayar, Detail).
- Filter: cari, kategori, tujuan, tanggal, urutan, sembunyikan pembayaran. Kategori & tujuan bisa diubah langsung di tabel (langsung tersimpan). Unduh Excel (sheet Tagihan + Transaksi).

## 4. Catatan Developer (alur goodang.id)
- Tombol **Catatan Dev** kiri bawah / **Alt+N** → Jenis (Bug, Data Salah, Tampilan, Ide Fitur, Lainnya) · Prioritas (Tinggi, Sedang, Rendah) · catatan · **Tunjuk bagian halaman** (selector + teks elemen) · halaman `web:<menu>` otomatis.
- ID **DN-YYMMDD-HHMMSS-rrr** dibuat di perangkat; disimpan dulu di antrean lokal → dikirim ke server (ID sama = tidak dobel); gagal → "N perlu dikirim ulang".
- Status: Baru → Dikerjakan → Selesai / Ditolak. Halaman Catatan Developer: filter status & halaman, cari, **Unduh Permintaan (.md)**, JSON, Konteks Memori, Catatan baru, Sembunyikan widget; Edit, Catatan penyelesaian, Hapus.
- Claude menyebut ID catatan yang dikerjakan di laporan.

## 5. Cara mengubah kode (untuk Claude)
- Logika bisnis = bagian "KODE BISNIS KARTUKU (Code.gs)" di file .ts (juga `Code.gs` di paket). Rute baru di `ROUTES_`; sheet baru di `SCHEMA` + `TENANT` (+ view di SQL). Kolom baru ditambahkan **di ujung** daftar kolom sheet.
- Jangan pakai `await` di kode bisnis; akses luar lewat `UrlFetchApp` / `DriveApp`.
- Ikon kategori = nama ikon (food, car, bag, bolt, health, tv, brief, gift, trend, handshake, tag, coins, hand, school, game, box, receipt, megaphone, wallet, card, home2, heart, plane, phone, shirt, paw, pin) → `ic(nama)`.

## 6. Log permintaan
| ID | Isi | Status |
|---|---|---|
| (26 Okt 2026) | Susun ulang di Supabase dengan alur KartuKu GAS; ikon vektor | Selesai — kartuku-sb 2026.10.26 |
| (27 Okt 2026) | Palet & tampilan versi rekap lama, sidebar, Catatan Developer alur goodang, Rekap Tagihan 1 halaman, API key Gemini di Pengaturan | Selesai — kartuku-sb 2026.10.27 |
| DN-261026-163910-424 | Klik Abaikan tidak melompat ke atas (scroll & kotak ringkasan dipertahankan saat render ulang) | Selesai — kartuku-sb 2026.10.28 |
| DN-261026-163809-142 | Penampil PDF: zoom 50–400% (tombol / Ctrl+scroll) + lapisan teks pdf.js agar bisa disalin | Selesai — kartuku-sb 2026.10.28 |
| DN-261026-163446-180 | API key format `AQ.` diterima + Memori AI di Supabase | Selesai — kartuku-sb 2026.10.28 |
| DN-261026-191702-151 | Batas AI 10×/6 jam dihapus | Selesai — 2026.10.29 |
| DN-261026-191857-412 | Poin & Miles, nama program bebas | Selesai — 2026.10.29 |
| DN-261026-191635-204 | Centang & aksi massal baris ringkasan + konfirmasi | Selesai — 2026.10.29 |
| DN-261026-191528-293 | Header lebih ramping + pie chart kategori | Selesai — 2026.10.29 |
| DN-261026-191411-791 | Konfirmasi Yakin / Tidak Jadi untuk langkah krusial | Selesai — 2026.10.29 |
| DN-261026-191334-439 | Hierarki tampilan baru; info halaman di pojok kanan bawah → lompat ke PDF | Selesai — 2026.10.29 |
| DN-261026-191235-483 | Kartu ringkas klik-untuk-edit + warna status | Selesai — 2026.10.29 |
| DN-261026-191122-256 | Jenis paling kiri, kategori setelah nama (autofill dari nama), split di kanan nominal | Selesai — 2026.10.29 |
| DN-261026-190847-899 | Bagian split menjorok & lebih kecil | Selesai — 2026.10.29 |
| DN-261026-180443-521 | Semua jenis boleh + / − (refund di kategori sama) | Selesai — 2026.10.29 |
| DN-261026-180334-540 | Tagihan lalu & total pembayaran jadi baris Tagihan / Pembayaran | Selesai — 2026.10.29 |
| DN-261026-180205-413 | Geser urutan baris (seret / tombol naik-turun) | Selesai — 2026.10.29 |
| DN-261026-175934-253 | Tambah Jenis manual | Selesai — 2026.10.29 |
| DN-261026-175324-493 | Tambah Tujuan manual | Selesai — 2026.10.29 |
| DN-261026-190647-821 | Tambah & hapus kategori dari pilihan kategori | Selesai — 2026.10.29 |
| DN-261026-174940-769 | Tombol Pintar crash (muat ulang tanpa henti) | Selesai — 2026.10.29 |

## 7. Ide berikutnya
- Impor data lama dari Google Sheets KartuKu ke `kk_rows`.
- Kurs mata uang asing belum diuji langsung di Supabase.
- PWA / ikon aplikasi HP.
- Ringkasan poin/miles di Beranda & target promo (Konsultan Kartu Kredit).
- `Code.gs` versi Google Apps Script belum disamakan dengan 2026.10.29 (Supabase adalah versi utama).


## Rilis kartuku-sb 2026.10.31 (27 Okt 2026) — 34 catatan selesai
- File berubah: `index.html`, `booq_edge_function_SATU_FILE.ts`, `20261026100000_kartuku.sql` (jalankan ulang — aman).
- Kolom baru: Transactions `Items` (JSON beli apa/qty/sku), `Channel` (ONLINE/OFFLINE/QRIS); Cards `Bank, Network, Card_Type, Tier, Card_Context` (biaya, SnK, rules, claims, promo), `Stmt_Template`; Accounts `Acc_No, Holder, Branch, Csv_Map`.
- Settings baru: `Custom_Clients` (klien reimburse), `Custom_Loans` (cicilan manual), `Channel_Map` (channel yang dipelajari per merchant).
- Endpoint baru: `api_saveCardContext`, `api_aiAssist` (ROWS/ICON, hemat token), `api_aiSnk` (PDF/URL/teks), `api_billTx` + `replace` di `api_importStatement` (edit ulang tagihan), `api_payFromCsv`.
- Menu baru: Rekening (`tab a`), Cicilan (`tab c`), SnK & Benefit (`tab q`), Kelola → Klien; mobile: tombol "Lainnya".
- Status catatan dev: daftar `DN_DONE` di index.html → otomatis pindah ke Selesai saat aplikasi dibuka.
- Istilah: "Tujuan" sekarang disebut "Akun" di UI (nilai data tetap kolom Purpose).


## Rilis kartuku-sb 2026.11.01 (27 Okt 2026) — review UX/UI + 16 catatan selesai
- File berubah: `index.html`, `booq_edge_function_SATU_FILE.ts`. SQL **tidak** perlu dijalankan ulang.
- Endpoint baru: `api_uploadFile` (berkas umum → kk_files, ref STRUK/CICILAN), `api_getFile`, `api_setChannel` (ubah Channel saja). `api_readProofDate` dipakai juga untuk bukti cicilan.
- Items (Transactions) format v2: `{v:2, lines:[{inv,desc,amt}], fees:{ship,admin,other}, files:[{id,name,mime}]}` — "Beli apa/Qty/SKU" dihapus dari UI (format lama tetap terbaca). Di frontend disimpan di `row.itm` (BUKAN `row.it` — itu tenor cicilan).
- Custom_Loans: `plan:[{date,amount,note}]`, `pays:[{id,date,amount,note,proof:{fileId,name,mime},src}]`, catatan s.d. 1000 karakter. Bukti wajib untuk pembayaran baru.
- Clients: phone dinormalisasi `+62XX-XXXX-XXXX` di server & klien.
- UI: font default Inter (pilihan Inter/IBM Plex/Public Sans/Sistem + ukuran Ringkas/Normal/Besar di Pengaturan → Tampilan, localStorage `kk_ui`); tombol sekunder berlatar (beda dari input); tabel verifikasi pakai container query `vt` (3 tata letak menurut lebar panel); pemisah Dokumen↔Tabel bisa digeser (`kk_spl`); kalender dropdown custom untuk semua `input[type=date]` & kolom dmyF; textarea `.nta` (Enter = simpan/blur, Shift+Enter = baris baru); chip channel diklik → menu cepat.
- Semua penimpaan ada di blok terakhir index.html "kartuku-sb 2026.11.01".

| ID | Isi | Status |
|---|---|---|
| DN-261027-080545-684 | Font profesional & ukuran ringkas | Selesai — 2026.11.01 |
| DN-261027-080302-982 | Rincian cukup invoice/keterangan/nominal + multi bukti | Selesai — 2026.11.01 |
| DN-261027-075942-186 | Rincian opsional di popup ala keranjang + ongkir/admin/lainnya | Selesai — 2026.11.01 |
| DN-261027-075342-183 | Format HP +62XX-XXXX-XXXX | Selesai — 2026.11.01 |
| DN-261027-074746-514 | Tabel tidak pecah huruf per huruf saat sempit | Selesai — 2026.11.01 |
| DN-261027-071920-151 | Hapus Beli apa, Catatan di semua input | Selesai — 2026.11.01 |
| DN-261027-071754-575 | Kartu & split ringkas | Selesai — 2026.11.01 |
| DN-261027-070934-515 | Dua kotak keterangan digabung | Selesai — 2026.11.01 |
| DN-261027-070702-476 | Hierarki tulisan baris disusun ulang | Selesai — 2026.11.01 |
| DN-261027-070241-356 | Channel "?" klik untuk memilih | Selesai — 2026.11.01 |
| DN-261027-065442-390 | Riwayat urut tanggal bayar | Selesai — 2026.11.01 |
| DN-261027-065226-319 | Riwayat bisa diedit + baca bukti otomatis | Selesai — 2026.11.01 |
| DN-261027-065043-411 | Kalender dropdown di semua tanggal | Selesai — 2026.11.01 |
| DN-261027-064934-803 | Bukti wajib saat catat pembayaran cicilan | Selesai — 2026.11.01 |
| DN-261027-064839-627 | Catatan Shift+Enter | Selesai — 2026.11.01 |
| DN-261027-064618-875 | Rencana pembayaran cicilan (input/edit/hapus) | Selesai — 2026.11.01 |

### Ide berikutnya (saran)
- Pengingat H-3 cicilan & tagihan di Beranda; beban cicilan bulanan vs limit kartu untuk memilih kartu promo 0% berikutnya.
- Rincian & bukti juga di form transaksi manual.


## Rilis kartuku-sb 2026.11.02 (27 Okt 2026, siang) — 19 catatan selesai
- File berubah: `index.html`, `booq_edge_function_SATU_FILE.ts`, `20261026100000_kartuku.sql` (opsional — hanya menambah kolom Location & File_Hash di view; aman dijalankan ulang).
- Kolom baru (di ujung): Transactions `Location`; Bills `File_Hash` (SHA-256 file tagihan, untuk tolak duplikat). AI statement kini mengembalikan `location` per baris dan `network/tier/cardType` di profil kartu.
- Endpoint baru: `api_aiItems` (teks OCR struk → lines/fees/k; hanya teks dikirim), `api_getDevContext` / `api_saveDevContext` (Settings `Dev_Context`, `Dev_Context_At`).
- Card_Context tambahan: `limitGroup` (limit bersama), `sources` (link website resmi). cardOut_ menambah `Holder_First` (nama depan pemegang) untuk label kartu.
- Frontend: label kartu `cardLbl(c)` = Nama · pemegang · ••4digit; tombol Edit tunggal di detail tagihan → `billReedit` (+ PDF dimuat ulang `stmtLoad`, highlight `pdfHL`); status baris `ai` (ungu) sampai Selesai; tombol "Isi N baris dengan AI"; Rincian: drop/paste ke tombol → OCR lokal → `api_aiItems`; penampil bukti kecil `fView`; Transaksi: tab Terkonfirmasi (Bill_ID / Import_Key) · Memo · Semua, kartu ringkas `txC`; form transaksi "Detail lainnya"; Konteks Memori modal (`ctxView`); log permintaan di modal Catatan Dev; konfirmasi aktif/nonaktif kartu & tandai lunas; channel label Online · EDC · QRIS.

| ID | Isi | Status |
|---|---|---|
| DN-261027-121104-200 | Drop/paste bukti ke tombol Rincian → OCR → AI isi | Selesai — 2026.11.02 |
| DN-261027-120427-877 | Tombol Isi dengan AI di popup Rincian (OCR lokal) | Selesai — 2026.11.02 |
| DN-261027-120352-581 | Penampil bukti kecil + zoom | Selesai — 2026.11.02 |
| DN-261027-120041-108 | Satu tombol AI untuk semua baris + cek satu per satu | Selesai — 2026.11.02 |
| DN-261027-115828-875 | Nama kartu: pemegang + 4 digit | Selesai — 2026.11.02 |
| DN-261027-115505-989 | Log permintaan di modal Catatan Dev | Selesai — 2026.11.02 |
| DN-261027-091341-498 | Tolak tagihan duplikat persis | Selesai — 2026.11.02 |
| DN-261027-091309-726 | Satu tombol Edit di detail tagihan | Selesai — 2026.11.02 |
| DN-261027-091017-173 | Kolom Lokasi terpisah + tanda luar negeri | Selesai — 2026.11.02 |
| DN-261027-090833-876 | Kapsul channel rapi: Online · EDC · QRIS | Selesai — 2026.11.02 |
| DN-261027-090530-479 | PDF muncul saat edit ulang + highlight baris | Selesai — 2026.11.02 |
| DN-261027-090150-644 | Konteks Memori dilihat & diperbarui | Selesai — 2026.11.02 |
| DN-261027-115355-566 | Kartu transaksi ringkas, bisa dibuka | Selesai — 2026.11.02 |
| DN-261027-074043-684 | Transaksi: tab Terkonfirmasi vs Memo (mobile) | Selesai — 2026.11.02 |
| DN-261027-073834-657 | Form transaksi: bagian opsional dilipat | Selesai — 2026.11.02 |
| DN-261027-092224-997 | Konteks & SnK dari website resmi | Selesai — 2026.11.02 |
| DN-261027-091851-872 | Limit bersama antar kartu | Selesai — 2026.11.02 |
| DN-261027-091722-371 | Konfirmasi aktif/nonaktif kartu | Selesai — 2026.11.02 |
| DN-261027-091524-423 | Info kartu dari AI + konfirmasi perubahan | Selesai — 2026.11.02 |

### Ide berikutnya
- Deteksi anomali lanjutan dari Lokasi: kota baru untuk merchant langganan, 2 kota berjauhan di hari yang sama.
- Rincian & bukti di form transaksi manual; limit bersama juga dihitung di peringatan "limit tinggi" server.


## Rilis kartuku-sb 2026.11.03 (28 Okt 2026) — 9 catatan selesai
- File berubah: `index.html`, `booq_edge_function_SATU_FILE.ts` (SQL tidak berubah dari 2026.11.02).
- Format tanggal global **DD-Mmm-YYYY** (`fdd`, `dmyMask`, `dnDate`); parser `dmyISO` tetap menerima format lama.
- Akun & Sub akun: Purposes kini `{name, personal, parent}` (parent = PERSONAL / BUSINESS / nama akun utama). Helper `akTops/akSubs/akParent/akLbl/akPanel/akOpts/akSet`. Transaksi menyimpan 1 nilai Purpose (sub bila dipilih). Reimburse disembunyikan dari tabel verifikasi (data lama tetap).
- Baris verifikasi v3 (`vrow/vEdit/vKids`): kategori kecil sebelum nama (tidak dobel), tanggal bertumpuk, lokasi di bawah nama, panel edit 3 kolom, channel = segmented `.segc`, akun = pil `.akg`. AI otomatis mengisi setelah upload (Pengaturan → Tampilan → "Isi otomatis dengan AI").
- Duplikat tagihan: file sama (File_Hash) atau kartu + periode/tgl cetak sama → dialog Edit / Batalkan (`dupAsk`).
- Endpoint baru: `api_ctxIngest` (catatan + PDF/screenshot + ≤6 website di-scrape server → 1x AI → konteks + `suggest` sesuai pola pemakaian), `api_saveCardImage` (gambar kartu dari link/unggahan → kk_files, `Card_Context.imageId`), `api_saveBankLogo` (Settings `Bank_Logos`, data URL kecil; dari PDF tagihan).
- Kelola Kartu v3: gambar kartu kiri (`cardFace`, default desain otomatis), status di sebelah nama, aksi di kanan, limit bersama inline (`lgTog`). Logo bank/jaringan = ikon resmi dari domain bank (Google favicon service) atau logo tersimpan dari PDF.
- PDF viewer: "Pas lebar" memaksa fit + auto-fit saat panel digeser; zoom 10%. Bottom sheet: `dg` baru (tarik dari pegangan atau isi saat scroll di atas).

| ID | Isi | Status |
|---|---|---|
| DN-261028-004608-369 | Kartu baris tagihan dirapikan + akun/sub akun | Selesai — 2026.11.03 |
| DN-261028-001350-974 | AI bar kiri/kanan + Konteks memori (ketik/file/website) | Selesai — 2026.11.03 |
| DN-261028-000853-334 | Semua tanggal DD-Mmm-YYYY | Selesai — 2026.11.03 |
| DN-261028-000754-979 | Pas lebar & zoom PDF | Selesai — 2026.11.03 |
| DN-261027-234944-982 | Tagihan sudah ada → Edit / Batalkan | Selesai — 2026.11.03 |
| DN-261028-000412-405 | Limit bersama inline | Selesai — 2026.11.03 |
| DN-261027-235924-213 | Kartu: gambar kiri, aksi kanan, status di nama | Selesai — 2026.11.03 |
| DN-261027-235520-255 | Logo bank & jaringan + update kartu dikonfirmasi | Selesai — 2026.11.03 |
| DN-261027-223457-553 | Popup mudah ditarik untuk ditutup | Selesai — 2026.11.03 |

### Ide berikutnya
- Rekap Tagihan dikelompokkan per Akun utama dengan rincian Sub akun.
- Konteks memori: jadwal scrape ulang website resmi tiap bulan; usulan masuk ke Beranda.


## Rilis kartuku-sb 2026.11.04 (28 Okt 2026) — 38 catatan selesai
- File berubah: `index.html`, `booq_edge_function_SATU_FILE.ts`. SQL **tidak** perlu dijalankan ulang.
- **Prinsip kerja Claude (wajib, dari catatan pemilik):** (1) arsitektur & tampilan selalu RINGKAS; (2) teks penjelasan minimal — penjelasan wajib taruh di hover (`tipI()` / `data-tip`); (3) selalu pilih alur paling produktif & minim human error tanpa menunggu diminta (mis. penampil gambar digabung, bukti langsung dibaca); (4) semua input gambar wajib bisa klik / seret / Ctrl+V; (5) AI selalu key gratis dulu.
- **AI 2 key:** Kelola → Pengaturan: "Key gratis" (`p:APP_GEMINI_API_KEY` / secret `GEMINI_API_KEY`) dan "Key berbayar" (`p:APP_GEMINI_API_KEY_PAID` / secret `GEMINI_API_KEY_PAID`). `geminiCall_` → `geminiTry_` gratis maks 3 gagal → berbayar. Model terpilih: `GEMINI_MODEL_AUTO` / `GEMINI_MODEL_AUTO_PAID`. Metrik `ai_tier_free/paid` (tampil di Pengaturan).
- **Akun:** `customPurposes_` kini mengirim `parent` (bug lama: sub akun hilang induknya setelah reload). Urutan = urutan array Custom_Purposes. Kelola → **Akun** (G='u', `akH/akBind/akMove/akRen/akAdd/akDel`, modal `akModal`). Rute `api_renamePurpose` (ganti nama + transaksi lama ikut). `ppMgr` lama diarahkan ke Kelola Akun. Pribadi/Bisnis bawaan selalu paling depan.
- **Tabel verifikasi v4:** `vrow` grid `lr4` (tanggal · transaksi · kapsul [AKUN › sub] (Kategori) (Channel) · nominal); `vEdit` grid `e4` (thumbnail bukti · nominal + catatan · akun/sub akun + kategori + channel); tanggal = kapsul terkunci `dChip/dUnl`; jenis tanpa select → `tyPick`. Status konfirmasi baru `r.cf` (hanya dari Selesai; edit ulang tagihan = semua cf). Belum cf = transparan. Selesai membuka baris berikutnya. Simpan dengan baris belum cf / selisih total → konfirmasi. `r.rb` (reimburse) dipaksa false saat simpan.
- **Catatan:** `ntSet` → `ntNorm` (seragamkan dengan riwayat, fuzzy ≤1 huruf) + `ntUndo`; `ntLocal` (merchant + nominal sama) setelah baca; AI `api_aiAssist` ROWS menerima `hist` & `ocr`, mengembalikan `nt`. Flag `r.ntAI` (ungu miring).
- **Bukti:** `thbH` thumbnail (hover = `lens` zoom, klik kanan = `ocrShow`, klik = Rincian), `itQuick` → upload → `itAuto` (OCR cache `OCRC[fileId]`, `invFind` pola no. pesanan → `invHint` ke `api_aiItems`, yang kini juga mengembalikan `date` & `note`). Rincian `itR` 2 kolom (penampil kiri, kartu pesanan kanan). Dobel no. pesanan: `rowDup/invAll`.
- **Pemilih kategori** `kpOpen` (⚙ Kategori → `catMgr` baru, ketik = tambah dengan ikon `iconFor`, klik ikon = `kf2`). Pustaka ikon `ICON_KW` (±180 ikon, kata kunci Indonesia) + `icLib` (cari). Ikon baru antara lain: cake, pizza, motor, wifi, steth, tooth, users, building, warehouse, gear, pen, loc, scan, dll.
- **Tanggal masuk akal:** `dSane()` setelah baca — tanggal di luar (tgl cetak −80 hari … +5 hari) dicoba dibalik DD/MM↔MM/DD / tahun ±1.
- **Duplikat:** rute `api_dupCheck` dipanggil saat file dipilih (`up`), setelah baca (`ekstrak`), dan saat kartu dipilih (`pickCard`).
- **Rekonsiliasi:** `rcBar()` lengket di bawah tabel (`#rcb`).
- **Poin & Miles:** `saveRewards_` mengisi saldo awal dari periode sebelumnya menurut tanggal; di tabel `rwPrev` menampilkan saldo periode lalu / peringatan periode sesudahnya.
- **Konteks kartu sama persis:** `prodKey_` (bank + nama produk tanpa pemegang) → `ctxShare_` di `api_saveCardContext` & `saveCardCtx_` (limit, limitGroup, klaim tetap per kartu). Template baca lokal dipinjam dari kartu bank/produk sama (`tplTry` wrapper).
- **Cicilan:** `civ` baru (kartu `ci4`): gambar kiri (Settings `Inst_Meta` {name,img,fee} untuk cicilan kartu; Loans `img`, `fee`), meteran Rencana · Aktual · Biaya % dari pokok, aksi kanan. `saveLists` menerima `instMeta`, `akunOrder`.
- **Global:** `tidyEl` (spasi/enter berlebih dibuang di semua input), `showOpenFilePicker({id: halaman})` mengingat folder per halaman, seret/tempel gambar generik (`data-fz="idInput"`), sidebar web `html.dsk` (ciut ke ikon <1200px atau tombol «, localStorage `kk_rail`, submenu Kelola saat hover), tooltip `#tipx`, `tipify()` mengubah paragraf penjelasan panjang jadi ikon i.
- Konfirmasi Pembayaran `bp` baru: bukti kiri → `pset` OCR → tanggal (`pdates`), nominal (`amtFind`), rekening; AI (`pai`) otomatis bila tanggal tak terbaca.

| ID | Isi | Status |
|---|---|---|
| DN-261028-220309-734 | Kelola Akun kapsul + gear (seret, ganti nama) | Selesai — 2026.11.04 |
| DN-261028-215539-146 | Tipografi & susunan profesional, penjelasan di hover | Selesai — 2026.11.04 |
| DN-261028-214618-797 | Spasi / enter berlebih dibuang di semua input | Selesai — 2026.11.04 |
| DN-261028-213854-489 | Akun & sub-akun dipisah, induk tersorot | Selesai — 2026.11.04 |
| DN-261028-213534-213 | AI gratis dulu, 3x gagal → berbayar | Selesai — 2026.11.04 |
| DN-261028-213309-104 | Poin & miles ikut urutan tanggal | Selesai — 2026.11.04 |
| DN-261028-211054-707 | Bukti bayar langsung OCR + quick view + Show OCR | Selesai — 2026.11.04 |
| DN-261028-205115-940 | Halaman tagihan minim teks | Selesai — 2026.11.04 |
| DN-261028-135934-469 | Tanggal DD/MM vs MM/DD masuk akal | Selesai — 2026.11.04 |
| DN-261028-133138-808 | Pemilih kategori ⚙ + ketik tambah | Selesai — 2026.11.04 |
| DN-261028-132655-703 | Ikon pensil & keranjang | Selesai — 2026.11.04 |
| DN-261028-132520-655 | Pustaka ikon + kata kunci + cari | Selesai — 2026.11.04 |
| DN-261028-110445-271 | Total baris = total tagihan (bar rekonsiliasi) | Selesai — 2026.11.04 |
| DN-261028-110313-721 | Kapsul 1 kolom | Selesai — 2026.11.04 |
| DN-261028-105909-261 | Folder terakhir per halaman | Selesai — 2026.11.04 |
| DN-261028-105648-573 | No. pesanan dari screenshot | Selesai — 2026.11.04 |
| DN-261028-104948-881 | Tanggal terkunci | Selesai — 2026.11.04 |
| DN-261028-103348-367 | Konteks memori: ringkasan di kanan | Selesai — 2026.11.04 |
| DN-261028-102430-997 | AI isi semua kolom + seragamkan catatan | Selesai — 2026.11.04 |
| DN-261028-101815-295 | Catatan diisi AI, bisa diedit | Selesai — 2026.11.04 |
| DN-261028-101655-975 | Quick view zoom + auto baca AI | Selesai — 2026.11.04 |
| DN-261028-100928-481 | No. pesanan & nominal, cegah dobel | Selesai — 2026.11.04 |
| DN-261028-085140-389 | Baris rincian lebih lega | Selesai — 2026.11.04 |
| DN-261028-084846-131 | Reimburse dihapus | Selesai — 2026.11.04 |
| DN-261028-084216-213 | Web tidak jadi tampilan HP, sidebar ikon | Selesai — 2026.11.04 |
| DN-261028-083755-998 | Animasi buka/tutup | Selesai — 2026.11.04 |
| DN-261028-083516-252 | Foto kiri, nominal & catatan kanan | Selesai — 2026.11.04 |
| DN-261028-083114-364 | Hasil AI belum dianggap selesai, transparansi | Selesai — 2026.11.04 |
| DN-261028-010036-154 | Penampil gambar digabung | Selesai — 2026.11.04 |
| DN-261028-005715-670 | Pilihan Jenis dihapus | Selesai — 2026.11.04 |
| DN-261028-005035-506 | Tolak duplikat saat upload | Selesai — 2026.11.04 |
| DN-261028-004910-948 | Tombol edit ganda dihapus | Selesai — 2026.11.04 |
| DN-261028-212910-367 | Format OCR non-AI per bank & jenis kartu | Selesai — 2026.11.04 |
| DN-261028-212554-342 | Kartu cicilan baru | Selesai — 2026.11.04 |
| DN-261028-112646-758 | Kartu sama persis = konteks sama | Selesai — 2026.11.04 |
| DN-261028-081911-745 | Gambar kartu seret / Ctrl+V | Selesai — 2026.11.04 |
| DN-261028-011131-761 | Tombol pilih gambar dihapus | Selesai — 2026.11.04 |
| DN-261028-011027-350 | Semua input gambar seret / Ctrl+V | Selesai — 2026.11.04 |

### Ide berikutnya
- Rekap Tagihan dikelompokkan per Akun utama › Sub-akun.
- Pustaka ikon untuk sub-akun; ringkasan "siapa bayar berapa" per sub-akun di Beranda.
- Batas "Folder terakhir" hanya Chrome/Edge — Safari/Firefox tetap folder bawaan browser.


## Rilis kartuku-sb 2026.11.05 (30 Okt 2026) — 38 catatan selesai
- File berubah: `index.html`, `booq_edge_function_SATU_FILE.ts`. SQL **tidak** perlu dijalankan ulang (kolom baru di ujung sheet Accounts).
- Kolom baru: Accounts `Acc_Product` (nama produk: Tahapan, Everyday Account…), `Acc_Context` (JSON: purpose, notes, promos, benefits, rates, fees, terms, sources, suggest), `Bal_Snaps` (JSON [{v, at, note}] = Saldo Saat Ini + jam). `api_saveAccount` kini MEMPERTAHANKAN field yang tidak dikirim; `Bal_Snap_Add:{v}` menambah snapshot; Holder selalu kapital. accountsView_ mengirim `product, ctx, snaps`.
- Settings baru: `Smart_Formats` (maks 40), `Pdf_Pw` (password PDF per kunci `C:<bank>` / `F:<nama file>`).
- Kartu: Statement_Date / Due_Date boleh kosong. `cards_()` → `cardDays_()` menambah `Sd_Src/Dd_Src` (SET/LEARNED/NONE) + `Day_Range {sd:[min,max], dd:[min,max], n}` dari ≤12 tagihan; bila kosong dipakai tanggal tagihan terbaru (jatuh tempo = paling dekat). Card_Context baru: `minPay {pct, floor}`, `elig {minIncome, minLimit, minAge, docs, notes}`.
- Konteks tidak tercampur: `ctxScrub_()` membuang info bank / program poin lain (daftar `BANK_WORDS_`); `api_ctxIngest` menyebut kartu/rekening yang diproses, TANPA memori AI, menerima `files[]` (≤6) dan `accountId` (konteks rekening, `accCtxClean_`). Rute `api_ctxScrub` dijalankan sekali dari frontend (localStorage `kk_scrub1105`).
- Multi kartu (BCA): AI mengembalikan `cards[]` + `c4` per baris; frontend `mcApply()` (juga deteksi lokal nomor kartu tersamar) → `r.cd`; `api_importStatement` menerima `Sub_Card_ID` per baris → transaksi tersimpan di kartunya, Bill_ID tetap tagihan gabungan (billTx_ & edit ulang ikut Bill_ID). Jenis buatan otomatis **Pindah Limit** (base Pembayaran, `r.pld` +1/−1, tidak dikirim sebagai transaksi, dihitung di `rc4`). Lokasi berisi nama kartu dibuang (`locClean`, juga di aiSanitize_).
- Smart Parse: `spTry` (sebelum tplTry) mencocokkan penanda halaman (`anchors`, bukan nama transaksi/tanggal/jumlah baris) + bank; label ringkasan & label tanggal (`dlab`). Setelah baca AI → `spLearn` simpan `SP-<BANK>-<PRODUK>-NN` lewat `api_saveSmartFormat`; rute `api_smartFormats`. Gambar dengan OCR ≥200 karakter dikirim ke AI sebagai teks. `geminiCall_` mendukung `forcePaid`; `MAX_TOKENS` → ulang dengan key berbayar & 60k token.
- Password PDF: `pdfjsLib.getDocument` dibungkus → coba password tersimpan otomatis (juga stmtLoad); rute `api_pdfPw`.
- File upload tagihan disalin ke memori (`up` wrapper) — perbaikan "Gagal membaca file". `mi()` membuang .00/,00 (DEC2).
- Frontend baru: Tagihan `BQ` (cari/filter/urut) + Export (`rxExport`, Excel) / Import (`rxImport`, rute `api_aiMap` hanya header + 8 baris). Rekening `acv` 2 panel (`sxH` + `spl2Bind`, kunci localStorage `kk_sx_<nama>`), `rkPanel` (Saldo Saat Ini, kegunaan & konteks, promo, arus 30 hari), `rkF2` (logo, produk `ACC_PROD`, bisa di atas popup), `rkMutPanel`, jenis mutasi `RK_KD/RK_KC` (FEE, INST→Custom_Loans pays src MUTASI, INT, RB, INSTIN, XFER ke hutang/aset). Halaman **Cari Promo** (tab `x`, `pxv`). Menu rail **Kartu Kredit** (`data-t="kk"`, G='c') di bawah Rekening. Komponen gambar `qvShow` (hover) / `zView` (klik, kaca pembesar) / `lensBind`. Pemisah `#spl` bisa ditutup penuh (≤10% / ≥90%) → panah.
- Cicilan: pensil di sebelah nama (ciEdit), gambar setinggi kartu `object-fit:contain` + pensil/tong sampah (`ciImgDel`), form bayar `lp5` foto kiri.

| ID | Isi | Status |
|---|---|---|
| DN-261030-075156-331 | Banyak PDF di konteks kartu | Selesai — 2026.11.05 |
| DN-261029-230107-852 | Syarat pengajuan & minimum bayar di konteks | Selesai — 2026.11.05 |
| DN-261029-223315-902 | Tgl cetak & tempo tidak wajib, dipelajari | Selesai — 2026.11.05 |
| DN-261028-112814-733 | Konteks tidak tercampur antar bank | Selesai — 2026.11.05 |
| DN-261029-223127-850 | Menu Kartu di bawah Rekening | Selesai — 2026.11.05 |
| DN-261029-222701-536 | Saldo Saat Ini + timestamp, dicocokkan | Selesai — 2026.11.05 |
| DN-261029-222427-606 | Atas nama kapital | Selesai — 2026.11.05 |
| DN-261029-222335-735 | Konteks rekening + Cari Promo | Selesai — 2026.11.05 |
| DN-261029-221900-505 | Nama produk rekening + database | Selesai — 2026.11.05 |
| DN-261029-221315-618 | Logo bank | Selesai — 2026.11.05 |
| DN-261029-022217-754 | Logika pemasukan/pengeluaran + 2 panel | Selesai — 2026.11.05 |
| DN-261029-021528-137 | Biaya admin | Selesai — 2026.11.05 |
| DN-261029-021452-897 | Bayar cicilan → menu Cicilan | Selesai — 2026.11.05 |
| DN-261029-220831-307 | +Rekening di pembayaran (OCR) | Selesai — 2026.11.05 |
| DN-261029-215245-450 | Password PDF diingat | Selesai — 2026.11.05 |
| DN-261029-205542-892 | Gagal membaca file | Selesai — 2026.11.05 |
| DN-261029-203451-706 | Cari/filter/urut tagihan | Selesai — 2026.11.05 |
| DN-261029-203402-446 | Smart Parse ber-ID | Selesai — 2026.11.05 |
| DN-261029-174809-888 | Total tagihan Rp0 | Selesai — 2026.11.05 |
| DN-261029-174703-212 | Cari format dulu, simpan format | Selesai — 2026.11.05 |
| DN-261028-233827-717 | Export / Import rekap | Selesai — 2026.11.05 (menunggu data lama pemilik) |
| DN-261028-233452-293 | Seret gambar WhatsApp | Selesai — 2026.11.05 |
| DN-261028-233202-223 | Rasio foto bukti asli | Selesai — 2026.11.05 |
| DN-261028-232757-677 | Minimum bayar % / Rp | Selesai — 2026.11.05 |
| DN-261028-232538-492 | Abaikan .00 | Selesai — 2026.11.05 |
| DN-261028-232058-985 | Nominal terlihat di panel sempit | Selesai — 2026.11.05 |
| DN-261028-232007-375 | Nama kartu bukan lokasi | Selesai — 2026.11.05 |
| DN-261028-231905-609 | Pindah limit antar kartu BCA | Selesai — 2026.11.05 |
| DN-261028-231646-977 | BCA multi kartu | Selesai — 2026.11.05 |
| DN-261028-231420-163 | Klik perbesar + kaca pembesar | Selesai — 2026.11.05 |
| DN-261028-231200-844 | Warna akun vs sub-akun | Selesai — 2026.11.05 |
| DN-261028-230832-950 | Tambah/edit/hapus akun | Selesai — 2026.11.05 |
| DN-261028-225700-486 | Format → gratis → berbayar → simpan | Selesai — 2026.11.05 |
| DN-261028-225015-261 | Pemisah tutup penuh → panah | Selesai — 2026.11.05 |
| DN-261028-221422-133 | Rentang tanggal penagihan | Selesai — 2026.11.05 |
| DN-261029-024045-420 | Form bayar cicilan foto kiri | Selesai — 2026.11.05 |
| DN-261029-022853-946 | Gambar cicilan besar, PNG, edit/hapus | Selesai — 2026.11.05 |
| DN-261029-022410-963 | Ikon pensil di nama cicilan | Selesai — 2026.11.05 |

### Ide berikutnya
- Profiling kelayakan kartu (penghasilan vs `elig.minIncome`) di Beranda.
- Hapus / ganti nama format Smart Parse dari daftarnya.
- Struktur bagian multi kartu juga dipakai pada format Smart Parse untuk baca lokal per kartu.


## Rilis kartuku-sb 2026.11.06 (30 Okt 2026) — 15 catatan + 2 permintaan pemilik
- File berubah: `index.html`, `booq_edge_function_SATU_FILE.ts`. SQL tidak perlu dijalankan.
- Backend: rute `api_settleOld` (tagihan periode < bulan ini & belum lunas → `Legacy_Paid` = sisa, lalu `syncBill_`; dijalankan SEKALI otomatis dari frontend, flag localStorage `kk_settle1106`; fungsi manual `settleOld()`); `api_aiItems` mengembalikan `shop` per baris; `Pdf_Pw` menampung nilai terenkripsi (≤400 karakter).
- Password PDF: disimpan `enc1:<iv>.<ciphertext>` (AES-GCM, kunci PBKDF2 dari email pengguna + salt aplikasi), nilai lama otomatis dienkripsi ulang. Detail tagihan PDF terproteksi → `dpPw()` (kotak password + "Ingat password"); form upload punya centang `#f_rpwr`.
- Tagihan: 2 panel (`sxH('tag')`, detail lewat `bdtPanel()` yang menangkap `mo()` dari `bdt`), `bqSel(id)`, `BQ.bk / BQ.nw / BQ.sel`, quick filter kapsul logo bank & jaringan, mini kartu `blMini()` di tiap kartu tagihan.
- Konfirmasi pembayaran: `pdates` memilih tanggal paling masuk akal + `dpSync('f_pd')` mengisi tampilan kalender; rekening `.psw` (select dominan, + ikon kecil), saran OCR di `#psh`.
- Verifikasi: kolom `shop` di rincian (itemsOut v2 kini menyimpan shop), `ocrReclass()` setelah OCR bukti (kategori/akun/catatan, juga per bagian split), ringkasan bukti `.its` di panel baris non-split, drop file ke thumbnail via listener capture (baris .vx tidak lagi menelan drop), bagian split default bernama merchant.
- Tampilan: default font IBM Plex Sans (`uiGet`; pilihan manual tetap dihormati, flag `f1106`), `lbTidy()` memindah teks dalam kurung / setelah "—" dari label ke ikon i, ikon sidebar Kartu Kredit sejajar.
- Import rekap: akun yang belum ada dibuat otomatis; kolom `Cicilan ke` / `Cicilan dari` → Type Cicilan untuk kartu kredit.
- File data: `KartuKu_Import_Rekap_Kartu_Kredit_2024-2026.xlsx` (sheet Transaksi = format KartuKu Rekap v1, 3.125 baris Apr 2024–Sep 2026; Ringkasan per Akun; Kartu (Sumber); Dilewati = 108 baris pembayaran / tagihan lalu).

| ID | Isi | Status |
|---|---|---|
| DN-261030-114951-679 | Tagihan 2 sisi (detail di kanan) | Selesai — 2026.11.06 |
| DN-261030-114903-194 | Quick filter kapsul berlogo | Selesai — 2026.11.06 |
| DN-261030-113829-655 | Tanggal bayar dari bukti | Selesai — 2026.11.06 |
| DN-261030-112545-325 | Rekening dominan, + Rekening kecil | Selesai — 2026.11.06 |
| DN-261030-092124-743 | Font profesional seluruh aplikasi | Selesai — 2026.11.06 |
| DN-261030-092005-126 | Kotak password + ingat (terenkripsi) | Selesai — 2026.11.06 |
| DN-261030-091818-245 | Mini kartu + logo di daftar tagihan | Selesai — 2026.11.06 |
| DN-261030-090009-970 | Nama toko di rincian | Selesai — 2026.11.06 |
| DN-261030-085841-922 | Thumbnail bukti fleksibel | Selesai — 2026.11.06 |
| DN-261030-084728-930 | Isi ulang kategori & catatan setelah OCR | Selesai — 2026.11.06 |
| DN-261030-084411-746 | Hasil baca bukti di baris non-split | Selesai — 2026.11.06 |
| DN-261030-084105-675 | Seret PDF ke thumbnail | Selesai — 2026.11.06 |
| DN-261030-083919-160 | Split bernama merchant | Selesai — 2026.11.06 |
| DN-261030-090617-511 | Ikon Kartu Kredit sidebar | Selesai — 2026.11.06 |
| DN-261030-082416-964 | Label ringkas, penjelasan di hover | Selesai — 2026.11.06 |
| (30 Okt 2026) | Tagihan lama otomatis lunas tanpa bukti | Selesai — 2026.11.06 |
| (30 Okt 2026) | Rekap kartu kredit lama → file import | Selesai — file xlsx |


## Rilis kartuku-sb 2026.11.07 (30 Okt 2026) — 19 catatan selesai
- File berubah: `index.html`, `booq_edge_function_SATU_FILE.ts`. SQL **tidak** perlu dijalankan.
- Semua penimpaan frontend ada di blok terakhir index.html "kartuku-sb 2026.11.07" (CSS `css1107`, fungsi berakhiran `7`).
- Backend baru: `api_aiGround` (mode PROMO / LOGO / CARD — Gemini + Google Search grounding `tools:[{google_search:{}}]`, otomatis ulang tanpa pencarian bila model menolak; `NeedSignal` tetap dilempar), `api_cardProfile` (Manual Prompt → profil kartu + syarat), `api_billsFromTx` (transaksi kartu tanpa tagihan → tagihan per kartu & periode; `hints` dari kolom "Periode Tagihan" impor, `derive` dari tgl cetak; periode < bulan ini = lunas via Legacy_Paid; tagihan PDF/manual tidak disentuh; Import_Meta `{source:'IMPORT'}`).
- Settings baru: `Inst_Merge` [{id,name,purpose,keys:[gKey]}] (gabung cicilan), `Bank_Domains` {nama: domain} (logo hasil Google Search). `api_saveLists` menerima `instMerge`, `bankDomains`. `pubSettings_` mengirim keduanya.
- Card_Context baru: `profile` {role, bestFor[], avoid[], benefits[], prompts[{t,at}], at} (`profClean_`).
- `insights_`: "Kemungkinan dobel" dilewati bila kedua transaksi satu Bill_ID & rekonsiliasi tagihan tidak DIFF, atau satu upload mutasi (Action_ID sama).
- Frontend: rentang `RG7` (`rgBar/rgOpen/rgGet`, 1 kalender), `home` baru (`flow7`, `bars7`), `tv` baru (tabel Debet/Kredit `txF7/txDir7/txOpen7`, status `TQ7.st`), `rkv` baru, Tagihan `bv` wrapper v7 + `billView7` (panel kanan & modal mobile; cache `BVC7`, PDF `STC7`, password sesi `PWB7/PWS7`), `viewProof` → popup `pop7`, `pwCK/pwDec` kunci stabil (fallback 'kk'), `ensureBills()` + `reload` tidak memotong data bila sudah dimuat semua, impor kolom `period` → `billsFromTx7(hints)`.
- Kelola Kartu: mode limit bersama `lgMode7` (tombol Hubungkan di kartu, garis `lgLines7`), `cardTidy7` (AI CARD + `cardLocal7` deteksi salah input, simpan via `cardFull7`), badge `nwB7` (logo jaringan saja, BCA Card = bca.co.id) & `tyB7` (ikon jenis kartu SVG).
- Rekening: saldo class `.rkb` (bukan `.bl`), panel `rcPanel7` (selisih, transaksi bernominal sama, mutasi terakhir, `rcOpen7` = jadikan saldo awal), `logoAuto7` (maks 5 nama/sesi, 1x/30 hari per nama, localStorage `kk_lg7`).
- Cicilan: `instGroups` dijumlah per lembar tagihan (`imFix7`, `g.lines`), gabung `Inst_Merge`, usulan `imSuggest7` (dismiss `kk_imdis`), validasi `imCheck7` (kartu/bank, lembar tagihan sama, penerima mirip / pokok+biaya).
- SnK: `snv` 2 panel (`snPanel7`, `SQ.sel`), Manual Prompt `snPrompt7`. Cari Promo: `pxAsk7` + `pxCtx7` (konteks ≤15k karakter), hasil `PX.ai`.
- Catatan Dev: widget melayang disembunyikan; tombol + & antrean kirim ulang di menu sidebar; `dnNew` selalu memperbarui halaman draf.

| ID | Isi | Status |
|---|---|---|
| DN-261030-143134-614 | Cari Promo: AI + Google + database, rekomendasi kartu | Selesai — 2026.11.07 |
| DN-261030-142959-775 | SnK gaya Konteks Memori + Manual Prompt | Selesai — 2026.11.07 |
| DN-261030-142723-566 | Cicilan multi-baris + Gabung Cicilan | Selesai — 2026.11.07 |
| DN-261030-122212-112 | Logo bank + 4 digit di bawah gambar kartu | Selesai — 2026.11.07 |
| DN-261030-122034-333 | Limit bersama inline + garis penghubung | Selesai — 2026.11.07 |
| DN-261030-142449-605 | Logo bank via Google Search | Selesai — 2026.11.07 |
| DN-261030-142359-717 | Dobel diabaikan bila tagihan cocok | Selesai — 2026.11.07 |
| DN-261030-141902-136 | Saldo rapi + rekonsiliasi saldo | Selesai — 2026.11.07 |
| DN-261030-141700-988 | Rekap Tagihan ringkas | Selesai — 2026.11.07 |
| DN-261030-141414-357 | Transaksi 1 tabel Debet/Kredit | Selesai — 2026.11.07 |
| DN-261030-141223-325 | Beranda baru + kapsul & 1 kalender | Selesai — 2026.11.07 |
| DN-261030-140850-774 | Catatan Dev di sidebar | Selesai — 2026.11.07 |
| DN-261030-140806-557 | Data impor tampil + tagihan dari impor | Selesai — 2026.11.07 |
| DN-261030-123245-910 | Tagihan boleh tidak dipilih | Selesai — 2026.11.07 |
| DN-261030-122756-619 | Password PDF tidak diminta berulang | Selesai — 2026.11.07 |
| DN-261030-122433-782 | Panel kanan: PDF lalu transaksi, view only | Selesai — 2026.11.07 |
| DN-261030-122248-429 | Bukti di popup | Selesai — 2026.11.07 |
| DN-261030-121925-263 | AI rapikan data kartu + logo jaringan/jenis | Selesai — 2026.11.07 |
| DN-261030-121317-130 | Kartu tagihan: gambar besar, Bayar di kanan | Selesai — 2026.11.07 |

### Ide berikutnya
- Purpose cicilan gabungan ikut menulis kolom Purpose transaksinya (sekarang tampilan saja).
- Rekonsiliasi rekening: tombol catat selisih sebagai koreksi (ADJUST) lewat rute khusus.
- Rekomendasi kartu otomatis saat mencatat transaksi manual (memakai profil kartu).

### Tambahan 2026.11.07 (30 Okt 2026, permintaan pemilik) — widget Catatan Dev kembali
- Widget melayang `#dnfab` ditampilkan lagi (tombol navy bulat, label "Catatan Dev" muncul saat hover, badge merah = antrean kirim ulang). Klik = catatan baru, **seret = pindah posisi** (diingat di localStorage `kk_dnpos`), Alt+N tetap jalan.
- Tidak pernah tertutup: z-index maksimum 2147483647 + MutationObserver selalu memindah widget ke elemen terakhir `body` (di atas modal `mo`, popup bukti `pv7`, penampil `zv`, konfirmasi `ask-ov`). Jendela catatan `.dn-ov` z 2147483646. Bisa diklik walau popup sedang terbuka.
- Pilihan "Sembunyikan widget" lama di-reset sekali (flag `kk_dnw1107`); tombol + di sidebar tetap ada.
| (30 Okt 2026) | Widget Catatan Dev selalu tampil di atas semua halaman & popup, bisa diseret | Selesai — 2026.11.07 |

## Rilis kartuku-sb 2026.11.08 (30 Okt 2026 sore) — 12 catatan selesai
- File berubah: `index.html`, `booq_edge_function_SATU_FILE.ts` (WAJIB deploy ulang — field & rute baru). SQL tidak perlu.
- Backend: Settings baru `Akun_Meta` {akun: {icon, mode SELF|REIMBURSE|TITIP, payer (nama klien), note}} dan `Harta_List` [{id, side ASSET|DEBT, code (kode SPT), name, year, cost, value, valueAt, info, owner, lender, address, accountId, inNet, spt, note}] lewat `api_saveLists` (`akunMeta`, `harta`); loans menyimpan `rate` (%/thn flat) & `intYear` (Rp/thn); rute `api_bulkReimburse` (ids, client → Is_Reimburse, Reimburse_Client, status Pending).
- Frontend blok "kartuku-sb 2026.11.08" (fungsi berakhiran 7): `rgDraw` (hover tidak menggambar ulang → tgl akhir bisa diklik), `rgBar` + baris info rentang `.rgi`, `bars7` (SVG berlabel sumbu/tooltip/ringkasan), `donut7`, tombol Kelola Kategori & Kelola Harta (`hartaM7/hartaF7`, kode `HK7`/`UK7`), `.cat7` (Catat hanya web; #fab hanya HP), `meter7` (pokok biru / bunga amber / terbayar hijau), `qvShow` dimatikan di .ci4 Cicilan, kotak bunga di `lnF` + `lnCalc7` (bunga flat: Y=P×r; M=(P+Y×N/12)/N; dari P,N,M → Y,r; `lnEff7` bunga efektif), `akH` + kartu penanggung (`akMode7/akPayer7/akIcon7/akBulk7`), `clH` menampilkan akun per klien, Rekening: `acv` baru (klik = popup `rkOpen7`, kanan = `rkSum7`), `rkAuto7` (Upload CSV/PDF → deteksi bank & no rekening → `rkUp`), `rkMatch` + AI `api_aiSuggest` & deteksi transfer antar rekening (nominal kembar ±2 hari).

| ID | Isi | Status |
|---|---|---|
| DN-261030-175914-625 | Meter cicilan: warna pokok vs bunga | Selesai — 2026.11.08 |
| DN-261030-175551-321 | Foto cicilan tidak membesar saat hover | Selesai — 2026.11.08 |
| DN-261030-175348-417 | Kotak bunga (% & Rp/thn) + rumus saling mengisi | Selesai — 2026.11.08 |
| DN-261030-154400-258 | Kelola Akun: ikon + penanggung terhubung Klien | Selesai — 2026.11.08 |
| DN-261030-153926-232 | Tombol Kelola Kategori di Beranda | Selesai — 2026.11.08 |
| DN-261030-153857-447 | Kelola Harta (kolom SPT) | Selesai — 2026.11.08 |
| DN-261030-153723-799 | Grafik Beranda berlabel + donat | Selesai — 2026.11.08 |
| DN-261030-152852-518 | Catat (web) vs + (HP) | Selesai — 2026.11.08 |
| DN-261030-152744-275 | Tanggal akhir kalender bisa diklik | Selesai — 2026.11.08 |
| DN-261030-152708-544 | Info rentang tanggal di bawah kapsul | Selesai — 2026.11.08 |
| DN-261030-153528-749 | Upload CSV rekening otomatis + AI | Selesai — 2026.11.08 |
| DN-261030-142212-557 | Rekening popup + ringkasan kanan | Selesai — 2026.11.08 |

### Menunggu dari pemilik
- File excel pelaporan harta SPT Tahunan → cocokkan kode & kolom `Harta_List`, lalu impor.

## Rilis kartuku-sb 2026.11.09 — gelombang 1 (31 Okt 2026) — 11 dari 30 catatan
- File berubah: `index.html`, `booq_edge_function_SATU_FILE.ts` (WAJIB deploy ulang). SQL tidak perlu.
- Frontend blok terakhir "kartuku-sb 2026.11.09" (CSS `css1109a`, fungsi berakhiran `9`). Edit langsung: `kpOpen` menerima `o.kinds` (mis. `['Pemasukan']`), `rkSave` mengirim `Items` v2 berisi bukti (`files`).
- Global: tema dikunci terang (`data-theme=light` + observer); `render` dibungkus `path9/fromPath9` (posisi scroll elemen dalam #v dipertahankan, kelas `#v.nf9` = tanpa animasi saat render di tab sama); ukuran font fluid `clamp()`.
- Transaksi: `RG7.t={p:'all'}`, `rgCalc('all')`, kapsul Semua.
- Beranda: `bars7` + garis akumulasi pengeluaran (skala kanan).
- Kategori: `KM9.k` (Pengeluaran/Pemasukan) di `catMgr`, `kmAdd`.
- Rekening/Mutasi: `csvMap` mendeteksi kolom DB/CR tanpa judul (`DIR9`), koreksi arah dari kolom Saldo; `rkLink9` (bayar tagihan dari nominal sisa/minimum), `tpMatch9` (titip bayar: subset ≤4 transaksi per Titip_Person, toleransi max(2.500, 1%), sebagian = `tpFull 0`) → `api_setTitip` Lunas setelah simpan; `rkProof9` (fUp ref MUTASI → OCR → `api_aiAssist`); `rkCat9` (pemilih kategori popup); `rkSnapMut9` (Bal_Snaps_Set, note `MUTASI <file>`, at = akhir hari mutasi WIB; snapInfo memakai snapshot dengan `at` terbaru); `rkAiRec9` → `api_ctxIngest` {accountId, usage} → Acc_Context `suggest`, `aiPurpose`, `aiAt`; `logoFix9` (unggah logo → `api_saveBankLogo`, domain → `bankDomains`; bankLogo: Bank_Logos → Bank_Domains → bawaan).
- Harta: `hartaM7` v9 per tahun pajak (`HM7.y`, posisi 31 Des), baris otomatis `hartaAuto9` (rekening 011/012/019, kartu 102 `ccAt9`, cicilan 101/109 & piutang 021 `lnAt9`), field baru `sold` (server `Harta_List`), unduh Excel `hartaX9`.
- Backend: `Harta_List.sold`; `api_ctxIngest` rekening menerima `usage`.

| ID | Isi | Status |
|---|---|---|
| DN-261031-025452-973 | Selalu tampilan terang | Selesai — 2026.11.09 |
| DN-261030-185204-318 | Kelola Harta & Utang gaya SPT per tahun pajak | Selesai — 2026.11.09 |
| DN-261030-184849-836 | Garis akumulasi pengeluaran | Selesai — 2026.11.09 |
| DN-261030-210058-177 | Kapsul Semua di Transaksi | Selesai — 2026.11.09 |
| DN-261031-005626-374 | Saldo dari mutasi + rekomendasi AI rekening | Selesai — 2026.11.09 |
| DN-261031-005250-633 | Debet/Kredit mutasi + hubungkan tagihan/cicilan/titip | Selesai — 2026.11.09 |
| DN-261031-005131-779 | Pemilih kategori popup di mutasi | Selesai — 2026.11.09 |
| DN-261031-004921-922 | Tidak kedip / tidak loncat ke atas | Selesai — 2026.11.09 |
| DN-261031-004833-445 | Bukti per baris + Smart Matching titip + kategori pemasukan | Selesai — 2026.11.09 |
| DN-261031-003900-798 | Ukuran isi mengikuti layar | Selesai — 2026.11.09 |
| DN-261030-194552-752 | Perbaiki logo bank | Selesai — 2026.11.09 |

## Rilis kartuku-sb 2026.11.09 — gelombang 2 (Tagihan) & 3 (Cicilan) — 19 catatan
- File berubah: `index.html` (blok kedua "gelombang 2 & 3", CSS `css1109b`), `booq_edge_function_SATU_FILE.ts` (WAJIB deploy). SQL tidak perlu.
- Backend baru: Settings `Card_Family` {cardId:{parent, rel TAMBAHAN|ONLINE}} (`cardFam_()` dipakai reconcile, refund, edit refund), `Date_Fmt` {bank:{dm,md}}, `Fee_Map` {NAMA:POKOK|BUNGA|ADMIN|DENDA|IURAN|LAIN} — semua lewat `api_saveLists` (`cardFam`, `dateFmt`, `feeMap`) & dikirim di pubSettings. Rute `api_fetchFile` {url} → {name,mime,base64} (PDF/gambar, deteksi magic bytes), `api_aiInstMerge` {groups} → {groups:[{ids,name,why,conf}]}. `doFetches_` kini menyimpan isi biner (getBlob benar untuk PDF/gambar).
- `reconcile_`: kandidat = kartu satu keluarga + memo tanpa kartu (Card_ID kosong → diisi kartu tagihan saat cocok); transaksi impor Excel (Import_Key tanpa Bill_ID / tagihan IMPORT) boleh beda tanggal ±toleransi. Refund `#baris.bagian` = bagian split. `api_importStatement`: tagihan IMPORT yang semua transaksinya pindah ke tagihan PDF dihapus, `Legacy_Paid` dibawa, `syncBill_`.
- Frontend: `upT` = popup (`UP9`, `upM9/upPick9/upRead9/upPrev9/upGo9`, `quickInfo9`), `R.pre` dipakai setelah `ekstrak`; paste link saat kursor di kotak bukti (`urlFile9`); filter tagihan `BQ.rg9` (m/pm/c, `RG7.b`); pengingat `remind9()` (kartu `.bl.gh9`); `bp` → kelas `bp9`; foto kartu IndexedDB `kk9/img` (`idbGet9/idbPut9`, `imgFill` baru); OCR `ocrPrep9` (patch Tesseract.recognize); pola tanggal `dtApply9`, `ue` wrapper (`R.dv9`); memo HP `pvM`/`mtB` (`mtB` kini `let`); `rfoCands` + bagian split & tagihan lama; keluarga kartu `famM9/famS9/cardFam9` (bar multi kartu & Kelola Kartu).
- Cicilan: `feeType9` (regex + Fee_Map), rekap `feeRecap9` (Tahun ini / Semua), `gFees9` per cicilan, riwayat per ke-n `knH9`, cek & rapikan `feeRev9/feeSave9` (kategori via api_saveTransaction), gabung lagi `MG:<id>` (imMergeAsk7 diperluas), `imCheck7` longgar untuk nama sama beda lembar, `imChoose9` → `imAi9` (AI + usulan lokal).

| ID | Isi | Status |
|---|---|---|
| DN-261030-210545-994 | Pengingat tagihan belum diupload | Selesai — 2026.11.09 |
| DN-261030-205818-871 | Tanpa scrollbar di Tagihan | Selesai — 2026.11.09 |
| DN-261030-205738-573 | Filter Bulan ini / Bulan lalu / Rentang | Selesai — 2026.11.09 |
| DN-261030-205549-451 | Konfirmasi Pembayaran lebih besar | Selesai — 2026.11.09 |
| DN-261030-203818-547 | Reversal dari tagihan sebelumnya | Selesai — 2026.11.09 |
| DN-261030-202123-398 | Upload lewat URL | Selesai — 2026.11.09 |
| DN-261030-201923-141 | Belajar pola tanggal per bank | Selesai — 2026.11.09 |
| DN-261030-200917-120 | Refund dari transaksi split | Selesai — 2026.11.09 |
| DN-261030-200433-895 | OCR gambar & kolom rincian | Selesai — 2026.11.09 |
| DN-261030-195942-223 | Panel edit ringkas | Selesai — 2026.11.09 |
| DN-261030-195653-592 | Kartu tambahan & online | Selesai — 2026.11.09 |
| DN-261030-195422-132 | Memo HP terhubung | Selesai — 2026.11.09 |
| DN-261030-195043-215 | Baris tagihan ringkas | Selesai — 2026.11.09 |
| DN-261030-194220-574 | Impor Excel + PDF tidak dobel | Selesai — 2026.11.09 |
| DN-261030-192842-493 | Upload Tagihan popup + konfirmasi | Selesai — 2026.11.09 |
| DN-261030-191538-295 | Cache foto kartu | Selesai — 2026.11.09 |
| DN-261031-010620-232 | Rekap biaya, gabung lagi, Gabung dengan AI | Selesai — 2026.11.09 |
| DN-261030-185733-876 | Riwayat per cicilan ke-n | Selesai — 2026.11.09 |
| DN-261030-185614-417 | Jenis biaya & rapikan kategori (dipelajari) | Selesai — 2026.11.09 |

### Ide berikutnya
- Excel pelaporan harta SPT dari pemilik → cocokkan kode `Harta_List`.
- Pola tanggal juga dikirim ke AI pembaca statement; jenis biaya baru otomatis jadi kategori bila belum ada.

## Rilis kartuku-sb 2026.11.10 (31 Okt 2026 siang) — 27 catatan
- File berubah: `index.html` (blok "2026.11.10", CSS `css1110`), `booq_edge_function_SATU_FILE.ts` (WAJIB deploy). SQL tidak perlu.
- Backend: prompt `aiExtract` — mutasi: merchant = keterangan LENGKAP; kartu kredit: peta BLOK nomor kartu → `cardLast4`. `itemsClean_` v2 + `qty` per baris, `time`, `pay`, `fees.disc`. Settings baru `Card_Alias` {bankKey:last4 → cardId} (`saveLists.cardAlias`), `Spt_History` {tahun:{totH,totU,inc,harta[],utang[],src,at}} (`saveLists.sptHist`). Rute baru `api_aiStmtHead` {text} (ringkasan header tagihan), `api_aiSpt` {files} (baca SPT tahunan).
- Frontend utama: `.aiv` = isian AI ungu miring (hilang saat disentuh; `.vx.st-ai` untuk baris tagihan); `ld9()` loader layar; `imgGet9` (cache IndexedDB + 1 request per file + retry, semua gambar tersimpan dimuat saat start); `mcApply` peta blok kartu dari `R.o.lines` (`MASK9`, `mcCard9` + alias, `mcLink9`); `quickInfo9` header kolom + `upRead9` → `api_aiStmtHead`; `aiH` status key (`kk_aitest9`); `rkAuto7` baru (1 rekomendasi + %); mutasi: `mutParse9`, `rkLearn9` (riwayat → kategori/akun/catatan), `rkProof10` (struk → OCR → `api_aiItems` → catatan/No. pesanan + cek dobel), kapsul `rkSetK9/rkSetP9`, pratinjau PDF `mpvBuild9/mpvHi9` (#mpv9 di panel ringkasan kiri), catatan dikosongkan saat upload; `rkPanel7` + rekening & kartu per bank (`bkOf9`); `rkF2` tombol Ganti logo; `mvCards` + rekening bank sama + tombol Hubungkan limit; `bars7` baru (`smooth9` monotone cubic, tooltip `cxMv9`, kartu `.cs9`); Kelola Harta tab `HIST` (`sptM9/sptUp9/sptEd9/sptCopy9`); `txOpen7` baru (foto kiri, rincian kanan); `tf9` (+Catat 2 kolom, `FM.tf9` keranjang/biaya/jam/metode, kurs `fx9` open.er-api.com, wajib No. pesanan & metode, cek dobel di `ts`, Items v2 disisipkan di `call('api_saveTransaction')`).
- CSS global: scrollbar panel tipis (scrollbar halaman tetap), `#v` lebar penuh, tombol `.ib7/.ib4` tanpa kotak, kapsul akun tidak bergeser, `.e4` kolom penuh, mutasi ringkasan kiri sticky.

| ID | Status |
|---|---|
| DN-261031-135045-507 · 132650-148 · 132414-902 · 131949-321 · 131747-591 · 131152-197 · 124917-115 · 124507-909 · 085644-984 · 085506-263 · 085410-918 | Selesai — 2026.11.10 (Tagihan) |
| DN-261031-130129-784 | Selesai — 2026.11.10 (Pengaturan AI) |
| DN-261031-125838-248 · 120133-827 · 115422-891 · 115204-136 · 114917-767 · 114754-387 · 114544-222 · 114426-976 · 084834-150 · 083000-406 | Selesai — 2026.11.10 (Rekening) |
| DN-261031-124304-442 · 123838-745 | Selesai — 2026.11.10 (Beranda) |
| DN-261031-090620-462 | Selesai — 2026.11.10 (Kelola Kartu) |
| DN-261031-082442-378 · 081736-337 | Selesai — 2026.11.10 (Transaksi) |

## Rilis kartuku-sb 2026.11.11 (31 Okt 2026 malam) — 13 catatan
- File berubah: `index.html` (blok terakhir "kartuku-sb 2026.11.11", CSS `css1111`, fungsi berakhiran `11`), `booq_edge_function_SATU_FILE.ts` (**WAJIB deploy ulang** — rute & kolom baru). SQL tidak perlu.
- Backend baru: kolom Transactions **`Raw`** (di ujung; JSON {raw, ref, loc, pd, c4, cu, pg, ex}) diisi `api_importStatement` dari `rows[i].Raw` untuk semua transaksi hasil cocok/tambah (`rawClean_`). Prompt `aiExtract` kini mengembalikan `raw` + `extra` per baris → frontend `r.rw`, `r.ex` (`exClean_`).
- Rute baru: `api_loanShare` {loanId, pin, on, regen} → Settings `Loan_Share` {loanId:{tok,pin,on,at}} + indeks global kv `p:LSHARE_<tok>` = `uid|loanId`; `api_shareLog` {loanId} → Settings `Share_Log` (maks 600: at, loan, ev OPEN/PIN_FAIL/LOCKED/PROOF, ip, ua, lang, cc, city/region/country/isp dari ipwho.is (cache 6 jam), vid, scr, tz, plat, ref, touch, conn, mem); **`api_loanPub` = rute PUBLIK** (tanpa sesi) {tok, pin, cli, pid?, full?, quiet?} — `handleKartuKu` memuat data pemilik dari indeks token, `REQ_META_` (IP/UA dari header, diisi server di `Deno.serve`). PIN salah 8× → kunci 15 menit (`lsf:<tok>`). `api_aiFeeType` {names} → {map: nama → POKOK/BUNGA/ADMIN/DENDA/IURAN/LAIN}.
- Settings baru: `Loan_Share`, `Share_Log`, `Fee_Names` (nama biaya yang dipelajari; `saveLists.feeNames`). pubSettings mengirim `Loan_Share`, `Fee_Names`.
- Items v2: field baru `fl:[{n,a}]` (biaya dinamis, a boleh minus) + `lines[].shop` disimpan server; `fees.ship/admin/other` tetap = jumlah `fl` (other menampung sisa & diskon) agar kode lama tetap benar. `api_aiItems` mengembalikan `fl` (nama dipetakan `Fee_Names`).
- `api_aiSpt` menerima `text` ≤120k + `name`, paham e-SPT 1770 lama (CSV/TXT/XML), 1770 Lampiran IV, 1770 S Lampiran II, Coretax; frontend `sptOne11` membaca CSV/TXT/XML/Excel/ZIP (XLSX.CFB)/PDF (teks + file)/foto; file tahun sama digabung.
- Frontend: halaman publik `?ci=<token>` (`pubInit11/pubR11/pubGo11/pubZ11`, kelas `html.pub11`, sessionStorage `kk_pin11_<tok>`, visitor id localStorage `kk_vid11`); pemilik `shOpen11(i)` (tombol Bagikan di kartu cicilan manual). Cicilan: `knH9` baru (kapsul `fp11` + `fpPick11` → Fee_Map, tebakan AI di localStorage `kk_feeai11` via `feeAI11`, perkiraan `est11`). `FEE9` diperluas (INT/INTR/BNG, PROV/MTR). Tabel: `tBind11` (localStorage `kk_colw11`), daftar verifikasi `lrBind11` (`kk_lr4w11`). Mutasi: `m11Bind` (var `--m11`, `kk_mut11`, `kk_mut11c` = dokumen disembunyikan), kapsul akun `akPop11`. Grafik: kurva lewat titik saat pengeluaran berubah + titik hover `hd11`. Multi kartu: `near11` (digit tertukar / beda 1) di `mcCard9`, `mcFix11`. Penampil Rincian: `itVH/itVLoad` baru (`.v11`, `.vt11`). Biaya: `fl11*`. Raw: `rawOf11/rawH11`.

| ID | Status |
|---|---|
| DN-261031-213148-682 · 211917-944 | Selesai — 2026.11.11 (Cicilan) |
| DN-261031-204954-829 · 203502-236 | Selesai — 2026.11.11 (Beranda) |
| DN-261031-204605-331 | Selesai — 2026.11.11 (Semua tabel) |
| DN-261031-203020-128 · 202837-124 | Selesai — 2026.11.11 (Rekening) |
| DN-261031-201740-941 · 201326-229 · 200700-402 · 200552-131 · 200253-308 · 200111-679 | Selesai — 2026.11.11 (Tagihan) |

### Menunggu dari pemilik
- Konfirmasi 4 digit kartu tambahan DBS Live Fresh: ••3652 (lembar tagihan) vs ••3562 (terdaftar).
- Contoh file SPT format e-SPT 1770 lama bila masih gagal terbaca.

### Ide berikutnya
- Halaman bagikan juga untuk cicilan kartu kredit; notifikasi ke pemilik saat link dibuka.
- Kolom Raw dipakai untuk smart matching refund / reversal (ID pembayaran sama).

## Rilis kartuku-sb 2026.11.12 (31 Okt 2026 malam) — 7 catatan
- File berubah: `index.html` (blok "kartuku-sb 2026.11.12", CSS `css1112`, fungsi berakhiran `12`), `booq_edge_function_SATU_FILE.ts` (**WAJIB deploy ulang**). SQL tidak perlu.
- Backend: `api_loanShare` menerima **password** bebas (huruf/angka, 4–40 karakter; field tetap bernama `pin`); `api_loanPub` membandingkan password (trim), mengirim `loan.img` (boolean) & `intYear`, dan `{img:1}` mengembalikan gambar cicilan (`Custom_Loans.img`). Prompt `aiExtract` mode rekening TIDAK lagi meminta `raw`/`extra` (lebih cepat); kartu kredit tetap.
- Mutasi PDF: `mutLocal12` (pembaca lokal: tanggal dd/mm[/yyyy] atau dd Mmm yyyy, angka 1,234.56 / 1.234,56, akhiran DB/CR, saldo berjalan, SALDO AWAL/AKHIR, MUTASI CR/DB) dipakai lewat pembungkus `call('api_aiExtract', mode ACCOUNT)`; hanya diterima bila hitungan saldo/total cocok, selain itu tetap AI. Saldo per baris diisi ke `RKX.rows[i].bal` (`LMUT12`, `rkClassify`), `RKX.src='PDF_LOCAL'`.
- Loader `ld9` + tombol **Batal** (`ldCancel12`, `LD12`): bila baris mutasi sudah ada → lewati penantian (RKX.done); selain itu panggilan server berikutnya dibatalkan (error "Dibatalkan").
- Ringkasan mutasi `.rkp` bisa dilipat (`rkpTog12`, localStorage `kk_rkp12`).
- Warna cicilan disepakati: **Pokok hijau #16a34a · Bunga kuning #eab308 · Admin biru muda #38bdf8** (FT9, meter `.mt7` — cicilan kartu memakai `est11`, kotak `.es11 .k12`, bar komposisi `.sb12`, kapsul `.fp11`). Rencana = warna pudar, Aktual = warna penuh, "tercatat/sudah dibayar" = navy.
- PDF lampiran: komponen `pdfT12(id,name)` + `pdfFill12()` (halaman 1 via `imgGet9` → pdf.js, cache `PDFT12`), dipakai di `tfPv9` (+ Catat) & `txOpen7` (detail transaksi).
- Halaman publik v2: `pubCss11/pubInit11/pubGo11/pubR11/pubZ11` diganti (putih, loader `#pl12` min 2 detik, gambar `#im12`, grafik `.mt .bar` transisi 2,6 dtk sama untuk semua batang, kartu rencana `.pi` L/S/T/B + `nx`, penampil bukti `#pz12` dengan tombol Tutup di bawah foto). Modal pemilik `shR11/shSave11/shCopy11` v2 (`.sh12`, input `#sh_pw12`).

| ID | Status |
|---|---|
| DN-261031-224004-576 · 223829-754 · 223518-899 | Selesai — 2026.11.12 (Rekening) |
| DN-261031-222838-493 · 222759-841 · 221447-570 | Selesai — 2026.11.12 (Cicilan) |
| DN-261031-220038-727 | Selesai — 2026.11.12 (Transaksi) |

## Rilis kartuku-sb 2026.11.13 (1 Nov 2026) — 15 dari 16 catatan
- File berubah: `index.html` (blok "kartuku-sb 2026.11.13", CSS `css1113`, fungsi berakhiran `13`), `booq_edge_function_SATU_FILE.ts` (**WAJIB deploy ulang**). SQL tidak perlu.
- Backend: mode AI global `APP_AI_MODE` = FREE | PAID | COMBO (`aiMode_`, `api_setAiConfig {mode}`, `api_aiConfig.mode`); `api_aiProof {text}` → data bukti transfer (`pocr_`: toAcc/toName/toBank/fromAcc/fromName/fromBank/amount/date/time/ref/msg/method/status/ex); Custom_Loans: `gk` (kunci grup cicilan kartu), status `LINK`, pays `src:'CARD'` + `ocr`; Settings **`Learn_Map`** {xfer, note, rcpt} via `saveLists.learn` (dikirim di pubSettings); `api_loanPub` mengirim `pays[].ocr`.
- Cicilan kartu = cicilan tertaut (`ciBuild13/ciEnsure13/ciAct13`): dibuat saat tombol pertama ditekan; plan & pays (`C<n>`) dibangun dari transaksi kartu; status `LINK` (tidak ikut hitungan ACTIVE → tidak dobel); kartunya disembunyikan dari daftar cicilan orang; sinkron otomatis bila dibagikan (`ciAutoSync13`); nama ikut Inst_Meta.
- Pola dipelajari (`lrnSet13`): `xfer` (kunci `xKey13`: A+no.rek / N+nama / C+kode) → rekening tujuan; `note` (kunci `mKey9`) → catatan mutasi; `rcpt` (kunci token struk `sigTok13`) → {m merchant, il label No. pesanan, tl label total} untuk baca struk tanpa AI (`tplFind13`, `tplLearn13`).
- Mutasi: catatan wajib terisi (`rkNoteFill13`: pola → riwayat → AI ROWS → nama keterangan); kosongkan rekening tujuan (`rkOther13`, disimpan sebagai OUT/IN + catatan); bukti klik → `rkPfOpen13` (detail + rincian `r.itm9`, ikut Items saat simpan).
- + Catat: `tfPv9` (foto utuh, `.has13` menyembunyikan dropzone, Potong `crop13`/`tfCrop13` → baca ulang), `tfCart9` dinamis (`FM.tf9.fl`, Items.fl), `tfAI13` (Rinci AI), CSS mobile tanpa geser kanan-kiri.
- Bukti pembayaran cicilan: `pfLocal13` (regex) → `pfParse13` (AI bila belum lengkap) → `LZ.ocr` → tersimpan di pay.ocr; panel `.po13`; halaman publik `#pz12 .dt13` di samping foto.
- Loader seragam: `.spin` & `svg.ic.spin` jadi cincin yang sama dengan `#ld9`.

| ID | Status |
|---|---|
| DN-261101-094327-776 · 225641-864 | Selesai — 2026.11.13 (Loader) |
| DN-261101-093134-330 · 093037-231 · 092611-325 · 091546-494 | Selesai — 2026.11.13 (Rekening) |
| DN-261101-090724-676 · 020040-706 · 015729-525 · 014752-785 | Selesai — 2026.11.13 (Cicilan) |
| DN-261101-090022-355 · 230020-348 · 225929-497 · 230400-626 | Selesai — 2026.11.13 (Transaksi) |
| DN-261101-020337-331 | Selesai — 2026.11.13 (Kelola › Pengaturan) |
| DN-261101-020634-711 | **Menunggu Excel rekap harta dari pemilik** (Beranda › Kelola Harta) |

## Rilis kartuku-sb 2026.11.14 (2 Nov 2026) — 39 dari 40 catatan
- File berubah: `index.html` (blok terakhir "kartuku-sb 2026.11.14", CSS `css1114`, fungsi berakhiran `14`), `booq_edge_function_SATU_FILE.ts` (**WAJIB deploy ulang**). SQL tidak perlu.
- Backend: `aiJson14_` (JSON AI toleran + perbaikan jawaban terpotong) dipakai di semua parse jawaban Gemini (part `thought` dibuang); `api_aiItems` maxOutputTokens 8192 + ulang 1x (forcePaid, 16k) bila JSON rusak, mengembalikan `dt:[{k,v}]` (Detil transaksi); `itemsClean_` menyimpan `dt`; `cleanTx_` menerima `Src_Unknown` (EXPENSE tanpa sumber → Source_Type CC, Card_ID kosong = memo untuk dicocokkan tagihan/CSV); `cardDays_` memasukkan tanggal SET ke `Day_Range` + `Due_Urgent` (paling awal) untuk estimasi jatuh tempo; `shopCtx_()` (riwayat belanja dari Items 400 hari + `Learn_Map.merch`) masuk `aiMemoryCtx_`; `PROOF_MIMES_` + xlsx/xls/csv/txt.
- Frontend: loader global `#ld14` (rute tulis/AI >450 ms, kecuali saat `#ld9` / popup upload); format tersimpan per platform `tplKey14` = `P:<PLATFORM>:<JENIS>` (Shopee dll.) → `tplFind14/tplLearn14` (label il/tl/sl/dl di `Learn_Map.rcpt`), dipakai untuk SEMUA `api_aiItems` (bypass AI; `FAI14=1` = paksa AI) dan otomatis belajar dari jawaban AI; `callBackend` dibungkus (Src_Unknown, `dt` tf9, bukti tambahan & merchant mutasi ke Items); `itemsOut` + `dt`.
- Tagihan: pengingat per kartu (`.cls14`); `cardProfile` tidak menanyakan tgl cetak/tempo & bank sama; popup upload: pratinjau di-cache (`pv14`, `UP9.pv14`), daftar "Belum diupload" (`remind9`), ringkasan file `.qs14`, nilai tebakan = ungu & hanya nilai yang diubah pengguna (`U.pdU14/ddU14/btU14`) mengunci hasil AI, `upGo9` baru dengan loader di popup (`upBusy14`, `UP14.on`); `akPanel4` grid + ikon (`akIc14`, `akShort14`), sub-akun nama sama → disimpan "Nama · Akun"; `vKids` foto split `.k14`; `thbH` tombol `thx14` → `thbDel14`; `vEdit` tombol `vAI14`; `ocrReclass` lokal dulu (`kGuess14`), AI di latar (`ocrReclassAI14`); penampil Rincian tombol Teks (`itTxt14`, `.ot14`); Detil transaksi `dt14*` (ns `it` / `tf`).
- OCR: `OCRP14` (OCR mulai bersamaan dengan `fUp`), worker Tesseract dipakai ulang (`tw14`, `tessPatch14`), `ocrPrep14` (deteksi kertas `docBox14` → potong, maks 2000 px, kontras), `crop13` → `crop14` dengan kotak awal terdeteksi.
- Transaksi: `fabSheet` = `tf()`, `rcRead` → form + `tfFiles9`; tombol "Isi dengan AI" (`tfAIfill14/tfApply14`); "Kosongkan semua" (`tfClr14`); No. pesanan di bawah Merchant; opsi sumber `CC:__` (default kosong), tanggal default kosong & wajib; tebak sumber dari nomor tersamar (`tfGuess14`); biaya hanya tampil bila ada (`flOn14`); file Excel/CSV/teks read-only (`xlsPv14`, `sheetTxt14`); kolom metode bayar di tabel diklik → `pmEdit14`.
- Rekening: catatan = textarea `.nta14` + prediktif `#ac14` (`nix14/acFind14/acDup14`), merchant dari catatan (`detMer14/rkMer14`, `Learn_Map.merch`), saran kartu `rec14/rkRec14H`, maks 5 bukti (`rkPfs14`, `r.pfs`), isi akun & kategori `rkKP14`.
- Cicilan: tombol aksi cicilan kartu ditambahkan bila `.acts` hilang (penyebab: penimpaan 2026.11.04 menghapus `.acts`); ikon mata tengah + kedip (`EYEOFF14`); bukti transfer: No. ref 2 baris, `accMatch14` (rekening tersensor ↔ tercatat), pola per bank `Learn_Map.pf` (`pfKey14/pfLearn14`), edit pensil `pfEd14/pfSave14`.
- Mobile: viewport `maximum-scale=1, user-scalable=no` + `touch-action:manipulation`.

| ID | Status |
|---|---|
| DN-261102-161515-310 · 161412-667 · 160735-938 · 160417-100 · 160258-224 · 155059-360 · 154222-820 · 154023-800 · 153911-118 · 153021-241 · 152928-395 · 152709-804 · 152635-422 · 152312-394 · DN-261101-161820-518 | Selesai — 2026.11.14 (Tagihan) |
| DN-261101-212634-966 · 193822-672 · 193647-330 · 193605-488 · 163518-376 · 163244-338 · 162717-672 · 162620-711 · 160552-319 · 160352-424 · 160230-478 · 160015-840 | Selesai — 2026.11.14 (Transaksi) |
| DN-261101-195552-972 · 164455-947 | Selesai — 2026.11.14 (Beranda) |
| DN-261101-174944-954 · 174040-609 · 173343-282 · 172628-326 · 172440-995 · 103314-545 · 102457-485 | Selesai — 2026.11.14 (Rekening) |
| DN-261101-170105-343 · 165405-533 · 165301-747 | Selesai — 2026.11.14 (Cicilan) |
| DN-261101-020634-711 | **Menunggu Excel rekap harta dari pemilik** |

### Ide berikutnya
- Saran kartu (`rec14`) juga di form + Catat saat kategori dipilih.
- Pola format per platform bisa dilihat / dihapus dari Kelola › Pintar.

## Rilis kartuku-sb 2026.11.15 — gelombang 1 (Tagihan) · 5 Nov 2026 — 10 dari 42 catatan
- File berubah: `index.html` (blok "kartuku-sb 2026.11.15 — gelombang 1", CSS `css1115a`, fungsi berakhiran `15`; plus 1 edit langsung di `bankKey` → memanggil `bankSyn15` dulu), `booq_edge_function_SATU_FILE.ts` (**WAJIB deploy ulang**). SQL tidak perlu.
- Backend: `thinkCfg15_` + `geminiTry_` — semua panggilan Gemini ber-`responseMimeType: application/json` memakai `thinkingConfig` (Gemini 3 / flash-latest: `thinkingLevel:'low'`; 2.5 flash: `thinkingBudget` 512, lite 0; Pro tidak diubah). Bila model menjawab 400 soal thinking → diulang tanpa & diingat 6 jam (cache `nt15:<model>`). Panggilan boleh menolak percepatan dengan `deep15: true`. `saveLists.learn` kini menerima 24 jenis pola (dulu 12). `BANK_WORDS_` + sinonim (bank central asia, bank rakyat indonesia, bank negara indonesia, wondr, nisp, united overseas).
- Learn_Map jenis baru: `nobill` {cardId|YYYY-MM: {at}} (tidak ada tagihan → `remind9` menyaring), `upc` {L:<4digit,..> / F:<nama file tanpa angka>: cardId}, `upd` {cardId: {sd, dd, n}} (hari tgl cetak & jatuh tempo hasil koreksi), `upn` {cardId: nama nasabah}.
- Frontend: `bankSyn15` (kamus `BSYN15`, `bnorm15`), `pwAsk15` (jendela password tengah, dipakai popup upload; `pdfUnlock15(f,label)` siap dipakai upload mutasi), `pwRem15`, `nbSet15/nbPick15`, `upSig15/upLearnApply15`, loader detik `.tm15`, bar AI gagal `.af15` + `aiRetry15`, rekonsiliasi `rcCard15` (menggantikan kartu rekonsiliasi di `billExtra`), OCR posisi `ocrBox15/itPos15` (cache `OBX15`, tombol Teks → teks di posisi; Daftar = `itTxt0_15`), pembayaran banyak bukti `FM.pay.more15` (`pm15Add/pm15Read/pm15R`, `prAI15` → `api_aiProof`), tiap bukti tambahan = `api_uploadProof` + `api_confirmPayment` sendiri setelah bukti 1 tercatat.

| ID | Status |
|---|---|
| DN-261105-160000-140 · 155831-497 · DN-261104-135232-716 · 135144-370 · DN-261103-201219-405 · 200953-434 · DN-261102-202401-732 · 201945-697 · 201723-987 · 201459-373 | Selesai — 2026.11.15 gelombang 1 (Tagihan) |
| DN-261101-020634-711 | **Menunggu Excel rekap harta dari pemilik** |
| 31 catatan lain (Transaksi, Beranda, Rekening, Cicilan, Rekap Tagihan) | Gelombang 2 & 3 |

## Rilis kartuku-sb 2026.11.15 — gelombang 2 (Transaksi + Beranda) · 5 Nov 2026 — 13 catatan
- File berubah: `index.html` (blok "gelombang 2", CSS `css1115b`), `booq_edge_function_SATU_FILE.ts` (**WAJIB deploy ulang**). SQL tidak perlu.
- Backend: Settings **`Reimb_Bills`** [{id, no, client, date, due, note, items:[{id,d,m,k,pp,a}], total, status OPEN|PAID|VOID, paidAt, paidRef, paidAcc, at}] lewat `saveLists.reimbBills` (maks 400, dikirim di pubSettings). `itemsClean_` files menyimpan **`crop` {x,y,w,h}** (potong tampilan, foto asli utuh). `api_aiItems` mengembalikan **`cur`** (ISO, kosong = IDR) & **`totalF`** (desimal). `fxCtx15_()` = ringkasan transaksi mata uang asing (Original_Currency / Raw.cu, 400 hari) masuk `aiMemoryCtx_`.
- Frontend: `bLogo15/srcLbl15/srcInfo15` (logo bank / inisial), Beranda sumber dana `.sd15`; perbaikan Items lokal setelah simpan (wrapper `call` paling luar); potong: `fUp` → `boxOf15` (auto `crop`), `CROP15`, `cropWrap15/cropAll15`, `cropRect15`, `tfCrop13` non-destruktif + `tfReread15` (`cropBlob15`); alat OCR seragam `ocrBtns15` (Teks `posOn15` · OCR `ocrShow` · Penuh `fView`) di `tfPv9`, `txOpen7`, `rkPfOpen13` (`td15`); ID wajib `genId15` (KK-YYMMDD-XXXX) untuk Pengeluaran & Pemasukan; cari metadata `hay15/hayHit15` (Items lines/dt/files, Raw, nominal tanpa pemisah); filter kartu keluarga di `txF7`; centang `TX15` + `sb15R`; pemilih sumber dana `spBuild15/spOpen15/spGuess15` (select asli disembunyikan, default `CC:__` / kosong untuk Pemasukan); mata uang `fxDet15/fxApply15`; reimburse `rbOpen15/rbL15/rbSave15/rbHtml15/rbPrint15/rbText15/rbView15/rbList15/rbMark15/rbVoid15`, cocok mutasi `rbMatch15` (r.rb15, kind RB) → setelah `rkSave` `api_setReimburse` Cair + status PAID.

| ID | Status |
|---|---|
| DN-261104-135923-758 · 135645-620 · 135515-616 · 135325-325 · DN-261103-205728-502 · 161935-871 · DN-261102-225840-103 · 225801-691 · 225134-450 · 210354-873 · 210222-350 | Selesai — 2026.11.15 gelombang 2 (Transaksi) |
| DN-261104-112528-491 · DN-261103-112142-503 | Selesai — 2026.11.15 gelombang 2 (Beranda) |
| DN-261101-020634-711 | **Menunggu Excel rekap harta dari pemilik** |
| 18 catatan Rekening, Cicilan, Rekap Tagihan | Gelombang 3 |

## Rilis kartuku-sb 2026.11.15 — gelombang 3 (Rekening + Cicilan + Rekap Tagihan) · 5 Nov 2026 — 18 catatan
- File berubah: `index.html` (blok "gelombang 3", CSS `css1115c`). Backend sama dengan gelombang 2 (tidak ada perubahan tambahan). SQL tidak perlu.
- Rekening: `MX15` {text, open, close} dari teks mutasi (regex Saldo Awal/Akhir, Opening/Closing Balance) + `summaryRows` AI (PREV_BALANCE/CLOSING); `mutOC15` (saldo awal/akhir: dokumen → kolom saldo → snapshot sebelumnya), `rkSnap15` (saldo akhir dokumen → baris terakhir → `rkSnapMut9`), panel `fw15H` (cek alur uang) di `.pane-t` mutasi; `payMatch15` (CC_PAYMENT ber-Bill_ID tanpa Import_Key, nominal sama, ±4 hari → r.pay15, kind PAY, dilewati saat `rkSave`), kapsul `pkH15`; komentar saran kartu `rcFb15/rcFbS15` → `api_saveAiMemory` (ATURAN) + Learn_Map **`recfb`** {cardId|m:merchant / k:kategori: {no,t,at}} → `rec14` tidak menyarankan kartu itu; laporan konsolidasi `consol15` (nomor rekening ≥8 digit di teks → potongan teks per rekening) + antrean `RKQ15` (`rkQNext15/rkQSkip15/rkQStop15`, teks potongan menggantikan `p[0].text` api_aiExtract ACCOUNT); `pdfUnlock15` di `rkAuto7`/`rkUp`; seret-lepas file (`html.rkd15`, banyak file berurutan); daftar rekening per bank `.bg15`.
- Cicilan: `pfEd14` baru (grup TUJUAN `.pg15.to` / ASAL `.pg15.fr` / Transaksi, `#pf15a` rekening milikmu `fromGuess15`, datalist metode `PM15D` + Learn_Map **`pm`**, **`pfacc`** {'*': accId}); `pfParse13` menebak rekening asal (`fromG15`); `fpPick11` = jendela pilih (`FP15`, `fpSave15`) + klik capture; `instGroups` wrapper: Learn_Map **`cihide`** {gKey} disembunyikan + lunas bila tidak ada di tagihan terbaru kartu (`lg15`); `ciHide15/ciUnhide15/ciUn15`, `lnDel15` (hapus cicilan manual); `meter15` (Aktual = max(tercatat, perkiraan × ke-N/tenor)); gabung: kartu `.ci4.pk15` diklik (tanpa `.imck`), tombol `.gb15` per kartu (`imGb15`), toolbar global hanya saat mode gabung (+ Gabung dengan AI).
- Rekap Tagihan: `rkv` wrapper → `akSec15` (Akun › Sub-akun, centang `RKA15`, total pilihan, `rbAk15` → `rbOpen15`) & `catSec15` (semua kategori, batang min 3px).

| ID | Status |
|---|---|
| DN-261103-205119-674 · 205008-346 · 204652-541 · 204436-767 · 204033-224 · 203924-357 · 203712-278 · 202336-974 | Selesai — 2026.11.15 gelombang 3 (Rekening) |
| DN-261103-162726-211 · 162648-608 · 162612-434 · DN-261102-205549-103 · 205432-749 · 204617-979 · 204337-466 · 204112-135 | Selesai — 2026.11.15 gelombang 3 (Cicilan) |
| DN-261102-203901-865 · 203722-256 | Selesai — 2026.11.15 gelombang 3 (Rekap Tagihan) |
| DN-261101-020634-711 | **Menunggu Excel rekap harta dari pemilik** |

### Ide berikutnya
- Tombol batal "Tidak ada tagihan" (Learn_Map.nobill) di Kelola › Pintar.
- Saring tabel Rekap Tagihan per akun yang dicentang.
- Laporan konsolidasi: deteksi juga rekening yang belum terdaftar → tawarkan + Rekening.


## Rilis kartuku-sb 2026.11.16 (7 Nov 2026) — 17 catatan + desain ulang tampilan web
- File berubah: `index.html` (blok terakhir "kartuku-sb 2026.11.16", CSS `css1116`, fungsi berakhiran `16`; plus 2 edit langsung: `APP_VERSION`, dan perbaikan crash di `tf9`), `booq_edge_function_SATU_FILE.ts` (**WAJIB deploy ulang**). SQL tidak perlu.
- **Temuan akar masalah:**
  - `pdfjsLib.getDocument` read-only → pembungkus "coba password tersimpan" sejak 2026.11.04 tidak pernah aktif. Sekarang `window.pdfjsLib` dibungkus Proxy (`__p16`).
  - `tf9` crash (`insertBefore`) bila `#f_lb` sudah dipindah ke "Detail lainnya" → sisa tf9 (dropdown mata uang, keranjang, pratinjau) tidak jalan. Diperbaiki langsung di baris tf9.
  - Notifikasi `task_followup` dulu tampil sebagai "Reimburse belum cair".
- **Desain:** font default Inter (opsz) kecuali pengguna pernah memilih font (`f1106`); token `--fg/--ink2/--mu/--bd/--sunk/--ac`, sudut 8/12/16, angka tabular; tabel `.tt7`, tombol, input (kecuali `.ti`), popup, sidebar dirapikan.
- **Bank:** `BANK16` (±90 bank + kata kunci) menambah `BANK_DOM/BANK_CLR/BANKS/BSYN15`; `bankGuess16` (awalan unik), `bankAll16`, `bankNorm16` (nama di data diseragamkan saat render); `bLogo15` baru = logo dalam bingkai seragam, cadangan inisial warna merek. `kcbOpen/kcbIcon` baru (bank, jaringan, jenis, tier) + ikon di input `adorn16/adU16` (`NW16`, `trIc16`, `TY7`).
- **Pemilih berlogo `pk16`:** dipakai `spOpen15` (sumber dana) & filter metode bayar (`pfBuild16/pfOpen16`), dikelompokkan per bank (`srcItem16/pkSort16`).
- **Transaksi:** `TX16.rec` (transaksi baru disorot `.nw16`, bar `.nb16` + `txShow16` bila di luar filter; `mutate` & `ensureAll` dibungkus agar tidak hilang); ikon bukti `txPh16` + penampil gelap `lb16/lbR16/lbGo16/lbX16`; `pmFix16` & `srcChip16` (logo metode bayar); valas `fxAt16` (Frankfurter/ECB per tanggal → currency-api → `fx9`), `tfCur9/sc` baru (tidak mengosongkan nominal), `cuBuild16`, deteksi "USD 12" / "$12" di nominal, catatan sumber kurs `#f_xs16`, kurs masuk Detil transaksi.
- **Foto:** `cropWrap15` baru → `.cv16` (`cvLay16` hitungan piksel, selalu di tengah, Lihat utuh + penanda `.mk16`, zoom `.zg16`), tombol Penuh / klik foto = `cvBig16` (memenuhi popup yang sama, `.bigw16`, Esc = kecil), `boxOf15` lebih ketat (`cOk16`).
- **Tagihan:** `rfoCands` menyaring pembelian yang sudah tertaut refund/reversal; `afMark16/afBadge16` (iuran tahunan → jenis Iuran Tahunan + label); follow up `fwOpen16/fwSet16` (Note task: `BARU|`, `DIAJUKAN|`, `DIHAPUS|`, `DITOLAK|` + tanggal) lewat `api_updateTask`.
- **Rekening:** `PWF16` (password per berkas), `pdfUnlock15` & `readDoc` baru; `call('api_aiExtract')` mengubah PDF terenkripsi → gambar per halaman (`pdfImgs16`, maks 12); laporan gabungan `consol15` baru (`ACCL16`, `MX16`, `mx16R`, `mx16Go` → buat rekening baru → antrean `RKQ15`).
- **Kelola › Kartu:** `mvCards` membungkus kartu limit bersama dalam `.lg16` (limit sekali, terpakai & sisa); logo jaringan vektor di `.nw7`.
- **Backend:** `api_aiExtract` menerima `files[]` (gambar, maks 14); `AF_RE16_/AF_RV16_`, `feeScan16_` di `api_importStatement` (tandai Is_Annual_Fee + tugas; pembatalan menutup tugas), `ensureFeeTask_` jatuh tempo H+1 dengan Note `BARU|tgl`; `cleanTx_` deteksi iuran dari nama; notifikasi task mengirim `kind, note, refTx`.

| ID | Status |
|---|---|
| DN-261106-232455-586 · DN-261105-221604-732 · 221235-753 · 220937-125 · 220744-241 · 220045-622 · 180328-442 | Selesai — 2026.11.16 (Transaksi) |
| DN-261106-174355-727 · DN-261105-181153-171 | Selesai — 2026.11.16 (Tagihan) |
| DN-261105-222048-993 · 221927-161 | Selesai — 2026.11.16 (Rekening) |
| DN-261105-220629-409 · 220400-365 · 220349-989 · 220341-571 · 220320-397 | Selesai — 2026.11.16 (Kelola › Kartu) |
| DN-261107-123843-164 | Selesai sebagian — penampil & potong diperbaiki; **menunggu foto contoh dari pemilik** |
| DN-261101-020634-711 | **Menunggu Excel rekap harta dari pemilik** |

### Catatan uji
- Diuji di Chromium dengan data tiruan: Beranda, Transaksi (filter, ikon foto, penampil gelap, detail, Penuh, + Catat USD), Kelola › Kartu (limit bersama, ikon input), PDF berpassword + laporan gabungan 2 rekening, filter refund, penandaan iuran. Semua halaman tanpa error JavaScript.
- Kurs per tanggal memakai API publik (Frankfurter/ECB harian) — jam transaksi dicatat, kurs per jam tidak tersedia gratis.


## Rilis kartuku-sb 2026.11.17 (11 Nov 2026) — 5 dari 6 catatan
- File berubah: `index.html` (blok terakhir "kartuku-sb 2026.11.17", CSS `css1117`, fungsi berakhiran `17`; edit langsung: `APP_VERSION`, form catat transaksi (toggle cicilan → input tersembunyi `f_ib/f_ic/f_it`), ikon `kIc17` di `txRow`, `txC`, tabel `tv`), `booq_edge_function_SATU_FILE.ts` (**WAJIB deploy ulang**: `txSeq_` menambah `_seq` = urutan input di `api_bootstrap` & `queryTx_`, tidak disimpan ke tabel). SQL tidak perlu.
- **Popup (`dg` baru):** hanya tertutup dengan menarik `.gh` ≥30% tinggi popup (140–220px), garis merah = lepas untuk menutup; tidak ada tutup lewat geser isi / sentakan. Ketuk latar (`#m > .ov`, capture): HP tidak menutup; desktop menutup hanya bila pointerdown juga di latar & belum ada isian berubah (`data-dirty17`), selain itu `nudge17` (goyang + toast).
- **Kemarin:** `rgCalc('yd')`, tombol disisipkan setelah "Hari ini" di `rgBar` (Beranda & Transaksi).
- **Urutan dalam 1 tanggal (`daySort17` membungkus `txF7`):** jam transaksi dari `Items.time` bila ada; tanpa jam mewarisi jam input sebelumnya, lalu urutan input `_seq` (terbaru di atas). Transaksi baru tanpa `_seq` = paling akhir (`SEQ17/SQA17`). "Terlama" membalik; "Nominal terbesar" tidak diubah.
- Ikon jenis: Bayar tagihan = `card`, Transfer = `move`, Tarik tunai = `wallet`, Koreksi saldo = `scale`.

| ID | Status |
|---|---|
| DN-261109-201329-903 | Selesai — 2026.11.17 (Beranda › Catat transaksi) |
| DN-261108-163110-807 | Selesai — 2026.11.17 (Semua popup) |
| DN-261109-170206-274 | Selesai — 2026.11.17 (Transaksi) |
| DN-261109-165725-842 | Selesai — 2026.11.17 (Transaksi & Beranda) |
| DN-261107-201424-119 | Selesai — 2026.11.17 (Transaksi; perlu deploy Edge Function) |
| DN-261101-020634-711 | **Masih menunggu Excel rekap harta dari pemilik** |

### Catatan uji
- Chromium (desktop 1400px & HP 390px, data tiruan): kapsul Kemarin di Beranda & Transaksi, urutan hari yang sama (Terbaru/Terlama), ikon kategori/jenis, form tanpa toggle cicilan, popup: tarik 60px tidak menutup, 260px menutup, ketuk latar HP tidak menutup, desktop: latar menutup bila bersih & tidak menutup bila ada isian. Tanpa error JavaScript.



## Branding booq.id (sejak kartuku-sb 2026.11.18) — WAJIB diikuti untuk tampilan baru
- Nama & wordmark: **booq.id** (titik oranye), sub-judul "KartuKu · dompet pribadi". Tagline: "Teman keuangan pribadimu".
- Warna & peran: Deep Teal `#064E50` = struktur (sidebar, tombol utama, judul) · Mint Teal `#159B91` = aksen, fokus, centang · Orange `#FF922E` = "perlu kamu klik / isi" (tombol Catat, kotak wajib belum diisi, garis aktif sidebar) · Soft Gold `#FFD16B` = poin/miles, bunga · Cream `#F5F0E8` = latar (halaman `#F7F3EC`, kartu putih). Isian AI tetap **ungu miring**; isian hasil belajar dari koreksi = **garis hijau di kiri kotak** (`.lrn18`).
- Token CSS: `--pr --ac --or --or2 --gd --cr --bg --bd --mu`, sudut `--r1` 10 / `--r2` 16 / `--r3` 22. Font `--ff` (pilihan font manual pengguna tetap dihormati).
- Maskot **BOO** (dompet hijau 3D): data `BOO18` di index.html (WebP kecil tertanam), fungsi `boo18(nama, ukuran, kelas)`. Nama ekspresi: logo, happy, thinking, worried, relaxed, idea, celebrate, analyzing, uploading, success, error, money, goodjob, sad, cool, wink, offline, loading, stressed, hero, waiting, thanks, great, surprised, icon. File asli PNG transparan (29 ekspresi + loader + ikon aplikasi) ada di paket `assets/boo/` (`web/` = WebP 256px).
- Tempat BOO muncul: logo sidebar/header, layar masuk (`hero`), loader layar `#ld9/#ld14` (BOO melayang + gelembung, `ldPick18` memilih ekspresi dari pesan), loading halaman, keadaan kosong (`empty18`), toast (wajah senang/khawatir), sapaan Beranda `.gr18` (ekspresi mengikuti pengeluaran bulan ini vs bulan lalu tanggal sama; bisa ditutup per sesi).
- Prinsip: maskot = satu-satunya elemen "ramai"; sisanya tenang. Gerak hanya untuk loader. Hormati `prefers-reduced-motion`.
- Warna navy lama di stylesheet & atribut SVG diganti otomatis (`navy18`, pengganti teks style saat dimuat).

## Rilis kartuku-sb 2026.11.18 (13 Nov 2026) — branding + 13 dari 14 catatan
- File berubah: `index.html` (blok terakhir "kartuku-sb 2026.11.18", CSS `css1118`, `css1118b`, `css1118c`, fungsi berakhiran `18`; edit langsung: `APP_VERSION`), `booq_edge_function_SATU_FILE.ts` (**WAJIB deploy ulang** — kolom cicilan baru & Learn_Map 40 jenis). SQL tidak perlu.
- Backend: Custom_Loans + `method` (CICILAN|KRK), `itype` (FLAT|ANUITAS), `limit`, `intOn`, `krate` (%/thn KRK, terpisah dari `rate` flat), `draws` [{id,date,amount,kind D|B|A,note}] (= DEBET), `evts` [{id,date,type TENOR|RESTRUK,tenor,monthly,rate,itype,principal,note}]. `saveLists.learn` menerima 40 jenis pola.
- Learn_Map baru: **`ocr18`** {tanda format struk `sigTok13` → {m merchant final, a merchant versi AI, k kategori, s sumber dana, p metode bayar, pp akun, n, at}} · **`pay18`** {merchant ternormalisasi `pmKey18` → metode bayar}.
- Transaksi › + Catat: metode bayar berikon `pmDraw18` (kotak oranye bila kosong, tebakan `pmGuess18`: pola → e-commerce → QRIS → EDC → transfer → tunai; `F.payU18` = dipilih manual); Reimburse ke 5 pilihan `AK18` (`rb18/rbSet18`, sub-akun opsional, nilai di `#f_pp` = kolom Purpose; Roastery/Affiliate/Lainnya dibuat otomatis bila belum ada — `akEnsure18`, hanya setelah data termuat); "Rapikan akun" `akTidy18` (akun lama → sub-akun); isian reimburse klien lama disembunyikan di form; sumber dana `spLbl15` baru (••4 digit `.l418` selalu terlihat) + tebak dari 4 digit `l4Cands18/srcFromL418`; anti-dobel tempel `tfFiles9` (ukuran 4 dtk + SHA-256); cek dobel `dupFind18` di `ts`; belajar koreksi `ocrLearnSave18` (saat simpan) / `ocrLearnApply18` (setelah baca).
- Transaksi › filter: kapsul per bank `.bk18` (token `Q.s18`: `B:<bank>` / `S:<sumber>`; `txMatch18`), popover `#bk18p` (hover desktop, panah HP), banyak pilihan; `Q.s` lama otomatis dikonversi. Filter keluarga kartu lama (`cardFam9`) tidak dipakai lagi saat kapsul aktif.
- Esc global (`ESC18`): popup kecil yang punya Esc sendiri dibiarkan; `#m2` → `cm2()`, `#m` → `cm()` dengan konfirmasi bila `data-dirty17`.
- HP: `#v` tidak bisa digeser ke kanan; `.rg7 .cp`, `.kc7`, `.bk18` jadi baris gulir sejajar tepi; nominal tabel tidak patah; filter 2 kolom.
- Cicilan: pilihan metode di form (`lnF18`, `LN18`), KRK = buku besar `krk18()` (bunga harian saldo × %/365, dibukukan akhir bulan, bulan berjalan = bunga berjalan), kartu KRK (sisa hutang · bunga berjalan · sisa plafon), tombol Pinjam `krkDraw18`, Buku besar `krkLedger18` (+ unduh Excel `krkXls18`), bayar = `lnPay` (kredit). Cicilan tetap: Flat / Anuitas (`annuity18`, `lnAn18`), tombol **Tenor / restruktur** `lnRs18` (rencana sebelum tanggal berlaku tidak diubah; sisa dibagi ulang; riwayat di `evts`, tampil `.ev18`).

| ID | Status |
|---|---|
| DN-261113-114606-288 · 114536-450 | Selesai — 2026.11.18 (Cicilan; perlu deploy Edge Function) |
| DN-261113-113740-873 · 113436-755 · 112507-728 · 112258-517 · 112111-180 · 112046-234 · 111000-641 | Selesai — 2026.11.18 (Transaksi › + Catat) |
| DN-261112-215625-322 · 115003-457 · 100537-811 | Selesai — 2026.11.18 (Transaksi) |
| DN-261112-100335-938 | Selesai — 2026.11.18 (Semua popup) |
| DN-261101-020634-711 | **Masih menunggu Excel rekap harta dari pemilik** (Beranda › Kelola Harta) |

### Catatan uji
- Chromium (desktop 1400px & HP 390px, data tiruan): Beranda (sapaan BOO), Transaksi (kapsul bank: 1 kartu DBS → hanya kartu itu, + UOB → 2 sumber), + Catat (metode ditebak Online untuk Shopee, EDC dari struk ber-APPR CODE, sumber UOB ••7301 dari "VISA XXXX XXXX XXXX 7301", koreksi struk dipelajari & diterapkan ulang, tempel 3× file sama = 1 unggahan, cek dobel), Esc (bersih = tutup, ada isian = konfirmasi), Cicilan KRK (bunga Jul–Okt dihitung & dibukukan, sisa plafon), Tambah tenor 6 bulan (2 lunas + 16× = total tetap). Lebar halaman HP = 390px. Tanpa error JavaScript.

### Ide berikutnya
- Halaman bagikan cicilan (publik) juga menampilkan buku besar KRK.
- Pengingat bunga KRK akhir bulan di Beranda; bandingkan bunga KRK vs promo cicilan 0% kartu kredit (Konsultan Kartu Kredit).
- Daftar pola yang dipelajari (`ocr18`, `pay18`) bisa dilihat / dihapus di Kelola › Pintar.


## Rilis kartuku-sb 2026.11.19 (13 Nov 2026 siang) — 11 dari 12 catatan
- File berubah: `index.html` (blok terakhir "kartuku-sb 2026.11.19", CSS `css1119`, `css1119b`, fungsi berakhiran `19`; edit langsung: `APP_VERSION`, `<head>` (manifest, apple-touch-icon, theme-color), penjaga posisi gulir di pembungkus `render` 2026.11.09 (pakai `window.SCR19`), pengamat warna navy 2026.11.18 (hanya elemen baru), JS 2026.11.18 tidak lagi menimpa apple-touch-icon), `booq_edge_function_SATU_FILE.ts` (**WAJIB deploy ulang**). File BARU di repo GitHub Pages: `manifest.webmanifest`, `icons/` (icon-192, icon-512, icon-maskable-512, apple-touch-icon 180, favicon-64). SQL tidak perlu.
- Backend: key **riset** `APP_GEMINI_API_KEY_RESEARCH` / secret `GEMINI_API_KEY_RESEARCH` (`api_setAiConfig {researchKey|removeResearch}`, `api_aiConfig.hasResearch/maskedResearch`). `geminiFree19_` = key riset → key gratis, **tidak pernah key berbayar** (semua pekerjaan otomatis). `groundFree19_` = + Google Search. Rute baru: `api_cardAuto19 {cardId?, force}` (1 kartu paling lama `autoAt` ≥14 hari → {cardId, found:{benefits,bestFor,avoid,promoX,rules,fees}, sources}; frontend menggabung & menyimpan lewat api_saveCardContext), `api_promoScrape19 {site, max}` (RSS `/feed/` → beranda; artikel belum dibaca (Settings `Promo_Seen`) → AI gratis → items + cards + seenAdd), `api_promoAsk19 {q, ctx, ground}`, `api_ruleAi19 {text, card}`, `api_promoDb19` (Promo_DB, Card_DB, seen, sites). `saveLists` baru: `promoDb` (≤500), `cardDb` (≤200), `promoSeen` (≤2000), `promoSites` (≤12). Settings baru: `Promo_DB`, `Card_DB`, `Promo_Seen`, `Promo_Sites` (tidak dikirim di bootstrap).
- Card_Context baru: `promoX` [{t, cat, merchant, from, to, minTx, benefit, cap, src OFFICIAL|EMAIL|BLOG|CREATOR|USER|AUTO, url, at}], `autoAt`, `autoSrc`; rules + `period` MONTH|STMT|RANGE, `start`, `months`, `days` [0–6], `kw`, `fromNth`, `pct`, `cap`, `src` AUTO|AI|MANUAL. `api_ctxIngest` menerima `texts[]` (banyak email, total ≤45k) & `ground` (Ringkasan AI Google → `overview {text, sources}`), mengembalikan `promoX`.
- Frontend: `snkProg` baru (periode `rPer19`, transaksi `rTx19`: keluarga kartu utama/tambahan, hari, kata kunci, min/trx; perkiraan cashback `est`), info syarat `.rx19`, form syarat + "Tulis syarat bebas → AI" (`snRai19`, `SR19`), `snRS` baru; pengingat `goals19/goalsH19` (banner `.gl19` di Tagihan & Beranda), notifikasi browser `notify19` (localStorage `kk_nt19`). SnK: bilah cari/tanya `.sq19` (`SN19`), tab "Kartu saya" / "Temukan & rekomendasi" (`findH19`, indeks `idx19`, sinonim `SYN19`, skor `score19`, kartu terbaik lokal `best19`, rekomendasi `recoH19`, otomasi `autoH19`), Tanya AI `snAsk19`; `PDB19` + `pdbLoad19/cardAuto19/scrape19/site19`; otomatis sekali sehari 30 dtk setelah buka (localStorage `kk_auto19` = tanggal, `kk_auto19off` = matikan). Panel kartu: promo terklasifikasi `.px19` + "Cari sekarang".
- Konteks kartu (ctxM): `CX19.texts` (+ Teks / email lain, .txt/.eml `cxTF19`), centang Ringkasan AI Google `#cx_g19`, pratinjau file `cxFl` baru (gambar kecil, PDF hal. 1) + pratinjau besar otomatis saat file ditambahkan `qv19`; `cxIngest` baru (promoX digabung, overview ditampilkan `.ov19`).
- Lain: kapsul bank `bkSet18/bkPop18` baru (instan, gambar kartu `.ci19`, sorot), `dnPlace7` hanya dihitung bila layar/posisi berubah, `dnFab` per bingkai; sidebar `brand19` (logo 40px tetap, tulisan BOOQ.ID `WM19`), ikon menu tetap posisinya; Tagihan `itQuick` → baca AI + `ocrReclassAI14` otomatis.

| ID | Status |
|---|---|
| DN-261113-133623-897 · 133553-947 | Selesai — 2026.11.19 (Transaksi) |
| DN-261113-133328-639 | Selesai — 2026.11.19 (HP: Tambahkan ke layar utama; unggah manifest + icons/) |
| DN-261113-133152-605 · 131453-778 | Selesai — 2026.11.19 (SnK & Benefit; perlu deploy Edge Function) |
| DN-261113-132820-275 · 131740-594 · 131537-849 | Selesai — 2026.11.19 (Kelola › Kartu › Konteks) |
| DN-261113-130410-712 · 125236-928 | Selesai — 2026.11.19 (Tagihan; syarat juga di SnK & Beranda) |
| DN-261113-123202-383 | Selesai — 2026.11.19 (Sidebar) |
| DN-261101-020634-711 | **Masih menunggu Excel rekap harta dari pemilik** |

### Catatan uji
- Chromium + data tiruan 2.100 transaksi: klik kapsul bank 450 ms → instan (render penuh 450 → 270 ms). Sidebar ciut: logo 40×40. SnK: cari "kartu terbaik bayar PLN" (sorot kata, promo PLN BCA), Tanya AI, rekomendasi, form syarat + AI. Pengingat di Tagihan & Beranda. Konteks: pratinjau PNG, teks email → promoX tersimpan. Tanpa error JavaScript.
- Belum bisa diuji langsung: isi feed pinterpoin.com (jaringan uji tidak membuka situs itu) — bila RSS tidak ada, otomatis membaca beranda.

### Ide berikutnya
- Rekomendasi kartu saat + Catat (kategori/merchant → kartu dengan promo aktif).
- Halaman kelola database promo (sembunyikan / tandai sudah dipakai).


## Rilis kartuku-sb 2026.11.20 (13 Nov 2026) — Rekap Harta (DN-261101-020634-711)
- File berubah: `index.html` (blok "kartuku-sb 2026.11.20", CSS `css1120`, fungsi berakhiran `20`; edit langsung `APP_VERSION`), `booq_edge_function_SATU_FILE.ts` (**WAJIB deploy ulang** — `saveLists.rekapHarta`, pubSettings `Rekap_Harta`). manifest & icons tidak berubah. SQL tidak perlu.
- Kerangka pemilik: harta bersih SPT tahun lalu (Spt_History[Y−1]; bila belum ada → rekap KartuKu 31-Des Y−1) + penghasilan setahun − PPh dibayar − biaya hidup pribadi ± lain-lain = harta bersih WAJAR → dibanding harta bersih **Laporan SPT** (harga perolehan, `spt!==false`) & **Rekap riil** (nilai saat ini, `inNet!==false`) per kelompok HG9 dari `hartaRows9(Y)`.
- Otomatis (`rhAuto20`): penghasilan = transaksi INCOME tahun Y (atau `Spt_History[Y].inc`), PPh = pengeluaran ber-kata pph/pajak/djp/mpn/e-billing, biaya hidup = pengeluaran akun Pribadi (Purpose PERSONAL / kosong) di luar pajak. Semua bisa ditimpa manual → Settings **`Rekap_Harta`** {tahun:{inc,tax,cons,other,note,at}} lewat `saveLists({rekapHarta})`; "pakai otomatis" menghapus isian manual.
- Status (`rekapM20`): wajar bila |selisih| ≤ maks(Rp10 jt, 5% penghasilan); lebih besar = kemungkinan penghasilan / utang belum tercatat; lebih kecil = biaya hidup / harta baru belum tercatat. Unduh Excel 3 sheet (`rhXls20`: Kewajaran, Dua versi, Daftar 31 Des). Tab "Rekap Harta" di Kelola Harta & Riwayat SPT.
- Format Excel rekap harta milik pemilik belum diterima — bila dikirim, kolom & kode dicocokkan ke tab ini.

| ID | Status |
|---|---|
| DN-261101-020634-711 | Selesai — 2026.11.20 (Beranda › Kelola Harta › Rekap Harta; perlu deploy Edge Function) |


## Rilis kartuku-sb 2026.11.21 (16 Nov 2026) — 6 catatan + auto-search benefit & promo berkeyakinan
- File berubah: `index.html` (blok terakhir "kartuku-sb 2026.11.21", CSS `css1121`, fungsi berakhiran `21`; edit langsung `APP_VERSION`), `booq_edge_function_SATU_FILE.ts` (**WAJIB deploy ulang**). manifest, icons & SQL tidak berubah.
- Backend baru: Settings **`Kk21`** {loy:[akun miles {id,prog,no,holder,tier,unit,site}], pool:{"program|bank": POOL|SPLIT}, fb:[koreksi {q,wrong,right,why,ok,at}] maks 200, hunt:{"C:<cardId>"|NEW: tanggal}} lewat `saveLists.kk21`, ikut pubSettings. Rute: `api_chat21 {page HOME|SNK, msgs, ctx, ground}` (geminiCall_ + memori AI + koreksi; balasan {reply, picks, follow, learned, memSaved}; koreksi yang terdeteksi disimpan ke Kk21.fb, fakta/preferensi ke AiMemory Source CHAT), `api_recoFb21` (tombol ✓/✕), `api_aiMiles21 {files,text}` (screenshot/email saldo miles), `api_promoHunt21 {mode OWNED|NEW, cards, topics, have}` (Google Search + AI gratis/riset; tiap item `cls` OFFICIAL|BLOG|SOSMED, `conf` 5–99, `srcs` [{d,cls,ver,uri}]). `api_saveReward` menerima Card_ID `L:<id akun miles>`. Promo_DB menyimpan `cls, conf, srcs, own, ty, hunt` (batas 600 KB); src `SOSMED` diterima.
- Keyakinan: Resmi (domain bank/jaringan/mitra, + Bank_Domains) 88 · Blog/media 60 (+6 blog kartu kredit spt pinterpoin) · Sosmed 35; +8 bila beberapa jenis sumber, +4 bila domain ditemukan di grounding Google (✓), −10 bila tidak, −30 bila sudah berakhir, −8 promo tanpa tanggal.
- Frontend: obrolan `chH21/chSend21/chRf21` (riwayat localStorage `kk_ch21_HOME|SNK`), konteks `ctxHome21/ctxSnk21`; `snAsk19` = kirim ke obrolan SNK. Belajar: `fbW21/fbAdj21` (bobot kata × kartu dari Kk21.fb: benar +1, 👍 +0,6, salah −1,5) di `best19` (ditimpa), `fbAsk21/fxGo21` (pilih kartu yang benar), tombol ✕ di baris "Kartumu untuk pengeluaran terbesar". Auto-search `hunt21` (otomatis: 1 kartu/hari bergilir, kartu baru 1×/minggu, localStorage `kk_hunt21`; mati bila otomatis SnK dimatikan), `huH21`, filter Keyakinan `SN21.cf`, urutan "Keyakinan tertinggi", `riH19` baru (badge `cfH21`, sumber `sdH21`), panel kartu "Auto-search".
- Poin & Miles (`mvw` ditimpa): `rwGroups21` (gabungan 1 saldo per bank: regex `POOLRX21` mis. Livin'poin, atau saldo sama persis di periode sama; Pisahkan/Gabungkan → Kk21.pool), `rwLatest21` (saldo terakhir; kosong / 0 mencurigakan → dihitung saldo lalu + didapat − ditukar + ±, tanda ≈ + peringatan; cek saldo awal ≠ saldo lalu), tabel mutasi `.mt21`, total per satuan + hangus terdekat; akun miles `lyOpen21/lySave21/lyDel21` (preset `LOYP21`), baca screenshot `msOpen21/msRead21/msSave21`.
- Gambar kartu: thumbnail `ctMake21` 480×303 (pangkas pinggiran polos, cover rasio 1,586, kartu tegak diputar) di localStorage `kk_ct21` → `ctSet21` memasang src sinkron (imgFill & MutationObserver); dibuat di latar saat aplikasi dibuka; dibersihkan bila gambar kartu diganti.
- Livin'poin: situs resmi Bank Mandiri — satu program poin per nasabah dari Livin', kartu kredit & debit.
- Miles: GarudaMiles / KrisFlyer belum menyediakan API publik perorangan; login otomatis dengan password pengguna tidak dipakai (keamanan, OTP/captcha) → screenshot / email + tombol Buka situs.

| ID | Status |
|---|---|
| DN-261113-171651-548 | Selesai — 2026.11.21 (Beranda; perlu deploy Edge Function) |
| DN-261113-171549-953 | Selesai — 2026.11.21 (SnK & Benefit; perlu deploy Edge Function) |
| DN-261113-171201-413 | Selesai — 2026.11.21 (Kelola › Poin & Miles; via screenshot/email, API tidak tersedia) |
| DN-261113-171038-627 | Selesai — 2026.11.21 (Kelola › Poin & Miles) |
| DN-261113-170952-807 | Selesai — 2026.11.21 (Kelola › Poin & Miles) |
| DN-261113-170842-416 | Selesai — 2026.11.21 (Tagihan) |
| (pemilik 16 Nov) Auto-search benefit & promo + keyakinan sumber | Selesai — 2026.11.21 (SnK & Benefit) |

### Catatan uji
- Chromium (desktop 1400px & HP 390px, backend tiruan): obrolan Beranda & SnK (kirim, saran lanjutan, ✕ → pilih BCA → `best19("bayar PLN")` memilih BCA "dipelajari dari koreksimu", koreksi lewat ketikan → lencana Dipelajari), auto-search (2 item: Resmi 96% dengan 2 sumber ✓, Sosmed 27%), filter keyakinan, panel kartu; Poin & Miles (Livin'poin 2 kartu → 1 kartu 13.112, Pisahkan → per kartu; BCA 0 setelah 5.000 → 5.250 ≈ + peringatan; screenshot → akun GarudaMiles 48.250 tersimpan); Tagihan: gambar berpinggiran transparan jadi penuh tanpa celah, src thumbnail terpasang sebelum layar digambar setelah muat ulang. Lebar HP 390px tanpa geser samping. Tanpa error JavaScript.
- Belum diuji langsung: Gemini & Google Search sungguhan (jaringan uji tertutup).


## Rilis kartuku-sb 2026.11.22 (17 Nov 2026) — 8 catatan
- File berubah: `index.html` (blok baru "kartuku-sb 2026.11.22" setelah blok 11.21, CSS `css1122`, fungsi berakhiran `22`) dan `booq_edge_function_SATU_FILE.ts` (**WAJIB deploy ulang**). Opsional: SQL pg_cron (dibuat dari aplikasi).
- Backend: `hunt21Core_` (prompt diperkaya: days, how, terms, elig ALL|NEW_CARDHOLDER|NEW_CUSTOMER|REGISTER|SELECTED, newDays; promo kedaluwarsa dibuang; `inelig` diisi bila welcome bonus / nasabah baru tapi kartu sudah lama → keyakinan −25), `cardSince21_` (Card_Context.since / periode tagihan tertua / Created_At), `hunt21Save_` (simpan ke Promo_DB + Kk21.hunt di server, buang hasil auto-search yang sudah berakhir). `api_promoHunt21 {mode, cardId, cards, topics, have, save:true}` → `added`. Pencarian 24 jam: `api_cron21Key` (buat/matikan kunci; property `CRON21_<key>`=uid, `CRON21U_<uid>`=key) + rute publik `api_cron21 {key}` (handleKartuKu memuat data pemilik kunci; tiap putaran: kartu baru tiap 7 hari, lalu 1 kartu milik terlama, lalu 1 kategori belanja teratas/hari; status di `Kk21.cron {at,n,last}`). Kk21.loy: bal, asOf, sts, stsU, next, toNext, tierExp, exp, expDate, logo. `api_aiMiles21` + tierExpiry, nextTier, toNext, statusUnit. Chat SNK: wajib bandingkan milik vs belum punya, cek tanggal & eligibility. `api_aiItems`: `det` [{n,q,p,a,o}] detail barang, biaya beda jenis tidak digabung, mata uang asing 2 desimal. Promo_DB menyimpan days, how, terms, elig, newDays, inelig.
- SQL pencarian 24 jam (dibuat oleh tombol SnK › Auto-search › "Aktifkan pencarian 24 jam"): `cron.schedule('booq-promo-hunt','17 */2 * * *', net.http_post(... {"action":"api_cron21","args":[{"key":"…"}]}))`. Mematikan: tombol Matikan + `select cron.unschedule('booq-promo-hunt');`.
- Frontend: tooltip kosong disembunyikan (`#tipx:empty`); bukti struk di daftar transaksi tagihan (`rcFill22`, lightbox `lbOpen22`); mata uang (`ALLCUR22` dari Intl, `itCur22`, `itSum` / `itLs` / `fl11Row` / `fl11Sync` versi desimal, `itemsOut` menyimpan Rupiah teralokasi kurs aktual + amtF/aF/feesF, cur, rEst, rAct, totF, dt "Kurs"); detail barang `detH22` di popup Rincian, form Transaksi (lewat pembungkus fetch `DET22`), dan detail Transaksi (`txD`); akun miles ringkas (`rwCard21` versi 22, `loyLogo22` favicon program/maskapai, `lgOpen22` Login & perbarui → msOpen21 + baca clipboard saat kembali, `msSave21` menyimpan status ke akun); SnK satu input (kotak BOO = filter + tanya, `.sq19 .sb` disembunyikan), panel `cmpH22` Kartumu vs Belum punya, `ctxSnk21` versi 22 (sejak kapan kartu dimiliki, label MILIK/BELUM PUNYA/TIDAK ELIGIBLE), filter "Tidak eligible (n)", `hunt21` versi 22 (simpan di server), status & pengaturan 24 jam `crOpen22`.

| ID | Status |
|---|---|
| DN-261117-003346-751 | Selesai — 2026.11.22 (Tagihan › Rincian & bukti; Transaksi › form) |
| DN-261117-000643-733 | Selesai — 2026.11.22 (Tagihan › detail › Transaksi) |
| DN-261117-002351-100 | Selesai — 2026.11.22 (Kelola › Poin & Miles) |
| DN-261117-002214-488 | Selesai — 2026.11.22 (Kelola › Poin & Miles; login embed tidak dimungkinkan → Login & perbarui via screenshot) |
| DN-261117-001750-235 | Selesai — 2026.11.22 (menu samping) |
| DN-261117-001658-816 | Selesai — 2026.11.22 (SnK & Benefit; 24 jam butuh SQL pg_cron sekali) |
| DN-261117-000732-689 | Selesai — 2026.11.22 (SnK & Benefit) |
| DN-261116-212148-130 | Selesai — 2026.11.22 (Transaksi; Tagihan › Rincian & bukti) |

### Catatan uji 2026.11.22
- Chromium desktop 1400px & HP 390px, backend tiruan: tooltip menu kosong tidak tampil; thumbnail bukti di baris transaksi tagihan → foto besar + X menutup; popup Rincian SGD 18.50 + biaya 3.50 = SGD 22.00 ≈ Rp255.200 (kurs 11.600), akurat Rp258.000 → kurs aktual 11.727,27 (+1,1%), Items tersimpan Rp216.955 + 21.695 + 19.350 = Rp258.000; detail barang tampil di detail Transaksi; kartu GarudaMiles ringkas (saldo, tier, progres ke Silver, hangus, tombol Login ulang & perbarui), total Miles ikut; SnK satu input (mengetik menyaring + pindah ke Temukan, fokus tetap), panel Kartumu vs Belum punya, welcome bonus kartu lama tersembunyi di "Tidak eligible (1)", jendela SQL 24 jam; obrolan SnK + koreksi tetap jalan. Tanpa geser samping di HP, tanpa error JavaScript.
- Belum diuji langsung: Gemini/Google Search sungguhan, pg_cron Supabase, logo favicon (jaringan uji tertutup).


## Rilis kartuku-sb 2026.11.23 (17 Nov 2026) — 15 catatan
- File berubah: **hanya `index.html`** (blok "kartuku-sb 2026.11.23" setelah blok 11.22, CSS `css1123`, fungsi berakhiran `23`). Edge Function sama dengan 2026.11.22 — tidak perlu deploy ulang (bila 11.22 sudah dideploy).
- Kategori ML (`mlModel23/mlPredict23/mlLearn23/mlAuto23/mlChips23`): Naive Bayes multi-fitur (merchant + bentuk ternormalisasi, nama, catatan, barang struk, lokasi, channel, akun, kartu, jenis baris, rentang nominal, hari/tanggal, mata uang), bobot terbaru > lama, koreksi manual lewat pembungkus `ue` disimpan di localStorage `kk_ml23` (maks 400, bobot 2,5). Isi otomatis bila ≥80% (kSrc "pola", lencana `.ml23b`), selain itu 3 saran di bawah Kategori.
- Baris verifikasi (`vEdit` dibungkus): `.e4.l23` grid foto kiri `.ph23` (thb besar: klik / Ctrl+V / seret), `.c-mid` hijau, `.c-r` oranye, tanggal biru, footer gradasi.
- Dropdown bisa dicari (`ssOpen23` dkk.): semua `<select>` ≥6 opsi (kecuali `data-ns23`), cari nama + grup + metadata `SYN23`, ↑↓ Enter Esc, posisi atas/bawah otomatis, HP = lembar bawah.
- PDF: `hlApply`/`pdfHL` ditimpa — sorotan `.kk-hl` dipakai ulang & bergeser (transition), tanpa lompat ke atas halaman.
- Kotak bisa dikecilkan: `.gl19` & `.imb7` (`colDeco23`, localStorage `kk_col23`).
- Tagihan › detail: foto bukti masuk ke kolom nama (`rcFill22` ditimpa, `.n.ph23`).
- Lightbox `#lb16`: klik = zoom di tempat (`.st.z23`) + tombol perbesar/perkecil.
- Detail transaksi (`txOpen7` dibungkus): kotak `fxBox23` mata uang asli + nominal, "Baca dari bukti" (itText → api_aiItems), simpan `Original_Currency`, `Amount`, `Exchange_Rate`=IDR/nominal (Rupiah tidak berubah); kurs pasar dibandingkan.
- Form transaksi: tombol `#gid23` "Buat ID otomatis" (centang disembunyikan), `descId23` = MERCHANT-YYMMDDHHMM-SUMBER-KAT-NOMINAL; `unify23` menyatukan `#tf9ct` + `#dt14t` dalam `.un23`; `#dt22f` disembunyikan.
- SnK: utas obrolan `TH23` (localStorage `kk_th23`, migrasi dari `kk_ch21_SNK`), sidebar `.sb23` (cari, klik, hapus), pemilih konteks `pkH23` (Umum / topik `TOP23` / kartu / kategori, bisa dicari), fokus dikirim lewat `ctxSnk21` ("FOKUS OBROLAN …" + data kartu bila konteks kartu); atribut panel `data-tw23`.
- Kelola › Kartu: toolbar `.kf23` (cari metadata, urut bank/nama/limit/jatuh tempo/cetak/iuran, filter Aktif/Nonaktif/jaringan) via DOM (`kfApply23`).

| ID | Status |
|---|---|
| DN-261117-122743-660 | Selesai — 2026.11.23 (Tagihan › verifikasi) |
| DN-261117-122133-229 | Selesai — 2026.11.23 (Tagihan › verifikasi) |
| DN-261117-121223-275 | Selesai — 2026.11.23 (semua halaman) |
| DN-261117-121151-974 | Selesai — 2026.11.23 (Tagihan › verifikasi) |
| DN-261117-120932-580 | Selesai — 2026.11.23 (Tagihan › verifikasi PDF) |
| DN-261117-024220-108 | Selesai — 2026.11.23 (Tagihan) |
| DN-261117-024213-296 | Selesai — 2026.11.23 (Tagihan / Beranda) |
| DN-261117-022926-230 | Selesai — 2026.11.23 (Tagihan › detail) |
| DN-261117-120413-370 | Selesai — 2026.11.23 (Transaksi › bukti) |
| DN-261117-120332-348 | Selesai — 2026.11.23 (Transaksi › detail) |
| DN-261117-024020-343 | Selesai — 2026.11.23 (Transaksi › Catat) |
| DN-261117-023948-704 | Selesai — 2026.11.23 (Transaksi › Catat) |
| DN-261117-023717-247 | Selesai — 2026.11.23 (Transaksi › Catat) |
| DN-261117-115828-889 | Selesai — 2026.11.23 (SnK & Benefit) |
| DN-261117-101133-469 | Selesai — 2026.11.23 (Kelola › Kartu Kredit) |

### Catatan uji 2026.11.23
- Chromium 1400px & HP 390px, backend tiruan: ML "SHOPEE JAKARTA SELATAN" → Belanja Online terisi otomatis (pola), baris baru tampil 3 saran %, klik saran → kategori terisi + contoh belajar tersimpan; tata letak baris baru (foto kiri / HP foto di atas); dropdown mata uang dicari "yen" → JPY, Enter memilih; ID otomatis "ZUSCOFFEE-261117-45K" dan tombol hilang setelah terisi; kotak kurs di detail transaksi (USD 12,50 → kurs aktual 16.517,12); zoom lightbox tanpa jendela baru; cari kartu "bca" → 1 dari 3; SnK konteks Dining & kartu BCA masuk ke konteks AI, riwayat bisa dipindah; kotak info dikecilkan & diingat; foto bukti di kiri nama transaksi tagihan. Uji 11.21–11.22 tetap lolos, tanpa error JavaScript.
- Belum diuji langsung: sorotan PDF dengan PDF tagihan asli, kurs pasar (fx9) & AI sungguhan (jaringan uji tertutup).

## Rilis kartuku-sb 2026.11.24 (19 Nov 2026) — 18 catatan + audit hitungan
Blok frontend `fe24` (CSS `css1124`, fungsi berakhiran 24). **Backend berubah** → deploy ulang Edge Function: `api_bulkPurpose24` (mut_, ganti Purpose banyak transaksi sekaligus) & `api_promoDoc24` (PDF/gambar/link → promo → Promo_DB, kolom baru `doc`).

**Aturan hitung (berlaku semua halaman):** pengeluaran = Kind EXPENSE (refund/cashback negatif mengurangi). `CC_PAYMENT` (bayar tagihan) & `TRANSFER` = pelunasan / pindah dana → **tidak** masuk Debet/pengeluaran, ditampilkan terpisah. Klik Beranda → Transaksi menyalin periode Beranda & menghapus filter lama (`nav24`). `dedupe24` membuang baris ID ganda di `S.tx` tiap render. Panel `aud24` = "Cek hitungan".

| ID | Menu › lokasi | Isi singkat |
|---|---|---|
| DN-261119-113503-240 | Transaksi (+Beranda) | audit hitungan: periode & filter disamakan, chip filter aktif, footer tanpa pelunasan, "Cek hitungan" (per jenis, kemungkinan dobel, kurs, Rp 0) |
| DN-261118-151301-606 | Semua dropdown kategori/akun/sub-akun | ketik → "+ Tambah …" (`addOpt24`); sub-akun selalu tampil |
| DN-261118-150350-921 | Transaksi › tabel | bayar tagihan = baris abu "pelunasan", tak dihitung |
| DN-261118-145944-269 | Semua popup ≥8 pilihan (`popMenu`) | kotak cari |
| DN-261118-144027-728 | Transaksi › tabel | kolom Channel (EDC/Online/QRIS) kiri Metode bayar, klik = saring |
| DN-261117-161751-806 | Semua jendela | X kanan atas (`x24`), Esc |
| DN-261117-143954-438 | Lightbox `#lb16` | roda/cubit zoom, seret geser (`ZM24`) |
| DN-261119-113313-517 · 112604-751 · 112453-833 | Rekap Tagihan | papan kolom akun per **bulan cetak**; seret/⇄/pilih banyak; draf lokal → Simpan 1× (`RK24`, `api_bulkPurpose24`); klik = detail; tampilan lama di "Rincian per kartu…" |
| DN-261119-092512-240 | SnK › Konteks kartu | form kosong setelah AI; papan promo berwarna (hijau aktif · oranye ≤7 hari · biru akan datang · abu berakhir); warna sama di daftar SnK |
| DN-261119-091347-914 | SnK › BOO | tombol (+) lampiran PDF/gambar/link (juga tempel/seret) → `api_promoDoc24`; placeholder "Apa yang bisa Boo bantu hari ini?" |
| DN-261117-161424-795 | SnK › BOO | tiap masuk SnK = obrolan baru + sapaan konteks (`snkGreet24`); tersimpan setelah kirim pesan; picker konteks tetap di "Obrolan baru" |
| DN-261118-172822-362 | Tagihan › daftar | teks & chip ringkas |
| DN-261118-172750-618 | Tagihan (≥1100px) | 3 kolom daftar/detail/PDF, lebar & urutan tersimpan (`kk_b3w_24`, `kk_b3o_24`, toggle `kk_b3_24`); klik baris transaksi → sorot di PDF (`hl24`) |
| DN-261118-172105-724 | Tagihan › Belum diupload | bulan berjalan tampil walau belum cetak ("akan terbit") |
| DN-261118-144221-493 | Tagihan › kotak belum masuk tagihan | kecil tersimpan (kunci tetap `imb7:unbilled24`, chip ikut tersembunyi) |
| DN-261117-143634-371 | Beranda › Catat dari struk | belajar baris nominal ("TOTAL BAYAR") per format struk + lencana "dipelajari N×" |

### Catatan uji 2026.11.24
Playwright desktop 1400/1500 & HP 390: Beranda→Transaksi periode sama, footer = chip kategori, pelunasan terpisah, Cek hitungan menemukan pasangan dobel; Rekap: seret & ⇄ (HP), tambah sub-akun, simpan 1 request; Tagihan 3 kolom + sorot PDF; SnK sapaan, lampiran → promo; zoom lightbox; tambah kategori dari dropdown. Regresi t1/t6/t8/u1/u3 lolos (u3 disesuaikan: picker kini lewat "Obrolan baru").

## Rilis kartuku-sb 2026.11.25 (19 Nov 2026 malam) — 16 catatan baru
Blok `fe25` (CSS `css1125`); Rekap Tagihan diubah langsung di blok 24. **Backend berubah → deploy ulang Edge Function**: `api_catTidy25` (usulan AI rapikan kategori), `api_catApply25` (terapkan, 1 request), `api_renamePurpose25` (ganti nama akun + semua transaksi), `api_rekap` param `by:'print'` (bulan terbit), `api_saveLists` + `uiPrefs`/`akTops`/`akLabels`, `pubSettings_` + `Ui_Prefs`/`Ak_Tops`/`Ak_Labels`, split menyimpan `Purpose` per bagian, `reconcile_`: **lembar tagihan = acuan** (memo salah kartu/rekening dipindah ke kartu tagihan, tanggal ikut tagihan, catatan "[dikoreksi lembar tagihan…]", `summary.moved`).
Preferensi tampilan per pengguna: kunci localStorage `kk_spl, kk_colw11, kk_col23, kk_b3_24, kk_b3o_24, kk_b3w_24, kk_bvpdf, kk_rail, kk_bo25, kk_rsm25` disinkron ke Settings `Ui_Prefs` (server menang saat login).
Akun utama buatan = purpose tanpa parent + terdaftar di `Ak_Tops` → otomatis masuk `AK18` (`akSync25`). Label Pribadi/Bisnis = `Ak_Labels` (hanya tampilan; `ppName` tetap).

| ID | Menu › lokasi | Isi singkat |
|---|---|---|
| DN-261119-151903-755 | Catat (Pilih kategori) · Kelola kategori | optgroup per jenis; "Rapikan kategori dengan AI" (gabung dobel, kategori→akun, nama, jenis) |
| DN-261119-124055-843 | Beranda (≥1100px) | panel Boo kanan setinggi layar, lipat (`kk_bo25`) |
| DN-261119-131254-550 | SnK › panel kartu | papan promo + cxSum + tombol Konteks / Tanya Boo; progres lama di details |
| DN-261119-130901-843 | Rekap Tagihan | pensil = ganti nama akun; kolom "+ Akun baru" (klik / seret) |
| DN-261119-130719-255 | Upload tagihan · Rekap | statement = acuan (pindah memo salah kartu); Rekap hanya transaksi ber-Bill_ID, bulan terbit |
| DN-261119-130545-151 | Rekap Tagihan | tanpa centang/pegangan: tahan & geser; HP tekan lama; klik = detail; Ctrl/Shift = pilih banyak |
| DN-261119-130120-950 | Rekap Tagihan | "Belum ada akun" paling kanan |
| DN-261119-125823-159 | Transaksi › tabel · Split | kolom Akun pembayar; label "Bagian i/n · 1 baris tagihan"; akun per bagian split |
| DN-261119-125727-673 | Transaksi › tabel | kategori & akun atas–bawah |
| DN-261119-125535-492 | Catat dari struk | jendela ±96% layar, HP penuh |
| DN-261119-125332-427 | Semua (ukuran panel) | `Ui_Prefs` per pengguna |
| DN-261119-125137-416 | Tagihan › rekonsiliasi | pembagian debit per kategori & akun |
| DN-261119-125019-126 | Tagihan › daftar | kartu tagihan baru (`.b25`) |
| DN-261119-124834-840 | Tagihan 3 kolom | tahan judul kolom & geser, kolom lain bergeser beranimasi (FLIP) |
| DN-261119-124626-493 | Tagihan › detail | ringkasan rekonsiliasi (`rs25`), rincian lengkap dibuka di tempat |
| DN-261119-124354-502 | Tagihan 3 kolom | tinggi penuh sampai bawah layar (`b3Fit25`) |

Catatan: 18 ID lain di file permintaan 19-Nov (240, 606, 921, 269, 728, 806, 438, 517, 751, 833, 092512-240, 914, 795, 362, 618, 724, 144221-493, 371) sudah selesai di 2026.11.24 — tutup di Catatan Developer.

### Catatan uji 2026.11.25
Playwright 1400/1500 & 390: panel Boo lipat/buka & tersimpan ke server; kolom Akun pembayar; Rekap tahan-geser ke "+ Akun baru" → buat akun → ganti nama; ringkasan rekonsiliasi + per kategori/akun; geser kolom 3-kolom beranimasi tersimpan; tinggi penuh; SnK panel kartu; rapikan kategori (usulan → terapkan). Regresi t1/t6/t8/u1/u3/t24* lolos.


## Rilis kartuku-sb 2026.11.26 (23 Nov 2026) — 36 catatan + persiapan SOC
- File berubah: `index.html` (blok `fe26`, CSS `css1126`, fungsi berakhiran `26` + **edit langsung** di sumbernya: `b3on24`, `b3Fit25`, tombol 3 kolom dihapus, `upT9(cid,per)`, `vEdit` (tombol `ai26`, `dupH26`), `rawOf11`/`fpPick11` (bug `S.txAll`), `akTops`/`akSubs`/`akSync25`, widget Catatan Dev (`dnPick` banyak bagian, lampiran, `dnMd26`, `dnZip26`), validasi No. ID, kapsul channel Transaksi, papan Rekap (`rkv` 24: `.sp26`, kolom “+ Akun baru” setelah “Belum ada akun”, drag `rkPh26`), obrolan Beranda lama dimatikan, `APP_VERSION`) dan `booq_edge_function_SATU_FILE.ts` (**WAJIB deploy ulang**). Baru: **SOC-BOOQ.md**, folder `dev-tools/` (harness uji, tidak diunggah). SQL tidak perlu.
- Backend: DevNotes kolom baru **`Files`** (di ujung) + `Element` s.d. 2.400 / `Element_Text` 1.200 karakter (beberapa bagian dipisah baris baru); `api_uploadFile` menerima `ref:'DEVNOTE'` untuk gambar/PDF/teks/CSV/JSON/ZIP/XLSX/DOCX/MP4/WebM; `api_chat21` peran HOME = asisten keuangan pribadi seluruh aplikasi + balasan `acts:[{label,go,q}]` (tombol buka halaman).
- Tagihan: ruang kerja penuh layar (`html.tb9`/`html.tbR26` → `#v` = tinggi layar − header `--hd26`, panel bergulir sendiri, tanpa JS saat zoom), 3 kolom selalu (≥900px), daftar baris rata (`.gh9`/`.bl`), detail = transaksi selalu terbuka + nota subtotal/total (`rs26`, `.rk26`, `rsSub26`), upload dari 1 kartu → `.nb26`.
- Verifikasi baris: `vAI26` (satu tombol AI), `dupInfo26/dupChip26/dupH26/dupUse26` (acuan `r.dup26={k,use:'row'|'old',tid,oid}`; `row` → catatan lama disamakan setelah `api_importStatement` sukses), data lembar tagihan di `.c-mid`.
- ML: `Learn_Map.ml26` {merchant ternormalisasi → {k,n,w,pp,ch,at}} maks 400 (`ml26Build` sekali sehari, `ml26Put` tiap koreksi/simpan) memperkuat `mlPredict23`; `mlForm26` di form Catat.
- OCR: `itText` membaca PDF scan (render → OCR per halaman, maks 4), teks/HTML/EML, Excel, HEIC; `ocrFile9` fallback ke `itText`; `ocrParse26` (toko, No. pesanan, tanggal/jam, barang qty×nama, biaya, total, ••4 digit); Rincian: AI gagal → `itLocal26`.
- Transaksi: filter di judul tabel (`thF26`, popover `.hp26`, state tetap `Q.*`/`TQ7.st`; filter lama disembunyikan di desktop), pencarian prediktif `fz26/fzW26/lev26` + saran `sg26`, jendela Catat ±82% + `−` (`min26/unmin26`, kapsul `#mn26`) & `×` (`close26`), kartu “Hasil baca struk” `#ocr26` (`ocrCard26/ocrFill26`, merchant dari teks struk), No. ID opsional.
- Semua jendela: panduan ukuran 82vw × 82vh (desktop).
- BOO sidebar kanan semua halaman: `booMount26/booOpen26`, kunci `kk_boo26` (ikut Ui_Prefs), obrolan `APP` (riwayat HOME dipindah), di SnK = obrolan `SNK` (daftar riwayat `.sb23` disembunyikan, kotak di halaman = saring + tanya), konteks `ctxApp26` (halaman aktif + ringkasan), tombol `acts`.
- Kelola Akun: geser bebas (pointer + FLIP `flip26`), simpan `saveLists({akunOrder})` → Settings `Akun_Order`, dipakai `akTops/akSubs/AK18`.
- Rekap: `.sp26` kiri kelola akun (`.bd24` 2 kolom/baris) · kanan rincian (`.old26`), nama transaksi penuh, drag dengan placeholder `.kc24.ph26` + luncur.
- Catatan Dev: `dnEls26/dnElsSet26` (Element dipisah `\n`), `dnAtt26` (klik/seret/Ctrl+V, unggah langsung), tombol “+ Lampiran (.zip)” (JSZip dari cdnjs).

| ID | Menu › lokasi | Isi singkat |
|---|---|---|
| DN-261123-163342-561 | Tagihan › Upload (dari kartu) | hanya kartu yang diklik: tombol “Tidak ada tagihan di bulan ini” |
| DN-261123-163308-750 | Tagihan | bukan kartu — penuh sampai bawah seperti Excel, ringan saat zoom |
| DN-261120-122713-813 | Tagihan › Upload | “+ Konfirmasi untuk kartu lain…” → tombol sederhana |
| DN-261120-122216-271 | Tagihan › Rincian & bukti · Catat | OCR PDF scan & format lain |
| DN-261120-122019-458 | Tagihan › Rincian & bukti (HP) | layar penuh + isi dari OCR bila AI gagal |
| DN-261120-121857-434 | Kelola Akun (popup) | geser urutan semua kartu akun |
| DN-261120-121301-158 | Tagihan › verifikasi | pilih acuan bila No. pesanan sama |
| DN-261120-121119-250 | Tagihan › verifikasi | info “terhubung” (bukan merah) |
| DN-261120-120820-319 | Tagihan › verifikasi · Catat | metadata merchant tersimpan (ml26) |
| DN-261120-120715-452 | Tagihan › verifikasi · Catat | kategori ML dari kata kunci, merchant, barang |
| DN-261120-120608-776 | Tagihan › verifikasi | satu tombol “Isi dengan AI” di kaki panel |
| DN-261120-120527-316 | Tagihan › Input Tagihan | penuh sampai bawah |
| DN-261120-120422-327 | Tagihan › verifikasi | data lembar tagihan di dasar kartu tengah |
| DN-261119-201501-529 | Tagihan | diringankan (lihat catatan uji) |
| DN-261119-201133-189 | Tagihan | selalu 3 kolom |
| DN-261119-200937-523 | Tagihan › detail | rekonsiliasi rata, tanpa lipatan |
| DN-261119-200801-764 | Tagihan | 3 panel sama tinggi, penuh |
| DN-261119-200708-709 | Tagihan | tinggi otomatis penuh (menggantikan tarik manual) |
| DN-261119-200630-334 | Tagihan › detail | transaksi + subtotal/total seperti nota |
| DN-261119-200445-664 | Tagihan | tanpa ruang kosong |
| DN-261121-181509-848 | Beranda/Transaksi › Catat dari struk | rincian per barang |
| DN-261119-204153-441 | BOO | asisten keuangan pribadi |
| DN-261119-204129-505 | BOO | sidebar kanan hover + kunci, semua halaman |
| DN-261120-124238-590 | Transaksi › tabel | filter di judul tabel; kapsul = ganti |
| DN-261120-123822-779 | Transaksi › Catat | No. ID opsional |
| DN-261119-202151-251 | Transaksi › Catat | − kecilkan / × tutup & hapus |
| DN-261119-202056-836 | Semua jendela | ukuran ±82% layar |
| DN-261119-201941-963 | Transaksi › cari | prediktif + saran |
| DN-261119-200126-803 | Transaksi › Catat | kartu Hasil baca struk |
| DN-261119-195940-131 | Transaksi › Catat | merchant dari teks struk |
| DN-261119-205437-468 | Catatan Dev | banyak bagian + lampiran + .zip |
| DN-261119-205353-780 | SnK | riwayat obrolan dihapus → sidebar BOO |
| DN-261119-202834-607 | Rekap | nama transaksi lengkap |
| DN-261119-202535-622 | Rekap | 2 bagian kiri/kanan |
| DN-261119-202503-446 | Rekap | kolom akun lebar, 2 per baris |
| DN-261119-202413-992 | Rekap · Kelola Akun | animasi geser & pratinjau tempat |

### Catatan uji 2026.11.26
Harness baru: backend asli (Edge Function) dijalankan di Node dengan DB memori + Playwright (Chromium) + Tesseract lokal; data uji 5 kartu, 58 tagihan, ±950 transaksi. Desktop 1400 & HP 390: semua halaman, form Catat (OCR struk PNG → toko/No./tanggal/total/kategori, − kecilkan & lanjutkan, × konfirmasi), PDF scan terbaca OCR (±2 dtk), Rincian HP terisi dari OCR saat AI tidak ada, filter judul tabel & cari “nko”, Rekap seret dengan placeholder → 1 perubahan, Kelola Akun geser Bisnis ke depan → `Akun_Order` tersimpan, Catatan Dev 2 bagian + lampiran tersimpan (`Files`), BOO hover/kunci/konteks. Tanpa error JavaScript. Render Tagihan ±60 ms (sama dengan 11.25) tetapi tanpa hitung ulang saat zoom & tanpa gulir halaman.
- Belum diuji langsung: Gemini sungguhan (balasan `acts`), PDF tagihan asli bank, pg_cron.

### Ide berikutnya
- SOC Fase 1 (pisah file sumber + build 1 file) — lihat SOC-BOOQ.md §4.
- BOO bisa menjalankan aksi ringan (mis. “tandai lunas”, “pindah akun”) dengan konfirmasi.

## Rilis kartuku-sb 2026.11.27 (28 Nov 2026) — 49 catatan (permintaan-booq-20261128)
- File berubah: `index.html` (blok `fe27` di ujung script + **edit langsung**: `dupFind18` (refKey27/sim27), `akSubs=p=>[]`, `catOpts` → `catSort27/catFull27`, form kategori `kf2` punya select **Induk** (`#k2_p`, kolom `Parent`), `tfFiles9` ditulis ulang **tanpa blokir** (entri sementara blob lokal → `X.up27=Promise.all`, `ocrQuick27`, `api_aiItems` → `fill27` efek ketik, `tfBusy27/aiWait27`), `cssPath` unik (`:nth-of-type`, 14 level) + sorotan pakai elemen asli `_n`, kartu Rekap `tNm27` + `rf27`), `booq_edge_function_SATU_FILE.ts`.
- Backend (WAJIB deploy ulang): `Categories` kolom baru **`Parent`** (di ujung; `cleanCat_`, `api_saveCategory` mempertahankan Parent lama), `ROUTES_` jadi `let` + rute **`api_aiCat27`** (AI rapikan kategori: gabung yang mirip / jadikan sub-kategori), `api_loanPub` mengirim `method, limit, intOn, krate, itype, draws` (halaman link KRK).
- Catat (Transaksi): penampil bukti tunggal `tfPv9`→`.pv27` (strip mini bisa digeser urutannya, PDF dirender `pdfImg27`, tombol Teks/OCR/Penuh untuk SEMUA jenis), unggahan `fUp` anti-dobel (`HU27` sidik isi file + `kk_up27` di localStorage, `shrink27`, coba ulang 3×), `callBackend` coba ulang otomatis 5xx/546 (aman karena actionId), kartu “Hasil baca struk” (`ocrCard26/ocrFill26` ditulis ulang) cermin dua arah dengan isian, panel kanan: isian di atas, hasil OCR/AI di bawah (`tfLay27`), kamera HP `cam27/camGo27`.
- ML merchant: `Learn_Map.mr27` (per format struk: baris mana = merchant, dari koreksi pengguna); nama platform (Shopee/Tokopedia/…) dilewati (`PLAT27`).
- **Satu kartu hasil baca** `rcH27(o)` dipakai: Rincian & bukti Tagihan (`itCard27`, editor dilipat `itEd27`, tabel “Detail pesanan” lama disembunyikan) dan Konfirmasi Pembayaran (`payCard27` → `payParse27` + `pfParse13` lokal/AI; klik nilai = fokus ke input `data-f27`). Penampil melayang `fView` dapat tombol OCR & Baca ulang.
- Tagihan › verifikasi: hubungkan baris ke transaksi tercatat `link27/cand27/lkH27/txPick27`, otomatis `auto27` (1 kandidat persis → terhubung; beberapa catatan yang jumlahnya persis → otomatis split), memo yang terhubung dihapus setelah simpan; split tampil seperti transaksi biasa; toolbar `.bl27/.gl27` (lonceng di bilah judul), “Tidak ada tagihan” `.nb27` → `nbSet15`; 3/2/1 kolom; BOO hanya pojok kanan bawah (tutup saat mouseout); quick view tanpa lup & rasio asli (`thbFill`); `topLayer27` mencegah Enter/Esc tembus.
- Transaksi tabel: No. ref abu-abu `txDeco27/refOf27`, filter bank & kartu + chip akun, klik judul lagi = tutup filter, ganti jenis tidak reset/lompat; sinkron latar `freshTx27` (sebelum cek dobel & saat kembali ke tab).
- Rekap Tagihan: kartu pakai `tNm27` (Label platform lama kalah oleh merchant baru), no. ref abu-abu, **dobel persis** (nominal + tanggal + no. ref + kartu) → `dupScan27` + bar “Hapus dobel” `dupDel27` (yang paling lengkap disimpan), garis geser `gut27` (`--l27`, `localStorage rkL27`). Simpan transaksi: Label platform lama dikosongkan bila merchant diganti.
- Cicilan › Bagikan: halaman publik `?ci=` dibungkus `pubR11` → lencana mode, KRK = plafon/dipinjam/dibayar/sisa (bukan rencana tenor), bagian **Rincian utang & pembayaran** (`pubLedger27`, saldo berjalan) + foto bukti besar (lazy, IntersectionObserver), zoom bukti s.d. 900px.
- Loading `ld9`: langkah “A → B” jadi checklist maju + pesan menenangkan, tanpa backdrop-blur (ringan di HP).
- Kelola: sub-akun dihapus (`subMerge27` menggabung ke induk), kategori punya Induk + pencarian sinonim `catSem27/SYN27` + rapikan AI di latar.

### Tabel ID → lokasi menu (2026.11.27)
| ID | Menu | Isi |
|---|---|---|
| DN-261128-113608-118 | Transaksi › Catat | Upload struk tanpa menunggu: foto/PDF langsung tampil, OCR+AI mengisi tiap kotak dengan efek ketik di latar; kamu bisa terus mengisi. |
| DN-261128-112524-761 | Transaksi › Catat | AI belajar dari koreksimu: baris yang kamu pilih sebagai merchant diingat per format struk (Learn_Map "mr27"). |
| DN-261128-112158-477 | Transaksi › Catat | Kartu "Hasil baca struk" selalu sinkron dengan isian transaksi (cermin dua arah). |
| DN-261127-155657-141 | Transaksi › Jepret struk (HP) | Tombol "Jepret struk": kamera langsung, dibaca otomatis, kategori ditebak, unggahan anti-dobel + coba ulang otomatis. |
| DN-261124-164738-902 | Transaksi › tabel | No. ref / ID pesanan abu-abu di bawah nama transaksi. |
| DN-261124-164658-575 | Transaksi › Catat | Alur otomatis: OCR lokal → AI isi semua kotak sampai kartu (••1234) & metode bayar, tanpa layar kunci penuh. |
| DN-261124-154250-773 | Transaksi › Catat | Nama merchant tidak lagi asal baris teratas (Shopee/Tokopedia dll dilewati); pakai pola yang dipelajari. |
| DN-261124-143416-416 | Transaksi › tabel | Ganti jenis transaksi tidak me-reset filter & tidak melompat ke atas. |
| DN-261124-142703-902 | Transaksi › filter | Filter bank & kartu tampil lagi; pencarian prediktif (salah ketik/konteks tetap ketemu). |
| DN-261124-142142-995 | Transaksi › Catat (bukti) | Banyak bukti: 1 penampil utama + strip mini yang bisa digeser urutannya, tanpa gulir panjang. |
| DN-261123-221153-687 | Transaksi › tabel | Klik judul kolom lagi = menutup menu filter. |
| DN-261123-220829-477 | Transaksi › Catat | Tanggal (dan jam) otomatis terisi dari hasil OCR. |
| DN-261123-220806-590 | Transaksi › Catat | Panel kanan: isian kamu di atas, hasil OCR/Smart AI di bawah. |
| DN-261123-220644-797 | Transaksi › Catat | Tidak ada loading layar penuh — hanya kotak yang sedang diproses yang berkedip. |
| DN-261123-190525-533 | Transaksi › filter | Filter per akun pembayar (chip ringkas) + kategori dirapikan. |
| DN-261123-165756-269 | Kelola › Akun | Sub-akun dihapus: semua sub-akun digabung ke akun induk (konteks pindah ke Kategori & sub-kategori). |
| DN-261123-165551-669 | Transaksi / Beranda | Data dari HP & web disinkron di latar sebelum cek dobel dan saat kembali ke aplikasi. |
| DN-261123-165504-441 | Transaksi › Rincian | Rincian otomatis seperti struk: per barang (qty × harga), biaya admin, ongkir, pajak, diskon, total. |
| DN-261125-110955-587 | Tagihan › Konfirmasi Pembayaran | Bukti bayar dibaca OCR (+AI) dan tampil di kartu "Hasil baca bukti bayar" yang sama; klik nilai untuk mengubah. |
| DN-261124-230822-420 | Tagihan › Input/Verifikasi | Baris tagihan bisa disambung dari pencarian transaksi; bila belum ada → upload struk. |
| DN-261124-230636-954 | Tagihan › Input/Verifikasi | Split tetap dicocokkan ke transaksi tercatat; jumlah persis → otomatis split & terhubung. |
| DN-261124-225449-882 | Tagihan › Simpan | Error HTTP 546/5xx/jaringan → coba ulang otomatis tanpa dobel (actionId). |
| DN-261124-113035-383 | Tagihan | Baris atas dirapatkan (lonceng & target kartu di bilah judul), warna tenang: teal utama, hijau lunas, kuning segera, merah hanya terlambat. |
| DN-261123-191347-354 | Tagihan › Input/Verifikasi | Baris yang cocok dengan transaksimu menampilkan struk & data lengkapnya. |
| DN-261123-191044-470 | Tagihan › Rincian & bukti | Satu kartu "Hasil baca struk" (fungsi sama dengan Catat); editor rincian dilipat di tombol "Ubah rincian" — tidak ada tabel berulang. |
| DN-261123-190737-430 | Tagihan › Input | Bilah AI ringkas & opsional. |
| DN-261123-190104-361 | Tagihan | "Tidak ada tagihan": klik → konfirmasi → selesai. |
| DN-261123-185710-452 | Semua halaman | BOO hanya di pojok kanan bawah, muncul saat kursor di tombolnya, tertutup saat kursor pergi. |
| DN-261123-183658-322 | Tagihan › Split | Tombol Selesai/Hapus selalu di bagian paling bawah kartu. |
| DN-261123-183104-678 | Tagihan › Split | Bagian split tampil seperti transaksi biasa: kiri bukti, kanan detail · akun · kategori. |
| DN-261123-182859-588 | Tagihan › Input/Verifikasi | Tombol "Cari transaksi" dari semua transaksi; tidak ketemu → upload struk. |
| DN-261123-182429-369 | Tagihan › Quick view | Tanpa kaca pembesar; ukuran mengikuti rasio asli (tanpa ruang kosong). |
| DN-261123-182103-333 | Tagihan › Input/Verifikasi | Hubungkan ke transaksi tercatat (lanjutan 182023-346). |
| DN-261123-182023-346 | Tagihan › Input/Verifikasi | Baris pembayaran terhubung ke riwayat bayar tagihan bulan lalu (struk & data bayar tampil). |
| DN-261123-181912-754 | Tagihan › Input | Halaman bisa bergulir sedikit, PDF & kartu edit setinggi layar; Enter/Esc tidak tembus ke belakang. |
| DN-261123-165123-268 | Kelola › Kategori | Sub-kategori (Induk) + pencarian kategori paham konteks + rapikan kategori dengan AI (di latar). |
| DN-261123-164817-685 | Transaksi › Catat (bukti) | Tambah foto/PDF bisa seret-lepas; banyak file sekaligus diproses AI. |
| DN-261123-164635-981 | Tagihan | 3 / 2 / 1 kolom mengikuti lebar jendela. |
| DN-261125-110327-256 | Cicilan › Bagikan (link publik) | Halaman link dibedakan KRK (plafon, dipinjam, dibayar, sisa) vs Cicilan tetap (tenor); Rincian utang & pembayaran di bawah dengan foto bukti besar. |
| DN-261125-104056-689 | Rekap Tagihan / Tagihan | Tombol OCR & Baca ulang ada di semua jenis bukti (gambar & PDF), termasuk penampil melayang. |
| DN-261125-103708-125 | Catatan Developer | Mode klik-sorot memakai selector unik + elemen asli → yang disorot tepat yang kamu klik. |
| DN-261125-103638-417 | Rekap Tagihan / Transaksi | Ganti merchant: judul otomatis lama (mis. "SHOPEE") ikut diganti; kartu Rekap memakai nama baru. |
| DN-261125-103239-889 | Semua halaman | Unggah/OCR/AI di latar; sidik jari isi file mencegah unggah 2× (juga setelah muat ulang). |
| DN-261125-102926-224 | Rekap Tagihan | No. ref abu-abu di bawah nama; transaksi dobel persis (nominal, tanggal, no. ID) ditandai + tombol "Hapus dobel". |
| DN-261125-101348-833 | Semua halaman | Loading dinamis ringan: langkah → jadi checklist yang maju + pesan menenangkan, tanpa blur berat. |
| DN-261125-100951-549 | Rekap Tagihan › Edit transaksi | Edit transaksi punya "Isi dengan AI" + alat bukti yang sama dengan Catat. |
| DN-261125-100521-585 | Semua penampil bukti | Satu penampil & satu kartu hasil baca untuk Catat, Edit, Rincian & bukti, Bayar tagihan — ubah satu, semua ikut. |
| DN-261125-095407-765 | Rekap Tagihan | Garis geser di antara 2 panel (desktop), lebar diingat; klik ganda = normal. |
| DN-261124-164327-380 | Beranda › Cek dobel | Cek dobel memakai no. referensi & kemiripan merchant — Telkomsel vs saldo iklan Shopee tidak dianggap sama. |

### Catatan uji 2026.11.27
Harness: backend asli di Node + DB memori + Playwright + Tesseract lokal. Desktop 1400 & HP 390: semua halaman tanpa error JS; alur Catat (foto tampil seketika, OCR isi merchant/ID/tanggal/total, kartu ••2082 cocok), PDF+gambar 1 penampil, auto-link & auto-split Tagihan, kartu hasil baca di Rincian & bukti dan Konfirmasi Pembayaran, Rekap (dobel + garis geser), halaman link Cicilan KRK & tenor diuji.
- Belum diuji langsung: Gemini sungguhan (`api_aiCat27`, isi AI), kamera HP fisik, PDF tagihan bank asli.

### Ide berikutnya
- SOC Fase 1 (pisah file sumber + build 1 file) — lihat SOC-BOOQ.md §4; lapisan `fe18…fe27` makin tebal → saatnya dirapikan.
