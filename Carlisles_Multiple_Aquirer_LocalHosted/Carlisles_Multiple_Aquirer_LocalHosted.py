"""
Acquirer's Multiple Calculator
================================
Pulls financial data from yfinance and calculates:
  Enterprise Value (EV) = Market Cap + Total Debt + Preferred Stock + Minority Interest - Cash
  EBIT                  = Operating Income (from income statement)
  Acquirer's Multiple   = EV / EBIT
 
Usage:
  python acquirers_multiple.py AAPL
  python acquirers_multiple.py AAPL MSFT GOOG
"""
import os
from dotenv import load_dotenv
import sys
import yfinance as yf
import psycopg2
import pandas as pd

load_dotenv("hidden_credentials.env")  # Load environment variables from .env file

#----------------------------------------------------------------
# Getting the list for the ticker iterator 
#----------------------------------------------------------------
unfiltered = pd.read_csv(
    'https://www.nasdaqtrader.com/dynamic/SymDir/otherlisted.txt',
    sep='|'
)

# Step 1: drop test issues
df = unfiltered[unfiltered['Test Issue'] == 'N']

# Step 2: drop ETFs using the dedicated column
df = df[df['ETF'] == 'N']

# Step 3: drop non-common-stock by Security Name keywords
exclude_keywords = [
    'Warrant', 'Warrants',
    'Preferred', 'Pfd',
    'Unit', 'Units',
    'Right ', 'Rights',
    'Note', 'Debenture',
    'Fund', 'Trust',
    'ETN',
    'Depositary'
]

pattern = '|'.join(exclude_keywords)
df = df[~df['Security Name'].str.contains(pattern, case=False, na=False)]

# Step 4: optionally KEEP only explicitly labeled common stock
df = df[df['Security Name'].str.contains('Common Stock', case=False, na=False)]

# Extract clean ticker list
clean_tickers = df['ACT Symbol'].tolist()
print(len(clean_tickers))
print(clean_tickers)


def get_value(source, *keys, default=0):
    """
    Safely pull a value from a dict-like object by trying multiple key names.
    Returns default (0) if none of the keys are found.
    """
    for key in keys:
        try:
            val = source.get(key)
            if val is not None:
                return float(val)
        except Exception:
            continue
    return default


def calculate_acquirers_multiple(ticker_symbol):
    ticker = yf.Ticker(ticker_symbol)
    info = ticker.info
    #-----------------------------------------------------------------
    # Close price as a data point
    #-----------------------------------------------------------------
    # Current stock price — used for reference alongside the multiple
    close_price = get_value(info, "currentPrice", "regularMarketPrice")
    #-----------------------------------------------------------------
  
    # Sector / Industry: used for Carlisle's Financial Services & Utilities exclusion
    sector = info.get("sector", "Unknown")
    industry = info.get("industry", "Unknown")

    # ----------------------------------------------------------------
    # ENTERPRISE VALUE COMPONENTS
    # ----------------------------------------------------------------

    # Market Cap: share price * shares outstanding
    market_cap = get_value(info, "marketCap")

    # Total Debt: yfinance sometimes labels this differently
    total_debt = get_value(info, "totalDebt", "longTermDebt")

    # Cash & Equivalents: money the company holds
    cash = get_value(info, "totalCash", "cashAndCashEquivalents")

    # Preferred Stock: special share class, senior to common equity
    # yfinance doesn't always report this; defaults to 0 if missing
    preferred_stock = 0
    try:
        bs = ticker.balance_sheet
        if not bs.empty:
            for label in ["Preferred Stock", "PreferredStock"]:
                if label in bs.index:
                    val = bs.loc[label].iloc[0]
                    if val is not None and str(val) != "nan":
                        preferred_stock = float(val)
                    break
    except Exception:
        pass

    # Minority Interest: the portion of subsidiaries not owned by the company
    minority_interest = get_value(info, "minorityInterest", "noncontrollingInterestInSubsidiaries")

    # Enterprise Value
    ev = market_cap + total_debt + preferred_stock + minority_interest - cash

    # ----------------------------------------------------------------
    # EBIT (Operating Income)
    # ----------------------------------------------------------------
    ebit = None
    try:
        financials = ticker.financials
        if not financials.empty:
            for label in ["Operating Income", "EBIT", "Ebit", "OperatingIncome"]:
                if label in financials.index:
                    val = financials.loc[label].iloc[0]
                    if val is not None and str(val) != "nan":
                        ebit = float(val)
                    break
    except Exception:
        pass

    # Fallback: try info dict
    if ebit is None:
        ebit = get_value(info, "operatingIncome", "ebit") or None

    # ----------------------------------------------------------------
    # ACQUIRER'S MULTIPLE
    # ----------------------------------------------------------------
    if ebit and ebit > 0:
        multiple = ev / ebit
    else:
        multiple = None

    return {
        "ticker":            ticker_symbol.upper(),
        "close_price":       close_price, 
        "sector":            sector,
        "industry":          industry,
        "market_cap":        market_cap,
        "total_debt":        total_debt,
        "cash":              cash,
        "preferred_stock":   preferred_stock,
        "minority_interest": minority_interest,
        "enterprise_value":  ev,
        "ebit":              ebit,
        "multiple":          multiple,
    }


