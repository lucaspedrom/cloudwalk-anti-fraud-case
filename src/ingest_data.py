# %%
import duckdb
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(BASE_DIR, "security-test", "transactional-sample.csv")
DB_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(DB_DIR, "transactions.sqlite")

def run_ingestion(csv_path=CSV_PATH, db_path=DB_PATH, verbose=True):
    """
    Ingests transactional CSV data into SQLite and creates performance indexes.
    Ensures idempotency (creates or updates records).
    """
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Source CSV file not found at: {csv_path}")

    con = duckdb.connect()
    con.execute("INSTALL sqlite; LOAD sqlite")
    
    norm_db_path = db_path.replace("\\", "/")
    norm_csv_path = csv_path.replace("\\", "/")
    
    con.execute(f"ATTACH '{norm_db_path}' AS sqlite_db (TYPE SQLITE)")

    table_exists = con.execute("""
        SELECT count(*)
        FROM information_schema.tables
        WHERE table_name = 'transactions'
    """).fetchone()[0]

    # Check if table exists and create it if not
    if table_exists == 0:
        con.execute("""
            CREATE TABLE IF NOT EXISTS sqlite_db.transactions (
                transaction_id BIGINT PRIMARY KEY,
                merchant_id BIGINT NOT NULL,
                user_id BIGINT NOT NULL,
                card_number VARCHAR NOT NULL,
                transaction_date TIMESTAMP NOT NULL,
                transaction_amount DOUBLE NOT NULL,
                device_id BIGINT,
                has_cbk BOOLEAN NOT NULL
            );
        """)
        con.execute(f"""
            INSERT INTO sqlite_db.transactions
            SELECT 
                CAST(transaction_id AS BIGINT) AS transaction_id,
                CAST(merchant_id AS BIGINT) AS merchant_id,
                CAST(user_id AS BIGINT) AS user_id,
                CAST(card_number AS VARCHAR) AS card_number,
                CAST(transaction_date AS TIMESTAMP) AS transaction_date,
                CAST(transaction_amount AS DOUBLE) AS transaction_amount,
                CAST(device_id AS BIGINT) AS device_id,
                CAST(has_cbk AS BOOLEAN) AS has_cbk
            FROM read_csv_auto('{norm_csv_path}');
        """)
        if verbose:
            print("✅ Table `transactions` successfully created and populated in SQLite.")
    else:
        database_records = con.execute("""
            SELECT count(*)
            FROM sqlite_db.transactions
        """).fetchone()[0]

        csv_records = con.execute(f"""
            SELECT count(*) FROM read_csv_auto('{norm_csv_path}')
        """).fetchone()[0]
        
        # Check if database is updated with the csv file
        if database_records == csv_records:
            if verbose:
                print(f"ℹ️ Database verified and up to date ({database_records} records).")
        else:
            con.execute(f"""
                INSERT INTO sqlite_db.transactions 
                SELECT            
                    CAST(transaction_id AS BIGINT) AS transaction_id,
                    CAST(merchant_id AS BIGINT) AS merchant_id,
                    CAST(user_id AS BIGINT) AS user_id,
                    CAST(card_number AS VARCHAR) AS card_number,
                    CAST(transaction_date AS TIMESTAMP) AS transaction_date,
                    CAST(transaction_amount AS DOUBLE) AS transaction_amount,
                    CAST(device_id AS BIGINT) AS device_id,
                    CAST(has_cbk AS BOOLEAN) AS has_cbk
                FROM read_csv_auto('{norm_csv_path}')
                WHERE transaction_id NOT IN (SELECT transaction_id FROM sqlite_db.transactions);
            """)
            if verbose:
                print(f"🔄 Database updated: {csv_records - database_records} new records inserted.")

    # Creation of index to speed up queries
    indexes = [
        "CREATE INDEX IF NOT EXISTS idx_tx_id ON sqlite_db.main.transactions(transaction_id);",
        "CREATE INDEX IF NOT EXISTS idx_user_id ON sqlite_db.main.transactions(user_id);",
        "CREATE INDEX IF NOT EXISTS idx_merchant_id ON sqlite_db.main.transactions(merchant_id);",
        "CREATE INDEX IF NOT EXISTS idx_card_number ON sqlite_db.main.transactions(card_number);",
        "CREATE INDEX IF NOT EXISTS idx_device_id ON sqlite_db.main.transactions(device_id);",
        "CREATE INDEX IF NOT EXISTS idx_date ON sqlite_db.main.transactions(transaction_date);",
    ]

    for idx in indexes:
        con.execute(idx)
        
    con.close()
    return True

if __name__ == "__main__":
    run_ingestion()
