import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px

# =========================
# CONFIG
# =========================
st.set_page_config(
    page_title="Analisa Saham Indonesia",
    layout="wide"
)

# =========================
# HELPER
# =========================
def rupiah(value):
    if value is None:
        return "-"
    if value >= 1e12:
        return f"Rp {value/1e12:.1f} T"
    if value >= 1e9:
        return f"Rp {value/1e9:.1f} M"
    return f"Rp {value:,.0f}"

# =========================
# HEADER
# =========================
st.title("📊 Platform Analisa Saham Indonesia")
st.caption(
    "Fundamental • Edukasi • Laporan Keuangan • Seasonality\n\n"
    "Dirancang agar **mudah dipahami oleh masyarakat Indonesia**"
)

st.divider()

# =========================
# INPUT
# =========================
kode = st.text_input(
    "Masukkan kode saham (contoh: BBRI, BBCA, TLKM)",
    placeholder="BBRI"
)

if kode:
    try:
        ticker = yf.Ticker(f"{kode}.JK")
        info = ticker.info

        st.success(f"Data ditemukan untuk **{kode}.JK**")

        # =========================
        # HARGA
        # =========================
        st.subheader("💰 Harga Saham Saat Ini")
        st.metric(
            label="Harga",
            value=f"Rp {info.get('currentPrice', 0):,.0f}"
        )

        st.divider()

        # =========================
        # RASIO UTAMA
        # =========================
        st.subheader("📌 Rasio Fundamental Utama")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("PER", f"{info.get('trailingPE', 0):.2f}x")
            st.caption(
                "**PER (Price Earnings Ratio)**\n\n"
                "Mengukur berapa kali investor membayar laba perusahaan.\n\n"
                "📍 PER rendah → saham relatif murah\n"
                "📍 PER tinggi → saham sudah mahal"
            )

        with col2:
            st.metric("PBV", f"{info.get('priceToBook', 0):.2f}x")
            st.caption(
                "**PBV (Price to Book Value)**\n\n"
                "Membandingkan harga saham dengan nilai buku perusahaan.\n\n"
                "📍 PBV < 1 → undervalued\n"
                "📍 PBV > 3 → perlu hati-hati"
            )

        with col3:
            roe = info.get("returnOnEquity", 0) * 100
            st.metric("ROE", f"{roe:.1f}%")
            st.caption(
                "**ROE (Return on Equity)**\n\n"
                "Mengukur kemampuan perusahaan menghasilkan laba dari modal.\n\n"
                "📍 ROE > 15% → perusahaan sehat\n"
                "📍 ROE rendah → manajemen kurang efisien"
            )

        st.divider()

        # =========================
        # RINGKASAN FUNDAMENTAL
        # =========================
        st.subheader("📘 Ringkasan Fundamental Perusahaan")

        data_fundamental = {
            "Market Cap": rupiah(info.get("marketCap")),
            "Laba Bersih": rupiah(info.get("netIncomeToCommon")),
            "Total Hutang": rupiah(info.get("totalDebt")),
            "Cash Flow Operasional": rupiah(info.get("operatingCashflow")),
        }

        st.table(pd.DataFrame(data_fundamental.items(), columns=["Item", "Nilai"]))

        st.divider()

        # =========================
        # LAPORAN KEUANGAN KUARTALAN
        # =========================
        st.subheader("📊 Laporan Keuangan Kuartalan")

        quarterly = ticker.quarterly_financials.T
        quarterly["Quarter"] = quarterly.index.astype(str)

        if "Net Income" in quarterly.columns:
            fig_q = px.bar(
                quarterly,
                x="Quarter",
                y="Net Income",
                title="Laba Bersih Per Kuartal",
                labels={"Net Income": "Laba Bersih"}
            )
            st.plotly_chart(fig_q, use_container_width=True)
        else:
            st.info("Data laba kuartalan tidak tersedia")

        st.divider()

        # =========================
        # SEASONALITY BULANAN
        # =========================
        st.subheader("📈 Seasonality Bulanan")

        hist = ticker.history(period="5y")
        hist["Month"] = hist.index.month
        monthly = hist.groupby("Month")["Close"].mean().reset_index()

        fig_m = px.line(
            monthly,
            x="Month",
            y="Close",
            title="Rata-rata Harga Saham per Bulan (Historis)",
            markers=True
        )
        st.plotly_chart(fig_m, use_container_width=True)

        st.caption(
            "📌 Grafik ini membantu melihat **pola musiman** saham "
            "(bulan mana cenderung kuat atau lemah)"
        )

    except Exception as e:
        st.error("Terjadi kesalahan saat mengambil data saham.")
