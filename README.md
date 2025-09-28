# Cryptocurrency Market Insights (Streamlit app)

## Description
A Streamlit application for visualizing and monitoring key KPIs of cryptocurrencies.
Main file: `Cripto_main.py`. 
### IMPORTANT
The app expects a CSV file `cryptocurrency.csv` with columns:
`timestamp, name, symbol, price_usd, vol_24h, total_vol, chg_24h, chg_7d, market_cap`.

The code converts some string columns into numeric fields for analysis:
- `price_usd_num`
- `vol_24h_num`
- `market_cap_num`
- `total_vol_num`
- `chg_24h_num`
- `chg_7d_num`

## Installation
pip install -r requirements.txt

## Run the app
streamlit run Cripto_main.py


