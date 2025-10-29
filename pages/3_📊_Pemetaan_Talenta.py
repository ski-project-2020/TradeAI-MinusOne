import streamlit as st
import pandas as pd
import plotly.express as px
from utils import load_data, load_classification_model

# --- Page Configuration ---
st.set_page_config(
    page_title="Pemetaan Talent Pool",
    page_icon="📊",
    layout="wide"
)

# --- Header ---
st.title("📊 Pemetaan Talent Pool")
st.markdown("Halaman ini memvisualisasikan pemetaan ASN ke dalam *talent pool* berdasarkan kinerja dan potensi menggunakan model klasifikasi.")

# --- Load Data and Model ---
df_asn = load_data('data/data_asn.csv')

if df_asn.empty:
    st.warning("Data ASN tidak dapat dimuat. Pastikan file 'data_asn.csv' ada.")
else:
    with st.spinner('Memuat model AI dan memproses data...'):
        model = load_classification_model()
        
        # Predict talent pool for each ASN
        # In a real scenario, features would be properly scaled and selected.
        # Here, we use the raw scores for demonstration.
        # Convert to numpy array to avoid feature name warning
        features = df_asn[['kinerja_2023', 'potensi']].values
        predictions = model.predict(features)
        pool_map = {0: 'Solid Contributor', 1: 'High Potential', 2: 'Low Performer'}
        df_asn['talent_pool'] = [pool_map.get(p, 'N/A') for p in predictions]

    # --- Main Content ---
    st.header("Visualisasi Sebaran Talenta ASN")

    # --- Sidebar for filtering ---
    with st.sidebar:
        st.header("Filter Data")
        talent_pool_options = ['Semua'] + sorted(df_asn['talent_pool'].unique())
        selected_pool = st.selectbox(
            "Filter berdasarkan Talent Pool:",
            options=talent_pool_options
        )

    # Filter data based on selection for both plot and dataframe
    if selected_pool == 'Semua':
        filtered_df = df_asn
    else:
        filtered_df = df_asn[df_asn['talent_pool'] == selected_pool]

    # --- Interactive Scatter Plot ---
    fig = px.scatter(
        filtered_df, # Use the filtered dataframe
        x='kinerja_2023',
        y='potensi',
        color='talent_pool',
        hover_name='nama',
        hover_data=['jabatan_sekarang', 'unit_kerja'],
        color_discrete_map={
            'High Potential': '#4a90e2',      # Primary Blue
            'Solid Contributor': '#87ceeb',   # Light Blue/Sky
            'Low Performer': '#e74c3c'       # Soft Red
        },
        title='Peta Kinerja vs Potensi ASN'
    )
    fig.update_layout(
        xaxis_title="Skor Kinerja",
        yaxis_title="Skor Potensi",
        legend_title="Talent Pool",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color='#dbeeff'
    )
    fig.update_traces(marker=dict(size=12, opacity=0.8))
    st.plotly_chart(fig, use_container_width=True)

    # --- Legend and Explanation ---
    with st.expander("ℹ️ Lihat Penjelasan Metodologi"):
        st.markdown("""
        #### Bagaimana Skor Dihitung?
        - **Skor Kinerja (Sumbu X):** Dalam prototipe ini, skor ini merupakan representasi nilai evaluasi kinerja tahunan.
        - **Skor Potensi (Sumbu Y):** Skor ini juga merupakan data dihitung dari berbagai faktor seperti hasil *assessment center*, rekam jejak, kompetensi manajerial dan potensi belajar.

        #### Definisi Talent Pool
        Model AI (`Random Forest`) mengklasifikasikan setiap ASN ke dalam salah satu dari tiga kategori berikut berdasarkan kombinasi skor kinerja dan potensi:

        - **<span style='color:#4a90e2;'>High Potential</span>:** ASN dengan kinerja dan potensi di atas rata-rata. Mereka adalah kandidat utama untuk promosi, suksesi, dan program akselerasi kepemimpinan.
        - **<span style='color:#87ceeb;'>Solid Contributor</span>:** ASN dengan kinerja yang solid dan konsisten. Mereka adalah tulang punggung organisasi yang andal pada peran mereka saat ini.
        - **<span style='color:#e74c3c;'>Low Performer</span>:** ASN yang menunjukkan kinerja dan/atau potensi di bawah ekspektasi. Mereka mungkin memerlukan intervensi pengembangan, pembinaan, atau rotasi.
        """, unsafe_allow_html=True)

    st.divider()

    # --- Filterable Dataframe ---
    st.header("Detail Data ASN")
    
    # Rename column for display
    display_df = filtered_df.rename(columns={'kinerja_2023': 'Kinerja'})
    display_df['nip'] = display_df['nip'].astype(str)
    st.dataframe(
        display_df[['nama', 'nip', 'jabatan_sekarang', 'unit_kerja', 'Kinerja', 'potensi', 'talent_pool']],
        use_container_width=True
    )