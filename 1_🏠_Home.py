import streamlit as st
import pandas as pd
from utils import load_data
import os

# --- Page Configuration ---
st.set_page_config(
    page_title="SIMANTRA Home",
    page_icon="🏠",
    layout="wide"
)

# --- Header ---
st.title("SIMANTRA: Sistem Manajemen Talenta Berintegritas")
st.markdown("""
Selamat datang di **SIMANTRA**, sebuah platform AI terpadu yang dirancang untuk mentransformasi 
manajemen talenta Aparatur Sipil Negara (ASN) menjadi lebih objektif, prediktif, dan berintegritas.
""")

# --- Main Content ---

# Load data to get total ASN
df_asn = load_data('data/data_asn.csv')

if not df_asn.empty:
    st.divider()

    # --- Key Performance Indicators ---
    st.header("Dashboard Utama")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(
            label="Total ASN Terdata",
            value=f"{df_asn.shape[0]} Orang"
        )
    with col2:
        # Dummy value as specified
        st.metric(
            label="Potensi Risiko Terdeteksi",
            value="15 Kasus",
            delta="-2% vs bulan lalu",
            delta_color="inverse"
        )
    with col3:
        # Dummy value as specified
        st.metric(
            label="Talent Pool High Potential",
            value="85 Orang",
            delta="+5% vs bulan lalu",
            delta_color="normal"
        )

    st.divider()

    # --- Mockup Image ---
    col_img, col_desc = st.columns([2, 3])
    with col_img:
        st.image("assets/logo.png", width=300)
    with col_desc:
        st.subheader("Visi SIMANTRA")
        st.markdown("""
        - **Objektivitas:** Mengurangi bias dalam pengambilan keputusan terkait karier ASN melalui analisis data yang komprehensif.
        - **Prediktif:** Memberikan rekomendasi proaktif untuk pengembangan karier dan perencanaan suksesi.
        - **Integritas:** Membangun sistem peringatan dini (*Early Warning System*) untuk mendeteksi potensi anomali dan menjaga integritas ASN.
        
        Silakan navigasi ke halaman lain melalui menu di sebelah kiri untuk menjelajahi fitur-fitur utama kami.
        """)
else:
    st.warning("Data ASN tidak ditemukan. Mohon jalankan `python create_dummy_data.py` terlebih dahulu.")

# --- Footer ---
st.markdown("---")
st.markdown("_TradeAI - MinusOne | SIMANTRA_")