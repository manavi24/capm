# Importing libraries
import streamlit as st
import pandas as pd
import yfinance as yf
import datetime
import CAPM_function

# Streamlit configuration
st.set_page_config(page_title="CAPM", page_icon="chart_with_upwards_trend", layout="wide")

st.title("Capital Asset Pricing Model")

# Fetching S&P 500 symbols
url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
tables = pd.read_html(url)
sp500_table = tables[0]
sp500_table.to_csv('sp500_symbols.csv', index=False)

df = pd.read_csv('sp500_symbols.csv')
symbols = df['Symbol'].tolist()

# Getting input from user
col1, col2 = st.columns([1, 1])
with col1:
    stocks_list = st.multiselect("Choose stocks", symbols, ['TSLA', 'AMZN', 'NVDA', 'GOOGL'])
with col2:
    year = st.number_input("Number of years", 1, 10)

# Downloading data for SP500
end = datetime.date.today()
start = datetime.date(end.year - year, end.month, end.day)

# Download SP500 data
try:
    SP500 = yf.download('^GSPC', start=start, end=end)['Adj Close'].rename('sp500').reset_index()
except Exception as e:
    st.error(f"Failed to download SP500 data: {e}")
    st.stop()

# Downloading data for selected stocks
stocks_df = pd.DataFrame()
for stock in stocks_list:
    try:
        data = yf.download(stock, start=start, end=end)
        stocks_df[stock] = data['Close']
    except Exception as e:
        st.error(f"Failed to download data for stock {stock}: {e}")
        continue

stocks_df.reset_index(inplace=True)

# Merging dataframes
SP500.columns = ['Date', 'sp500']
stocks_df['Date'] = pd.to_datetime(stocks_df['Date'])
SP500['Date'] = pd.to_datetime(SP500['Date'])
stocks_df = pd.merge(stocks_df, SP500, on='Date', how='inner')

# Displaying dataframes
col1, col2 = st.columns([1, 1])
with col1:
    st.markdown("### Dataframe head")
    st.dataframe(stocks_df.head(), use_container_width=True)
with col2:
    st.markdown("### Dataframe tail")
    st.dataframe(stocks_df.tail(), use_container_width=True)

# Visualization
col1, col2 = st.columns([1, 1])
with col1:
    st.markdown('### Price of all the stocks')
    st.plotly_chart(CAPM_function.interactive_plot(stocks_df))
with col2:
    normalized_stocks_df = CAPM_function.normalize(stocks_df)
    st.markdown('### Price of all the stocks after normalizing')
    st.plotly_chart(CAPM_function.interactive_plot(normalized_stocks_df))

# Calculations
stocks_daily_return = CAPM_function.daily_return(stocks_df)
beta = {}
alpha = {}

for i in stocks_daily_return.columns:
    if i not in ['Date', 'sp500']:
        b, a = CAPM_function.calculate_beta(stocks_daily_return, i)
        beta[i] = b
        alpha[i] = a

beta_df = pd.DataFrame({'Stock': beta.keys(), 'Beta Value': [round(i, 2) for i in beta.values()]})

# Displaying beta values
with col1:
    st.markdown('### Calculated Beta Value')
    st.dataframe(beta_df, use_container_width=True)

# CAPM return calculation
rf = 0
rm = stocks_daily_return['sp500'].mean() * 252

return_df = pd.DataFrame()
return_value = []
for stock, value in beta.items():
    return_value.append(round(rf + (value * (rm - rf)), 2))
return_df['Stock'] = stocks_list
return_df['Return Value'] = return_value

# Displaying CAPM returns
with col2:
    st.markdown('### Calculated return using CAPM')
    st.dataframe(return_df, use_container_width=True)




