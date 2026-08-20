"""
Script Consolidado de Extração de Insights & Validação de Heurísticas Antifraude
CloudWalk Technical Assessment — Data Analyst I
"""

import sys
import os
import importlib

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import views

importlib.reload(views)

con = views.con

def print_table(title: str, query: str):
    """Executa uma query no DuckDB e exibe os resultados formatados em tabela ASCII."""
    print("\n" + "="*80)
    print(f"📊 {title}")
    print("="*80)
    cursor = con.execute(query)
    columns = [desc[0] for desc in cursor.description]
    rows = cursor.fetchall()
    
    if not rows:
        print("Nenhum dado retornado.")
        return

    # Calculate column widths
    widths = [len(col) for col in columns]
    for row in rows:
        for i, val in enumerate(row):
            widths[i] = max(widths[i], len(str(val)))
            
    header = " | ".join(f"{col:<{widths[i]}}" for i, col in enumerate(columns))
    sep = "-+-".join("-" * widths[i] for i in range(len(columns)))
    print(header)
    print(sep)
    for row in rows:
        formatted_row = []
        for i, val in enumerate(row):
            if isinstance(val, float):
                formatted_row.append(f"{val:<{widths[i]}.2f}")
            else:
                formatted_row.append(f"{str(val):<{widths[i]}}")
        print(" | ".join(formatted_row))

def main():
    print("\n" + "#"*80)
    print("🛡️ CLOUDWALK ANTI-FRAUD INTELLIGENCE — RELATÓRIO CONSOLIDADO DE INSIGHTS")
    print("#"*80)

    # 1. Macro Métricas
    print_table("1. OVERVIEW MACRO DO PORTFÓLIO", "SELECT * FROM vw_overview_metrics")

    # 2. Comportamento e Riscos por Dispositivo
    print_table("2. RISCO POR TIPOLOGIA DE COMPORTAMENTO DO DISPOSITIVO", """
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

    # 3. Device Farming (Distribuição de Cartões por Aparelho)
    print_table("3. DEVICE FARMING: DISTRIBUIÇÃO DE CARTÕES POR APARELHO", """
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

    # 4. Sensibilidade por Faixa de Valor
    print_table("4. SENSIBILIDADE POR FAIXA DE VALOR (AMOUNT RANGE)", "SELECT * FROM vw_amount_range_analysis")

    # 5. Risco Temporal e Horários
    print_table("5. VULNERABILIDADE TEMPORAL (TURNOS DO DIA)", """
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

    # 6. Sequência de Tentativas do Usuário
    print_table("6. VELOCITY BURST: SEQUÊNCIA DA TENTATIVA DO USUÁRIO (N-th)", """
        SELECT 
            user_tx_seq,
            COUNT(*) as total_txs,
            SUM(has_cbk) as total_cbks,
            ROUND(SUM(has_cbk)*100.0/COUNT(*), 2) as cbk_rate_pct,
            ROUND(AVG(transaction_amount), 2) as avg_amount
        FROM vw_transaction_velocity
        GROUP BY user_tx_seq
        ORDER BY user_tx_seq
        LIMIT 15
    """)

    # 7. Sequência + Intervalo de Tempo
    print_table("7. VELOCIDADE: TENTATIVA × INTERVALO DE TEMPO", """
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
        LIMIT 20
    """)

    # 8. Categorização de Lojistas
    print_table("8. TIPIFICAÇÃO DE RISCO DOS LOJISTAS", """
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

    # 9. Top Lojistas Críticos
    print_table("9. TOP 10 LOJISTAS COM MAIOR PREJUÍZO ACUMULADO", """
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
        ORDER BY tt_value_cbk DESC
        LIMIT 10
    """)

    # 10. Heurística 1: Desvio de Valor vs Média Histórica
    print_table("10. HEURÍSTICA 1: DESVIO DE VALOR VS MÉDIA HISTÓRICA DO USUÁRIO", "SELECT * FROM vw_user_amount_deviation")

    # 11. Heurística 2: Constância de Dispositivos do Usuário
    print_table("11. HEURÍSTICA 2: CONSTÂNCIA DE DISPOSITIVOS POR USUÁRIO (1, 2 vs 3+)", "SELECT * FROM vw_user_device_expansion")

    # 12. Heurística 3: Migração de Cartão (Card Hopping)
    print_table("12. HEURÍSTICA 3: MIGRAÇÃO DE CARTÃO ENTRE USUÁRIOS (CARD HOPPING)", "SELECT * FROM vw_card_hopping_analysis")

    # 13. Heurística 4: Janelas de Velocidade (Burst Windows)
    print_table("13. HEURÍSTICA 4: JANELAS TEMPORAIS DE VELOCIDADE (BURST WINDOWS)", "SELECT * FROM vw_velocity_window_risk")

    # 14. Heurística 5: Merchant Hopping (Dispersão entre Lojistas)
    print_table("14. HEURÍSTICA 5: MERCHANT HOPPING (DIVERSIDADE DE LOJISTAS NO MESMO USUÁRIO)", "SELECT * FROM vw_merchant_hopping_analysis")

    # 15. Heurística 6: Probe & Scale (Escalação Abrupta de Valor)
    print_table("15. HEURÍSTICA 6: PROBE & SCALE (ESCALAÇÃO DE VALOR PÓS-APROVAÇÃO)", "SELECT * FROM vw_probe_and_scale_analysis")

    print("\n" + "="*80)
    print("✅ EXTRAÇÃO COMPLETA DE INSIGHTS E HEURÍSTICAS FINALIZADA!")
    print("="*80 + "\n")

if __name__ == "__main__":
    main()
