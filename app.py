import streamlit as st
import pandas as pd
import numpy as np
import base64
from io import BytesIO
import plotly.express as px

# =========================
# Page Config
# =========================
st.set_page_config(
    page_title="SPK SAW • Modern UI",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =========================
# Helpers
# =========================
def get_base64(file_path: str) -> str:
    with open(file_path, "rb") as f:
        return base64.b64encode(f.read()).decode()

def normalize_saw(df: pd.DataFrame, types: list[str]) -> pd.DataFrame:
    norm = df.copy().astype(float)
    for col, t in zip(df.columns, types):
        if t.lower() == "benefit":
            m = df[col].max()
            norm[col] = df[col] / m if m != 0 else 0
        else:  # cost
            mn = df[col].min()
            # handle division by zero / inf
            norm[col] = (mn / df[col]).replace([np.inf, -np.inf], 0).fillna(0)
    return norm

def to_csv_download(series: pd.Series, filename: str = "hasil_rangking.csv"):
    output = BytesIO()
    series.to_csv(output, header=["Skor"])
    b64 = base64.b64encode(output.getvalue()).decode()
    return f'<a class="dl" href="data:file/csv;base64,{b64}" download="{filename}">⬇️ Download Hasil Rangking (CSV)</a>'

# =========================
# Load logo
# =========================
try:
    logo_base64 = get_base64("logo.png")
except Exception:
    logo_base64 = None

# =========================
# Modern CSS (FIX sidebar input putih sampai ke DALAM)
# =========================
accent = "#7C3AED"

page_css = f"""
<style>
/* ===== App Background ===== */
[data-testid="stAppViewContainer"] {{
  background: radial-gradient(1200px 700px at 10% 10%, rgba(124,58,237,0.35), transparent 60%),
              radial-gradient(900px 600px at 90% 20%, rgba(34,197,94,0.25), transparent 55%),
              radial-gradient(800px 500px at 60% 90%, rgba(59,130,246,0.22), transparent 60%),
              linear-gradient(135deg, #0b1220 0%, #0b1220 40%, #070b14 100%);
  color: #E5E7EB;
  font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, "Apple Color Emoji","Segoe UI Emoji";
}}

/* Hide Streamlit default footer/menu */
#MainMenu {{visibility: hidden;}}
footer {{visibility: hidden;}}
header {{visibility: hidden;}}

/* ===== Sidebar Background ===== */
[data-testid="stSidebar"] {{
  background: linear-gradient(180deg, #0f172a, #020617) !important;
  border-right: 1px solid rgba(255,255,255,0.08);
}}
[data-testid="stSidebar"] * {{
  color: #E5E7EB !important;
}}
[data-testid="stSidebar"] .block-container {{
  padding-top: 1rem;
}}

/* =========================================================
   FIX PUTIH NUMBER INPUT (SUPER OVERRIDE)
   Streamlit number_input = BaseWeb
   Putihnya biasanya nempel di wrapper dalemnya.
   ========================================================= */

/* 1) Target container input baseweb */
[data-testid="stSidebar"] div[data-baseweb="input"] {{
  background: rgba(255,255,255,0.06) !important;
  border: 1px solid rgba(255,255,255,0.16) !important;
  border-radius: 14px !important;
  box-shadow: 0 10px 22px rgba(0,0,0,0.25) !important;
}}

/* 2) Paksa semua child wrapper jangan punya background putih */
[data-testid="stSidebar"] div[data-baseweb="input"] > div {{
  background: transparent !important;
}}
[data-testid="stSidebar"] div[data-baseweb="input"] div {{
  background: transparent !important;
}}

/* 3) Ada versi yang pakai base-input */
[data-testid="stSidebar"] div[data-baseweb="base-input"] {{
  background: transparent !important;
}}
[data-testid="stSidebar"] div[data-baseweb="base-input"] > div {{
  background: transparent !important;
}}

/* 4) Kadang stepper dibungkus role="group" */
[data-testid="stSidebar"] div[role="group"] {{
  background: transparent !important;
}}

/* 5) Field input: transparan + warna teks */
[data-testid="stSidebar"] div[data-baseweb="input"] input {{
  background: transparent !important;
  color: #E5E7EB !important;
  font-weight: 800 !important;
  font-size: 16px !important;
  caret-color: {accent} !important;
}}

/* 6) Placeholder */
[data-testid="stSidebar"] div[data-baseweb="input"] input::placeholder {{
  color: rgba(229,231,235,0.55) !important;
}}

/* 7) Tombol stepper (Increase/Decrease) */
[data-testid="stSidebar"] button[aria-label="Decrease"],
[data-testid="stSidebar"] button[aria-label="Increase"] {{
  background: rgba(255,255,255,0.08) !important;
  border: 1px solid rgba(255,255,255,0.14) !important;
  border-radius: 10px !important;
  color: #E5E7EB !important;
}}

/* Icon +/- kadang SVG terpisah */
[data-testid="stSidebar"] button[aria-label="Decrease"] svg,
[data-testid="stSidebar"] button[aria-label="Increase"] svg {{
  fill: #E5E7EB !important;
}}

/* 8) Hover stepper */
[data-testid="stSidebar"] button[aria-label="Decrease"]:hover,
[data-testid="stSidebar"] button[aria-label="Increase"]:hover {{
  background: rgba(124,58,237,0.25) !important;
  border-color: rgba(124,58,237,0.45) !important;
}}

/* 9) Focus glow */
[data-testid="stSidebar"] div[data-baseweb="input"]:focus-within {{
  border-color: rgba(124,58,237,0.55) !important;
  box-shadow: 0 0 0 3px rgba(124,58,237,0.25) !important;
}}

/* ===== Cards ===== */
.card {{
  background: rgba(255,255,255,0.06);
  border: 1px solid rgba(255,255,255,0.10);
  border-radius: 18px;
  padding: 18px 18px;
  box-shadow: 0 10px 25px rgba(0,0,0,0.25);
  backdrop-filter: blur(12px);
}}
.card + .card {{ margin-top: 14px; }}

/* ===== Hero ===== */
.hero {{
  position: relative;
  overflow: hidden;
  padding: 22px 24px;
  border-radius: 22px;
  border: 1px solid rgba(255,255,255,0.12);
  background: linear-gradient(135deg, rgba(124,58,237,0.20), rgba(34,197,94,0.12));
  box-shadow: 0 14px 35px rgba(0,0,0,0.32);
}}
.hero h1 {{
  margin: 0;
  font-size: 30px;
  letter-spacing: -0.5px;
}}
.hero p {{
  margin: 6px 0 0 0;
  color: rgba(229,231,235,0.82);
}}
.badge {{
  display: inline-flex;
  gap: 8px;
  align-items: center;
  padding: 6px 10px;
  border-radius: 999px;
  background: rgba(0,0,0,0.25);
  border: 1px solid rgba(255,255,255,0.12);
  font-size: 12px;
  color: rgba(229,231,235,0.85);
}}

/* ===== Button ===== */
button[kind="primary"], .stButton > button {{
  background: linear-gradient(135deg, {accent}, #4F46E5) !important;
  color: white !important;
  border: 0 !important;
  border-radius: 12px !important;
  padding: 0.65rem 1rem !important;
  font-weight: 800 !important;
}}
.stButton > button:hover {{
  filter: brightness(1.08);
  transform: translateY(-1px);
  transition: 0.15s ease;
}}

/* ===== Download link ===== */
a.dl {{
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 14px;
  border-radius: 12px;
  background: rgba(255,255,255,0.08);
  border: 1px solid rgba(255,255,255,0.14);
  color: #E5E7EB !important;
  text-decoration: none;
  font-weight: 800;
}}
a.dl:hover {{
  border-color: rgba(255,255,255,0.25);
  background: rgba(255,255,255,0.10);
}}

/* ===== Text ===== */
h2, h3 {{
  color: #F3F4F6 !important;
  letter-spacing: -0.3px;
}}
.small-muted {{
  color: rgba(229,231,235,0.75);
  font-size: 13px;
}}
hr {{
  border: none;
  height: 1px;
  background: rgba(255,255,255,0.10);
  margin: 14px 0;
}}

/* ===== Dataframe ===== */
[data-testid="stDataFrame"] {{
  border-radius: 14px;
  overflow: hidden;
  border: 1px solid rgba(255,255,255,0.10);
}}
</style>
"""
st.markdown(page_css, unsafe_allow_html=True)

# =========================
# Sidebar (Logo TOP + Controls)
# =========================
with st.sidebar:
    if logo_base64:
        st.markdown(
            f"""
            <div style="display:flex;justify-content:center;margin:6px 0 18px 0;">
                <img src="data:image/png;base64,{logo_base64}"
                     style="width:64px;height:64px;border-radius:999px;
                            border:2px solid {accent};
                            box-shadow:0 0 14px rgba(124,58,237,0.55);" />
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("### ⚙️ Pengaturan")
    st.caption("Atur jumlah alternatif & kriteria, lalu input data di tab utama.")

    jml_alternatif = st.number_input("Jumlah Alternatif", min_value=1, value=3, step=1)
    jml_kriteria = st.number_input("Jumlah Kriteria", min_value=1, value=3, step=1)

    st.markdown("---")
    st.markdown("### 🎛️ Opsi")
    auto_normalize_weight = st.toggle("Normalisasi bobot otomatis (jika total ≠ 1)", value=True)
    show_tables = st.toggle("Tampilkan tabel perhitungan lengkap", value=True)

# =========================
# Header / Hero
# =========================
colA, colB = st.columns([0.75, 0.25], vertical_alignment="center")
with colA:
    st.markdown(
        """
        <div class="hero">
          <div class="badge">📊 SAW • Sistem Pendukung Keputusan</div>
          <h1>SPK Metode Simple Additive Weighting (SAW)</h1>
          <p>Input data → normalisasi → pembobotan → ranking.</p>
        </div>
        """,
        unsafe_allow_html=True
    )
with colB:
    st.markdown(
        """
        <div class="card">
          <div style="font-weight:800; font-size:14px;">📌 Tips</div>
          <div class="small-muted">• Bobot idealnya total = 1</div>
          <div class="small-muted">• Benefit: makin besar makin baik</div>
          <div class="small-muted">• Cost: makin kecil makin baik</div>
        </div>
        """,
        unsafe_allow_html=True
    )

st.write("")

# =========================
# Tabs
# =========================
tab_input, tab_hasil, tab_about = st.tabs(["🧾 Input", "🏁 Hasil", "ℹ️ Info"])

if "results" not in st.session_state:
    st.session_state.results = None

# =========================
# INPUT TAB
# =========================
with tab_input:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("## 1) Kriteria (Nama, Bobot, Tipe)")
    st.markdown('<div class="small-muted">Gunakan form agar input stabil (tidak refresh tiap field).</div>', unsafe_allow_html=True)
    st.write("")

    with st.form("form_kriteria", clear_on_submit=False):
        nama_kriteria, bobot, tipe = [], [], []
        for i in range(int(jml_kriteria)):
            c1, c2, c3 = st.columns([0.50, 0.25, 0.25])
            with c1:
                nama_kriteria.append(st.text_input(f"Nama Kriteria {i+1}", value=f"K{i+1}"))
            with c2:
                bobot.append(st.number_input(f"Bobot {i+1}", min_value=0.0, value=1.0, step=0.1))
            with c3:
                tipe.append(st.selectbox(f"Tipe {i+1}", ["Benefit", "Cost"], index=0))

        st.form_submit_button("✅ Simpan Kriteria")

    st.markdown("</div>", unsafe_allow_html=True)

    st.write("")

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("## 2) Nilai Alternatif")
    st.markdown('<div class="small-muted">Masukkan nilai untuk setiap alternatif pada tiap kriteria.</div>', unsafe_allow_html=True)
    st.write("")

    with st.form("form_alternatif", clear_on_submit=False):
        data = []
        for i in range(int(jml_alternatif)):
            st.markdown(f"**Alternatif A{i+1}**")
            cols = st.columns(min(int(jml_kriteria), 4))
            row = []
            for j in range(int(jml_kriteria)):
                with cols[j % len(cols)]:
                    row.append(
                        st.number_input(
                            f"A{i+1} • {nama_kriteria[j]}",
                            min_value=0.0,
                            value=0.0,
                            step=1.0,
                            key=f"val_{i}_{j}"
                        )
                    )
                if (j + 1) % len(cols) == 0 and (j + 1) < int(jml_kriteria):
                    cols = st.columns(min(int(jml_kriteria) - (j + 1), 4))
            data.append(row)

        submitted_data = st.form_submit_button("🚀 Proses SAW")

    st.markdown("</div>", unsafe_allow_html=True)

    if submitted_data:
        df = pd.DataFrame(
            data,
            columns=nama_kriteria,
            index=[f"A{i+1}" for i in range(int(jml_alternatif))]
        )

        w = np.array(bobot, dtype=float)
        w_sum = w.sum()

        notes = []
        if w_sum == 0:
            notes.append("⚠️ Total bobot = 0. Setidaknya ada bobot > 0.")
            st.session_state.results = None
        else:
            if not np.isclose(w_sum, 1.0):
                if auto_normalize_weight:
                    w = w / w_sum
                    notes.append(f"ℹ️ Bobot dinormalisasi otomatis (total awal {w_sum:.4f} → 1.0).")
                else:
                    notes.append(f"⚠️ Total bobot = {w_sum:.4f} (disarankan 1.0).")

            norm_df = normalize_saw(df, tipe)
            skor = norm_df.dot(w)
            ranking = skor.sort_values(ascending=False)

            st.session_state.results = {
                "df": df,
                "norm": norm_df,
                "weights": w,
                "types": tipe,
                "ranking": ranking
            }

        for n in notes:
            st.info(n)

        st.success("Selesai diproses! Buka tab **🏁 Hasil** untuk melihat output.")

# =========================
# RESULT TAB
# =========================
with tab_hasil:
    res = st.session_state.results
    if res is None:
        st.warning("Belum ada hasil. Silakan isi input pada tab **🧾 Input** lalu klik **🚀 Proses SAW**.")
    else:
        ranking = res["ranking"]
        df = res["df"]
        norm_df = res["norm"]
        w = res["weights"]

        top_alt = ranking.index[0]
        top_score = float(ranking.iloc[0])

        m1, m2, m3 = st.columns(3)
        m1.metric("🏆 Alternatif Terbaik", top_alt)
        m2.metric("⭐ Skor Tertinggi", f"{top_score:.6f}")
        m3.metric("📌 Jumlah Alternatif", f"{len(ranking)}")

        st.write("")

        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("## 🏁 Rangking Akhir")
        rank_df = ranking.reset_index()
        rank_df.columns = ["Alternatif", "Skor"]
        rank_df["Peringkat"] = np.arange(1, len(rank_df) + 1)

        def highlight_top(row):
            if row["Alternatif"] == top_alt:
                return ["background-color: rgba(34,197,94,0.18)"] * len(row)
            return [""] * len(row)

        st.dataframe(
            rank_df[["Peringkat", "Alternatif", "Skor"]].style.apply(highlight_top, axis=1),
            use_container_width=True
        )

        st.markdown(to_csv_download(ranking), unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        st.write("")

        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("## 📊 Visualisasi Skor")
        fig = px.bar(
            x=ranking.index,
            y=ranking.values,
            title="Visualisasi Hasil Rangking",
            labels={"x": "Alternatif", "y": "Skor"},
        )
        fig.update_layout(
            height=420,
            margin=dict(l=10, r=10, t=60, b=10),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#E5E7EB"),
            title_font=dict(size=18),
        )
        fig.update_traces(marker_line_width=0)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

        if show_tables:
            st.write("")
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown("## 🧮 Detail Perhitungan")
            st.markdown('<div class="small-muted">Tabel nilai awal, normalisasi, dan bobot yang dipakai.</div>', unsafe_allow_html=True)

            st.markdown("### 📋 Tabel Nilai Awal")
            st.dataframe(df, use_container_width=True)

            st.markdown("### ⚙️ Normalisasi")
            st.dataframe(norm_df, use_container_width=True)

            st.markdown("### 🧷 Bobot (yang digunakan)")
            w_df = pd.DataFrame({"Kriteria": df.columns, "Bobot": w, "Tipe": res["types"]})
            st.dataframe(w_df, use_container_width=True)

            st.markdown("</div>", unsafe_allow_html=True)

# =========================
# ABOUT TAB
# =========================
with tab_about:
    st.markdown(
        """
        <div class="card">
          <h2>ℹ️ Tentang Aplikasi</h2>
          <p class="small-muted">
            Aplikasi ini menghitung SPK menggunakan metode SAW:
            normalisasi (Benefit/Cost) → pembobotan → penjumlahan skor → ranking.
          </p>
          <hr/>
          <div class="small-muted">
            <b>Benefit</b>: nilai dibagi maksimum.<br/>
            <b>Cost</b>: minimum dibagi nilai.
          </div>
        </div>
        """,
        unsafe_allow_html=True
    )
