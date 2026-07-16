#This script will make a SQL quesry to the database and port the table to a .csv for powerBI to use. 

#|||||||||||Package Imports|||||||||||||||||||||||||||||||||
import psycopg2
import pandas as pd
import os
from dotenv import load_dotenv
import sys

#|||||||||||Database Connection|||||||||||||||||||||||||||||
load_dotenv("hidden_credentials.env")  # Load environment variables from .env file
def get_db_connection():
    """
    This function opens and returns a connection to the local PostgreSQL database.
    Update the password field to match your postgres password inside of your hidden_credentials.env file. 
    """
    return psycopg2.connect(
    host=os.getenv("DB_HOST"),
    database=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD")
)
#|||||||||||SQL Query|||||||||||||||||||||||||||||||||||||||

csv_path = r"C:\Exports\latest_stocks.csv"

# Delete old CSV
if os.path.exists("C:\Users\dflau\OneDrive\Projects\Deep_Value_Stock_Evaluator\data\distinct_tickers.csv"):
    os.remove("C:\Users\dflau\OneDrive\Projects\Deep_Value_Stock_Evaluator\data\distinct_tickers.csv")

cur = conn.cursor()

cur.execute("""
COPY (
    SELECT DISTINCT ON (ticker) *
    FROM stocks
    ORDER BY ticker, date DESC
) TO 'C:"C:\Users\dflau\OneDrive\Projects\Deep_Value_Stock_Evaluator\data\distinct_tickers.csv"'
WITH (FORMAT CSV, HEADER);
        )
""")

conn.commit()

cur.close()
conn.close()

print("CSV export completed successfully.")
print("C:\Users\dflau\OneDrive\Projects\Deep_Value_Stock_Evaluator\data\distinct_tickers.csv")

