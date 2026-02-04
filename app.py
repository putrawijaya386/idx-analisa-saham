import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px

# ======================
# KONFIGURASI HALAMAN
# ======================
st.set_page_config(
    page_title="Analisis Saham Indonesia",
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
.info-box {
    background-color: #111827;
    padding: 15px;
    border-radius: 12px;
}
</style>
""", unsafe_allow_html=True)

# ======================
# HEADER
# ======================
st.title("📊 Platform Analisis Saham Indonesia")
st.caption("Fundamental • Grafik • Seasonality • Edukasi Nasional")

# ======================
# INPUT SAHAM
# ======================
kode = st.text_input(
    "Masukkan kode saham (contoh: BBCA.JK, TLKM.JK, BBRI.JK)",
    value="BBCA.JK"
)

if kode:
    saham = yf.Ticker(kode)
    info = saham.info

    # ======================
    # METRIK UTAMA
    # ======================
    st.subheader("📌 Ringkasan Utama")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Harga Saham", f"Rp {info.get('currentPrice',0):,.0f}")
    c2.metric("ROE", f"{info.get('returnOnEquity',0)*100:.2f}%")
    c3.metric("PBV", f"{info.get('priceToBook',0):.2f}")
    c4.metric("PER", f"{info.get('trailingPE',0):.2f}")

    # ======================
    # EDUKASI NASIONAL
    # ======================
    with st.expander("📘 Penjelasan Istilah (Bahasa Sederhana)", expanded=True):
        st.markdown("""
        **ROE (Return on Equity)**  
        Mengukur seberapa efisien perusahaan menghasilkan laba dari modal pemilik.

        **PBV (Price to Book Value)**  
        Menunjukkan apakah harga saham mahal atau murah dibanding nilai bukunya.

        **PER (Price Earning Ratio)**  
        Menggambarkan berapa tahun laba yang dibutuhkan untuk menutup harga saham.

        👉 Umumnya:
        - ROE tinggi = bagus  
        - PBV < 1 = relatif murah  
        - PER wajar tergantung sektor
        """)

    st.divider()

    # ======================
    # DATA HISTORIS
    # ======================
    df = saham.history(period="5y")
    df['Return'] = df['Close'].pct_change()
    df['Month'] = df.index.month
    df['Quarter'] = df.index.to_period("Q").astype(str)

    # ======================
    # GRAFIK KUARTAL
    # ======================
    st.subheader("📊 Pergerakan Harga Per Kuartal")

    quarter_df = df.groupby("Quarter")["Close"].mean().reset_index()
    quarter_df["Change"] = quarter_df["Close"].diff()
    quarter_df["Color"] = quarter_df["Change"].apply(
        lambda x: "Naik" if x >= 0 else "Turun"
    )

    fig_quarter = px.bar(
        quarter_df,
        x="Quarter",
        y="Close",
        color="Color",
        title="Harga Rata-rata Saham per Kuartal",
        color_discrete_map={
            "Naik": "#16a34a",
            "Turun": "#dc2626"
        }
    )

    fig_quarter.update_layout(
        width=900,
        height=280,
        autosize=False,
        showlegend=False,
        margin=dict(l=30, r=30, t=50, b=30)
    )

    st.markdown('<div class="scroll-container">', unsafe_allow_html=True)
    st.plotly_chart(fig_quarter, config={"responsive": False})
    st.markdown('</div>', unsafe_allow_html=True)

    # ======================
    # SEASONALITY BULANAN
    # ======================
    st.subheader("📆 Seasonality (Pola Bulanan)")

    seasonality = (
        df.groupby("Month")["Return"]
        .mean()
        .reset_index()
    )

    seasonality["Month"] = seasonality["Month"].map({
        1:"Jan",2:"Feb",3:"Mar",4:"Apr",5:"Mei",6:"Jun",
        7:"Jul",8:"Agu",9:"Sep",10:"Okt",11:"Nov",12:"Des"
    })

    seasonality["Color"] = seasonality["Return"].apply(
        lambda x: "Positive" if x >= 0 else "Negative"
    )

    fig_season = px.bar(
        seasonality,
        x="Month",
        y="Return",
        color="Color",
        title="Rata-rata Return Bulanan (Seasonality)",
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
        showlegend=False,
        margin=dict(l=30, r=30, t=50, b=30)
    )

    st.markdown('<div class="scroll-container">', unsafe_allow_html=True)
    st.plotly_chart(fig_season, config={"responsive": False})
    st.markdown('</div>', unsafe_allow_html=True)

    # ======================
    # INSIGHT OTOMATIS
    # ======================
    best = seasonality.loc[seasonality["Return"].idxmax()]
    worst = seasonality.loc[seasonality["Return"].idxmin()]

    st.success(
        f"📈 Bulan terbaik historis: **{best['Month']}** "
        f"({best['Return']*100:.2f}%)"
    )

    st.warning(
        f"📉 Bulan terlemah historis: **{worst['Month']}** "
        f"({worst['Return']*100:.2f}%)"
    )

    st.caption("⚠️ Data bersifat historis, bukan rekomendasi beli/jual.")
