import pandas as pd
import streamlit as st
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.model_selection import train_test_split
import numpy as np
import plotly.graph_objects as go
import networkx as nx
from pyvis.network import Network
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from typing import Tuple, Any, Dict

# --- Data Loading Functions ---

@st.cache_data
def load_data(file_path: str) -> pd.DataFrame:
    """Loads data from a CSV file with caching."""
    try:
        return pd.read_csv(file_path)
    except FileNotFoundError:
        st.error(f"File tidak ditemukan: {file_path}. Pastikan file tersebut ada di direktori 'data/'. Jalankan 'python create_dummy_data.py' terlebih dahulu.")
        return pd.DataFrame()

# --- Machine Learning Model Loading Functions ---

@st.cache_resource
def load_classification_model() -> RandomForestClassifier:
    """
    Trains and caches a dummy RandomForestClassifier.
    In a real scenario, this would load a pre-trained model.
    """
    # Create dummy data for training
    X = np.random.rand(100, 2) * 100
    y = np.random.randint(0, 3, 100)
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X, y)
    return model

@st.cache_resource
def load_anomaly_model() -> IsolationForest:
    """
    Trains and caches a dummy IsolationForest model.
    """
    # Create dummy data for training
    X = np.random.randn(200, 1) * 50 + 1000
    model = IsolationForest(contamination=0.1, random_state=42)
    model.fit(X)
    return model

@st.cache_resource
def load_sentiment_analyzer() -> SentimentIntensityAnalyzer:
    """Loads and caches the VADER sentiment analyzer."""
    return SentimentIntensityAnalyzer()

# --- Business Logic & Analysis Functions ---

def get_talent_pool_prediction(model: RandomForestClassifier, kinerja: float, potensi: float) -> str:
    """Predicts talent pool based on performance and potential scores."""
    # The model is dummy, so we map its output to our labels
    pool_map = {0: 'Solid Contributor', 1: 'High Potential', 2: 'Low Performer'}
    # Create a 2D array for prediction
    prediction_input = np.array([[kinerja, potensi]])
    prediction = model.predict(prediction_input)
    return pool_map.get(prediction[0], 'N/A')

def analyze_lhkpn_anomaly(model: IsolationForest, df_asn_lhkpn: pd.DataFrame) -> Tuple[pd.DataFrame, bool]:
    """Analyzes LHKPN data for anomalies using a model and simple rules."""
    if df_asn_lhkpn.empty or len(df_asn_lhkpn) < 2:
        return df_asn_lhkpn, False

    # Rule-based anomaly: Year-over-Year increase > 150% (more robust)
    df_asn_lhkpn['yoy_change'] = df_asn_lhkpn['total_kekayaan'].pct_change()
    df_asn_lhkpn['rule_anomaly'] = df_asn_lhkpn['yoy_change'] > 1.5

    # Model-based anomaly on the Year-over-Year change for more robust detection
    # We need to handle the first NaN value
    yoy_values = df_asn_lhkpn[['yoy_change']].fillna(0).values
    df_asn_lhkpn['model_anomaly'] = model.predict(yoy_values) == -1

    # Combine anomalies: An anomaly is now only flagged if BOTH the rule and the model detect it.
    # This makes the system much more selective.
    # Let's stick with OR for now to catch either rule or model, but the data generation is better.
    df_asn_lhkpn['is_anomaly'] = df_asn_lhkpn['rule_anomaly'] & df_asn_lhkpn['model_anomaly']
    
    has_anomaly = df_asn_lhkpn['is_anomaly'].any()
    return df_asn_lhkpn, has_anomaly

def analyze_sentiment(analyzer: SentimentIntensityAnalyzer, text: str) -> Dict[str, Any]:
    """Analyzes sentiment of a given text using VADER."""
    scores = analyzer.polarity_scores(text)
    compound = scores['compound']
    
    if compound >= 0.05:
        sentiment = "Positif"
    elif compound <= -0.05:
        sentiment = "Negatif"
    else:
        sentiment = "Netral"
        
    return {"sentiment": sentiment, "score": compound}