def fmt(value, prefix="$"):
    """Format a large number in millions for readability."""
    if value is None:
        return "N/A"
    return f"{prefix}{value / 1_000_000:,.1f}M"


def print_result(r):
    # Pull any string with an apostrophe out of f-strings to avoid
    # backslash-in-f-string SyntaxError in Python 3.11
    name              = r["ticker"]
    label_close       = "close_price"
    label_sector      = "Sector"
    label_industry   = "Industry"
    label_market_cap  = "+ Market cap"
    label_debt        = "+ Total debt"
    label_preferred   = "+ Preferred stock"
    label_minority    = "+ Minority interest"
    label_cash        = "- Cash"
    label_ev          = "Enterprise Value (EV)"
    label_ebit        = "EBIT (Operating Income)"
    label_multiple    = "Acquirer's Multiple"
    label_verdict     = "Verdict"
    label_na          = "N/A (EBIT negative or missing)"
    divider           = "=" * 45
    line              = "-" * 38

    print(f"\n{divider}")
    print(f"  {name} -- Acquirer's Multiple")
    print(f"{divider}")
    print(f"  {label_close:<28} ${r['close_price']:.2f}")  
    print(f"  {label_sector:<28} {r['sector']}")
    print(f"  {label_industry:<28} {r['industry']}")
    print(f"  {label_market_cap:<28} {fmt(r['market_cap'])}")
    print(f"  {label_debt:<28} {fmt(r['total_debt'])}")
    print(f"  {label_preferred:<28} {fmt(r['preferred_stock'])}")
    print(f"  {label_minority:<28} {fmt(r['minority_interest'])}")
    print(f"  {label_cash:<28} {fmt(r['cash'])}")
    print(f"  {line}")
    print(f"  {label_ev:<28} {fmt(r['enterprise_value'])}")
    print(f"  {label_ebit:<28} {fmt(r['ebit'])}")
    print(f"  {line}")

    if r["multiple"] is not None:
        m = r["multiple"]
        if m < 7:
            verdict = "Very cheap -- Carlisle's sweet spot"
        elif m < 12:
            verdict = "Reasonably priced"
        elif m < 20:
            verdict = "Getting expensive"
        else:
            verdict = "Likely overpriced"
        print(f"  {label_multiple:<28} {m:.1f}x")
        print(f"  {label_verdict:<28} {verdict}")
    else:
        print(f"  {label_multiple:<28} {label_na}")

    print(f"{divider}\n")


# ----------------------------------------------------------------
# DATABASE FUNCTIONS
# ----------------------------------------------------------------

def get_db_connection():
    """
    Opens and returns a connection to the local PostgreSQL database.
    Update the password field to match your postgres password.
    """
    return psycopg2.connect(
    host=os.getenv("DB_HOST"),
    database=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD")
)


