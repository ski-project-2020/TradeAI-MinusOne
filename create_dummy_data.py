import pandas as pd
import numpy as np
import random
from faker import Faker
import os

# Initialize Faker for Indonesian data
fake = Faker('id_ID')

# --- 1. Generate data_asn.csv ---
def create_data_asn(num_records=100):
    """Generates dummy data for ASN profiles."""
    pangkat_gol_options = ['III/a', 'III/b', 'III/c', 'III/d', 'IV/a', 'IV/b', 'IV/c']
    jabatan_options = [
        'Analis Kebijakan Pertama', 'Analis Kebijakan Muda', 'Analis Kebijakan Madya',
        'Perencana Pertama', 'Perencana Muda', 'Perencana Madya',
        'Auditor Pertama', 'Auditor Muda', 'Auditor Madya',
        'Pranata Komputer Pertama', 'Pranata Komputer Muda', 'Pranata Komputer Madya'
    ]
    unit_kerja_options = [
        'Biro Perencanaan', 'Biro Kepegawaian', 'Biro Hukum',
        'Inspektorat', 'Direktorat Kinerja ASN', 'Pusat Pengembangan Talenta'
    ]
    pendidikan_options = ['S1', 'S2', 'S3']

    data = []
    for i in range(1, num_records + 1):
        data.append({
            'id_asn': i,
            'nama': fake.name(),
            'nip': fake.unique.numerify(text='##################'),
            'pangkat_gol': random.choice(pangkat_gol_options),
            'jabatan_sekarang': random.choice(jabatan_options),
            'unit_kerja': random.choice(unit_kerja_options),
            'kinerja_2023': random.randint(60, 100),
            'potensi': random.randint(60, 100),
            'pendidikan_terakhir': random.choice(pendidikan_options),
            'lama_bekerja_thn': random.randint(2, 25),
            'gaji_bulanan': random.randint(5, 25) * 1_000_000,
            'total_hutang': random.randint(0, 500) * 1_000_000
        })
    return pd.DataFrame(data)

# --- 2. Generate data_lhkpn.csv ---
def create_data_lhkpn(asn_ids, num_years=5):
    """Generates dummy LHKPN data with potential anomalies."""
    data = []
    asn_with_anomaly = random.sample(asn_ids, k=5) # Select 5 ASN for anomaly

    for asn_id in asn_ids:
        # Start with a more varied base wealth
        kekayaan = random.randint(300, 1500) * 1_000_000
        # Assign a stable, individual growth rate for each ASN
        growth_rate = random.uniform(0.05, 0.15)
        
        for year in range(2019, 2019 + num_years):
            # Inject a very significant anomaly for selected ASN in a specific year
            if asn_id in asn_with_anomaly and year == 2022:
                kekayaan *= random.uniform(2.5, 4.0) # 150% to 300% jump
            else:
                # Apply a much more stable and predictable increase for normal data
                kekayaan *= (1 + growth_rate + random.uniform(-0.02, 0.02))

            data.append({
                'id_asn': asn_id,
                'tahun_lapor': year,
                'total_kekayaan': int(kekayaan)
            })
    return pd.DataFrame(data)

# --- 3. Generate data_relasi.csv ---
def create_data_relasi(asn_ids, num_relations=150):
    """Generates dummy social network data."""
    tipe_relasi_options = ['Kolega 1 Unit', 'Keluarga', 'Alumni Pelatihan', 'Transaksi Keuangan', 'Proyek Bersama']
    data = []
    for _ in range(num_relations):
        sumber, target = random.sample(asn_ids, 2)
        data.append({
            'id_asn_sumber': sumber,
            'id_asn_target': target,
            'tipe_relasi': random.choice(tipe_relasi_options)
        })
    return pd.DataFrame(data)

