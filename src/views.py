import duckdb
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "transactions.sqlite")

# Garante que o banco de dados e a tabela transactions existam antes de criar as VIEWs
try:
    from . import ingest_data
except ImportError:
    import ingest_data

ingest_data.run_ingestion(db_path=DB_PATH, verbose=False)

# Initiate connection with DuckDB
con = duckdb.connect()

# Install and load SQLite extension
con.execute("INSTALL sqlite; LOAD sqlite")

norm_db_path = DB_PATH.replace("\\", "/")
con.execute(f"ATTACH '{norm_db_path}' AS sqlite_db (TYPE SQLITE)")

def init_views(con_target=con):
    """Garante a criação de todas as VIEWs no DuckDB."""
    pass

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

# %%
# Heurística 1: Desvio de Valor vs Média Histórica do Próprio Usuário
con.execute("""
    CREATE OR REPLACE VIEW vw_user_amount_deviation AS
    WITH user_history AS (
        SELECT 
            transaction_id,
            user_id,
            transaction_amount,
            has_cbk,
            CAST(transaction_date AS TIMESTAMP) AS tx_dt,
            AVG(transaction_amount) OVER(
                PARTITION BY user_id 
                ORDER BY CAST(transaction_date AS TIMESTAMP) 
                ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING
            ) AS hist_avg_amount
        FROM sqlite_db.transactions
    )
    SELECT 
        CASE 
            WHEN hist_avg_amount IS NULL THEN '1. Primeira Compra (Sem Histórico)'
            WHEN transaction_amount > (hist_avg_amount * 2.5) THEN '2. Desvio Extremo (> 250% da Média)'
            WHEN transaction_amount > (hist_avg_amount * 1.5) THEN '3. Desvio Moderado (150% a 250%)'
            ELSE '4. Dentro do Padrão (<= 150%)'
        END AS user_amount_anomaly_group,
        COUNT(*) AS total_txs,
        SUM(CASE WHEN has_cbk THEN 1 ELSE 0 END) AS total_cbks,
        ROUND(SUM(CASE WHEN has_cbk THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS pct_cbk,
        ROUND(SUM(transaction_amount), 2) AS total_vol,
        ROUND(SUM(CASE WHEN has_cbk THEN transaction_amount ELSE 0 END), 2) AS cbk_vol,
        ROUND(SUM(CASE WHEN has_cbk THEN transaction_amount ELSE 0 END) * 100.0 / SUM(transaction_amount), 2) AS pct_cbk_vol,
        ROUND(AVG(transaction_amount), 2) AS avg_ticket
    FROM user_history
    GROUP BY user_amount_anomaly_group
    ORDER BY user_amount_anomaly_group;
""")

# %%
# Heurística 2: Constância de Dispositivos por Usuário (1, 2 vs 3+ Aparelhos)
con.execute("""
    CREATE OR REPLACE VIEW vw_user_device_expansion AS
    WITH user_devices AS (
        SELECT 
            user_id,
            COUNT(DISTINCT device_id) AS qtt_devices,
            COUNT(*) AS total_txs,
            SUM(CASE WHEN has_cbk THEN 1 ELSE 0 END) AS total_cbks,
            ROUND(SUM(transaction_amount), 2) AS total_vol,
            ROUND(SUM(CASE WHEN has_cbk THEN transaction_amount ELSE 0 END), 2) AS cbk_vol
        FROM sqlite_db.transactions
        GROUP BY user_id
    )
    SELECT 
        CASE 
            WHEN qtt_devices = 1 THEN '1 Dispositivo Único'
            WHEN qtt_devices = 2 THEN '2 Dispositivos (Monitoramento)'
            WHEN qtt_devices >= 3 THEN '3+ Dispositivos (Alto Risco)'
            ELSE 'Sem Dispositivo Registrado'
        END AS user_devices_group,
        COUNT(user_id) AS qtt_users,
        SUM(total_txs) AS total_txs,
        SUM(total_cbks) AS total_cbks,
        ROUND(SUM(total_cbks) * 100.0 / SUM(total_txs), 2) AS pct_cbk,
        ROUND(SUM(cbk_vol) * 100.0 / SUM(total_vol), 2) AS pct_cbk_vol,
        ROUND(SUM(total_vol) / SUM(total_txs), 2) AS avg_ticket
    FROM user_devices
    GROUP BY user_devices_group
    ORDER BY pct_cbk_vol DESC;
""")