def create_table_if_not_exists(cur):
    """
    Creates the stocks table if it doesn't already exist.
    Running this every time is safe -- IF NOT EXISTS means it won't
    overwrite data if the table is already there.

    Column notes:
      - ticker:             stock symbol e.g. AAPL
      - market_cap:         market capitalization in raw dollars
      - total_debt:         short + long term debt
      - cash:               cash and cash equivalents
      - preferred_stock:    value of preferred shares outstanding
      - minority_interest:  value of minority-owned subsidiary stakes
      - enterprise_value:   the full EV calculation
      - ebit:               operating income / earnings before interest & tax
      - acquirers_multiple: EV / EBIT -- the core metric
      - fetched_at:         timestamp of when this row was inserted,
                            auto-set by the database to the current time
    """
    cur.execute("""
        CREATE TABLE IF NOT EXISTS stocks (
            id                  SERIAL PRIMARY KEY,
            ticker              VARCHAR(10)   NOT NULL,
            close_price         NUMERIC,
            sector              VARCHAR(50),
            industry            VARCHAR(50),
            market_cap          NUMERIC,
            total_debt          NUMERIC,
            cash                NUMERIC,
            preferred_stock     NUMERIC,
            minority_interest   NUMERIC,
            enterprise_value    NUMERIC,
            ebit                NUMERIC,
            acquirers_multiple  NUMERIC,
            fetched_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)


def save_result_to_db(r):
    """
    Takes a result dict from calculate_acquirers_multiple() and
    inserts it as a new row in the stocks table.

    Each run appends a new row rather than overwriting -- this lets
    you track how the multiple changes over time for each ticker.
    """
    conn = None
    try:
        # Open connection and cursor
        conn = get_db_connection()
        cur = conn.cursor()

        # Create table if this is the first run
        create_table_if_not_exists(cur)

        # Insert the result row.
        # %s placeholders are psycopg2's safe way to pass values --
        # never use f-strings to build SQL, it's a security risk.
        cur.execute("""
            INSERT INTO stocks (
                ticker,
                close_price,
                sector,
                industry,
                market_cap,
                total_debt,
                cash,
                preferred_stock,
                minority_interest,
                enterprise_value,
                ebit,
                acquirers_multiple
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            r["ticker"],
            r["close_price"],
            r["sector"],
            r["industry"],
            r["market_cap"],
            r["total_debt"],
            r["cash"],
            r["preferred_stock"],
            r["minority_interest"],
            r["enterprise_value"],
            r["ebit"],
            r["multiple"],        # "multiple" in the dict = acquirers_multiple in the DB
        ))

        # Commit writes the transaction to the database.
        # Without this the insert is rolled back when the connection closes.
        conn.commit()

        print(f"  + {r['ticker']} saved to database.")

    except Exception as e:
        # If anything goes wrong, print the error but don't crash the script
        print(f"  x Database error for {r['ticker']}: {e}")

    finally:
        # Always close the connection, even if an error occurred
        if conn:
            conn.close()
# ----------------------------------------------------------------
# TICKER LIST
# ----------------------------------------------------------------

# Add or remove tickers from this list as needed.
# The script will loop through the manual list of tickers and calculate the Acquirer's Multiple for each one. This is here for testing reasons. 

TICKERS = clean_tickers
'''TICKERS = [
    "AAPL", "MSFT", "GOOG", "AMZN", "META",
    "NVDA", "BRK-B", "JPM", "JNJ", "V",
    "XOM", "UNH", "WMT", "PG", "MA",
    "HD", "CVX", "MRK", "ABBV", "PEP",
]'''


# ----------------------------------------------------------------
# MAIN
# ----------------------------------------------------------------

if __name__ == "__main__":

    print(f"\nRunning Acquirer's Multiple screen for {len(TICKERS)} tickers...\n")

    # Track successes and failures for a summary at the end
    success = []
    failed  = []

    for symbol in TICKERS:
        try:
            result = calculate_acquirers_multiple(symbol)
            print_result(result)
            save_result_to_db(result)
            success.append(symbol)

            # Small delay between calls to avoid yfinance rate limiting
            import time
            time.sleep(1)

        except Exception as e:
            print(f"\nError fetching {symbol}: {e}\n")
            failed.append(symbol)

    # Print a summary when the loop finishes
    print(f"\n{'='*45}")
    print(f"  Done. {len(success)} succeeded, {len(failed)} failed.")
    if failed:
        print(f"  Failed tickers: {', '.join(failed)}")
    print(f"{'='*45}\n")