def create_career_matrix_plot(asn_data: pd.Series) -> go.Figure:
    """Creates a dynamic stacked bar chart for career probability based on ASN data."""
    np.random.seed(asn_data['id_asn'])
    years = [2025, 2026, 2027] # Use integers for years
    
    # Base probabilities
    base_high = 10 + (asn_data['potensi'] - 50) / 2
    base_medium = 40
    base_low = 50 - base_high

    # Generate probabilities for 3 years with some randomness
    prob_high = [max(0, base_high + np.random.randint(-5, 5) + i*5) for i in range(3)]
    prob_medium = [max(0, base_medium + np.random.randint(-10, 10) - i*2) for i in range(3)]
    prob_low = [100 - ph - pm for ph, pm in zip(prob_high, prob_medium)]

    fig = go.Figure()
    # Updated color scheme for light theme
    fig.add_trace(go.Bar(y=years, x=prob_low, name='Rendah', orientation='h', marker_color='#FF6B6B')) # Light Red
    fig.add_trace(go.Bar(y=years, x=prob_medium, name='Sedang', orientation='h', marker_color='#FFD166')) # Light Yellow/Gold
    fig.add_trace(go.Bar(y=years, x=prob_high, name='Tinggi', orientation='h', marker_color='#06D6A0')) # Light Green/Teal

    fig.update_layout(
        barmode='stack',
        title_text='Matriks Probabilitas Waktu Promosi',
        xaxis_title="Probabilitas (%)",
        yaxis_title="Tahun",
        legend_title="Tingkat Probabilitas",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='#F0F2F6', # Match secondary background
        yaxis=dict(
            tickmode='array',
            tickvals=years,
            ticktext=[str(y) for y in years]
        )
    )
    return fig

def create_network_graph(df_relasi: pd.DataFrame, selected_asn_id: int, asn_map: Dict) -> str:
    """Creates and saves an interactive social network graph as an HTML file."""
    G = nx.from_pandas_edgelist(df_relasi, 'id_asn_sumber', 'id_asn_target', ['tipe_relasi'])

    # Create a subgraph centered on the selected ASN
    ego_graph = nx.ego_graph(G, selected_asn_id, radius=1)

    net = Network(
        height="600px",
        width="100%",
        bgcolor="#FFFFFF",
        font_color="black",
        notebook=True,
        directed=False,
        cdn_resources='remote'
    )
    
    # Define colors for risk
    risk_color_map = {
        'Transaksi Keuangan': 'red',
        'Keluarga': 'orange'
    }

    for node in ego_graph.nodes():
        nama = asn_map.get(node, f"ASN ID: {node}")
        title = f"Nama: {nama}"
        color = 'skyblue' if node != selected_asn_id else 'lime'
        net.add_node(node, label=nama, title=title, color=color, size=20 if node == selected_asn_id else 15)

    for edge in ego_graph.edges(data=True):
        sumber, target, data = edge
        tipe_relasi = data.get('tipe_relasi', 'N/A')
        color = risk_color_map.get(tipe_relasi, 'grey')
        width = 3 if color != 'grey' else 1
        sumber_nama = asn_map.get(sumber, f"ID: {sumber}")
        target_nama = asn_map.get(target, f"ID: {target}")
        edge_title = f"Relasi: {tipe_relasi}"
        net.add_edge(sumber, target, title=edge_title, color=color, width=width)

    net.set_options("""
    var options = {
      "physics": {
        "barnesHut": {
          "gravitationalConstant": -30000,
          "centralGravity": 0.1,
          "springLength": 150
        },
        "minVelocity": 0.75
      }
    }
    """)
    
    # Save to a temporary HTML file
    file_path = "network_graph.html"
    net.save_graph(file_path)
    return file_path
def analyze_financial_health(asn_financial_data: pd.Series) -> Tuple[bool, str]:
    """Analyzes financial data to determine if an ASN needs attention."""
    if asn_financial_data.empty:
        return False, "Data keuangan tidak ditemukan."

    gaji = asn_financial_data.get('gaji_bulanan', 0)
    hutang = asn_financial_data.get('total_hutang', 0)
    slik_flag = asn_financial_data.get('kualitas_debitur_buruk', 'N')

    gaji_tahunan = gaji * 12
    rasio_hutang_gaji = hutang / gaji_tahunan if gaji_tahunan > 0 else 0
    
    gaji_rendah_threshold = 8000000
    hutang_besar_threshold_ratio = 5.0

    gaji_tinggi = gaji > gaji_rendah_threshold
    hutang_besar = rasio_hutang_gaji > hutang_besar_threshold_ratio
    flag_kualitas_Y = slik_flag == 'Y'

    atensi = False
    reason = "Profil keuangan dan riwayat kredit dalam batas wajar."

    if (gaji_tinggi and not hutang_besar and flag_kualitas_Y) or \
       (gaji_tinggi and hutang_besar and flag_kualitas_Y) or \
       (not gaji_tinggi and hutang_besar and flag_kualitas_Y):
        atensi = True
        if not gaji_tinggi and hutang_besar:
            reason = "ASN memiliki gaji relatif rendah, namun total hutang sangat besar dan disertai riwayat kredit buruk (SLIK)."
        elif flag_kualitas_Y and hutang_besar:
            reason = "ASN memiliki total hutang yang besar dan riwayat kredit buruk (SLIK)."
        else:
            reason = "ASN memiliki riwayat kredit buruk (SLIK) meskipun rasio hutang terhadap gaji tergolong wajar."
            
    return atensi, reason