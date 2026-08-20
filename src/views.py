#%%
import duckdb

db_path = "data/transactions.sqlite"

# Initiate connection with DuckDB
con = duckdb.connect()

# Install and load SQLite extension
con.execute("INSTALL sqlite; LOAD sqlite")
# Attach the SQLite database file
con.execute(f"ATTACH '{db_path}' AS sqlite_db (TYPE SQLITE)")

#%%
con.execute("""
    CREATE OR REPLACE VIEW vw_overview_metrics AS
    SELECT
        COUNT(DISTINCT transaction_id) as qtt_transactions,
        ROUND(SUM(transaction_amount), 2) as tt_value_transactions,
        ROUND(AVG(transaction_amount), 2) as avg_value_transaction,
        ROUND(MAX(transaction_amount), 2) as max_value_transaction,
        ROUND(MIN(transaction_amount), 2) as min_value_transaction,
        COUNT(DISTINCT card_number) as qtt_cards,
        COUNT(DISTINCT device_id) as qtt_devices,
        COUNT(DISTINCT merchant_id) as qtt_merchants,
        SUM(CASE WHEN has_cbk THEN 1 ELSE 0 END) as qtt_cbk,
        ROUND(SUM(CASE WHEN has_cbk THEN transaction_amount ELSE 0 END), 2) as tt_value_cbk,
        ROUND(qtt_cbk * 100.0 / qtt_transactions, 2) AS pct_cbk,
        ROUND(tt_value_cbk * 100.0 / tt_value_transactions, 2) AS pct_value_cbk
    FROM sqlite_db.transactions;
""")

#%%
# Create a view for analyzing users profiles
con.execute("""
    CREATE OR REPLACE VIEW vw_user_risk_profile AS
    SELECT
        user_id,
        COUNT(DISTINCT transaction_id) as qtt_transactions,
        ROUND(SUM(transaction_amount), 2) as tt_value_transactions,
        ROUND(AVG(transaction_amount), 2) as avg_value_transaction,
        ROUND(MAX(transaction_amount), 2) as max_value_transaction,
        ROUND(MIN(transaction_amount), 2) as min_value_transaction,
        COUNT(DISTINCT card_number) as qtt_cards,
        COUNT(DISTINCT device_id) as qtt_devices,
        COUNT(DISTINCT merchant_id) as qtt_merchants,
        SUM(CASE WHEN has_cbk THEN 1 ELSE 0 END) as qtt_cbk,
        ROUND(SUM(CASE WHEN has_cbk THEN transaction_amount ELSE 0 END), 2) as tt_value_cbk,
        ROUND(qtt_cbk * 100.0 / qtt_transactions, 2) AS pct_cbk,
        ROUND(tt_value_cbk * 100.0 / tt_value_transactions, 2) AS pct_value_cbk
    FROM sqlite_db.transactions
    GROUP BY user_id
    ORDER BY pct_cbk DESC, tt_value_transactions DESC;
""")

# %%
con.execute("""
    CREATE OR REPLACE VIEW vw_merchant_risk_profile AS
    SELECT
        merchant_id,
        COUNT(DISTINCT transaction_id) as qtt_transactions,
        ROUND(SUM(transaction_amount), 2) as tt_value_transactions,
        ROUND(AVG(transaction_amount), 2) as avg_value_transaction,
        ROUND(MAX(transaction_amount), 2) as max_value_transaction,
        ROUND(MIN(transaction_amount), 2) as min_value_transaction,
        COUNT(DISTINCT card_number) as qtt_cards,
        COUNT(DISTINCT device_id) as qtt_devices,
        COUNT(DISTINCT user_id) as qtt_users,
        SUM(CASE WHEN has_cbk THEN 1 ELSE 0 END) as qtt_cbk,
        ROUND(SUM(CASE WHEN has_cbk THEN transaction_amount ELSE 0 END), 2) as tt_value_cbk,
        ROUND(SUM(CASE WHEN has_cbk THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS pct_cbk,
        ROUND(tt_value_cbk * 100.0 / tt_value_transactions, 2) AS pct_value_cbk,
        CASE WHEN pct_value_cbk > 1 THEN 'High Risk' ELSE 'Low Risk' END as risk_level
    FROM sqlite_db.transactions
    GROUP BY merchant_id
    ORDER BY pct_cbk DESC, tt_value_transactions DESC;
""")

