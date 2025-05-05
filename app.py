import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Amazon 业务绩效仪表盘", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_csv("amazon.csv")
    df['discounted_price'] = df['discounted_price'].str.replace('₹', '').str.replace(',', '').astype(float)
    df['actual_price'] = df['actual_price'].str.replace('₹', '').str.replace(',', '').astype(float)
    df['discount_percentage'] = df['discount_percentage'].str.replace('%', '').astype(float)
    df['rating'] = pd.to_numeric(df['rating'], errors='coerce')
    df['rating_count'] = df['rating_count'].str.replace(',', '').astype(float)
    df['estimated_sales'] = df['rating_count'] * df['discounted_price']
    df['main_category'] = df['category'].apply(lambda x: str(x).split('|')[0])
    return df

df = load_data()

average_discount = df['discount_percentage'].mean()
average_rating = df['rating'].mean()
total_reviews = df['rating_count'].sum()
total_sales = df['estimated_sales'].sum()

st.title("📊 Amazon 业务绩效仪表盘")

col1, col2, col3, col4 = st.columns(4)
col1.metric("平均折扣 (%)", f"{average_discount:.2f}")
col2.metric("平均评分", f"{average_rating:.2f}")
col3.metric("总评论数量", f"{int(total_reviews):,}")
col4.metric("估算总销售额 (₹)", f"{total_sales:,.2f}")

st.markdown("---")

sales_by_category = df.groupby('main_category')['estimated_sales'].sum().reset_index()
fig1 = px.pie(
    sales_by_category,
    names='main_category',
    values='estimated_sales',
    title='不同大类别的销售额占比'
)
st.plotly_chart(fig1, use_container_width=True)

st.markdown("---")

df_scatter = df.dropna(subset=['estimated_sales', 'rating', 'discount_percentage'])
df_scatter = df_scatter[(df_scatter['estimated_sales'] > 0) & (df_scatter['discount_percentage'] >= 20)]

fig2 = px.scatter(
    df_scatter,
    x='discount_percentage',
    y='rating',
    size='estimated_sales',
    size_max=20,
    title='折扣百分比 vs 评分（折扣 ≥ 20%）',
    trendline='ols',
    hover_data=['product_name']
)
st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")

category_rating = df.groupby('main_category')['rating'].mean().reset_index()
fig3 = px.bar(
    category_rating,
    x='main_category',
    y='rating',
    title='不同大类别的商品平均评分'
)
st.plotly_chart(fig3, use_container_width=True)
