import duckdb
import pandas as pd
from bs4 import BeautifulSoup
import os

DATA_DIR = "Dataset"
OUTPUT_FILE = "jobs_clean.csv"
SAMPLE_SIZE = 1000

def process_data():
    print("Initializing DuckDB connection...")

    con = duckdb.connect(database=':memory:')
    print(" [SQL] Executing complex SQL query to extract and clean data...")

    query = f"""
    SELECT 
        p.job_id,
        p.company_name,
        p.title,
        p.description,
        p.max_salary,
        p.pay_period,
        p.location,
        p.formatted_work_type,
        p.skills_desc
    FROM read_csv_auto('{DATA_DIR}/postings.csv') AS p
    WHERE p.description IS NOT NULL AND p.company_name IS NOT NULL AND p.skills_desc IS NOT NULL
    ORDER BY RANDOM()
    LIMIT {SAMPLE_SIZE}
    """
    try:
        df = con.execute(query).df()
        print(" [SQL] Data extraction and cleaning completed.")
    except Exception as e:
        print(f" [SQL] Error during SQL execution: {e}")
        return

    df['text_to_embed'] = (
        "Job ID: " + df['job_id'].astype(str) + ".\n " +
        "Job Title: " + df['title'].fillna("Unknown Role") + ".\n " +
        "Company: " + df['company_name'].fillna("Unknown Company") + ".\n " +
        "Location: " + df['location'].fillna("Unknown") + ".\n " +
        "Type: " + df['formatted_work_type'].fillna("Unknown") + ".\n " +
        "Description: " + df['description']+".\n " +
        "Skills: " + df['skills_desc'].fillna("Not Specified") + ".\n " +
        " Salary: " + df['max_salary'].astype(str).fillna("Not Specified") + " \n" + df['pay_period'].fillna("YEARLY")
    )

    print(f"Saving cleaned data to CSV...{OUTPUT_FILE}")
    df.to_csv(OUTPUT_FILE, index=False)
    print("Data saved successfully.")

if __name__ == "__main__":
    if not os.path.exists(DATA_DIR):
        print(f"❌ Error: Folder '{DATA_DIR}' not found.")
        print("   Please create a folder named 'Dataset' and put your Kaggle CSV files inside.")
    else:
        process_data()
    