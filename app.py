import streamlit as st
import yfinance as yf
import plotly.express as px

st.set_page_config(
    page_title="Analisis Saham Indonesia",
    layout="wide"
)

# =====================
# CSS SCROLL HORIZONTAL
# =====================
st.markdown("""
<style>
.scroll-box {
    overflow-x: auto;
    overflow-y: hidden;
    width: 100%;
}
</style>
""", unsafe_allow_html=True)

st.title("📊 Platform Analisis Saham Indonesia")
st.caption("Fundamental • Skor • Laba Bersih • Seasonality 5 Tahun")

# =====================
# INPUT KODE (TANPA .JK)
# =====================
kode_input = st.text_input(
    "Masukkan kode saham (contoh: BBCA, TLKM, BBRI)",
    "BBCA"
).upper()

kode = f"{kode_input}.JK"

# =====================
# FUNGSI AMAN
# =====================
def safe_float(x, default=0.0):
    try:
        return float(x)
    except (TypeError, ValueError):
        return default

@st.cache_data
def load_data(kode):
    saham = yf.Ticker(kode)
    info = saham.info
    harga = saham.history(period="5y", interval="1mo")
    laba = saham.financials.T
    return info, harga, laba

# =====================
# MAIN
# =====================
if kode_input:
    try:
        info, df, laba = load_data(kode)

        # =====================
        # METRIK UTAMA
        # =====================
        harga_now = safe_float(info.get("currentPrice"))
        roe = safe_float(info.get("returnOnEquity")) * 100
        pbv = safe_float(info.get("priceToBook"))
        pe = safe_float(info.get("trailingPE"))

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Harga", f"Rp {harga_now:,.0f}")
        c2.metric("ROE", f"{roe:.2f}%")
        c3.metric("PBV", f"{pbv:.2f}")
        c4.metric("PER", f"{pe:.2f}")

        # =====================
        # SKOR SAHAM
        # =====================
        skor = 0
        if roe > 15: skor += 30
        elif roe > 10: skor += 20
        elif roe > 5: skor += 10

        if pbv < 1: skor += 25
        elif pbv < 2: skor += 15
        elif pbv < 3: skor += 5

        if 0 < pe < 15: skor += 25
        elif pe < 25: skor += 15
        elif pe < 40: skor += 5

        skor = min(skor, 100)
        st.subheader(f"⭐ Skor Saham: **{skor}/100**")

        # =====================
        # PENJELASAN
        # =====================
        with st.expander("📘 Penjelasan ROE, PBV, PER"):
            st.markdown("""
**ROE (Return on Equity)**  
Kemampuan perusahaan menghasilkan laba dari modal sendiri.

**PBV (Price to Book Value)**  
Menilai mahal/murah harga saham dibanding nilai buku.

**PER (Price to Earnings Ratio)**  
Berapa kali investor membayar laba perusahaan.
""")

        # =====================
        # LABA BERSIH 5 TAHUN
        # =====================
        kolom_laba = None
        for col in [
            "Net Income",
            "Net Income Common Stockholders"
        ]:
            if col in laba.columns:
                kolom_laba = col
                break

        if kolom_laba:
            laba_bersih = laba[kolom_laba].dropna().tail(5)
            laba_df = laba_bersih.reset_index()
            laba_df.columns = ["Tahun", "Laba Bersih"]
            laba_df["Status"] = laba_df["Laba Bersih"].apply(
                lambda x: "Positif" if x >= 0 else "Negatif"
            )

            fig_laba = px.bar(
                laba_df,
                x="Tahun",
                y="Laba Bersih",
                color="Status",
                title="💰 Laba Bersih Tahunan (5 Tahun)",
                color_discrete_map={
                    "Positif": "#16a34a",
                    "Negatif": "#dc2626"
                }
            )
            fig_laba.update_layout(height=300, showlegend=False)

            st.markdown('<div class="scroll-box">', unsafe_allow_html=True)
            st.plotly_chart(fig_laba, use_container_width=False)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.warning("Data laba bersih tidak tersedia.")

        # =====================
        # SEASONALITY
        # =====================
        if not df.empty and "Close" in df.columns:
            df["Return"] = df["Close"].pct_change()
            df["Month"] = df.index.month

            season = df.groupby("Month")["Return"].mean().reset_index()
            season["Month"] = season["Month"].map({
                1:"Jan",2:"Feb",3:"Mar",4:"Apr",5:"Mei",6:"Jun",
                7:"Jul",8:"Agu",9:"Sep",10:"Okt",11:"Nov",12:"Des"
            })
            season["Status"] = season["Return"].apply(
                lambda x: "Positif" if x >= 0 else "Negatif"
            )

            fig_season = px.bar(
                season,
                x="Month",
                y="Return",
                color="Status",
                title="📆 Seasonality Rata-rata Bulanan (5 Tahun)",
                color_discrete_map={
                    "Positif": "#16a34a",
                    "Negatif": "#dc2626"
                }
            )
            fig_season.update_layout(
                height=260,
                showlegend=False,
                yaxis_tickformat=".2%"
            )

            st.markdown('<div class="scroll-box">', unsafe_allow_html=True)
            st.plotly_chart(fig_season, use_container_width=False)
            st.markdown('</div>', unsafe_allow_html=True)

    except Exception as e:
        st.error("Data tidak ditemukan atau Yahoo Finance bermasalah.")
        st.caption(str(e))

st.caption("⚠️ Data edukatif, bukan rekomendasi beli/jual.")
