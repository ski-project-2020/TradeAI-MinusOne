# SIMANTRA: Sistem Manajemen Talenta Berintegritas

**SIMANTRA** adalah prototipe aplikasi web berbasis AI yang dibangun menggunakan Streamlit untuk kompetisi hackathon. Aplikasi ini bertujuan untuk mentransformasi manajemen talenta Aparatur Sipil Negara (ASN) di Indonesia menjadi lebih objektif, prediktif, dan berintegritas.

## ✨ Fitur Utama

Aplikasi ini memiliki beberapa fitur utama yang diimplementasikan sebagai aplikasi multi-halaman:

1.  **🏠 Home:** Dashboard utama yang menampilkan KPI penting terkait manajemen talenta.
2.  **👤 Profil Talenta 360°:** Memberikan pandangan mendalam tentang profil setiap ASN, termasuk rekomendasi karier yang dipersonalisasi dan analisis sentimen dari ulasan kinerja.
3.  **📊 Pemetaan Talent Pool:** Menggunakan model klasifikasi untuk memetakan ASN ke dalam _talent pool_ berdasarkan kinerja dan potensi mereka.
4.  **🚨 Early Warning System (EWS):** Sistem deteksi dini proaktif untuk mengidentifikasi anomali, termasuk:
    - **Deteksi Anomali LHKPN:** Menganalisis laporan kekayaan untuk menemukan lonjakan yang tidak wajar.
    - **Analisis Jaringan Sosial:** Memvisualisasikan relasi antar ASN untuk mengidentifikasi potensi konflik kepentingan atau KKN.

## 🚀 Cara Menjalankan Aplikasi

Pastikan Anda memiliki **Python 3.8+** terinstal di sistem Anda.

### 1. Clone Repositori (Jika Berlaku)

```bash
git clone [URL_REPOSITORI_ANDA]
cd [NAMA_FOLDER_REPOSITORI]
```

### 2. Buat dan Aktifkan Virtual Environment (Direkomendasikan)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Instal Dependensi

Instal semua pustaka yang dibutuhkan menggunakan file `requirements.txt`.

```bash
pip install -r requirements.txt
```

### 4. Buat File Data Dummy

Aplikasi ini memerlukan data sintetis untuk berjalan. Jalankan skrip berikut untuk membuatnya. File-file data akan dibuat di dalam folder `data/`.

```bash
python create_dummy_data.py
```

### 5. Jalankan Aplikasi Streamlit

Setelah data dibuat, jalankan aplikasi utama Streamlit.

```bash
streamlit run 1_🏠_Home.py
```

Aplikasi akan terbuka secara otomatis di browser default Anda.

---

_Dibuat dengan ❤️ untuk Hackathon._
