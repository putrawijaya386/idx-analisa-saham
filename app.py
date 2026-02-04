import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px

# ======================
# CONFIG PAGE
# ======================
st.set_page_config(
    page_title="Analisis Saham Indonesia",
    layout="wide"
)

# ======================
# CSS ANTI LOMPAT
# ======================
st.markdown("""
<style>
.scroll-container {
    overflow-x: auto;
    overflow-y: hidden;
    white-space: nowrap;
    padding-bottom: 10px;
}
.metric-box {
    background-color: #111827;
    padding: 15px;
    border-radius: 12px;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

# ======================
# HEADER
# ======================
st.title("📊 Platform Analisis Saham Indonesia")
st.caption("Fundamental • Seasonality • Edukasi | Data Otomatis")

# ======================
# INPUT SAHAM
# ======================
kode = st.text_input("Masukkan kode saham (contoh: BBCA.JK)", "BBCA.JK")

if kode:

    saham = yf.Ticker(kode)
    info = saham.info

    # ======================
    # METRIK UTAMA
    # ======================
    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Harga", f"Rp {info.get('currentPrice',0):,.0f}")
    col2.metric("ROE", f"{info.get('returnOnEquity',0)*100:.2f}%")
    col3.metric("PBV", f"{info.get('priceToBook',0):.2f}")
    col4.metric("PER", f"{info.get('trailingPE',0):.2f}")

    st.divider()

    # ======================
    # EDUKASI
    # ======================
    with st.expander("📘 Penjelasan Istilah (Untuk Pemula)", expanded=True):
        st.markdown("""
        **ROE (Return on Equity)**  
        Mengukur kemampuan perusahaan menghasilkan laba dari modal pemegang saham.

        **PBV (Price to Book Value)**  
        Membandingkan harga saham dengan nilai buku perusahaan.

        **PER (Price Earning Ratio)**  
        Menunjukkan berapa tahun laba yang dibutuhkan untuk menutup harga saham.
        """)

    # ======================
    # DATA HISTORIS
    # ======================
    df = saham.history(period="5y")
    df['Return'] = df['Close'].pct_change()
    df['Month'] = df.index.month
    df['Quarter'] = df.index.to_period("Q").astype(str)

    # ======================
    # QUARTERLY BAR CHART
    # ======================
    quarter_df = df.groupby('Quarter')['Close'].mean().reset_index()

    fig_quarter = px.bar(
        quarter_df,
        x="Quarter",
        y="Close",
        title="📊 Harga Rata-rata Per Kuartal",
        height=300
    )

    fig_quarter.update_layout(
        autosize=False,
        margin=dict(l=20, r=20, t=50, b=20)
    )

    st.markdown('<div class="scroll-container">', unsafe_allow_html=True)
    st.plotly_chart(fig_quarter, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ======================
    # SEASONALITY
    # ======================
    seasonality = (
        df.groupby('Month')['Return']
        .mean()
        .reset_index()
    )

    seasonality['Month'] = seasonality['Month'].map({
        1:'Jan',2:'Feb',3:'Mar',4:'Apr',5:'Mei',6:'Jun',
        7:'Jul',8:'Agu',9:'Sep',10:'Okt',11:'Nov',12:'Des'
    })

    fig_season = px.bar(
        seasonality,
        x="Month",
        y="Return",
        title="📆 Seasonality Return Bulanan",
        height=280
    )

    fig_season.update_layout(
        yaxis_tickformat=".2%",
        autosize=False,
        margin=dict(l=20, r=20, t=50, b=20)
    )

    st.markdown('<div class="scroll-container">', unsafe_allow_html=True)
    st.plotly_chart(fig_season, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ======================
    # INSIGHT OTOMATIS
    # ======================
    best_month = seasonality.loc[seasonality['Return'].idxmax()]
    worst_month = seasonality.loc[seasonality['Return'].idxmin()]

    st.success(
        f"📈 Bulan terbaik historis: **{best_month['Month']}** "
        f"({best_month['Return']*100:.2f}%)"
    )

    st.warning(
        f"📉 Bulan terlemah historis: **{worst_month['Month']}** "
        f"({worst_month['Return']*100:.2f}%)"
    )
