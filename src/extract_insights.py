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
