import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.container import BarContainer
import streamlit as st
import seaborn as sns
import math
from functools import wraps
from datetime import datetime

def transform_string_to_datetime(sr: pd.Series) -> pd.Series:
    """
    Transform sr (df_crypto['timestamp']) from string into datetime
    """
    return pd.to_datetime(sr.astype(str))

def transform_string_to_num(sr: pd.Series) -> pd.Series:
    """
    Transform sr (df_crypto['price_usd']) from string into numbers
    deletes "," symbols
    :param: pd.Series
    :returns: pd.Series
    example: 1,234.56 -> 1234.56
    """
    return pd.to_numeric(sr.astype(str).str.replace(',', ''), errors='coerce')

def transform_dollars_str_to_num(sr: pd.Series) -> pd.Series:
    """
        Transforms sr (df_crypto['vol_24h'] and df_crypto['market_cap']) from string into numbers
        delete unnecessary symbols - $ from the left, B, M, K from the end
        (and multiply on e+9, E+6, e+3)
        may be NaNs, if value does not much the format
        :param sr: pd.Series
        :returns: pd.Series
        example: $171.53B -> 171530000000
                 $171.53M -> 171530000
                 $1.64K -> 1640
    """
    num = sr.astype(str).str.replace('$', '', regex=False)  # remove symbol $

    factor = num.str[-1].map({'T': 1e12, 'B': 1e9, 'M': 1e6, 'K': 1e3}) # suffix (T, B, M, K) to factor

    pure_num = num.str[:-1].where(num.str[-1].isin(['T', 'B', 'M', 'K']), num)   #number without a suffix, if there is

    return pd.to_numeric(pure_num.str.replace(',', ''), errors='coerce') * factor.fillna(1)


def transform_percent_str_to_num(sr: pd.Series) -> pd.Series:
    """
        Transforms sr (total_vol, chg_24h and chg_7d) from string to numbers
        deletes symbol % from the right
        may be NaNs, if value does not much the format
        :param sr: np_array
        :returns: array
        example: 17% -> 17, -1.66% ->-1.66
    """
    return pd.to_numeric(
        sr.astype(str)
        .str.replace('%', '', regex=False)
        .str.replace('+', '', regex=False),
        errors='coerce'
    )


def drop_na_line(df: pd.DataFrame, *columns) -> pd.DataFrame:
    """
    Deletes from dataframe lines, for which the value of column is NaN
    """
    for col in columns:
        df = df.dropna(subset=[col])
    return df