#%%
con.execute("""
    CREATE OR REPLACE VIEW vw_device_and_card_sharing AS
    SELECT
        COALESCE(CAST(device_id AS VARCHAR), 'NO_DEVICE') AS device_id_label,
        COUNT(DISTINCT transaction_id) AS qtt_transactions,
        COUNT(DISTINCT user_id) AS qtt_users,
        COUNT(DISTINCT card_number) AS qtt_cards,
        COUNT(DISTINCT merchant_id) AS qtt_merchants,
        ROUND(SUM(transaction_amount), 2) AS tt_value_transaction,
        ROUND(AVG(transaction_amount), 2) AS avg_value_transaction,
        SUM(CASE WHEN has_cbk THEN 1 ELSE 0 END) AS qtt_cbk,
        ROUND(SUM(CASE WHEN has_cbk THEN transaction_amount ELSE 0 END), 2) AS tt_value_cbk,
        ROUND(SUM(CASE WHEN has_cbk THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS pct_cbk,
        -- Classificação do padrão de risco do dispositivo
        CASE 
            WHEN device_id IS NULL THEN 'Missing Device (High Risk)'
            WHEN COUNT(DISTINCT user_id) > 1 AND COUNT(DISTINCT card_number) > 1 THEN 'Device Farm / Multi-Account'
            WHEN COUNT(DISTINCT card_number) > 2 THEN 'Card Testing Multi-Card'
            WHEN COUNT(DISTINCT user_id) > 1 THEN 'Multi-User Single Device'
            ELSE 'Normal Device'
        END AS device_behavior_type
    FROM sqlite_db.transactions
    GROUP BY device_id
    ORDER BY qtt_cbk DESC, qtt_users DESC, qtt_cards DESC;
""")

# %%
con.execute("""
    CREATE OR REPLACE VIEW vw_card_sharing AS
    SELECT
        card_number,
        COUNT(DISTINCT transaction_id) AS qtt_transactions,
        COUNT(DISTINCT user_id) AS qtt_users,
        COUNT(DISTINCT device_id) AS qtt_devices,
        COUNT(DISTINCT merchant_id) AS qtt_merchants,
        ROUND(SUM(transaction_amount), 2) AS tt_value_transaction,
        SUM(CASE WHEN has_cbk THEN 1 ELSE 0 END) AS qtt_cbk,
        ROUND(SUM(CASE WHEN has_cbk THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS pct_cbk
    FROM sqlite_db.transactions
    GROUP BY card_number
    HAVING COUNT(DISTINCT user_id) > 1 OR COUNT(DISTINCT device_id) > 1 OR qtt_cbk > 0
    ORDER BY qtt_cbk DESC, qtt_users DESC, qtt_devices DESC;
""")
# %%
con.execute("""
    CREATE OR REPLACE VIEW vw_transaction_velocity AS
    WITH enriched_tx AS (
        SELECT 
            transaction_id,
            merchant_id,
            user_id,
            card_number,
            device_id,
            CAST(transaction_date AS TIMESTAMP) AS transaction_date,
            transaction_amount,
            has_cbk,
            -- Previous transaction by same user
            LAG(CAST(transaction_date AS TIMESTAMP)) OVER(
                PARTITION BY user_id
                ORDER BY CAST(transaction_date AS TIMESTAMP)
            ) AS prev_user_tx_date,
            LAG(transaction_amount) OVER(
                PARTITION BY user_id
                ORDER BY CAST(transaction_date AS TIMESTAMP)
            ) AS prev_user_tx_amount,
            LAG(merchant_id) OVER(
                PARTITION BY user_id
                ORDER BY CAST(transaction_date AS TIMESTAMP)
            ) AS prev_user_merchant_id,
            -- Previous transaction by same card
            LAG(CAST(transaction_date AS TIMESTAMP)) OVER (
                PARTITION BY card_number
                ORDER BY CAST(transaction_date AS TIMESTAMP)
            ) AS prev_card_tx_date,
            -- Sequential number of transactions for the same user
            ROW_NUMBER() OVER(
                PARTITION BY user_id
                ORDER BY CAST(transaction_date AS TIMESTAMP)
            ) AS user_tx_seq
        FROM sqlite_db.transactions            
    )
    SELECT 
        transaction_id,
        merchant_id,
        user_id,
        card_number,
        device_id,
        transaction_date,
        transaction_amount,
        has_cbk,
        user_tx_seq,
        prev_user_tx_date,
        -- Time difference for the last transaction of the same user (seconds and minutes)
        date_diff('second', prev_user_tx_date, transaction_date) AS user_diff_seconds,
        ROUND(date_diff('second', prev_user_tx_date, transaction_date)/60.0, 2) AS user_diff_minutes,
        -- Time difference for the previous transaction of the same card (seconds)
        date_diff('second', prev_card_tx_date, transaction_date) AS card_diff_seconds,
        -- Value variation
        ROUND(transaction_amount - COALESCE(prev_user_tx_amount, transaction_amount), 2) AS amount_diff,
        -- Comportamental Velocity Flags
        CASE 
            WHEN date_diff('second', prev_user_tx_date, transaction_date) <= 120 THEN 1
            ELSE 0
        END AS is_burst_2min,
        CASE
            WHEN date_diff('second', prev_user_tx_date, transaction_date) <= 600 THEN 1
            ELSE 0
        END AS is_burst_10min,
        CASE
            WHEN date_diff('second', prev_user_tx_date, transaction_date) <= 3600 THEN 1
            ELSE 0
        END AS is_burst_1h,
        CASE
            WHEN date_diff('second', prev_user_tx_date, transaction_date) <= 86400 THEN 1
            ELSE 0
        END AS is_burst_24h,
        CASE 
           WHEN merchant_id = prev_user_merchant_id AND date_diff('second', prev_user_tx_date, transaction_date) <= 300 THEN 1
           ELSE 0
        END AS is_same_merchant_burst
    FROM enriched_tx
    ORDER BY transaction_date;
""")

