import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px

# ======================
# KONFIGURASI HALAMAN
# ======================
st.set_page_config(
    page_title="Platform Analisis Saham Indonesia",
    layout="wide"
)

# ======================
# CSS (ANTI HILANG SAAT SCROLL)
# ======================
st.markdown("""
<style>
.scroll-container {
    overflow-x: auto;
    overflow-y: hidden;
    width: 100%;
}
.score-box {
    background-color: #0f172a;
    padding: 20px;
    border-radius: 14px;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

# ======================
# HEADER
# ======================
st.title("📊 Platform Analisis Saham Indonesia")
st.caption("Fundamental • Skor Saham • Pembanding • Seasonality • Edukasi Nasional")

# ======================
# INPUT SAHAM
# ======================
colA, colB = st.columns(2)

with colA:
    kode_1 = st.text_input("Kode Saham Utama (contoh: BBCA.JK)", "BBCA.JK")

with colB:
    kode_2 = st.text_input("Bandingkan Dengan (opsional)", "BBRI.JK")

# ======================
# FUNGSI AMBIL DATA
# ======================
def get_data(kode):
    saham = yf.Ticker(kode)
    info = saham.info
    hist = saham.history(period="5y")
    return info, hist

# ======================
# FUNGSI SKOR SAHAM (0–100)
# ======================
def hitung_skor(info):
    skor = 0

    roe = info.get("returnOnEquity", 0)
    pbv = info.get("priceToBook", 0)
    pe = info.get("trailingPE", 0)
    debt = info.get("debtToEquity", 0)

    if roe > 0.15: skor += 30
    elif roe > 0.10: skor += 20
    elif roe > 0.05: skor += 10

    if pbv < 1: skor += 25
    elif pbv < 2: skor += 15
    elif pbv < 3: skor += 5

    if pe > 0 and pe < 15: skor += 25
    elif pe < 25: skor += 15
    elif pe < 40: skor += 5

    if debt < 1: skor += 20
    elif debt < 2: skor += 10

    return min(skor, 100)

# ======================
# AMBIL DATA SAHAM UTAMA
# ======================
if kode_1:
    info1, df1 = get_data(kode_1)
    skor1 = hitung_skor(info1)

    st.subheader("📌 Ringkasan Saham Utama")

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Harga", f"Rp {info1.get('currentPrice',0):,.0f}")
    c2.metric("ROE", f"{info1.get('returnOnEquity',0)*100:.2f}%")
    c3.metric("PBV", f"{info1.get('priceToBook',0):.2f}")
    c4.metric("PER", f"{info1.get('trailingPE',0):.2f}")
    c5.metric("Skor Saham", f"{skor1}/100")

    # ======================
    # EDUKASI SKOR
    # ======================
    with st.expander("📘 Cara Membaca Skor Saham"):
        st.markdown("""
        **80–100** : Sangat kuat  
        **60–79**  : Layak dipertimbangkan  
        **40–59**  : Cukup / netral  
        **<40**    : Perlu hati-hati  

        Skor dihitung dari **ROE, PBV, PER, dan Hutang**.
        """)

    # ======================
    # DATA HISTORIS
    # ======================
    df1['Return'] = df1['Close'].pct_change()
    df1['Month'] = df1.index.month
    df1['Quarter'] = df1.index.to_period("Q").astype(str)

    # ======================
    # SEASONALITY
    # ======================
    season = df1.groupby("Month")["Return"].mean().reset_index()
    season["Month"] = season["Month"].map({
        1:"Jan",2:"Feb",3:"Mar",4:"Apr",5:"Mei",6:"Jun",
        7:"Jul",8:"Agu",9:"Sep",10:"Okt",11:"Nov",12:"Des"
    })
    season["Color"] = season["Return"].apply(lambda x: "Positive" if x >= 0 else "Negative")

    fig_season = px.bar(
        season,
        x="Month",
        y="Return",
        color="Color",
        title="📆 Seasonality Return Bulanan",
        color_discrete_map={
            "Positive": "#16a34a",
            "Negative": "#dc2626"
        }
    )

    fig_season.update_layout(
        width=900,
        height=260,
        autosize=False,
        yaxis_tickformat=".2%",
        showlegend=False
    )

    st.markdown('<div class="scroll-container">', unsafe_allow_html=True)
    st.plotly_chart(fig_season, config={"responsive": False})
    st.markdown('</div>', unsafe_allow_html=True)

# ======================
# PERBANDINGAN SAHAM
# ======================
if kode_2:
    info2, _ = get_data(kode_2)
    skor2 = hitung_skor(info2)

    st.subheader("⚖️ Perbandingan Saham")

    banding = pd.DataFrame({
        "Metrik": ["Harga", "ROE", "PBV", "PER", "Skor"],
        kode_1: [
            info1.get("currentPrice",0),
            info1.get("returnOnEquity",0)*100,
            info1.get("priceToBook",0),
            info1.get("trailingPE",0),
            skor1
        ],
        kode_2: [
            info2.get("currentPrice",0),
            info2.get("returnOnEquity",0)*100,
            info2.get("priceToBook",0),
            info2.get("trailingPE",0),
            skor2
        ]
    })

    st.dataframe(banding, use_container_width=True)

    if skor1 > skor2:
        st.success(f"📈 {kode_1} lebih unggul secara fundamental")
    elif skor1 < skor2:
        st.warning(f"📉 {kode_2} lebih unggul secara fundamental")
    else:
        st.info("⚖️ Keduanya relatif seimbang")

st.caption("⚠️ Data historis & edukatif, bukan rekomendasi beli/jual.")
