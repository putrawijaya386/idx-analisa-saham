import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(
    page_title="IDX Smart Analyzer",
    page_icon="📊",
    layout="wide"
)

st.markdown("""
<style>
body {
    background-color: #0e1117;
}
.block-container {
    padding-top: 2rem;
}
</style>
""", unsafe_allow_html=True)

st.title("📊 IDX Smart Analyzer")
st.caption("Platform analisa saham Indonesia • Sederhana • Edukatif • Real-time")

st.markdown("---")

st.subheader("🔎 Cari Saham Indonesia")
kode = st.text_input(
    "Masukkan kode saham (contoh: BBCA, BBRI, TLKM)",
    placeholder="BBCA"
)

if kode:
    kode = kode.upper() + ".JK"

    try:
        saham = yf.Ticker(kode)
        info = saham.info

        st.success(f"Data ditemukan untuk {kode}")

        col1, col2, col3 = st.columns(3)

        col1.metric("💰 Harga Saat Ini", f"Rp {info.get('currentPrice', 'N/A')}")
        col2.metric("📈 PER", info.get("trailingPE", "N/A"))
        col3.metric("📊 PBV", info.get("priceToBook", "N/A"))

        st.markdown("### 📑 Ringkasan Fundamental")

        data = {
            "Market Cap": info.get("marketCap"),
            "ROE": info.get("returnOnEquity"),
            "Total Hutang": info.get("totalDebt"),
            "Cash Flow": info.get("operatingCashflow"),
            "Laba Bersih": info.get("netIncomeToCommon")
        }

        df = pd.DataFrame.from_dict(data, orient="index", columns=["Nilai"])
        st.table(df)

        st.markdown("### 🎓 Edukasi Singkat")
        st.info(
            "PER dan PBV rendah belum tentu bagus. "
            "Perhatikan juga ROE, arus kas, dan kemampuan bayar hutang."
        )

    except Exception as e:
        st.error("Data saham tidak ditemukan atau sedang bermasalah.")
