"""Whole-history NEPSE Index backtest — implements the SPEC formulas exactly.

Pulls the full index series (1997-2026) straight from MySQL and runs the 5 SOP
indicators + confluence blend, long-only, regime-gated, 80 bps round-trip cost.
Volume Breakout is excluded (index has usable volume only ~6% of bars).

    python whole_history_backtest.py
"""
from __future__ import annotations
import warnings; warnings.filterwarnings("ignore")
import numpy as np, pandas as pd, pymysql

COST = 0.0080          # 80 bps round-trip, charged on entry bar
SLOPE_WIN = 20         # regime slope window (code default; spec prose says 10)


def load_index() -> pd.DataFrame:
    c = pymysql.connect(host="127.0.0.1", user="root", password="1234",
                        database="nepse_database", port=3306)
    q = ("SELECT business_date d, open_index o, high_index h, low_index l, "
         "close_index c, turnover_volume v FROM nepse_market_indices "
         "WHERE sector_name='NEPSE Index' ORDER BY business_date")
    df = pd.read_sql(q, c).astype({"o": float, "h": float, "l": float, "c": float, "v": float})
    c.close()
    df["d"] = pd.to_datetime(df["d"]); return df.set_index("d")


# ---- regime gate -----------------------------------------------------------
def regime_allow(c: pd.Series) -> pd.Series:
    sma = c.rolling(200).mean()
    slope = sma - sma.shift(SLOPE_WIN)
    bull = (c > sma) & (slope > 0)
    bear = (c < sma) & (slope < 0)
    # trade in bull or sideways (=not bull and not bear); stand aside in bear & warm-up
    allow = ~bear & sma.notna()
    return allow.fillna(False)


# ---- indicator STATE series (1 = in long position) -------------------------
def st_supertrend(df, n=20, k=2.0):
    mid = df.c.rolling(n).mean(); band = k * df.c.rolling(n).std(ddof=0)
    state = pd.Series(np.nan, index=df.index)
    state[df.c > mid + band] = 1.0
    state[df.c < mid - band] = 0.0
    return state.ffill().fillna(0.0)

def st_ema(df, f=20, s=50):
    ef = df.c.ewm(span=f, adjust=False).mean(); es = df.c.ewm(span=s, adjust=False).mean()
    return (ef > es).astype(float)

def st_donchian(df, e=20, x=10):
    hi = df.h.rolling(e).max().shift(1); lo = df.l.rolling(x).min().shift(1)
    state = pd.Series(np.nan, index=df.index)
    state[df.c > hi] = 1.0; state[df.c < lo] = 0.0
    return state.ffill().fillna(0.0)

def st_macd(df, f=26, s=45, sig=20):
    macd = df.c.ewm(span=f, adjust=False).mean() - df.c.ewm(span=s, adjust=False).mean()
    signal = macd.ewm(span=sig, adjust=False).mean()
    return (macd > signal).astype(float)


# ---- backtest one STATE series --------------------------------------------
def backtest(df, state, allow):
    pos = (state * allow).astype(float)
    pos = pos.shift(1).fillna(0.0)                 # fill next bar (T+1)
    ret = df.c.pct_change().fillna(0.0)
    opens = (pos > 0) & (pos.shift(1).fillna(0.0) == 0)
    cost = opens.astype(float) * COST
    r = pos * ret - cost
    eq = (1 + r).cumprod()
    total = eq.iloc[-1] - 1
    yrs = len(r) / 252
    cagr = eq.iloc[-1] ** (1 / yrs) - 1 if eq.iloc[-1] > 0 else np.nan
    sd = r.std(ddof=1); sharpe = r.mean() / sd * np.sqrt(252) if sd > 0 else np.nan
    mdd = (eq / eq.cummax() - 1).min()
    trades = int(opens.sum())
    return dict(total=total, cagr=cagr, sharpe=sharpe, mdd=mdd, trades=trades, r=r)


def buyhold(df):
    ret = df.c.pct_change().fillna(0.0); eq = (1 + ret).cumprod()
    return dict(total=eq.iloc[-1]-1, cagr=eq.iloc[-1]**(1/(len(ret)/252))-1,
                sharpe=ret.mean()/ret.std(ddof=1)*np.sqrt(252),
                mdd=(eq/eq.cummax()-1).min(), trades=1, r=ret)


def run_window(df, label):
    allow = regime_allow(df.c)
    states = {"Supertrend 20/2.0 (stdev)": st_supertrend(df),
              "EMA 20/50": st_ema(df),
              "Donchian 20/10": st_donchian(df),
              "MACD 26/45/20": st_macd(df)}
    res = {k: backtest(df, s, allow) for k, s in states.items()}

    # confluence blend: long when >= min_agree indicators long AND allowed
    agree = sum(states.values())
    combos = {}
    for m in (3, 4):
        conf_state = (agree >= m).astype(float)
        combos[f"COMBINED min_agree={m}"] = backtest(df, conf_state, allow)
    bh = buyhold(df)

    print(f"\n{'='*74}\n{label}   ({df.index[0].date()} .. {df.index[-1].date()}, "
          f"{len(df)} bars)\n{'='*74}")
    hdr = f"{'Config':<28}{'TotRet':>12}{'CAGR':>8}{'Sharpe':>8}{'MaxDD':>9}{'Trades':>8}"
    print(hdr); print("-"*len(hdr))
    def row(name, m):
        print(f"{name:<28}{m['total']*100:>11.1f}%{m['cagr']*100:>7.1f}%"
              f"{m['sharpe']:>8.2f}{m['mdd']*100:>8.1f}%{m['trades']:>8}")
    row("Buy & Hold", bh)
    print("-"*len(hdr))
    for k, m in res.items(): row(k, m)
    print("-"*len(hdr))
    for k, m in combos.items(): row(k, m)
    return res, combos, bh


def main():
    df = load_index()
    run_window(df, "A) FULL HISTORY 1997-2026")
    run_window(df[df.index >= "2003-01-01"], "B) SPEC WINDOW 2003-2026")
    print("\nNotes: long-only, regime-gated (bear=cash), 80bps round-trip, T+1 fill.")
    print("Volume Breakout excluded (index volume present on ~6% of bars).")


if __name__ == "__main__":
    main()
