# %%
import duckdb
import os

csv_path = "security-test/transactional-sample.csv"
db_path = "data/transactions.sqlite"

con = duckdb.connect()

con.execute("INSTALL sqlite; LOAD sqlite")
con.execute(f"ATTACH '{db_path}' AS sqlite_db (TYPE SQLITE)")

table_exists = con.execute ("""
        SELECT count(*)
        FROM information_schema.tables
        WHERE table_name = 'transactions'
    """).fetchone()[0]

# Check if table exists and create it if not
if table_exists == 0:
    con.execute(f"""
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
        FROM read_csv_auto('{csv_path}');
    """)
    print("`transactions` table sucessfully created.")
else:
    database_records = con.execute("""
        SELECT count(*)
        FROM sqlite_db.transactions
    """).fetchone()[0]

    csv_records = con.execute(f"""
        SELECT count(*) FROM read_csv_auto('{csv_path}')
    """).fetchone()[0]
    # Check if database is updated with the csv file
    if database_records == csv_records:
        print("Database already created and updated.")
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
            FROM read_csv_auto('{csv_path}')
            WHERE transaction_id NOT IN (SELECT transaction_id FROM sqlite_db.transactions);
        """)
        print(f"Database updated. {csv_records - database_records} new rows inserted.")

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