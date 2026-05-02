import pandas as pd
import yfinance as yf

stocks = pd.read_csv("stocks.csv")

# -----------------------------
# Indicator calculations
# -----------------------------
def compute(df):
    if df.empty:
        return df

    df['EMA10'] = df['Close'].ewm(span=10).mean()
    df['EMA20'] = df['Close'].ewm(span=20).mean()

    delta = df['Close'].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    rs = gain.rolling(14).mean() / loss.rolling(14).mean()
    df['RSI'] = 100 - (100 / (1 + rs))

    df['VolSMA'] = df['Volume'].rolling(20).mean()

    return df


# -----------------------------
# Condition check (SAFE)
# -----------------------------
def check(df):
    # 🔴 Important safety checks
    if df is None or df.empty or len(df) < 30:
        return "NO"

    latest = df.iloc[-1]
    prev = df.iloc[-2]

    try:
        cond1 = prev['EMA10'] < prev['EMA20'] and latest['EMA10'] > latest['EMA20']
        cond2 = latest['Volume'] > 1.5 * latest['VolSMA']
        cond3 = latest['RSI'] > 50
        cond4 = latest['EMA10'] > latest['EMA20']
        cond5 = latest['Close'] > latest['Close'].rolling(20).mean().iloc[-1]

        return "YES" if (cond1 and cond2 and cond3 and cond4 and cond5) else "NO"

    except:
        return "NO"


# -----------------------------
# Main loop
# -----------------------------
results = []

for _, row in stocks.iterrows():
    sym = row['Symbol']
    sec = row['Sector']

    print(f"Processing: {sym}")  # helps debugging in Actions

    try:
        d = yf.download(sym, period="3mo", interval="1d", progress=False)
        w = yf.download(sym, period="6mo", interval="1wk", progress=False)
        m = yf.download(sym, period="1y", interval="1mo", progress=False)

        d = compute(d)
        w = compute(w)
        m = compute(m)

        results.append([
            sym,
            sec,
            check(d),
            check(w),
            check(m)
        ])

    except Exception as e:
        print(f"Error with {sym}: {e}")

        # Still append row so dashboard is never empty
        results.append([sym, sec, "NO", "NO", "NO"])


# -----------------------------
# Save output
# -----------------------------
df_out = pd.DataFrame(results, columns=["Symbol","Sector","Daily","Weekly","Monthly"])

df_out.to_csv("output.csv", index=False)

print("✅ Output generated")
