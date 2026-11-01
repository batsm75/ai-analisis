# 🤖 AI Trading Terminal

AI trading analyzer yang berjalan **di terminal (Termux / Linux / macOS / Windows)**.
Mengambil data market langsung dari **TwelveData** + **SoSoValue** via API key, lalu
menganalisis chart pattern secara otomatis menggunakan **Groq AI** sebagai otak utama.
Hasilnya berupa **setup trade** (BUY / SELL / WAIT) lengkap dengan entry, stop loss,
take profit, invalidasi, dan reasoning.

> ⚠️ **Disclaimer**: Alat ini hanya untuk edukasi & analisis. Bukan saran investasi.
> Selalu lakukan manajemen risiko dan verifikasi sendiri.

---

## ✨ Fitur

- **Menu 1 — Analisis**: input simbol & timeframe → AI membaca chart pattern → setup rapi.
  Ada tombol **Refresh** (analisis ulang) dan **Kembali ke menu utama**.
- **Menu 2 — Pengaturan Trade**:
  - Risk : Reward
  - Metode analisis (pilih nomor **1–5**):
    1. **SND** — Supply & Demand
    2. **SNR** — Support & Resistance
    3. **SMC** — Smart Money Concepts
    4. **ICT** — Inner Circle Trader
    5. **SESSION KILLZONE** — London / NY killzone
  - Target pips (input bebas)
- **Menu 3 — Env**: kelola semua API key & URL langsung dari aplikasi, tersimpan di `.env`.
- Setiap pindah menu: **clear screen** dulu, baru tampilkan menu tujuan.
- API key **hanya disimpan di `.env`** lokal pengguna (tidak pernah di-commit ke GitHub).

---

## 🧰 Tech Stack

| Komponen | Teknologi | Alasan |
|---|---|---|
| Bahasa | Python 3.8+ | Jalan native di Termux tanpa emulator |
| UI terminal | `rich` | Tampilan warna, tabel, panel yang rapi & mudah dibaca |
| Env | `python-dotenv` | Simpan API key di `.env` |
| HTTP | `requests` | Panggil REST API TwelveData, SoSoValue, Groq |
| AI Brain | **Groq** (OpenAI-compatible) | Model `qwen/qwen3.8-27b`, cepat & gratis |
| Data 1 | **TwelveData** | Forex / saham / crypto / indeks (time_series) |
| Data 2 | **SoSoValue v3** | US equity & perpetual futures (candles) |

---

## 📁 Struktur Folder

```
ai-trading-terminal/
├── main.py                  # Entry point: python main.py
├── requirements.txt
├── .env.example             # Template konfigurasi (copy jadi .env)
├── .gitignore               # .env & config.json TIDAK ikut ter-commit
├── README.md
└── src/
    ├── __init__.py
    ├── config.py            # Path, env loader, metode analisis, setting trade
    ├── ui.py                # Clear screen, banner, input, tabel, masking
    ├── clients.py           # Client: TwelveData, SoSoValue, Groq
    ├── analysis.py          # Orkestrasi: fetch data → prompt AI → parse setup
    └── menus.py             # Menu utama + Analisis + Pengaturan + Env
```

File lokal yang **dibuat otomatis saat dipakai** (tidak ada di repo):
- `.env` — API key & URL kamu
- `config.json` — pengaturan trade (RR, metode, target pips)

---

## 🚀 Instalasi di Termux (Android)

```bash
# 1. Install Python & Git (jika belum)
pkg update && pkg upgrade -y
pkg install python git -y

# 2. Clone dari GitHub (ganti URL dengan repo kamu)
git clone https://github.com/USERNAME/ai-trading-terminal.git
cd ai-trading-terminal

# 3. Install dependensi
pip install -r requirements.txt

# 4. Jalankan
python main.py
```

> Saat pertama kali dijalankan, file `.env` otomatis dibuat dari `.env.example`.
> Buka **menu [3] Env** untuk mengisi API key, atau edit manual: `nano .env`

### Dapatkan API Key
| Layanan | Link | Catatan |
|---|---|---|
| Groq | https://console.groq.com/keys | Gratis, model default `qwen/qwen3.8-27b` |
| TwelveData | https://twelvedata.com/account/api-keys | Free tier 8 req/menit |
| SoSoValue | https://sosovalue.com/developer | v3: US equity & perpetual futures |

---

## 📤 Upload ke GitHub

```bash
cd ai-trading-terminal
git init
git add .
git commit -m "AI Trading Terminal v1.0"
git branch -M main
git remote add origin https://github.com/USERNAME/ai-trading-terminal.git
git push -u origin main
```

✅ `.env` dan `config.json` **otomatis diabaikan** Git (sudah ada di `.gitignore`),
jadi API key kamu aman tidak ikut ter-upload.

---

## 🧪 Pengujian

Pengujian yang dilakukan pada proyek:
- **Syntax check**: `python -m py_compile main.py src/*.py` — wajib lulus.
- **Import check**: modul ter-load tanpa error.
- **Unit logika parsing JSON AI**: `_extract_json()` menangani respons ber-fence markdown.
- **Alur menu offline**: navigasi tanpa API key menampilkan peringatan yang jelas.

Yang **belum** diuji otomatis (butuh API key asli + jaringan):
- Panggilan nyata ke TwelveData / SoSoValue / Groq.
- Format respons AI yang bervariasi (sudah ada fallback tampilan teks mentah).

Untuk uji koneksi cepat setelah mengisi key:
```bash
python -c "from src.clients import TwelveDataClient; print(TwelveDataClient().get_candles('EUR/USD','1h',3)[-1])"
```

---

## 🛠️ Deployment / Menjalankan

Tidak ada server — aplikasi ini berjalan lokal di perangkat kamu. Cukup:
```bash
python main.py
```
Untuk update dari GitHub: `git pull && pip install -r requirements.txt`

---

## 📌 Status Proyek

**Selesai (MVP):**
- ✅ 3 menu utama + clear screen di setiap transisi
- ✅ Pengambilan data TwelveData (time_series) + SoSoValue (candles v3)
- ✅ Analisis Groq AI dengan 5 metode (SND/SNR/SMC/ICT/Killzone) + RR + target pips
- ✅ Setup output: arah, pattern, entry, SL, TP, RR, invalidasi, level, reasoning
- ✅ Tombol Refresh & kembali di menu analisis
- ✅ Manajemen API key via menu Env, tersimpan di `.env`
- ✅ `.gitignore` aman + README + struktur siap `git clone`

**Catatan / batasan:**
- SoSoValue v3 saat ini hanya mencakup **US equity & perpetual futures** (belum spot forex).
  Untuk pair forex, analisis tetap berjalan penuh menggunakan TwelveData; status SoSoValue
  ditampilkan sebagai info di panel sumber data.
- Jika model `qwen/qwen3.8-27b` tidak tersedia di akun Groq kamu, ubah `GROQ_MODEL`
  di menu Env (mis. `llama-3.3-70b-versatile`).

**Langkah berikutnya (opsional):**
- Tambahkan indikator teknis (RSI, MACD, EMA) di sisi lokal.
- Simpan riwayat analisis ke file JSON/CSV.
- Tambahkan alert notifikasi bila setup terpenuhi.
