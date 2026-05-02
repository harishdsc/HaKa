import pandas as pd
import yfinance as yf

stocks = pd.read_csv("stocks.csv")

def compute(df):
    df['EMA10'] = df['Close'].ewm(span=10).mean()
    df['EMA20'] = df['Close'].ewm(span=20).mean()

    delta = df['Close'].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    rs = gain.rolling(14).mean() / loss.rolling(14).mean()
    df['RSI'] = 100 - (100 / (1 + rs))

    df['VolSMA'] = df['Volume'].rolling(20).mean()
    return df

def check(df):
    latest = df.iloc[-1]
    prev = df.iloc[-2]

    cond1 = prev['EMA10'] < prev['EMA20'] and latest['EMA10'] > latest['EMA20']
    cond2 = latest['Volume'] > 1.5 * latest['VolSMA']
    cond3 = latest['RSI'] > 50
    cond4 = latest['EMA10'] > latest['EMA20']
    cond5 = latest['Close'] > latest['Close'].mean()

    return cond1 and cond2 and cond3 and cond4 and cond5

results = []

for _, row in stocks.iterrows():
    try:
        sym = row['Symbol']
        sec = row['Sector']

        d = yf.download(sym, period="3mo", interval="1d")
        w = yf.download(sym, period="6mo", interval="1wk")
        m = yf.download(sym, period="1y", interval="1mo")

        d = compute(d)
        w = compute(w)
        m = compute(m)

        results.append([
            sym,
            sec,
            "YES" if check(d) else "NO",
            "YES" if check(w) else "NO",
            "YES" if check(m) else "NO"
        ])

    except:
        continue

pd.DataFrame(results, columns=["Symbol","Sector","Daily","Weekly","Monthly"]).to_csv("output.csv", index=False)