# --- 4. Generate data_sentimen.csv ---
def create_data_sentimen(asn_ids, num_reviews_per_asn=3):
    """Generates dummy performance review narratives."""
    positive_templates = [
        "{} menunjukkan integritas luar biasa dan profesionalisme yang tinggi. Kinerjanya sangat hebat dan selalu melampaui ekspektasi.",
        "Kinerja {} sangat memuaskan, fantastis, dan patut dipuji. Dia adalah aset yang sangat berharga bagi tim.",
        "{} adalah pribadi yang ceria, selalu kolaboratif dan solutif. Inovasinya membawa dampak yang sangat positif dan menguntungkan.",
        "Sangat senang dengan kontribusi {}. Selalu proaktif, dapat diandalkan, dan hasilnya selalu sempurna.",
        "Luar biasa, {} selalu menunjukkan kinerja terbaik, sangat direkomendasikan untuk proyek penting selanjutnya."
    ]
    negative_templates = [
        "{} sangat buruk dalam kolaborasi dan seringkali menciptakan suasana tidak nyaman. Ini masalah serius.",
        "Manajemen waktu {} sangat mengecewakan dan sering terlambat. Ini menghambat pekerjaan tim.",
        "Sangat disayangkan, inisiatif dari {} sangat kurang. Kinerjanya di bawah standar dan tidak memuaskan.",
        "Tingkat ketelitian {} dalam laporan sangat buruk dan sering menyebabkan kesalahan fatal. Ini tidak bisa diterima.",
        "Komunikasi {} sangat buruk, seringkali tidak jelas dan menyebabkan kebingungan. Sangat sulit bekerja sama."
    ]
    data = []
    asn_df = create_data_asn(len(asn_ids)) # Create a temporary df to get names
    asn_map = asn_df.set_index('id_asn')['nama'].to_dict()

    for asn_id in asn_ids:
        nama_asn = asn_map.get(asn_id, "ASN")
        for _ in range(num_reviews_per_asn):
            if random.random() > 0.3: # 70% positive
                ulasan = random.choice(positive_templates).format(nama_asn.split()[0])
            else:
                ulasan = random.choice(negative_templates).format(nama_asn.split()[0])
            data.append({
                'id_asn': asn_id,
                'ulasan_naratif': ulasan
            })
    return pd.DataFrame(data)

# --- 5. Generate data_slik.csv ---
def create_data_slik(asn_ids):
    """Generates dummy SLIK OJK data."""
    data = []
    for asn_id in asn_ids:
        # 20% chance of having a bad record
        kualitas = 'Y' if random.random() < 0.2 else 'N'
        data.append({
            'id_asn': asn_id,
            'kualitas_debitur_buruk': kualitas
        })
    return pd.DataFrame(data)

def main():
    """Main function to generate and save all dummy data files."""
    print("Membuat direktori 'data' jika belum ada...")
    os.makedirs('data', exist_ok=True)

    # Generate ASN data
    print("Membuat data_asn.csv...")
    df_asn = create_data_asn(100)
    df_asn.to_csv('data/data_asn.csv', index=False)
    all_asn_ids = df_asn['id_asn'].tolist()

    # Generate LHKPN data for a subset of ASN
    print("Membuat data_lhkpn.csv...")
    lhkpn_asn_ids = random.sample(all_asn_ids, 20)
    df_lhkpn = create_data_lhkpn(lhkpn_asn_ids)
    df_lhkpn.to_csv('data/data_lhkpn.csv', index=False)

    # Generate relation data
    print("Membuat data_relasi.csv...")
    df_relasi = create_data_relasi(all_asn_ids)
    df_relasi.to_csv('data/data_relasi.csv', index=False)

    # Generate sentiment data
    print("Membuat data_sentimen.csv...")
    df_sentimen = create_data_sentimen(all_asn_ids)
    df_sentimen.to_csv('data/data_sentimen.csv', index=False)

    # Generate SLIK data
    print("Membuat data_slik.csv...")
    df_slik = create_data_slik(all_asn_ids)
    df_slik.to_csv('data/data_slik.csv', index=False)

    print("\nSemua file data dummy berhasil dibuat di dalam folder 'data/'.")
    print("Jalankan 'pip install -r requirements.txt' dan 'streamlit run 1_🏠_Home.py' untuk memulai aplikasi.")

if __name__ == '__main__':
    main()