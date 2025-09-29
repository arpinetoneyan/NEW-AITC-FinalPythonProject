import pandas as pd
import streamlit as st
import project_functions as pf


pd.set_option("display.max_columns", None)  # show all columns
pd.set_option("display.width", None)        # don't cut lines
pd.set_option("display.max_colwidth", None) # show all fields

df_crypto = pd.read_csv('cryptocurrency.csv')
df_stocks = pd.read_csv('stocks.csv')
# print(df_crypto.shape)
df_crypto['timestamp'] = pf.transform_string_to_datetime(df_crypto['timestamp'])

df_crypto['price_usd_num'] = pf.transform_string_to_num(df_crypto['price_usd'])

df_crypto['vol_24h_num'] = pf.transform_dollars_str_to_num(df_crypto['vol_24h'])
df_crypto['market_cap_num'] = pf.transform_dollars_str_to_num(df_crypto['market_cap'])

df_crypto['total_vol_num'] = pf.transform_percent_str_to_num(df_crypto['total_vol'])
df_crypto['chg_24h_num'] = pf.transform_percent_str_to_num(df_crypto['chg_24h'])
df_crypto['chg_7d_num'] = pf.transform_percent_str_to_num(df_crypto['chg_7d'])
na_list = ['name','price_usd_num', 'vol_24h_num', 'market_cap_num', 'total_vol_num', 'chg_24h_num', 'chg_7d_num']
df_crypto = pf.drop_na_line(df_crypto, *na_list)

#------------------------------------define time start and end#------------------------------------
max_date = df_crypto['timestamp'].max().date()
min_date = df_crypto['timestamp'].min().date()

#------------------------------------streamlit interface#------------------------------------
st.title("Cryptocurrency Market Insights")
col1, col2, col3, col4 = st.columns(4)
with col1:
    pf.card_info(df_crypto)
with col2:
    pf.total_market_cap(df_crypto)
with col3:
    pf.max_market_cap(df_crypto)
with col4:
    pf.most_expensive_crypto(df_crypto)
col1, col2, col3, col4 = st.columns(4)
with col1:
    pf.top_gainer_24h(df_crypto)
with col2:
    pf.top_loser_24h(df_crypto)
with col3:
    pf.top_gainer_7d(df_crypto)
with col4:
    pf.top_loser_7d(df_crypto)


#---------------------Get info about top 10 crypto BLOCK-------------------
st.title("Get info about TOP cryptos")

column_library = {"Market Capacity": "market_cap_num", "Price (USD)": "price_usd_num", "Volume in 24 hours": "vol_24h_num"}
action_options_list = ["Market Capacity", "Price (USD)", "Volume in 24 hours"]

# top_crypto_list = pf.get_top_crypto_list(df_crypto)
top_n = st.selectbox("Choose Top N", options=["5", "10"])
bitcoin = st.checkbox("Exclude Top 1")
action_top = st.selectbox("Choose parameter", options=action_options_list)
if st.button("Get Info about TOP"):
    top_crypto_list = pf.get_top_crypto_list(df_crypto, int(top_n), column_library[action_top], bitcoin)
    pf.plot_crypto_field(df_crypto, min_date, max_date, *top_crypto_list, field=column_library[action_top], f_name=action_top)


#---------------------Get info about crypto BLOCK-------------------
st.title("Get info about crypto")

crypto_list = pf.get_crypto_list(df_crypto)
option_cripto_name = st.selectbox("Choose Crypto", options=crypto_list)
action = st.selectbox("Choose action", options=["Get main info", "Plot"])
date_range = st.date_input(
    "Choose date range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date = end_date = date_range

if action == "Get main info":
    if st.button("Get Info"):
        pf.get_crypto_main_info(df_crypto, option_cripto_name, start_date, end_date)

if action == "Plot":
    if st.button("Get Info"):
        pf.plot_crypto_field(df_crypto, start_date, end_date, option_cripto_name)


#print(df_crypto.head())
# ******************************** Count Plot for Top N Cryptocurrencies by Count ***********************************

st.title("Top cryptos by count")
pf.count_plot_top_n_by_name(df_crypto, 'name', 20)
