# SOC-BOOQ — Peta Arsitektur & Rencana Separation of Concerns
_booq.id · KartuKu · disusun di rilis **kartuku-sb 2026.11.26** (23 Nov 2026), diperbarui **2026.11.27** (§8). Lampirkan file ini bersama KONTEKS-BOOQ.md saat memulai pekerjaan SOC._

> Tujuan: memecah aplikasi menjadi bagian-bagian yang masing-masing punya SATU tanggung jawab, **tanpa mengubah perilaku** yang sudah dipakai pemilik. Dokumen ini belum mengubah kode — ini peta + urutan kerja + aturan.

---

## 1. Kondisi sekarang (diukur dari kode 2026.11.26)

| Bagian | Angka | Catatan |
|---|---|---|
| `index.html` | ±12.500 baris · 2,57 MB · **1 tag `<script>`** | HTML + CSS + JS + gambar BOO (base64) jadi satu |
| Blok rilis bertumpuk | 31 blok (`kartuku-sb 2026.10.31` … `2026.11.26`) | tiap rilis menambah blok di akhir file |
| Pola “bungkus ulang” (monkey-patch) | `call` ×22 · `render` ×17 · `tblH` ×11 · `civ` ×10 · `rkPrev` ×9 · `bv` ×8 · `ts` ×7 · `tf` ×7 · `rkUp` ×7 | perilaku akhir = urutan pembungkus (lihat §3) |
| Definisi ulang fungsi | `vEdit` 5× · `vrow` 4× | hanya definisi terakhir yang hidup; sisanya kode mati |
| Pengamat DOM | 33 `MutationObserver` · ±210 listener global (`document`/`window`) | sebagian besar memantau `document.body` seluruhnya |
| CSS | 48 `<style>` disuntik lewat JS + 1 `<style>` utama · banyak `!important` | aturan saling menimpa antar rilis |
| Penyimpanan perangkat | 37 kunci `localStorage` (`kk_*`), 10 di antaranya disinkron ke server (`Ui_Prefs`) | |
| Backend `booq_edge_function_SATU_FILE.ts` | ±3.900 baris · 128 rute `api_*` · 17 sheet di `SCHEMA` | pengganti GAS + logika bisnis + adaptor Postgres + server HTTP dalam 1 file |

### Gejala yang dirasakan pemilik (dan akar teknisnya)
- **Berat / sering error** (DN-261119-201501-529): setiap `render()` melewati ±17 pembungkus; beberapa membongkar HTML jadi DOM lalu jadi teks lagi (`tp.innerHTML = h … return tp.innerHTML`) di `bv`, `tv`, `vEdit`, `chH21`, `snPanel7`, `rkv`. Kesalahan di satu pembungkus sering “ditelan” `try/catch` sehingga fitur diam-diam tidak jalan (contoh yang diperbaiki di 2026.11.26: `S.txAll` dipakai sebagai daftar padahal penanda 1/0 → data lembar tagihan tidak pernah tampil).
- **Perubahan kecil = Replace-All 2,5 MB**, rawan salah tempel.
- **Konflik tampilan**: CSS rilis lama dan baru sama-sama `!important`.

---

## 2. Peta tanggung jawab (concern) saat ini → target modul

