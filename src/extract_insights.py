import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import views

con = views.con

def print_table(title, query):
    print("\n" + "="*70)
    print(title)
    print("="*70)
    cursor = con.execute(query)
    columns = [desc[0] for desc in cursor.description]
    rows = cursor.fetchall()
    
    # Calculate widths
    widths = [len(col) for col in columns]
    for row in rows:
        for i, val in enumerate(row):
            widths[i] = max(widths[i], len(str(val)))
            
    header = " | ".join(f"{col:<{widths[i]}}" for i, col in enumerate(columns))
    sep = "-+-".join("-" * widths[i] for i in range(len(columns)))
    print(header)
    print(sep)
    for row in rows:
        print(" | ".join(f"{str(val):<{widths[i]}}" for i, val in enumerate(row)))

print_table("1. OVERVIEW METRICS", "SELECT * FROM vw_overview_metrics")

print_table("2. DEVICE BEHAVIOR RISK", """
    SELECT 
        device_behavior_type,
        COUNT(*) as devices,
        SUM(qtt_transactions) as txs,
        SUM(qtt_cbk) as cbks,
        ROUND(SUM(qtt_cbk) * 100.0 / SUM(qtt_transactions), 2) as cbk_tx_rate_pct,
        ROUND(SUM(tt_value_cbk) * 100.0 / SUM(tt_value_transaction), 2) as cbk_val_rate_pct,
        ROUND(AVG(avg_value_transaction), 2) as avg_ticket
    FROM vw_device_and_card_sharing
    GROUP BY device_behavior_type
    ORDER BY cbk_tx_rate_pct DESC
""")

print_table("3. VELOCITY BURST (CONSECUTIVE TRANSACTIONS)", """
    SELECT 
        is_burst_2min,
        is_burst_10min,
        is_burst_1h,
        is_burst_24h,
        COUNT(*) as total_txs,
        SUM(has_cbk) as total_cbks,
        ROUND(SUM(has_cbk) * 100.0 / COUNT(*), 2) as cbk_rate_pct,
        ROUND(AVG(transaction_amount), 2) as avg_amount
    FROM vw_transaction_velocity
    WHERE prev_user_tx_date IS NOT NULL
    GROUP BY is_burst_2min, is_burst_10min, is_burst_1h, is_burst_24h
    ORDER BY is_burst_2min DESC, is_burst_10min DESC, is_burst_1h DESC, is_burst_24h DESC
""")

print_table("4. AMOUNT RANGE RISK", "SELECT * FROM vw_amount_range_analysis")

print_table("5. HOURLY & TIME PERIOD RISK", """
    SELECT 
        time_period,
        SUM(qtt_transactions) as total_txs,
        SUM(qtt_cbk) as total_cbks,
        ROUND(SUM(qtt_cbk) * 100.0 / SUM(qtt_transactions), 2) as cbk_rate_pct,
        ROUND(AVG(avg_value_transaction), 2) as avg_ticket
    FROM vw_temporal_hourly_risk
    GROUP BY time_period
    ORDER BY cbk_rate_pct DESC
""")

print_table("6. TOP HIGH RISK MERCHANTS", """
    SELECT 
        merchant_id,
        qtt_transactions,
        tt_value_transactions,
        qtt_cbk,
        tt_value_cbk,
        pct_cbk,
        pct_value_cbk,
        risk_level
    FROM vw_merchant_risk_profile
    WHERE qtt_cbk > 0
    ORDER BY pct_value_cbk DESC, tt_value_cbk DESC
    LIMIT 10
""")

