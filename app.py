import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# konfigurasi halaman
st.set_page_config(
    page_title="Dashboard Analisis Penjualan",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# fungsi load dataset


@st.cache_data
def load_data():
    return pd.read_csv("data/dataset_bee_cycle.xlsx - Sheet1.csv")


# load data penjualan
df_sales = load_data()  # memanggil fungsi load_data
df_sales.columns = df_sales.columns.str.lower(
).str.replace(' ', '_')  # ubah jadi lower case
df_sales['order_date'] = pd.to_datetime(
    df_sales['order_date'])  # ubah ke datetime

# judul dashboard
st.title("Dashboard Analisis Penjualan Bee Cycle")
st.markdown("Dashboard ini menyediakan gambaran umum *sales performance*, **trend**, dan distribusi berdasaran berbagai macam dimensi")

st.sidebar.header("Filter & Navigasi")

pilihan_halaman = st.sidebar.radio(
    "Pilihan Halaman:",
    ("Overview Dashboard", "Prediksi Penjualan")
)

# filter (yang akan muncul hanya di halaman Overview Dashboard)
if pilihan_halaman == "Overview Dashboard":
    st.sidebar.markdown("### Filter Data Dashboard")

    # filter tanggal
    min_date = df_sales['order_date'].min().date()
    max_date = df_sales['order_date'].max().date()

    date_range = st.sidebar.date_input(
        "Pilih Date Range:",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )

    if len(date_range) == 2:
        start_date_filter = pd.to_datetime(date_range[0])
        end_date_filter = pd.to_datetime(date_range[1])

        filtered_df = df_sales[(df_sales['order_date'] >= start_date_filter) &
                               (df_sales['order_date'] <= end_date_filter)]
    else:
        filtered_df = df_sales

    # filter berdasarkan wilayah
    selected_regions = st.sidebar.multiselect(
        "Pilih Wilayah:",
        options=df_sales['territory_groups'].unique().tolist(),
        default=df_sales['territory_groups'].unique().tolist()
    )

    filtered_df = filtered_df[filtered_df['territory_groups'].isin(
        selected_regions)]
else:
    filtered_df = df_sales.copy()

# konten halaman utama
if pilihan_halaman == "Overview Dashboard":
    # metrics utama
    st.subheader("Ringkasan Performance Penjualan")

    col1, col2, col3 = st.columns([3, 3, 3])

    total_sales = filtered_df['totalprice_rupiah'].sum()
    total_orders = filtered_df['order_detail_id'].nunique()
    total_products_sold = filtered_df['quantity'].sum()

    with col1:
        st.metric(label="Total Penjualan", value=f"Rp {total_sales:,.2f}")
    with col2:
        st.metric(label="Jumlah Pesanan", value=f"{total_orders:,}")
    with col3:
        st.metric(label="Jumlah Produk Terjual",
                  value=f"{total_products_sold:,}")

    # line chart trend penjualan
    sales_by_month = filtered_df.groupby(
        'order_date')['totalprice_rupiah'].sum().reset_index()
    # memastikan urutan bulannya benar
    sales_by_month['order_date'] = pd.to_datetime(
        sales_by_month['order_date']).dt.to_period('M')
    sales_by_month = sales_by_month.sort_values('order_date')
    sales_by_month['order_date'] = sales_by_month['order_date'].astype(str)

    fig_monthly_sales = px.line(
        sales_by_month,
        x='order_date',
        y='totalprice_rupiah',
        title='Total Penjualan per Bulan'
    )
    st.plotly_chart(fig_monthly_sales, use_container_width=True)

    # visualisasi dengan tab, lebih detail
    st.subheader("Detailed Sales Performance")

    # membuat tab 1, tab 2
    tab1, tab2 = st.tabs(["Kategori Produk", "Wilayah"])

    with tab1:
        st.write("#### Penjualan Berdasarkan Kategori Produk")

        sales_by_payment = filtered_df.groupby(
            'category'
        )['totalprice_rupiah'].sum().reset_index()

        fig_payment = px.bar(
            sales_by_payment,
            x='category',
            y='totalprice_rupiah',
            color='category'
        )

        # menampilkan bar chart
        st.plotly_chart(fig_payment, use_container_width=True)

    with tab2:
        st.write("#### Penjualan Berdasarkan Wilayah")

        sales_by_region = filtered_df.groupby(
            'territory_groups'
        )['totalprice_rupiah'].sum().reset_index()

        fig_region = px.bar(
            sales_by_region,
            x='territory_groups',
            y='totalprice_rupiah',
            color='territory_groups'
        )
        st.plotly_chart(fig_region, use_container_width=True)