# %%
# Heurística 3: Migração de Cartões entre Múltiplos Usuários (Card Hopping)
con.execute("""
    CREATE OR REPLACE VIEW vw_card_hopping_analysis AS
    WITH card_users AS (
        SELECT 
            card_number,
            COUNT(DISTINCT user_id) AS qtt_users_on_card,
            COUNT(DISTINCT device_id) AS qtt_devices_on_card,
            COUNT(*) AS total_txs,
            SUM(CASE WHEN has_cbk THEN 1 ELSE 0 END) AS total_cbks,
            ROUND(SUM(transaction_amount), 2) AS total_vol,
            ROUND(SUM(CASE WHEN has_cbk THEN transaction_amount ELSE 0 END), 2) AS cbk_vol
        FROM sqlite_db.transactions
        GROUP BY card_number
    )
    SELECT 
        CASE 
            WHEN qtt_users_on_card = 1 AND qtt_devices_on_card = 1 THEN '1 Usuário & 1 Dispositivo'
            WHEN qtt_users_on_card = 1 AND qtt_devices_on_card > 1 THEN '1 Usuário em Múltiplos Dispositivos'
            WHEN qtt_users_on_card = 2 THEN '2 Usuários no Mesmo Cartão (Card Hopping)'
            ELSE '3+ Usuários no Mesmo Cartão'
        END AS card_sharing_pattern,
        COUNT(card_number) AS qtt_cards,
        SUM(total_txs) AS total_txs,
        SUM(total_cbks) AS total_cbks,
        ROUND(SUM(total_cbks) * 100.0 / SUM(total_txs), 2) AS pct_cbk,
        ROUND(SUM(cbk_vol) * 100.0 / SUM(total_vol), 2) AS pct_cbk_vol,
        ROUND(SUM(total_vol) / SUM(total_txs), 2) AS avg_ticket
    FROM card_users
    GROUP BY card_sharing_pattern
    ORDER BY pct_cbk_vol DESC;
""")

# %%
# Heurística 4: Janelas Temporais de Velocidade (Burst Windows)
con.execute("""
    CREATE OR REPLACE VIEW vw_velocity_window_risk AS
    WITH tx_interval AS (
        SELECT 
            transaction_id,
            user_id,
            card_number,
            has_cbk,
            transaction_amount,
            date_diff('second', 
                LAG(CAST(transaction_date AS TIMESTAMP)) OVER (
                    PARTITION BY user_id ORDER BY CAST(transaction_date AS TIMESTAMP)
                ), 
                CAST(transaction_date AS TIMESTAMP)
            ) AS seconds_since_last_tx
        FROM sqlite_db.transactions
    )
    SELECT 
        CASE 
            WHEN seconds_since_last_tx IS NULL THEN '0. Primeira Transação do Usuário'
            WHEN seconds_since_last_tx <= 60 THEN '1. Super Rajada (<= 1 min)'
            WHEN seconds_since_last_tx <= 300 THEN '2. Rajada Rápida (1 a 5 min)'
            WHEN seconds_since_last_tx <= 1800 THEN '3. Janela Curta (5 a 30 min)'
            WHEN seconds_since_last_tx <= 86400 THEN '4. Janela Média (30 min a 24h)'
            ELSE '5. Mais de 24h / Espaçado'
        END AS velocity_window,
        COUNT(*) AS total_txs,
        SUM(CASE WHEN has_cbk THEN 1 ELSE 0 END) AS total_cbks,
        ROUND(SUM(CASE WHEN has_cbk THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS pct_cbk,
        ROUND(SUM(CASE WHEN has_cbk THEN transaction_amount ELSE 0 END) * 100.0 / SUM(transaction_amount), 2) AS pct_cbk_vol,
        ROUND(AVG(transaction_amount), 2) AS avg_ticket
    FROM tx_interval
    GROUP BY velocity_window
""")