# 7. Histograma de cartões por dispositivo
print_table("7. CARDS PER DEVICE DISTRIBUTION (DEVICE FARMING DEEP-DIVE)", """
    WITH dev_cards AS (
        SELECT 
            device_id,
            COUNT(DISTINCT card_number) as num_cards,
            COUNT(*) as txs,
            SUM(has_cbk) as cbks,
            SUM(transaction_amount) as tt_val,
            SUM(CASE WHEN has_cbk THEN transaction_amount ELSE 0 END) as cbk_val
        FROM sqlite_db.transactions
        WHERE device_id IS NOT NULL
        GROUP BY device_id
    )
    SELECT 
        num_cards,
        COUNT(*) as count_devices,
        SUM(txs) as total_txs,
        SUM(cbks) as total_cbks,
        ROUND(SUM(cbks)*100.0/SUM(txs), 2) as cbk_tx_rate_pct,
        ROUND(SUM(cbk_val)*100.0/SUM(tt_val), 2) as cbk_val_rate_pct,
        ROUND(SUM(tt_val)/SUM(txs), 2) as avg_ticket
    FROM dev_cards
    GROUP BY num_cards
    ORDER BY num_cards
""")

# 8. Sequência de transações do usuário (1ª, 2ª, 3ª, 4ª tentativa)
print_table("8. USER TRANSACTION SEQUENCE (N-th TRANSACTION IN A ROW)", """
    WITH user_seq AS (
        SELECT 
            user_id,
            user_tx_seq,
            has_cbk,
            transaction_amount
        FROM vw_transaction_velocity
    )
    SELECT 
        user_tx_seq,
        COUNT(*) as total_txs,
        SUM(has_cbk) as total_cbks,
        ROUND(SUM(has_cbk)*100.0/COUNT(*), 2) as cbk_rate_pct,
        ROUND(AVG(transaction_amount), 2) as avg_amount
    FROM user_seq
    GROUP BY user_tx_seq
    ORDER BY user_tx_seq
""")

# 9. Cruzamento: Sequência + Intervalo de Tempo
print_table("9. VELOCITY DEEP DIVE: TRANSACTION SEQUENCE + TIME INTERVAL", """
    SELECT 
        user_tx_seq,
        CASE 
            WHEN user_diff_seconds <= 120 THEN '1. <= 2 min'
            WHEN user_diff_seconds <= 600 THEN '2. 2 a 10 min'
            WHEN user_diff_seconds <= 3600 THEN '3. 10 a 60 min'
            ELSE '4. > 60 min'
        END as time_interval,
        COUNT(*) as total_txs,
        SUM(has_cbk) as total_cbks,
        ROUND(SUM(has_cbk)*100.0/COUNT(*), 2) as cbk_rate_pct,
        ROUND(AVG(transaction_amount), 2) as avg_amount
    FROM vw_transaction_velocity
    WHERE prev_user_tx_date IS NOT NULL
    GROUP BY user_tx_seq, time_interval
    ORDER BY user_tx_seq, time_interval
""")

# 10. Lojistas: Linhas de corte por volume de chargebacks
print_table("10. MERCHANT RISK CATEGORIZATION (MINIMUM CHARGEBACK THRESHOLD)", """
    SELECT 
        CASE 
            WHEN qtt_cbk >= 4 AND pct_value_cbk > 1 THEN 'High Risk (Established Fraud)'
            WHEN qtt_transactions <= 3 AND pct_cbk >= 100.0 THEN 'High Risk (Fraudulent Onboarding)'
            WHEN qtt_cbk BETWEEN 1 AND 3 THEN 'Indeterminate / Watchlist (1-3 cbks)'
            ELSE 'Low Risk (0 cbks)'
        END as merchant_category,
        COUNT(*) as count_merchants,
        SUM(qtt_transactions) as total_txs,
        ROUND(SUM(tt_value_transactions), 2) as total_vol,
        SUM(qtt_cbk) as total_cbks,
        ROUND(SUM(tt_value_cbk), 2) as total_cbk_vol,
        ROUND(SUM(qtt_cbk)*100.0/SUM(qtt_transactions), 2) as cbk_tx_rate,
        ROUND(SUM(tt_value_cbk)*100.0/SUM(tt_value_transactions), 2) as cbk_val_rate
    FROM vw_merchant_risk_profile
    GROUP BY merchant_category
    ORDER BY cbk_val_rate DESC
""")