| Concern | Sekarang tersebar di (fungsi / blok) | Target modul |
|---|---|---|
| Koneksi server | `callBackend`, `call` (+22 pembungkus: pencatat AI, Raw tagihan, DET22, dupe, chat, dll.), `mutate`, antrean catatan dev `dnQ` | `core/api.js` — 1 klien + **middleware terdaftar** (bukan bungkus berantai) |
| State | global `S`, `R` (input tagihan), `Q` (filter transaksi), `FM` (form), `BQ`, `RK`, `RK24`, `TH23`, `CH21`, `SN19`, `UP9`, `ITM`, `DN`, `BOO26`, `ML23/ML26` | `core/store.js` per domain (`tx`, `bills`, `cards`, `ui`), satu cara mengubah state + event `changed` |
| Navigasi & render | `go`, `render` (+17), `tab`, `railSync` | `core/router.js` + tiap halaman `mount()/update()` sendiri (render parsial, tidak membangun ulang seluruh `#v`) |
| Format & util | `rp`, `fg`, `fdd`, `pn`, `nrm23`, `tCase26`, `num26`, `E`, `ic`/`P` | `core/format.js`, `core/icons.js` |
| Komponen UI | `mo/cm`, `mo2/cm2`, `askSure`, `popMenu`, `ssOpen23` (dropdown cari), `hpOpen26` (filter judul), `flip26` (animasi geser), lightbox `lb16`, kalender `dp*`, `toast` | `ui/*.js` — dipakai semua halaman |
| Logika transaksi (murni) | `txF7` (+3), `hayHit15`/`fz26` (cari), `tvSum24`, `dedupe24`, `isNC24`, `amt7`, `live7`, `splitGrp25` | `domain/transactions.js` (tanpa DOM, bisa diuji) |
| Logika tagihan & rekonsiliasi | `reconcile_` (server), `billView7`, `rs26`, `rsGrp25`, `remind9`, `noBill15`, `dupInfo26` | `domain/bills.js` + `features/tagihan/*` |
| Kategori / ML | `detect`, `mlModel23`, `mlPredict23` (+ml26), `ml26Build/Put`, `kGuess14`, `Learn_Map.*` | `domain/learning.js` |
| OCR & dokumen | `itText` (+3), `ocrFile9`, `readDoc`, `pdfText26`, `ocrParse26`, `tessPatch14`, `loadOCR` | `domain/documents.js` (worker terpisah disarankan) |
| Akun pembayar | `AK18`, `akTops`, `akSubs`, `akOrd26`, `akSync25`, `cpurps`, `ppName` | `domain/accounts.js` |
| Halaman | Beranda `home`, Transaksi `tv`/`tf`/`tf9`, Tagihan `bv`/`rv`/`vEdit`/`itR`, Rekap `rkv`, Rekening `acv`, Cicilan `civ`, SnK `snv`, Kelola `mv*`, Catatan Dev `dnv` | `features/<halaman>/` (view + controller) |
| Asisten BOO | `chH21`, `chSend21`, `ctxHome21`, `ctxSnk21`, `ctxApp26`, `booMount26`, `TH23` | `features/boo/` |
| Tampilan | 49 blok CSS | `styles/tokens.css` (branding §Branding di KONTEKS), `styles/components.css`, `styles/<halaman>.css` |
| Backend | 1 file: lapisan GAS (SpreadsheetApp, DriveApp…), auth, `SCHEMA/TENANT`, 128 rute, Gemini, promo, adaptor Postgres | `server/gas-shim.ts`, `server/auth.ts`, `server/schema.ts`, `server/routes/*.ts` (tx, bills, ai, promo, devnotes, rewards, settings), `server/db-postgres.ts`, `server/main.ts` — dibundel jadi 1 file untuk editor Supabase |

---

## 3. Rantai pembungkus terpanjang (urutan = perilaku)
Urutan rilis yang membungkus fungsi (paling atas = paling awal dieksekusi di dalam). Saat SOC, **satu rantai dilebur jadi satu fungsi** lalu diuji ulang dengan skenario di §6.

| Fungsi | Jumlah | Rilis yang membungkus |
|---|---|---|
| `call` | 22 | 11.02, 11.05, 11.06×2, 11.09, 11.10×2, 11.11, 11.12×2, 11.13×3, 11.14, 11.15×2, 11.16, 11.21, 11.22, 11.25, 11.26×2 |
| `render` | 17 | 11.04, 11.05, 11.08, 11.09×2, 11.10, 11.15, 11.16, 11.18, 11.19, 11.21×2, 11.23, 11.24, 11.25, 11.26×2 |
| `tblH` | 11 | 10.31×2, 11.01, 11.02×2, 11.03, 11.04, 11.05, 11.15, 11.16, 11.23 |
| `civ` | 10 | 11.05, 11.07, 11.08, 11.09, 11.11, 11.12, 11.13, 11.14, 11.15, 11.18 |
| `rkPrev` | 9 | 11.01, 11.05, 11.09, 11.10, 11.11, 11.13, 11.14, 11.15×2 |
| `bv` | 8 | 11.02, 11.05, 11.06, 11.07, 11.09, 11.14, 11.24, 11.25 |
| `ts` / `tf` | 7 / 7 | 10.31–11.26 |
| `rkUp` | 7 | 11.05–11.15 |
| `mvCards` | 6 | 11.02–11.16 |
| `vEdit` (definisi ulang) | 5 | 10.31×2, 11.01, 11.03, 11.04 (+ pembungkus 11.11, 11.23, 11.26) |
| `itAuto`, `tv`, `tfFiles9`, `ctxM`, `ekstrak`, `sv` | 5 | |