# %%
con.execute("""
    CREATE OR REPLACE VIEW vw_amount_range_analysis AS
    WITH ranked_amounts AS (
        SELECT
            transaction_id,
            transaction_amount,
            has_cbk,
            CASE 
                WHEN transaction_amount < 100 THEN '01. $ 0 - 100'
                WHEN transaction_amount < 500 THEN '02. $ 100 - 500'
                WHEN transaction_amount < 1000 THEN '03. $ 500 - 1.000'
                WHEN transaction_amount < 2000 THEN '04. $ 1.000 - 2.000'
                WHEN transaction_amount < 3500 THEN '05. $ 2.000 - 3.500'
                ELSE '06. > $ 3.500'
            END AS amount_range
        FROM sqlite_db.transactions
    )
    SELECT
        amount_range,
        COUNT(transaction_id) AS qtt_transactions,
        ROUND(SUM(transaction_amount), 2) AS tt_amount,
        ROUND(AVG(transaction_amount), 2) AS avg_amount,
        SUM(CASE WHEN has_cbk THEN 1 ELSE 0 END) AS qtt_cbk,
        ROUND(SUM(CASE WHEN has_cbk THEN transaction_amount ELSE 0 END), 2) AS tt_value_cbk,
        ROUND(SUM(CASE WHEN has_cbk THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS pct_cbk,
        ROUND(SUM(CASE WHEN has_cbk THEN transaction_amount ELSE 0 END) * 100.0 / SUM(transaction_amount), 2) AS pct_value_cbk
    FROM ranked_amounts
    GROUP BY amount_range
    ORDER BY amount_range;
""")

# %%
con.execute("""
    CREATE OR REPLACE VIEW vw_temporal_hourly_risk AS
    WITH hourly_tx AS (
        SELECT
            transaction_id,
            transaction_amount,
            CAST(transaction_date AS TIMESTAMP) AS transaction_date,
            has_cbk,
            hour(CAST(transaction_date AS TIMESTAMP)) AS tx_hour,
            CASE 
                WHEN hour(CAST(transaction_date AS TIMESTAMP)) BETWEEN 0 AND 5 THEN 'Midnight (00h-06h)'
                WHEN hour(CAST(transaction_date AS TIMESTAMP)) BETWEEN 6 AND 11 THEN 'Morning (06h-12h)'
                WHEN hour(CAST(transaction_date AS TIMESTAMP)) BETWEEN 12 AND 17 THEN 'Afternoon (12h-18h)'
                ELSE 'Evening (18h-24h)'
            END AS time_period
        FROM sqlite_db.transactions
    )
    SELECT
        tx_hour,
        time_period,
        COUNT(transaction_id) AS qtt_transactions,
        ROUND(SUM(transaction_amount), 2) AS tt_value_transactions,
        ROUND(AVG(transaction_amount), 2) AS avg_value_transaction,
        SUM(CASE WHEN has_cbk THEN 1 ELSE 0 END) AS qtt_cbk,
        ROUND(SUM(CASE WHEN has_cbk THEN transaction_amount ELSE 0 END), 2) AS tt_value_cbk,
        ROUND(SUM(CASE WHEN has_cbk THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS pct_cbk,
        ROUND(SUM(CASE WHEN has_cbk THEN transaction_amount ELSE 0 END) * 100.0 / SUM(transaction_amount), 2) AS pct_value_cbk
    FROM hourly_tx
    GROUP BY tx_hour, time_period
    ORDER BY tx_hour;
""")
