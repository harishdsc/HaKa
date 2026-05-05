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
    if df is None or len(df) < 30:
        return "NO"

    latest = df.iloc[-1]

    score = 0

    # EMA Trend
    if latest['EMA10'] > latest['EMA20']:
        score += 1

    # Recent crossover (relaxed)
    if df['EMA10'].iloc[-3] < df['EMA20'].iloc[-3] and latest['EMA10'] > latest['EMA20']:
        score += 1

    # Volume
    if latest['Volume'] > 1.2 * latest['VolSMA']:
        score += 1

    # RSI
    if latest['RSI'] > 50:
        score += 1

    return "YES" if score >= 2 else "NO"


results = []

for _, row in stocks.iterrows():
    sym = row['Symbol']
    sec = row['Sector']

    print(f"Processing: {sym}")

    try:
        df = yf.download(sym, period="6mo", interval="1d", progress=False)

        if df is None or df.empty:
            raise Exception("No data")

        df.index = pd.to_datetime(df.index)

        df = compute(df)

        # ✅ REAL WEEKLY & MONTHLY
        w = df.resample('W').last()
        m = df.resample('M').last()

        w = compute(w)
        m = compute(m)

        daily = check(df)
        weekly = check(w)
        monthly = check(m)

        results.append([sym, sec, daily, weekly, monthly])

    except Exception as e:
        print(f"Error: {sym}", e)
        results.append([sym, sec, "NO", "NO", "NO"])


pd.DataFrame(results, columns=["Symbol","Sector","Daily","Weekly","Monthly"]).to_csv("output.csv", index=False)

print("DONE")