---

## 4. Urutan kerja SOC (bertahap, perilaku tetap)

| Fase | Isi | Hasil untuk pemilik | Uji lulus bila |
|---|---|---|---|
| **0 · Fondasi** (sudah di 2026.11.26) | harness uji lokal (backend asli di memori + Playwright), aturan rilis §5, peta ini | — | `dev-tools/` jalan, smoke test tanpa error JS |
| **1 · Pisah file sumber** | `src/` berisi `core/`, `ui/`, `domain/`, `features/`, `styles/`; skrip build menggabung jadi **1 `index.html`** (GitHub Pages tetap sama) | tetap 1 file untuk diunggah; Claude cukup mengirim file yang berubah di `src/` + hasil build | hasil build identik secara perilaku (smoke test) |
| **2 · Lebur rantai per halaman** | mulai **Tagihan** (`bv`×8, `vEdit`, `tblH`×11), lalu Transaksi (`tv`, `tf`, `ts`), Rekap, Cicilan (`civ`×10), Rekening | Tagihan & Transaksi lebih ringan (render parsial) | skenario §6 per halaman + ukur waktu render (target < 25 ms untuk 1.000 transaksi) |
| **3 · Store & event** | `core/store.js` + delegasi event terdaftar per halaman; hapus `MutationObserver` global yang bisa diganti hook render | lebih sedikit “kedip” & error diam | 0 observer pada `document.body` kecuali yang perlu |
| **4 · CSS** | satukan 49 blok jadi token + komponen + per halaman; buang `!important` yang saling tindih | tampilan konsisten | tangkapan layar desktop 1400 & HP 390 sama |
| **5 · Backend modul** | pecah `.ts` jadi modul; bundel ke 1 file; uji unit `domain` (rekonsiliasi, hitungan, kurs) | deploy tetap 1 tempel | uji unit + smoke test |
| **6 · Data & aset** | BOO WebP base64 → file `assets/boo/*.webp` (cache browser), `kk_*` diringkas | muat awal lebih cepat | ukuran `index.html` < 1 MB |

---

## 5. Aturan sementara (berlaku sejak 2026.11.26 sampai SOC selesai)
1. **Ubah langsung di sumbernya** bila definisi jelas (contoh 11.26: `b3on24`, `b3Fit25`, `akTops`, `akSync25`, `vEdit` footer, widget Catatan Dev). Blok rilis baru hanya untuk fitur baru.
2. Jangan menambah pembungkus `render`/`call` baru kecuali benar-benar lintas halaman; bila perlu, kerjakan di DOM yang sudah tampil (contoh `thF26` dekorasi judul tabel) — **tanpa membongkar HTML ulang**.
3. Fungsi murni (tanpa DOM) ditulis terpisah & diberi nama jelas (`ocrParse26`, `fz26`, `akOrd26`) agar mudah dipindah ke `domain/` saat SOC.
4. Satu blok CSS per rilis (`css11xx`), hindari `!important` kecuali menimpa CSS lama.
5. Setiap ID catatan → `DN_DONE` + tabel di KONTEKS-BOOQ.md (menu › lokasi).
6. Setiap rilis diuji dengan `dev-tools/` (desktop 1400 & HP 390) — tidak ada error JavaScript.
7. Kolom baru di sheet selalu di ujung `SCHEMA`; perubahan backend ditandai “WAJIB deploy ulang”.

