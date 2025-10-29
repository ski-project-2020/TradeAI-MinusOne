import streamlit as st
import pandas as pd
import numpy as np
from utils import load_data, load_sentiment_analyzer, analyze_sentiment, create_career_matrix_plot, analyze_financial_health

# --- Page Configuration ---
st.set_page_config(
    page_title="Profil Talenta 360°",
    page_icon="👤",
    layout="wide"
)

# --- Header ---
st.title("👤 Profil Talenta 360°")
st.markdown("Halaman ini menyajikan analisis mendalam mengenai profil setiap ASN, termasuk rekomendasi karier dan pengembangan diri.")

# --- Load Data ---
df_asn = load_data('data/data_asn.csv')
df_sentimen = load_data('data/data_sentimen.csv')
df_slik = load_data('data/data_slik.csv')

if df_asn.empty or df_sentimen.empty or df_slik.empty:
    st.warning("Data tidak dapat dimuat. Pastikan file 'data_asn.csv', 'data_sentimen.csv', dan 'data_slik.csv' ada.")
else:
    df_asn_merged = pd.merge(df_asn, df_slik, on='id_asn', how='left')
    # --- Sidebar for ASN Selection ---
    with st.sidebar:
        st.header("Filter Profil")
        # Create a name to id mapping for easier lookup
        asn_name_map = df_asn_merged.set_index('nama')['id_asn'].to_dict()
        selected_asn_name = st.selectbox(
            "Pilih Nama ASN:",
            options=sorted(df_asn_merged['nama'].unique())
        )
        selected_asn_id = asn_name_map[selected_asn_name]

    # --- Main Content ---
    st.header(f"Analisis Profil: {selected_asn_name}")

    # Get selected ASN data
    asn_data = df_asn_merged[df_asn_merged['id_asn'] == selected_asn_id].iloc[0]

    # Display basic info
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info(f"**Nama:** {asn_data['nama']}")
    with col2:
        st.info(f"**NIP:** {asn_data['nip']}")
    with col3:
        st.info(f"**Jabatan:** {asn_data['jabatan_sekarang']}")

    st.divider()

    # --- Promotion Metrics ---
    col_promo1, col_promo2 = st.columns(2)
    with col_promo1:
        # Generate dynamic value based on ASN ID and potential
        np.random.seed(asn_data['id_asn'])
        prob_promosi = int(60 + (asn_data['potensi'] - 60) * 0.4 + np.random.randint(0, 10))
        st.metric("Probabilitas Promosi", f"{prob_promosi}%", help="Dihasilkan secara dinamis berdasarkan profil ASN")
    with col_promo2:
        # Generate dynamic value based on ASN ID and performance
        np.random.seed(asn_data['id_asn'] + 1) # Use different seed
        syarat_promosi = int(70 + (asn_data['kinerja_2023'] - 60) * 0.3 + np.random.randint(0, 10))
        st.metric("Pemenuhan Syarat Promosi", f"{syarat_promosi}%", help="Dihasilkan secara dinamis berdasarkan profil ASN")

    st.divider()
    
    # --- Early Warning System Status ---
    st.subheader("Status Peringatan Dini (EWS)")
    atensi, reason = analyze_financial_health(asn_data)
    if atensi:
        st.error(f"🔴 **Perlu Atensi**\n\n**Alasan:** {reason}")
    else:
        st.success(f"🟢 **Tidak Perlu Atensi**\n\n**Alasan:** {reason}")

    st.divider()

    # --- Tabs for Detailed Analysis ---
    tab1, tab2 = st.tabs(["📈 Rekomendasi Karier", "🧠 Pengembangan Diri"])

    with tab1:
        st.subheader("Rekomendasi Jenjang Karier Berikutnya")
        
        col_rec1, col_rec2 = st.columns([1, 2])
        with col_rec1:
            st.info("**Rekomendasi Prioritas:**")
            
            # --- Dynamic Recommendation Logic ---
            np.random.seed(asn_data['id_asn']) # Seed for consistency
            
            high_potential_roles = ["Ketua Tim Proyek Strategis", "Analis Kebijakan Senior", "Juru Bicara Pimpinan"]
            development_focus = ["Peningkatan Kinerja Individu", "Pelatihan Manajemen Proyek", "Sertifikasi Keahlian Teknis"]
            
            rekomendasi_1 = "Tidak ada rekomendasi"
            rekomendasi_2 = "Fokus pada tugas saat ini"

            # High potential and high performance
            if asn_data['potensi'] > 85 and asn_data['kinerja_2023'] > 85:
                rekomendasi_1 = np.random.choice(high_potential_roles)
                rekomendasi_2 = "Program Akselerasi Kepemimpinan"
            # High potential, lower performance
            elif asn_data['potensi'] > 85:
                rekomendasi_1 = "Mentoring dengan Pejabat Senior"
                rekomendasi_2 = np.random.choice(development_focus)
            # High performance, lower potential
            elif asn_data['kinerja_2023'] > 85:
                rekomendasi_1 = "Spesialisasi di Bidang Saat Ini"
                rekomendasi_2 = "Menjadi Mentor bagi Junior"
            # Lower performers
            else:
                rekomendasi_1 = np.random.choice(development_focus)
                rekomendasi_2 = "Konseling Kinerja"

            st.success(f"1. **{rekomendasi_1}**")
            st.warning(f"2. **{rekomendasi_2}**")
            
            st.markdown("""
            *Rekomendasi ini dihasilkan secara dinamis berdasarkan profil kinerja dan potensi ASN.*
            """)

        with col_rec2:
            st.plotly_chart(create_career_matrix_plot(asn_data), use_container_width=True)

    with tab2:
        st.subheader("Analisis Sentimen dan Rekomendasi Pengembangan")
        
        # Load sentiment model
        with st.spinner('Menganalisis sentimen ulasan...'):
            analyzer = load_sentiment_analyzer()
        
        # Filter sentiment data for the selected ASN
        asn_reviews = df_sentimen[df_sentimen['id_asn'] == selected_asn_id]

        if not asn_reviews.empty:
            # Combine all reviews into one text block for overall analysis
            full_text_reviews = ". ".join(asn_reviews['ulasan_naratif'].tolist())
            # Analyze sentiment for each review and average the score
            total_compound_score = 0
            reviews_list = asn_reviews['ulasan_naratif'].tolist()
            for review in reviews_list:
                total_compound_score += analyzer.polarity_scores(review)['compound']
            
            avg_compound_score = total_compound_score / len(reviews_list)

            if avg_compound_score >= 0.05:
                sentiment = "Positif"
                sentiment_color = "green"
            elif avg_compound_score <= -0.05:
                sentiment = "Negatif"
                sentiment_color = "red"
            else:
                sentiment = "Netral"
                sentiment_color = "orange"

            st.markdown(f"**Sentimen Ulasan Kinerja Keseluruhan:** <span style='color:{sentiment_color}; font-weight:bold;'>{sentiment}</span> (Skor: {avg_compound_score:.2f})", unsafe_allow_html=True)

            st.text_area("Contoh Ulasan Diterima:", "\n- ".join(reviews_list), height=150, disabled=True)

            st.markdown("**Rekomendasi Personalized Learning Path:**")
            
            # --- Dynamic Learning Path Logic ---
            np.random.seed(asn_data['id_asn'] + 2) # Use different seed
            
            leadership_path = ["Kepemimpinan Adaptif", "Manajemen Perubahan", "Pengambilan Keputusan Strategis"]
            technical_path = ["Analisis Data Tingkat Lanjut", "Manajemen Proyek Agile", "Keamanan Siber"]
            communication_path = ["Komunikasi Publik & Negosiasi", "Resolusi Konflik", "Kecerdasan Emosional"]
            
            if sentiment == "Negatif":
                rekomendasi_belajar = f"Fokus pada: **{np.random.choice(communication_path)}**."
                st.warning(rekomendasi_belajar)
            elif asn_data['potensi'] > 80:
                rekomendasi_belajar = f"Disarankan mengambil: **{np.random.choice(leadership_path)}**."
                st.success(rekomendasi_belajar)
            else:
                rekomendasi_belajar = f"Tingkatkan keahlian teknis dengan: **{np.random.choice(technical_path)}**."
                st.success(rekomendasi_belajar)
        else:
            st.info("Tidak ada data ulasan kinerja naratif yang ditemukan untuk ASN ini.")