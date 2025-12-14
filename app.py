import streamlit as st
import pandas as pd
import numpy as np
import base64
from io import BytesIO
import plotly.express as px

st.set_page_config(page_title="SPK Metode SAW", page_icon="📊", layout="wide")

# === Fungsi untuk ubah logo jadi base64 agar tampil di CSS ===
def get_base64(file_path):
    with open(file_path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

logo_base64 = get_base64("logo.png")  # pastikan logo.png ada di folder yang sama

# === CSS Desain Bersih ===
page_bg = f"""
<style>
[data-testid="stAppViewContainer"] {{
    background: linear-gradient(135deg, #0d1b2a, #1b263b, #415a77);
    color: white;
    font-family: 'Poppins', sans-serif;
}}

.header {{
    position: relative;
    background: rgba(255, 255, 255, 0.08);
    border-radius: 25px;
    padding: 25px 40px;
    display: flex;
    align-items: center;
    backdrop-filter: blur(10px);
    box-shadow: 0px 4px 15px rgba(0,0,0,0.4);
    overflow: hidden;
    margin-bottom: 30px;
}}

/* === Logo tunggal, menyatu di background === */
.header::before {{
    content: "";
    position: absolute;
    left: 30px;
    top: 25px;
    width: 110px;
    height: 110px;
    background-image: url("data:image/png;base64,{logo_base64}");
    background-size: cover;
    background-position: center;
    border-radius: 50%;
    border: 2px solid #ffd60a;
    box-shadow: 0px 0px 15px rgba(255,214,10,0.4);
}}

.header-content {{
    margin-left: 170px;
}}

.section {{
    background: rgba(255, 255, 255, 0.15);
    border-radius: 20px;
    padding: 25px;
    margin-top: 20px;
    box-shadow: 0px 4px 15px rgba(0,0,0,0.3);
}}

h1, h2, h3 {{
    color: #ffd60a !important;
}}
button[data-baseweb="button"] {{
    background: linear-gradient(135deg, #ffd60a, #ffc300);
    color: #000 !important;
    font-weight: bold;
    border: none;
    border-radius: 10px;
}}
a {{
    color: #ffd60a;
    text-decoration: none;
    font-weight: bold;
}}
</style>
"""
st.markdown(page_bg, unsafe_allow_html=True)

# === Header (cukup satu kali) ===
st.markdown("""
<div class='header'>
    <div class='header-content'>
        <h1>📊 Sistem Pendukung Keputusan (SPK)</h1>
        <h3>Metode Simple Additive Weighting (SAW)</h3>
        <p><i>Universitas Bina Bangsa</i></p>
    </div>
</div>
""", unsafe_allow_html=True)

# === Input Data ===
st.markdown("<div class='section'>", unsafe_allow_html=True)
st.subheader("1️⃣ Input Data Alternatif dan Kriteria")
col1, col2 = st.columns(2)
with col1:
    jml_alternatif = st.number_input("Jumlah Alternatif", min_value=1, value=3)
with col2:
    jml_kriteria = st.number_input("Jumlah Kriteria", min_value=1, value=3)
st.markdown("</div>", unsafe_allow_html=True)

# === Input Kriteria ===
st.markdown("<div class='section'>", unsafe_allow_html=True)
st.subheader("2️⃣ Masukkan Nama Kriteria, Bobot, dan Tipe")
nama_kriteria, bobot, tipe = [], [], []
for i in range(jml_kriteria):
    c1, c2, c3 = st.columns(3)
    with c1:
        nama_kriteria.append(st.text_input(f"Nama Kriteria {i+1}", f"K{i+1}"))
    with c2:
        bobot.append(st.number_input(f"Bobot {i+1}", min_value=0.0, value=1.0))
    with c3:
        tipe.append(st.selectbox(f"Tipe {i+1}", ["Benefit", "Cost"]))
st.markdown("</div>", unsafe_allow_html=True)

# === Input Nilai Alternatif ===
st.markdown("<div class='section'>", unsafe_allow_html=True)
st.subheader("3️⃣ Masukkan Nilai Alternatif")
data = []
for i in range(jml_alternatif):
    row = []
    st.markdown(f"*Alternatif A{i+1}*")
    for j in range(jml_kriteria):
        row.append(st.number_input(f"Nilai A{i+1} - {nama_kriteria[j]}", min_value=0.0, value=0.0))
    data.append(row)
st.markdown("</div>", unsafe_allow_html=True)

# === Proses SAW ===
if st.button("🚀 Proses dan Tampilkan Hasil"):
    df = pd.DataFrame(data, columns=nama_kriteria, index=[f"A{i+1}" for i in range(jml_alternatif)])
    st.markdown("<div class='section'>", unsafe_allow_html=True)
    st.write("### 📋 Tabel Nilai Awal")
    st.dataframe(df)

    # Normalisasi
    norm_df = df.copy()
    for i in range(len(nama_kriteria)):
        if tipe[i] == "Benefit":
            norm_df[nama_kriteria[i]] = df[nama_kriteria[i]] / df[nama_kriteria[i]].max()
        else:
            norm_df[nama_kriteria[i]] = df[nama_kriteria[i]].min() / df[nama_kriteria[i]]

    st.write("### ⚙ Normalisasi")
    st.dataframe(norm_df)

    # Hasil SAW
    hasil = norm_df.dot(np.array(bobot))
    ranking = hasil.sort_values(ascending=False)
    st.write("### 🏆 Hasil Akhir (Rangking)")
    st.dataframe(ranking)

    # Grafik Visual
    fig = px.bar(
        x=ranking.index,
        y=ranking.values,
        color=ranking.index,
        title="Visualisasi Hasil Rangking",
        color_discrete_sequence=["#ffd60a", "#ffc300", "#003566"]
    )
    st.plotly_chart(fig, use_container_width=True)

    # Download hasil CSV
    output = BytesIO()
    ranking.to_csv(output)
    b64 = base64.b64encode(output.getvalue()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="hasil_rangking.csv">📥 Download Hasil Rangking (CSV)</a>'
    st.markdown(href, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)