---

## 6. Skenario uji regresi (dipakai tiap fase)
- **Tagihan**: daftar (3 kolom ≥900px, baris rata), pilih tagihan → detail + rekonsiliasi nota, PDF di kolom kanan, Upload dari kartu → tombol “Tidak ada tagihan di bulan ini”, Edit ulang tagihan → verifikasi baris (Isi dengan AI tunggal, info No. pesanan terhubung + pilih acuan, data lembar tagihan), Simpan.
- **Transaksi**: filter judul kolom (semua kolom), cari “nko”, kapsul channel = ganti, Catat dari struk (OCR → kartu hasil baca + kategori ML), − kecilkan / × tutup, simpan tanpa No. ID.
- **Rekap**: 2 bagian, 2 kolom akun per baris, seret kartu → pratinjau tempat → Simpan 1×.
- **BOO**: hover tepi kanan, kunci, kirim pesan di tiap halaman (konteks halaman ikut), SnK → percakapan di sidebar.
- **Kelola Akun**: geser urutan, pindah sub-akun.
- **Catatan Dev**: tunjuk beberapa bagian, lampiran Ctrl+V, unduh .md & .zip.
- **HP 390px**: semua halaman tanpa geser samping; Rincian & bukti layar penuh.

---

## 7. Cara menjalankan harness uji (untuk Claude)
Folder `dev-tools/` (tidak perlu diunggah ke GitHub Pages):
1. `npm i pdfjs-dist@3.11.174 chart.js@4.4.1 xlsx@0.18.5 @tailwindcss/browser@4 tesseract.js@5.1.1 tesseract.js-core@5.1.1 @tesseract.js-data/eng @tesseract.js-data/ind jszip` (CDN diarahkan ke paket lokal).
2. `./build_backend.sh booq_edge_function_SATU_FILE.ts` → `backend.mjs` (Edge Function asli, adaptor Postgres diganti DB memori `db.json`).
3. `node server.mjs <folder-app> 8787` → daftar akun via `api_register`, isi data `python3 seed.py`.
4. `python3 smoke.py 1400` dan `python3 smoke.py 390` → semua langkah + daftar error JavaScript.

---

## 8. Tambahan rilis 2026.11.27 (28 Nov 2026)
- **Komponen bersama baru** (calon modul `ui/proof` di SOC): `rcH27(o)` = satu kartu "Hasil baca" (judul, sumber OCR/AI, meta yang bisa diklik → input `data-f27`, tabel barang/biaya/total, catatan selisih). Dipakai `itCard27` (Rincian & bukti) dan `payCard27` (Konfirmasi Pembayaran). `ocrCard26` (Catat) masih punya render sendiri → **Fase SOC berikutnya: pindahkan ke `rcH27`** agar 1 fungsi untuk semua.
- Penampil bukti: `tfPv9` (.pv27) di Catat/Edit, `fView` (.fvw) melayang di Rekap/Tagihan (sekarang punya tombol OCR yang sama), `#m2 .it2v` di Rincian. Target SOC: satu `ProofViewer` dengan mode inline / melayang.
- Pembungkus baru 11.27: `ts` ×2, `itR`, `itOpen`, `pset`, `fView`, `rkv` ×2, `pubR11`, `ld9`, `fUp`, `call` (via `callBackend`), `thbFill`, `tfPv9`. Rantai `rkv` & `ts` makin panjang → prioritas lebur di Fase 2.
- Edit langsung di sumber (bukan pembungkus): `tfFiles9`, `cssPath`, `dnPick`, `dupFind18`, `catOpts`, `akSubs`, `kf2/kf2S`, render kartu Rekap `.kc24`.
- Uji regresi tambahan untuk §6: (1) upload struk → foto tampil < 300 ms, OCR mengisi; (2) unggah file yang sama 2× → 1 unggahan; (3) Rincian & bukti → kartu hasil baca + "Ubah rincian"; (4) Rekap: transaksi dobel persis → bar "Hapus dobel"; (5) link Cicilan KRK & tenor.
