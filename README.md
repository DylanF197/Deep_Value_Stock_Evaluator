Carlisle's Multiple Acquirer Analytics
Overview:

This project automates financial analysis by:
- Downloading market data
- Connecting to PostgreSQL
- Cleaning financial datasets
- Producing Power BI visualizations from the clean data.

  Technologies:
  - Python (Libraries: sys, yfinance, pandas, psycopg2, os, dotenv, load_dotenv) 
  - SQL
  - Postgres Database
  - Power BI

How to run this: 
  To run this project here are the basic steps. Clone this repository and install the requirments. Set up your own hidden_credentials.env file. This is a file hidden somewhere safe that holds sensitive information. If you don't do this, you will be hard coding credentials and that is not cyber secure. This repo has that file name in the gitignore so it will not show up to be exposed if you make your own. Point the python script to a postgres database in the hidden_credentials.env file you make. Then run the script. It will show in a terminal all the data going into a database and tell you what succeeds and what fails. After this has run roughly all 1500 tickers, you can generate the power BI report from the data in the database. 
 
Finalized Report Example: 

<img width="1283" height="718" alt="image" src="https://github.com/user-attachments/assets/3f853c72-7055-4477-bd7f-23551feffae5" />


Architecture: 

<img width="222" height="521" alt="image" src="https://github.com/user-attachments/assets/1aa63943-3937-4274-a61b-72bc26d8261f" />

Future Improvements: 
- Automated Scheduling
- Market Indicators
- Historical Testing
- A B Hypothesis testing
- Automated Dashboard
  
