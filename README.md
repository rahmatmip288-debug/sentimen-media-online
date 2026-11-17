# 🏛️ Aplikasi Analisis Sentimen Berita Online Pemerintah Kabupaten Bangka

Aplikasi berbasis web modern untuk memonitor dan menganalisis sentimen pemberitaan media daring terhadap kinerja, kebijakan, dan program kerja **Pemerintah Kabupaten Bangka** (Provinsi Kepulauan Bangka Belitung).

Pengguna dapat menganalisis berita secara otomatis cukup dengan memasukkan tautan (URL) portal berita, atau memasukkan teks secara manual jika berita berasal dari portal berbayar/dokumen internal. Sistem secara cerdas akan mengekstrak konten, menghitung skor indeks sentimen (**POSITIF**, **NEGATIF**, atau **NETRAL**), mendeteksi tingkat relevansi terhadap entitas Kabupaten Bangka, serta memberikan penyorotan visual (*highlighter*) pada kata-kata kunci.

---

## 🛠️ Tools & Teknologi yang Digunakan

Aplikasi ini dibangun menggunakan arsitektur modular yang menggabungkan backend Python yang ringan dan efisien dengan antarmuka frontend yang responsif dan interaktif:

### 1. Backend & Server
- **[Python 3.10+ / 3.11](https://www.python.org/)**: Bahasa pemrograman inti untuk logika bisnis, scraping, dan komputasi sentimen.
- **[Flask 3.x](https://flask.palletsprojects.com/)**: Microframework web berbasis Python untuk menangani routing HTTP, REST API endpoint, dan session management.
- **[Werkzeug](https://werkzeug.palletsprojects.com/)**: Modul utilitas WSGI dan enkripsi keamanan password berbasis hash (`generate_password_hash` & `check_password_hash`).
- **[Jinja2](https://palletsprojects.com/p/jinja/)**: Templating engine untuk rendering antarmuka HTML dinamis.

### 2. Web Scraping & Ekstraksi Data
- **[Requests](https://requests.readthedocs.io/)**: HTTP client untuk mengunduh konten halaman web dari berbagai URL portal berita online dengan dukungan custom User-Agent dan header anti-blocking.
- **[BeautifulSoup4 (bs4)](https://www.crummy.com/software/BeautifulSoup/)**: Library parser HTML untuk membersihkan elemen iklan, navigasi, skrip, dan komentar, serta mengekstrak judul, tanggal rilis, dan isi berita secara akurat.

### 3. Database & Penyimpanan Lokal
- **[SQLite3](https://www.sqlite.org/)**: Database relasional embedded bawaan Python. Tidak memerlukan instalasi server database eksternal (zero-configuration).
  - Menyimpan data riwayat analisis berita (`news_history`).
  - Menyimpan kamus kata kunci sentimen dinamis (`keywords`).
  - Menyimpan konfigurasi admin dan jadwal rotasi password (`settings` & `password_logs`).
  - Berkas database otomatis dibuat dan disimpan di `bangka_sentimen.db`.

### 4. Mesin Analisis Sentimen (NLP / Rule-Based)
- **Weighted Keyword Matching Engine**: Algoritma pencocokan kata berbobot dengan kategori Positif, Negatif, Netral, dan Entitas Pemkab Bangka.
- **Negation & Booster Handling**: Detektor kata sangkalan (*tidak, belum, bukan, tanpa, gagal*) dan penguat (*sangat, luar biasa, terbukti*) yang mampu membalikkan atau melipatgandakan polaritas kata sentimen.
- **Bangka Context Relevance Scorer**: Mengukur seberapa spesifik berita tersebut membahas wilayah/aparat Pemkab Bangka (Sungailiat, Belinyu, Pj Bupati, Sekda, OPD, DPRD Bangka, dll).
- **Regex & String Processing**: Digunakan untuk tokenisasi kalimat dan penyorotan teks sentimen (*color-coded HTML highlighting*).

### 5. Frontend & UI / Visualisasi Data
- **[Tailwind CSS](https://tailwindcss.com/) (via CDN)**: Utility-first CSS framework untuk membangun tampilan modern, responsif, dan konsisten dengan palet warna resmi Pemkab Bangka.
- **[Chart.js](https://www.chartjs.org/) (via CDN)**: Library diagram interaktif untuk menampilkan visualisasi rasio sentimen (*doughnut chart*) secara real-time.
- **[Font Awesome 6](https://fontawesome.com/) (via CDN)**: Kumpulan ikon modern untuk memperkaya navigasi dan tombol antarmuka.
- **[Google Fonts - Plus Jakarta Sans](https://fonts.google.com/specimen/Plus+Jakarta+Sans)**: Tipografi modern dan bersih untuk kenyamanan membaca laporan.
- **Vanilla JavaScript (ES6+)**: Logika frontend berbasis asynchronous fetch API, penanganan modal login/ganti password, kalkulasi statistik, pagination, dan interaktivitas tanpa dependensi framework JavaScript yang berat.

### 6. Otomasi & Deployment Lokal
- **Batch Launcher (`run_app.bat`)**: Skrip otomasi Windows untuk menjalankan server dan langsung membuka browser dalam 1 klik.

---

## 🌟 Fitur Utama Aplikasi

1. **Analisis Berita Otomatis via URL (Web Scraper)**
   - Mendukung portal berita lokal dan nasional (Bangka Pos, Babelpos, Detik, Kompas, Antara Babel, portal resmi Pemkab Bangka, dll).
   - Ekstraksi otomatis: Judul, portal media, tanggal, dan teks berita bersih dari iklan.
2. **Mode Input Cadangan (Teks Manual)**
   - Dapat digunakan untuk dokumen rilis pers internal, PDF teks, atau portal berbayar (*paywall*).
3. **Kamus Kata Kunci Sentimen Dinamis**
   - Tambah, ubah bobot, dan hapus kata kunci positif, negatif, netral, maupun konteks daerah.
   - Tombol **Reset ke Standar Pemkab Bangka** untuk mengembalikan kamus ke konfigurasi awal yang sudah dikalibrasi.
4. **Keamanan & Rotasi Sandi Admin Berkala**
   - Dilengkapi sistem login terproteksi.
   - Pilihan rotasi password (15, 30, 60, atau 90 hari) dengan banner pengingat otomatis jika sandi telah melewati masa aktif.
5. **Dashboard Statistik & Riwayat Analisis**
   - Diagram lingkaran persentase sentimen.
   - Tabel riwayat lengkap dengan penanda sentimen dan skor indeks.
   - Fitur **Ekspor Laporan ke format CSV / Excel** untuk pelaporan pimpinan.

---

## 📋 Prasyarat Sistem

- **Sistem Operasi**: Windows 10/11, Linux, atau macOS
- **Python**: Versi 3.10 atau 3.11+
- **Peramban Web**: Google Chrome, Microsoft Edge, Mozilla Firefox, atau browser modern lainnya
- **Koneksi Internet**: Diperlukan untuk scraping URL berita online dan memuat CDN frontend

---

## 📦 Instalasi Dependensi

1. Buka terminal (Command Prompt / PowerShell) dan arahkan ke direktori proyek:
   ```powershell
   cd d:\Rahmat\project\antigrafity2
   ```

2. Pasang semua pustaka yang dibutuhkan menggunakan `requirements.txt`:
   ```powershell
   pip install -r requirements.txt
   ```

---

## 🚀 Cara Menjalankan Aplikasi

### Cara 1: Menggunakan File Batch (Rekomendasi untuk Windows)
Cukup klik ganda (*double click*) berkas:
```
run_app.bat
```
Server akan menyala dan browser Anda akan otomatis membuka halaman aplikasi di `http://localhost:5000`.

### Cara 2: Menjalankan via Terminal / Command Prompt
Jalankan perintah berikut:
```powershell
python app.py
```
Setelah server aktif, buka browser dan kunjungi:
```
http://localhost:5000
```

---

## 🔐 Akun & Akses Administrator

- **Password Default Awal**: `adminbangka`
- **Cara Mengganti Password & Mengatur Jadwal Rotasi**:
  1. Klik tombol **"Ganti Sandi"** pada navbar pojok kanan atas.
  2. Masukkan password saat ini (`adminbangka`).
  3. Masukkan password baru dan konfirmasi (minimal 6 karakter).
  4. Tentukan siklus pengingat rotasi sandi (misal: 30 hari).
  5. Klik tombol **"Simpan Password Baru"**.

---

## 📁 Struktur Direktori Berkas

```
antigrafity2/
│
├── app.py                  # Server utama web (Flask API, session, & routing)
├── database.py             # Manajemen SQLite (tabel settings, keywords, riwayat analisis)
├── scraper.py              # Engine web scraping berita online & pembersihan HTML
├── analyzer.py             # Engine kalkulasi sentimen berbobot, negasi, & penyorot teks
├── requirements.txt        # Daftar pustaka dependensi Python yang dibutuhkan
├── run_app.bat             # Skrip peluncur otomatis 1-klik untuk Windows
├── bangka_sentimen.db      # Database lokal SQLite (dibuat otomatis saat app berjalan)
├── README.md               # Dokumentasi lengkap aplikasi dan panduan teknis
│
├── templates/
│   └── index.html          # Antarmuka web modern (Dashboard analitik & modal)
│
└── static/
    ├── css/
    │   └── custom.css      # Custom styling, scrollbar, badge, dan animasi
    └── js/
        └── app.js          # Logika frontend, charting, AJAX request, dan state management
```

---

## 📄 Lisensi & Pemeliharaan

Dikembangkan khusus untuk kebutuhan analisis publikasi dan pemantauan opini publik di lingkungan **Pemerintah Kabupaten Bangka**.
