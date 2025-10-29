import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils import load_data, load_anomaly_model, analyze_lhkpn_anomaly, create_network_graph, analyze_financial_health
import streamlit.components.v1 as components
import os

# --- Page Configuration ---
st.set_page_config(
    page_title="Early Warning System",
    page_icon="🚨",
    layout="wide"
)

# --- Header ---
st.title("🚨 Early Warning System")
st.markdown("Sistem Peringatan Dini untuk mendeteksi potensi anomali dan risiko integritas secara proaktif.")

# --- Load Data ---
df_lhkpn = load_data('data/data_lhkpn.csv')
df_relasi = load_data('data/data_relasi.csv')
df_asn = load_data('data/data_asn.csv')
df_slik = load_data('data/data_slik.csv') # Load the new SLIK data

if df_lhkpn.empty or df_relasi.empty or df_asn.empty or df_slik.empty:
    st.warning("Satu atau lebih file data tidak dapat dimuat. Pastikan semua file data ada di direktori 'data/'.")
else:
    # Merge ASN and SLIK data for easier access
    df_asn_merged = pd.merge(df_asn, df_slik, on='id_asn')

    # Create mappings for names
    asn_id_to_name = df_asn_merged.set_index('id_asn')['nama'].to_dict()
    asn_name_to_id = df_asn_merged.set_index('nama')['id_asn'].to_dict()

    # --- Sidebar for ASN Selection (Combined Filter) ---
    with st.sidebar:
        st.header("Filter ASN")
        # Get a list of all ASN names available in any of the datasets for EWS
        lhkpn_ids = set(df_lhkpn['id_asn'].unique())
        relasi_ids = set(pd.unique(df_relasi[['id_asn_sumber', 'id_asn_target']].values.ravel('K')))
        combined_ids = sorted(list(lhkpn_ids.union(relasi_ids)))
        
        available_names = sorted([asn_id_to_name.get(id) for id in combined_ids if asn_id_to_name.get(id) is not None])
        
        selected_name = st.selectbox(
            "Pilih Nama ASN untuk dianalisis:",
            options=available_names,
            key="ews_select"
        )
        selected_id = asn_name_to_id[selected_name]

    # --- Tabs for EWS Features ---
    tab1, tab2, tab3 = st.tabs(["🔍 Deteksi Anomali LHKPN", "🕸️ Analisis Konflik Kepentingan", "💰 Analisis Keuangan & SLIK"])

    # --- Tab 1: LHKPN Anomaly Detection ---
    with tab1:
        st.header("Deteksi Anomali Laporan Harta Kekayaan (LHKPN)")

        # Filter LHKPN data for the selected ASN
        df_asn_lhkpn = df_lhkpn[df_lhkpn['id_asn'] == selected_id].sort_values('tahun_lapor')

        if not df_asn_lhkpn.empty:
            with st.spinner("Menganalisis data LHKPN..."):
                model = load_anomaly_model()
                result_df, has_anomaly = analyze_lhkpn_anomaly(model, df_asn_lhkpn.copy())

            if has_anomaly:
                st.warning(f"**Peringatan:** Terdeteksi potensi anomali pada laporan kekayaan {selected_name}.")

            # Plot LHKPN history
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=result_df['tahun_lapor'],
                y=result_df['total_kekayaan'],
                mode='lines+markers',
                name='Total Kekayaan',
                line=dict(color='#4a90e2') # Primary Blue
            ))

            # Highlight anomalies
            anomalies = result_df[result_df['is_anomaly']]
            if not anomalies.empty:
                fig.add_trace(go.Scatter(
                    x=anomalies['tahun_lapor'],
                    y=anomalies['total_kekayaan'],
                    mode='markers',
                    marker=dict(color='#e74c3c', size=15, symbol='x'), # Soft Red
                    name='Anomali Terdeteksi'
                ))

            fig.update_layout(
                title=f"Riwayat Total Kekayaan {selected_name}",
                xaxis_title="Tahun Lapor",
                yaxis_title="Total Kekayaan (Rp)",
                yaxis_tickformat=',.0f',
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font_color='#dbeeff'
            )
            st.plotly_chart(fig, use_container_width=True)

            with st.expander("Lihat Data Detail dan Hasil Analisis"):
                # Display only the relevant columns
                display_cols = ['tahun_lapor', 'total_kekayaan', 'yoy_change', 'is_anomaly']
                st.dataframe(result_df[display_cols])
        else:
            st.info(f"Tidak ada data LHKPN yang ditemukan untuk {selected_name}.")

    # --- Tab 2: Social Network Analysis ---
    with tab2:
        st.header("Analisis Potensi Konflik Kepentingan")

        if selected_id not in relasi_ids:
            st.warning(f"Tidak ditemukan data relasi untuk {selected_name}.")
        else:
            with st.spinner("Membuat visualisasi jaringan..."):
                html_file_path = create_network_graph(df_relasi, selected_id, asn_id_to_name)
            
            try:
                with open(html_file_path, 'r', encoding='utf-8') as f:
                    source_code = f.read()
                components.html(source_code, height=610)
            except FileNotFoundError:
                st.error("Gagal membuat file visualisasi jaringan.")
            finally:
                # Clean up the temporary file
                if os.path.exists(html_file_path):
                    os.remove(html_file_path)
        
        st.info("""
        **Cara Membaca Graf:**
        - **Node Hijau:** ASN yang dipilih.
        - **Node Biru:** Relasi langsung (kolega, teman, dll).
        - **Garis Merah:** Menandakan relasi 'Transaksi Keuangan' (potensi risiko tinggi).
        - **Garis Oranye:** Menandakan relasi 'Keluarga' (potensi konflik kepentingan).
        """)

    # --- Tab 3: Financial & SLIK Analysis ---
    with tab3:
        st.header("Analisis Kewajaran Hutang dan Riwayat Kredit (SLIK)")
        
        # Get the full data for the selected ASN
        asn_financial_data = df_asn_merged[df_asn_merged['id_asn'] == selected_id]
        
        if asn_financial_data.empty:
            st.error(f"Data keuangan lengkap untuk {selected_name} tidak ditemukan.")
        else:
            asn_financial_data = asn_financial_data.iloc[0]
            atensi, reason = analyze_financial_health(asn_financial_data)
            
            # Display the results
            st.subheader(f"Hasil Analisis untuk: {selected_name}")
            
            gaji = asn_financial_data.get('gaji_bulanan', 0)
            hutang = asn_financial_data.get('total_hutang', 0)
            gaji_tahunan = gaji * 12
            rasio_hutang_gaji = hutang / gaji_tahunan if gaji_tahunan > 0 else 0

            col1, col2, col3 = st.columns(3)
            col1.metric("Gaji Bulanan", f"Rp {gaji:,.0f}")
            col2.metric("Total Hutang", f"Rp {hutang:,.0f}")
            col3.metric("Rasio Hutang/Gaji Tahunan", f"{rasio_hutang_gaji:.2f}x")

            if atensi:
                st.error(f"🔴 **Status: Perlu Atensi**\n\n**Alasan:** {reason}")
            else:
                st.success(f"🟢 **Status: Tidak Perlu Atensi**\n\n**Alasan:** {reason}")