def make_card(func):
    """
    Decorator -
    Takes function which returns (title, value),
    makes Streamlit-card with predefined design.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        title, value = func(*args, **kwargs)
        title_size = 14
        value_size = 18
        html = f"""
            <div style="
                background: #1f77b4;
                color: #fff;
                width: 170px;
                padding: 16px 18px;
                border-radius: 10px;
                border: 2px solid #0f3d6b;
                box-shadow: 0 4px 10px rgba(0,0,0,0.12);
                margin-bottom: 10px;
            ">
              <div style="font-size: {title_size}px; font-weight: 700; opacity: 0.95;">
                {title}
              </div>
              <div style="font-size: {value_size}px; font-weight: 800; margin-top: 8px; letter-spacing: 0.5px;">
                {value}
              </div>
            </div>
        """
        st.markdown(html, unsafe_allow_html=True)
        return title, value
    return wrapper


# --- KPI cards ---
# ----------------- Crypto count
@make_card
def card_info(df):
    title = "Crypto count"
    count = df['name'].nunique()
    count_str = f"{count:_}"
    return title, count_str

# ------------------ Total Market Cap
@make_card
def total_market_cap(df):
    title = "Total Market Cap"
    total = df['market_cap_num'].sum()
    return title, f"${short_format_num(total)}"

# ------------------ Top Market Cap
@make_card
def max_market_cap(df):
    title = "Top Market Cap"
    row = df.loc[df['market_cap_num'].idxmax()]
    return title, f"{row['name']} — ${short_format_num(row['market_cap_num'])}"

# ------------------ Most Expensive Crypto
@make_card
def most_expensive_crypto(df):
    title = "Most Expensive"
    row = df.loc[df['price_usd_num'].idxmax()]
    return title, f"{row['name']} — ${short_format_num(row['price_usd_num'])}"

# ------------------ Top Gainer (24h)
@make_card
def top_gainer_24h(df):
    title = "Top Gainer (24h)"
    row = df.loc[df['chg_24h_num'].idxmax()]
    return title, f"{row['name']} — {row['chg_24h_num']:.2f}%"

# ------------------ Top Loser (24h)
@make_card
def top_loser_24h(df):
    title = "Top Loser (24h)"
    row = df.loc[df['chg_24h_num'].idxmin()]
    return title, f"{row['name']} — {row['chg_24h_num']:.2f}%"

# ------------------ Top Gainer (7d)
@make_card
def top_gainer_7d(df):
    title = "Top Gainer (7d)"
    row = df.loc[df['chg_7d_num'].idxmax()]
    return title, f"{row['name']} — {row['chg_7d_num']:.2f}%"

# ------------------ Top Loser (7d)
@make_card
def top_loser_7d(df):
    title = "Top Loser (7d)"
    row = df.loc[df['chg_7d_num'].idxmin()]
    return title, f"{row['name']} — {row['chg_7d_num']:.2f}%"

def short_format_num(num):
    """
    Format large numbers with suffixes:
    K = thousand, M = million, B = billion, T = trillion
    """
    for unit in ["", "K", "M", "B", "T"]:
        if abs(num) < 1000:
            return f"{num:.1f}{unit}"
        num /= 1000
    return f"{num:.1f}P"

def get_crypto_list(df):
  #print(df['name'].unique())
  return df['name'].unique()

import pandas as pd

def get_top_crypto_list(df, n=10, by="market_cap_num", top1=True):
    """
    Return top-n cryptos from df sorted by column `by` (default: market_cap_num).
    - df: pandas DataFrame
    - n: number of top items (default 10)
    - by: column name to sort by (default 'market_cap_num')
    - return list of names
    - if by is not a column, raise error
    """
    if by not in df.columns:
        raise ValueError(f"Column {by!r} not found in dataframe")

    # Create a copy to avoid changing original df
    tmp = df.copy()

    # Drop rows where name is missing or sorting column is NaN
    top_names = (tmp.dropna(subset=[by])
        .sort_values(by=by, ascending=False)
        .drop_duplicates(subset=["name"])
        .head(n)["name"].tolist()
    )

    if top1:
        return top_names[1:]
    return top_names


def fmt_num(x, dec):
    """Format numeric x with thousands '_' and dec decimals. Return '-' for NaN."""
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return "-"
    try:
        return format(x, f"_.{dec}f") + "$"
    except Exception:
        return str(x)

def fmt_percent(x, dec):
    """Format percent-like numbers and append % sign."""
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return "-"
    try:
        return format(x, f"_.{dec}f") + "%"
    except Exception:
        return str(x)

def get_crypto_main_info(df, crypto, price_decimals=1, change_decimals=1):
  """
  prints basic info about crypto
  df - dataframe
  crypto - name of crypto
  price_decimals - number of decimals for price
  change_decimals - number of decimals for change
  """
  crypto_df = df[df['name'] == crypto]
  if crypto_df.empty:
    st.write(f"No data for {crypto!r}")
    return

  # get no number fields
  name = crypto_df['name'].iloc[0]
  symbol = crypto_df['symbol'].iloc[0]

  # get number fields
  price_mean = crypto_df['price_usd_num'].mean()
  price_median = crypto_df['price_usd_num'].median()
  price_min = crypto_df['price_usd_num'].min()
  price_max = crypto_df['price_usd_num'].max()

  chg24_mean = crypto_df['chg_24h_num'].mean()
  chg24_min = crypto_df['chg_24h_num'].min()
  chg24_max = crypto_df['chg_24h_num'].max()

  chg7_mean = crypto_df['chg_7d_num'].mean()
  chg7_min = crypto_df['chg_7d_num'].min()
  chg7_max = crypto_df['chg_7d_num'].max()

  # EXTRACT
  st.write(f"name: {name}")
  st.write(f"symbol: {symbol}")
  st.text(f"price in $, mean: {fmt_num(price_mean, price_decimals)}")
  st.text(f"price in $, median: {fmt_num(price_median, price_decimals)}")
  st.text(f"price in $, min: {fmt_num(price_min, price_decimals)}")
  st.text(f"price in $, max: {fmt_num(price_max, price_decimals)}")

  st.write(f"change in last 24 hours - mean: {fmt_percent(chg24_mean, change_decimals)}")
  st.write(f"change in last 24 hours - min: {fmt_percent(chg24_min, change_decimals)}")
  st.write(f"change in last 24 hours - max: {fmt_percent(chg24_max, change_decimals)}")

  st.write(f"change in last 7 days - mean: {fmt_percent(chg7_mean, change_decimals)}")
  st.write(f"change in last 7 days - min: {fmt_percent(chg7_min, change_decimals)}")
  st.write(f"change in last 7 days - max: {fmt_percent(chg7_max, change_decimals)}")

  return


def plot_crypto_field(df_main, start_date, end_date, *cryptos, field='price_usd_num', f_name='Price (USD)', figsize=(10, 6)):
    """
    Plots the price of cryptos in USD and displays the figure in Streamlit.
    - df: dataframe with columns 'timestamp', 'name', 'price_usd_num'
    - cryptos: one or more crypto names (strings)
    - figsize: tuple for figure size
    - date_format: optional strftime format for x-axis (e.g. '%Y-%m-%d')
    """
    start_datetime = datetime.combine(start_date, datetime.min.time())
    end_datetime = datetime.combine(end_date, datetime.max.time())

    df = df_main[(df_main['timestamp']>=start_datetime) & (df_main['timestamp']<=end_datetime)]

    fig, ax = plt.subplots(figsize=figsize)

    plotted = False
    for crypto in cryptos:
        crypto_df = df[df['name'] == crypto]
        if crypto_df.empty:
            st.warning(f"No data for {crypto!r}")
            continue
        # sort by timestamp
        crypto_df = crypto_df.sort_values('timestamp')
        sns.lineplot(x='timestamp', y=field, data=crypto_df, ax=ax, label=crypto)
        plotted = True

    if not plotted:
        st.info("No series to plot.")
        plt.close(fig)
        return None

    ax.set_title(f_name + " — " + ", ".join(cryptos))
    ax.set_xlabel("Timestamp")
    ax.set_ylabel(f_name)
    ax.grid(True, linestyle='--', alpha=0.4)
    ax.legend(title="Crypto")

    # rotate x ticks for readability
    plt.xticks(rotation=30, ha='right')

    plt.tight_layout()

    st.pyplot(fig)      # Display in Streamlit

    plt.close(fig)      # close figure to free memory

    return fig

def count_plot_top_n_by_name(df: pd.DataFrame, col: str, n: int):
    """
    Plots Count Plot for top N cryptocurrencies by col by count
    """

    if col not in df.columns:
        st.error(f"Column {col!r} not found in DataFrame")
        return None

    # get top n
    top_n = df[col].value_counts().head(n).index

    fig, ax = plt.subplots(figsize=(12, 6))

    sns.countplot(
        data=df[df[col].isin(top_n)],
        y=col,
        order=top_n,
        color="green",
        ax=ax
    )

    ax.set_title(f"Top {n} by Count")
    ax.set_xlabel("Count")
    ax.set_ylabel(col)

    # labels on bars
    for container in ax.containers:
        if isinstance(container, BarContainer):
            ax.bar_label(container, label_type="center", color="white", fontsize=12)

    fig.tight_layout()
    st.pyplot(fig)
    return fig