# %%
# Heurística 5: Merchant Hopping (Dispersão entre Múltiplos Lojistas pelo mesmo Usuário)
con.execute("""
    CREATE OR REPLACE VIEW vw_merchant_hopping_analysis AS

    WITH user_merchants AS (
        SELECT 
            user_id,
            COUNT(DISTINCT merchant_id) AS qtt_merchants,
            COUNT(*) AS total_txs,
            SUM(CASE WHEN has_cbk THEN 1 ELSE 0 END) AS total_cbks,
            ROUND(SUM(transaction_amount), 2) AS total_vol,
            ROUND(SUM(CASE WHEN has_cbk THEN transaction_amount ELSE 0 END), 2) AS cbk_vol
        FROM sqlite_db.transactions
        GROUP BY user_id
    )
    SELECT 
        CASE 
            WHEN qtt_merchants = 1 THEN '1. Um Único Lojista'
            WHEN qtt_merchants = 2 THEN '2. Dois Lojistas Distintos'
            ELSE '3. Três ou Mais Lojistas (Merchant Hopping)'
        END AS merchant_diversity_group,
        COUNT(user_id) AS qtt_users,
        SUM(total_txs) AS total_txs,
        SUM(total_cbks) AS total_cbks,
        ROUND(SUM(total_cbks) * 100.0 / SUM(total_txs), 2) AS pct_cbk,
        ROUND(SUM(cbk_vol) * 100.0 / SUM(total_vol), 2) AS pct_cbk_vol,
        ROUND(SUM(total_vol) / SUM(total_txs), 2) AS avg_ticket
    FROM user_merchants
    GROUP BY merchant_diversity_group
    ORDER BY merchant_diversity_group;
""")

# %%
# Heurística 6: Probe & Scale (Escalação Abrupta de Valor pós-Aprovação)
con.execute("""
    CREATE OR REPLACE VIEW vw_probe_and_scale_analysis AS
    WITH user_growth AS (
        SELECT 
            transaction_id,
            user_id,
            transaction_amount,
            has_cbk,
            LAG(transaction_amount) OVER(
                PARTITION BY user_id 
                ORDER BY CAST(transaction_date AS TIMESTAMP)
            ) AS prev_amount
        FROM sqlite_db.transactions
    )
    SELECT 
        CASE 
            WHEN prev_amount IS NULL THEN '1. Primeira Transação (Sem Anterior)'
            WHEN transaction_amount > prev_amount * 2 THEN '2. Escalação Abrupta (> 2x da anterior)'
            WHEN transaction_amount > prev_amount THEN '3. Aumento Moderado (1x a 2x)'
            WHEN transaction_amount = prev_amount THEN '4. Mesmo Valor Repetido'
            ELSE '5. Valor Menor que a Anterior'
        END AS amount_progression_group,
        COUNT(*) AS total_txs,
        SUM(CASE WHEN has_cbk THEN 1 ELSE 0 END) AS total_cbks,
        ROUND(SUM(CASE WHEN has_cbk THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS pct_cbk,
        ROUND(SUM(transaction_amount), 2) AS total_vol,
        ROUND(SUM(CASE WHEN has_cbk THEN transaction_amount ELSE 0 END), 2) AS cbk_vol,
        ROUND(SUM(CASE WHEN has_cbk THEN transaction_amount ELSE 0 END) * 100.0 / SUM(transaction_amount), 2) AS pct_cbk_vol,
        ROUND(AVG(transaction_amount), 2) AS avg_ticket
    FROM user_growth
    GROUP BY amount_progression_group
    ORDER BY amount_progression_group;
""")


