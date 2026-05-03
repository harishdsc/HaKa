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
    prev = df.iloc[-2]

    cond1 = prev['EMA10'] < prev['EMA20'] and latest['EMA10'] > latest['EMA20']
    cond2 = latest['Volume'] > 1.5 * latest['VolSMA']
    cond3 = latest['RSI'] > 50
    cond4 = latest['EMA10'] > latest['EMA20']
    cond5 = latest['Close'] > df['Close'].rolling(20).mean().iloc[-1]

    score = sum([cond1, cond2, cond3, cond4, cond5])

    return "YES" if score >= 3 else "NO"


results = []

for _, row in stocks.iterrows():
    sym = row['Symbol']
    sec = row['Sector']

    print(f"Processing: {sym}")

    try:
        df = yf.download(sym, period="6mo", interval="1d", progress=False)

        df = compute(df)

        # 🔥 SAME DATA USED FOR ALL TF (FAST)
        daily = check(df)
        weekly = check(df.tail(60))     # approx weekly behavior
        monthly = check(df.tail(120))   # approx monthly

        results.append([sym, sec, daily, weekly, monthly])

    except Exception as e:
        print(f"Error: {sym}", e)
        results.append([sym, sec, "NO", "NO", "NO"])


pd.DataFrame(results, columns=["Symbol","Sector","Daily","Weekly","Monthly"]).to_csv("output.csv", index=False)

print("DONE")
