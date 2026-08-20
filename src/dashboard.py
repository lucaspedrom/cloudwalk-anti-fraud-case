import streamlit as st
import duckdb
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import sys
import importlib

# Set up paths and auto-reload views
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import views
importlib.reload(views)

# Page Configuration
st.set_page_config(
    page_title="CloudWalk Anti-Fraud Intelligence",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
    }
    .metric-card {
        background: linear-gradient(135deg, #1e2638 0%, #151a24 100%);
        border: 1px solid #2d3748;
        border-radius: 12px;
        padding: 16px;
        color: #ffffff;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }
    .metric-value {
        font-size: 22px;
        font-weight: 700;
        color: #00d26a;
    }
    .metric-label {
        font-size: 12px;
        color: #a0aec0;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .highlight-red {
        color: #f5365c;
    }
    
    /* Menu Navigation Button Styles */
    div[data-testid="stSidebar"] .stButton > button {
        width: 100%;
        text-align: left;
        display: flex;
        align-items: center;
        justify-content: flex-start;
        padding: 0.65rem 1rem;
        border-radius: 10px;
        font-size: 0.92rem;
        font-weight: 600;
        transition: all 0.2s ease-in-out;
        margin-bottom: 0.35rem;
    }
    div[data-testid="stSidebar"] .stButton > button[kind="secondary"] {
        background-color: rgba(255, 255, 255, 0.04);
        border: 1px solid rgba(255, 255, 255, 0.08);
        color: #cbd5e0;
    }
    div[data-testid="stSidebar"] .stButton > button[kind="secondary"]:hover {
        background-color: rgba(255, 255, 255, 0.12);
        border-color: rgba(255, 255, 255, 0.25);
        color: #ffffff;
        transform: translateX(4px);
    }
    div[data-testid="stSidebar"] .stButton > button[kind="primary"] {
        background: linear-gradient(90deg, #00d26a 0%, #00b05b 100%);
        border: 1px solid #00d26a;
        color: #0d1117;
        font-weight: 700;
        box-shadow: 0 4px 12px rgba(0, 210, 106, 0.3);
    }
    div[data-testid="stSidebar"] .stButton > button[kind="primary"]:hover {
        background: linear-gradient(90deg, #00e875 0%, #00c465 100%);
        border-color: #00e875;
    }
    
    /* Strategy Cards */
    .strategy-card {
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 15px;
        color: #ffffff;
    }
    .card-green {
        background: linear-gradient(135deg, rgba(0, 210, 106, 0.12) 0%, rgba(0, 176, 91, 0.04) 100%);
        border: 1px solid #00d26a;
    }
    .card-yellow {
        background: linear-gradient(135deg, rgba(254, 176, 25, 0.12) 0%, rgba(217, 119, 6, 0.04) 100%);
        border: 1px solid #feb019;
    }
    .card-red {
        background: linear-gradient(135deg, rgba(245, 54, 92, 0.12) 0%, rgba(225, 29, 72, 0.04) 100%);
        border: 1px solid #f5365c;
    }
    .card-blue {
        background: linear-gradient(135deg, rgba(37, 99, 235, 0.12) 0%, rgba(30, 58, 138, 0.04) 100%);
        border: 1px solid #3b82f6;
    }
    </style>
""", unsafe_allow_html=True)

# Connection with DuckDB
con = views.con

# ==============================================================================
# SELETOR DE IDIOMA / LANGUAGE SELECTOR
# ==============================================================================
st.sidebar.markdown("### 🌐 Idioma / Language")
lang_option = st.sidebar.radio(
    "Selecione o idioma / Select language:",
    ["🇧🇷 Português", "🇺🇸 English"],
    index=0,
    horizontal=True,
    label_visibility="collapsed"
)
is_en = (lang_option == "🇺🇸 English")

# ==============================================================================
# DICIONÁRIO DE INTERNACIONALIZAÇÃO (I18N & GRAPH LABELS)
# ==============================================================================
LABEL_MAPS = {
    "user_amount_anomaly_group": {
        "1. Primeira Compra (Sem Histórico)": "1. First Purchase (No History)",
        "2. Desvio Extremo (> 250% da Média)": "2. Extreme Spike (> 250% of Avg)",
        "3. Desvio Moderado (150% a 250%)": "3. Moderate Spike (150% to 250%)",
        "4. Dentro do Padrão (<= 150%)": "4. Typical Range (<= 150%)"
    },
    "user_devices_group": {
        "1 Dispositivo Único": "1 Unique Device",
        "2 Dispositivos (Monitoramento)": "2 Devices (Monitoring)",
        "3+ Dispositivos (Alto Risco)": "3+ Devices (High Risk)",
        "Sem Dispositivo Registrado": "No Device Registered"
    },
    "card_sharing_pattern": {
        "1 Usuário & 1 Dispositivo": "1 User & 1 Device",
        "1 Usuário em Múltiplos Dispositivos": "1 User on Multi-Devices",
        "2 Usuários no Mesmo Cartão (Card Hopping)": "2 Users on Same Card (Hopping)",
        "3+ Usuários no Mesmo Cartão": "3+ Users on Same Card"
    },
    "velocity_window": {
        "0. Primeira Transação do Usuário": "0. 1st User Transaction",
        "1. Super Rajada (<= 1 min)": "1. Super Burst (<= 1 min)",
        "2. Rajada Rápida (1 a 5 min)": "2. Fast Burst (1 to 5 min)",
        "3. Janela Curta (5 a 30 min)": "3. Short Window (5 to 30 min)",
        "4. Janela Média (30 min a 24h)": "4. Mid Window (30 min to 24h)",
        "5. Mais de 24h / Espaçado": "5. > 24h / Spaced"
    },
    "merchant_diversity_group": {
        "1. Um Único Lojista": "1. Single Merchant",
        "2. Dois Lojistas Distintos": "2. Two Distinct Merchants",
        "3. Três ou Mais Lojistas (Merchant Hopping)": "3. 3+ Distinct Stores (Hopping)"
    },
    "amount_progression_group": {
        "1. Primeira Transação (Sem Anterior)": "1. 1st Transaction (No Prior)",
        "2. Escalação Abrupta (> 2x da anterior)": "2. Abrupt Spike (> 2x Prior)",
        "3. Aumento Moderado (1x a 2x)": "3. Moderate Increase (1x to 2x)",
        "4. Mesmo Valor Repetido": "4. Exact Same Amount",
        "5. Valor Menor que a Anterior": "5. Lower than Prior Amount"
    },
    "time_period_pt": {
        "Midnight (00h-06h)": "Madrugada (00h-06h)",
        "Morning (06h-12h)": "Manhã (06h-12h)",
        "Afternoon (12h-18h)": "Tarde (12h-18h)",
        "Evening (18h-24h)": "Noite (18h-24h)"
    }
}

I18N = {
    "hub_title": "Anti-Fraud Hub" if is_en else "Antifraude Hub",
    "case_sub": "Technical Assessment: Data Analyst I" if is_en else "Case Técnico: Data Analyst I",
    "nav_header": "Main Menu" if is_en else "Menu Principal",
    "dataset_info": "💡 **Dataset:** 3,199 mobile transactions with real chargeback tags." if is_en else "💡 **Dataset:** 3.199 transações móveis com marcação de chargebacks reais.",
    "menu_items": [
        {
            "id": "page_1",
            "label": "📊  1. Dataset Overview" if is_en else "📊  1. Apresentação da Base",
            "desc": "Executive metrics and macro KPIs" if is_en else "Visão executiva e KPIs macro"
        },
        {
            "id": "page_2",
            "label": "🔍  2. Fraud Patterns & Analysis" if is_en else "🔍  2. Padrões & Diagnóstico",
            "desc": "Amounts, schedules and device farming" if is_en else "Valores, horários e aparelhos"
        },
        {
            "id": "page_3",
            "label": "🚨  3. Critical Entities" if is_en else "🚨  3. Entidades Críticas",
            "desc": "Merchants, cards, devices and accounts" if is_en else "Lojistas, cartões e contas"
        },
        {
            "id": "page_4",
            "label": "🎯  4. Insights & Policy Proposal" if is_en else "🎯  4. Insights & Proposta",
            "desc": "Heuristics, 3-path matrix and engine architecture" if is_en else "Heurísticas, matriz de 3 vias e motor"
        }
    ]
}

if "selected_page" not in st.session_state:
    st.session_state.selected_page = "page_1"

# Sidebar Navigation Header
st.sidebar.title(I18N["hub_title"])
st.sidebar.markdown(f"**{I18N['case_sub']}**")
st.sidebar.markdown("---")
st.sidebar.markdown(f"### {I18N['nav_header']}")

for item in I18N["menu_items"]:
    is_active = (st.session_state.selected_page == item["id"])
    btn_type = "primary" if is_active else "secondary"
    
    if st.sidebar.button(
        item["label"],
        key=f"nav_{item['id']}",
        use_container_width=True,
        type=btn_type,
        help=item["desc"]
    ):
        st.session_state.selected_page = item["id"]
        st.rerun()

current_page = st.session_state.selected_page
st.sidebar.markdown("---")
st.sidebar.info(I18N["dataset_info"])


# ==============================================================================
# PÁGINA 1: APRESENTAÇÃO DA BASE DE DADOS / DATASET OVERVIEW
# ==============================================================================
if current_page == "page_1":
    if is_en:
        st.header("Transactional Portfolio Overview")
        st.markdown("Executive summary and macro KPIs of the analyzed payments dataset.")
    else:
        st.header("Panorama Geral da Base Transacional")
        st.markdown("Visão executiva e métricas macro do portfólio de pagamentos analisado.")
    
    overview = con.execute("SELECT * FROM vw_overview_metrics").df().iloc[0]
    
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">{"Total Transactions" if is_en else "Total Transações"}</div>
                <div class="metric-value">{int(overview['qtt_transactions']):,}</div>
                <small style="color:#a0aec0">100% Mobile</small>
            </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">{"Total Volume ($)" if is_en else "Volume Total ($)"}</div>
                <div class="metric-value">$ {overview['tt_value_transactions']:,.2f}</div>
                <small style="color:#a0aec0">{"Avg Ticket" if is_en else "Ticket Médio"}: $ {overview['avg_value_transaction']:,.2f}</small>
            </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">{"Total Chargebacks" if is_en else "Total Chargebacks"}</div>
                <div class="metric-value highlight-red">{int(overview['qtt_cbk'])} txs</div>
                <small class="highlight-red"><b>{overview['pct_cbk']:.2f}%</b> {"of total" if is_en else "do total"}</small>
            </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">{"Fraud Loss ($)" if is_en else "Prejuízo Fraude ($)"}</div>
                <div class="metric-value highlight-red">$ {overview['tt_value_cbk']:,.2f}</div>
                <small class="highlight-red"><b>{overview['pct_value_cbk']:.2f}%</b> {"of revenue" if is_en else "do faturamento"}</small>
            </div>
        """, unsafe_allow_html=True)
    with col5:
        avg_cbk_ticket = overview['tt_value_cbk'] / overview['qtt_cbk'] if overview['qtt_cbk'] > 0 else 0
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">{"Fraud Avg Ticket" if is_en else "Ticket Médio Fraude"}</div>
                <div class="metric-value highlight-red">$ {avg_cbk_ticket:,.2f}</div>
                <small style="color:#f5365c">+116% vs {"Legitimate" if is_en else "Legítimo"}</small>
            </div>
        """, unsafe_allow_html=True)
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Donut Charts
    c_chart1, c_chart2 = st.columns(2)
    with c_chart1:
        labels_tx = ['Legitimate (Approved)', 'Fraud (Chargeback)'] if is_en else ['Legítimas (Aprovadas)', 'Fraudes (Chargebacks)']
        fig_donut_tx = go.Figure(data=[go.Pie(
            labels=labels_tx,
            values=[overview['qtt_transactions'] - overview['qtt_cbk'], overview['qtt_cbk']],
            hole=.55,
            marker_colors=['#00d26a', '#f5365c']
        )])
        fig_donut_tx.update_layout(
            title="Distribution by Transaction Count" if is_en else "Distribuição por Quantidade de Transações",
            template="plotly_dark",
            margin=dict(t=40, b=20, l=20, r=20),
            height=320
        )
        st.plotly_chart(fig_donut_tx, use_container_width=True)
        
    with c_chart2:
        labels_val = ['Legitimate Volume ($)', 'Fraud Volume ($)'] if is_en else ['Volume Legítimo ($)', 'Volume Fraude ($)']
        fig_donut_val = go.Figure(data=[go.Pie(
            labels=labels_val,
            values=[overview['tt_value_transactions'] - overview['tt_value_cbk'], overview['tt_value_cbk']],
            hole=.55,
            marker_colors=['#00d26a', '#f5365c']
        )])
        fig_donut_val.update_layout(
            title="Distribution by Financial Volume ($)" if is_en else "Distribuição por Volume Financeiro ($)",
            template="plotly_dark",
            margin=dict(t=40, b=20, l=20, r=20),
            height=320
        )
        st.plotly_chart(fig_donut_val, use_container_width=True)

    # Data Sample Explorer
    st.subheader("📋 Sample Data Explorer" if is_en else "📋 Amostra dos Dados Transacionais")
    filter_opts = ["All Transactions", "Chargebacks Only (Fraud)", "Legitimate Only"] if is_en else ["Todas as Transações", "Apenas Chargebacks (Fraudes)", "Apenas Transações Legítimas"]
    filter_type = st.radio("Filter data by status:" if is_en else "Filtrar dados por status:", filter_opts, horizontal=True)
    
    where_clause = ""
    if filter_type in ["Chargebacks Only (Fraud)", "Apenas Chargebacks (Fraudes)"]:
        where_clause = "WHERE has_cbk = 1"
    elif filter_type in ["Legitimate Only", "Apenas Transações Legítimas"]:
        where_clause = "WHERE has_cbk = 0"
        
    df_sample = con.execute(f"SELECT * FROM sqlite_db.transactions {where_clause} LIMIT 100").df()
    st.dataframe(df_sample, use_container_width=True, height=280)


# ==============================================================================
# PÁGINA 2: ANÁLISES & PADRÕES DE FRAUDE / FRAUD PATTERNS
# ==============================================================================
elif current_page == "page_2":
    if is_en:
        st.header("Analytical Diagnosis & Fraud Patterns")
        st.markdown("In-depth investigation across dimensions revealing fraudulent behavior.")
    else:
        st.header("Análises Realizadas & Diagnóstico de Fraude")
        st.markdown("Investigação profunda das dimensões que revelam o comportamento fraudulento.")
    
    # 1. Risco por Faixa de Valor
    st.subheader("1. Ticket Size Risk Sensitivity" if is_en else "1. Sensibilidade por Faixa de Valor (Ticket Size Risk)")
    df_amount = con.execute("SELECT * FROM vw_amount_range_analysis").df()
    
    fig_amount = px.bar(
        df_amount,
        x="amount_range",
        y="pct_cbk",
        text="pct_cbk",
        title="Chargeback Rate (%) by Amount Range" if is_en else "Taxa de Chargeback (%) por Faixa de Valor",
        labels={"amount_range": "Amount Range" if is_en else "Faixa de Valor", "pct_cbk": "Chargeback Rate (%)" if is_en else "Taxa de Chargeback (%)"},
        color="pct_cbk",
        color_continuous_scale="Reds"
    )
    fig_amount.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    fig_amount.update_layout(template="plotly_dark", height=380)
    st.plotly_chart(fig_amount, use_container_width=True)
    
    if is_en:
        st.info(r"💡 **Insight:** Transactions up to \$ 500 show low risk (< 4.2%). Above **\$ 3,500**, exactly **50% of transactions are fraudulent**. Instead of a blind Hard Block, we recommend **Step-Up 3DS 2.0 / Biometrics** to avoid rejecting legitimate high-value customers.")
    else:
        st.info(r"💡 **Insight:** Compras até \$ 500 apresentam baixo risco (< 4,2%). Acima de **\$ 3.500**, exatamente **50% das transações são fraudes**. Em vez de Hard Block cego, recomendamos **Desafio 3DS 2.0 / Biometria** para não recusar os 50% de clientes legítimos.")
    
    st.markdown("---")
    
    # 2. Padrão Temporal e Horário
    st.subheader("2. Temporal Vulnerability (Hours & Day Periods)" if is_en else "2. Vulnerabilidade Temporal (Horários e Turnos)")
    col_t1, col_t2 = st.columns(2)
    
    with col_t1:
        df_hourly = con.execute("""
            SELECT 
                time_period,
                SUM(qtt_transactions) as total_txs,
                SUM(qtt_cbk) as total_cbks,
                ROUND(SUM(qtt_cbk) * 100.0 / SUM(qtt_transactions), 2) as cbk_rate_pct,
                ROUND(AVG(avg_value_transaction), 2) as avg_ticket
            FROM vw_temporal_hourly_risk
            GROUP BY time_period
            ORDER BY cbk_rate_pct DESC
        """).df()
        
        if not is_en:
            df_hourly["time_period"] = df_hourly["time_period"].map(LABEL_MAPS["time_period_pt"]).fillna(df_hourly["time_period"])
        
        fig_period = px.bar(
            df_hourly,
            x="time_period",
            y="cbk_rate_pct",
            text="cbk_rate_pct",
            title="Fraud Rate (%) by Day Period" if is_en else "Taxa de Fraude (%) por Turno do Dia",
            labels={"time_period": "Period" if is_en else "Turno", "cbk_rate_pct": "Fraud Rate (%)" if is_en else "Taxa Fraude (%)"},
            color="cbk_rate_pct",
            color_continuous_scale="Viridis"
        )
        fig_period.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        fig_period.update_layout(template="plotly_dark", height=340)
        st.plotly_chart(fig_period, use_container_width=True)

        
    with col_t2:
        df_hours_24 = con.execute("SELECT tx_hour, pct_cbk FROM vw_temporal_hourly_risk ORDER BY tx_hour").df()
        fig_hours = px.line(
            df_hours_24,
            x="tx_hour",
            y="pct_cbk",
            markers=True,
            title="Risk Curve across 24 Hours (00h to 23h)" if is_en else "Curva de Risco por Hora do Dia (00h às 23h)",
            labels={"tx_hour": "Hour of Day" if is_en else "Hora do Dia", "pct_cbk": "Chargeback Rate (%)" if is_en else "Taxa de Chargeback (%)"},
            line_shape="spline"
        )
        fig_hours.update_layout(template="plotly_dark", height=340)
        st.plotly_chart(fig_hours, use_container_width=True)
        
    st.markdown("---")
    
    # 3. Dispositivos e Múltiplos Cartões
    st.subheader("3. Device Farming & Multi-Card Concentration" if is_en else "3. Device Farming & Concentração de Cartões por Aparelho")
    
    df_dev_cards = con.execute("""
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
    """).df()
    
    fig_dev = px.bar(
        df_dev_cards,
        x="num_cards",
        y="cbk_val_rate_pct",
        text="cbk_val_rate_pct",
        title="Financial Loss (%) vs. Number of Cards per Device" if is_en else "Perda Financeira por Fraude (%) vs. Qtd de Cartões no Dispositivo",
        labels={"num_cards": "Cards per Device" if is_en else "Cartões Distintos no Aparelho", "cbk_val_rate_pct": "% Financial Loss" if is_en else "% Perda Financeira ($)"},
        color="cbk_val_rate_pct",
        color_continuous_scale="Reds"
    )
    fig_dev.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    fig_dev.update_layout(template="plotly_dark", height=380)
    st.plotly_chart(fig_dev, use_container_width=True)
    
    if is_en:
        st.info("💡 **Derived Rule:** Devices with 3 to 4 cards trigger **Step-Up (3DS)**. Devices with **more than 4 cards** cause over **89% financial loss**, justifying an **Immediate Hard Decline**.")
    else:
        st.info("💡 **Regra Derivada:** Dispositivos com 3 a 4 cartões entram em **Step-Up (3DS)**. Aparelhos com **mais de 4 cartões** geram mais de **89% de perda**, justificando o **Hard Block Imediato**.")

    st.markdown("---")
    
    # 4. Velocidade e Tentativas Seguidas
    st.subheader("4. Velocity Burst & Consecutive Retries" if is_en else "4. Velocidade de Disparo e Retentativas (Velocity Burst)")
    
    df_velocity_summary = con.execute("""
        SELECT 
            user_tx_seq,
            COUNT(*) as total_txs,
            SUM(has_cbk) as total_cbks,
            ROUND(SUM(has_cbk)*100.0/COUNT(*), 2) as cbk_rate_pct
        FROM vw_transaction_velocity
        WHERE user_tx_seq <= 15
        GROUP BY user_tx_seq
        ORDER BY user_tx_seq
    """).df()
    
    fig_vel = px.line(
        df_velocity_summary,
        x="user_tx_seq",
        y="cbk_rate_pct",
        markers=True,
        title="Fraud Probability by Attempt Sequence Order (1st to 15th+ retry)" if is_en else "Probabilidade de Fraude pela Ordem da Tentativa do Usuário (1ª à 15ª+ tentativa)",
        labels={"user_tx_seq": "Attempt Sequence Number" if is_en else "N-ésima Tentativa do Usuário", "cbk_rate_pct": "Chargeback Rate (%)" if is_en else "Taxa de Chargeback (%)"},
        color_discrete_sequence=["#f5365c"]
    )
    fig_vel.update_layout(template="plotly_dark", height=350)
    st.plotly_chart(fig_vel, use_container_width=True)


# ==============================================================================
# PÁGINA 3: PRINCIPAIS ENTIDADES CRÍTICAS / CRITICAL ENTITIES
# ==============================================================================
elif current_page == "page_3":
    if is_en:
        st.header("Key Critical Entities Associated with Fraud")
        st.markdown("Detailed investigation of merchants, devices, users and shared cards concentrating risk.")
        tab_names = ["🏪 High-Risk Merchants", "📱 Suspicious Devices (Device Farming)", "👤 Critical Users", "💳 Shared Cards (Card Hopping)"]
    else:
        st.header("Principais Entidades Associadas a Fraude")
        st.markdown("Identificação detalhada dos atores que mais concentraram prejuízos.")
        tab_names = ["🏪 Lojistas de Alto Risco", "📱 Dispositivos Suspeitos (Device Farming)", "👤 Usuários Críticos", "💳 Cartões Compartilhados (Card Hopping)"]
    
    entity_tab1, entity_tab2, entity_tab3, entity_tab4 = st.tabs(tab_names)
    
    # 1. Lojistas
    with entity_tab1:
        st.subheader("Merchant Risk Categorization" if is_en else "Classificação de Risco dos Estabelecimentos Comerciais")
        df_merchants_cat = con.execute("""
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
        """).df()
        st.dataframe(df_merchants_cat, use_container_width=True)
        
        st.subheader("Top 15 Merchants with Highest Accumulated Loss" if is_en else "Top 15 Lojistas com Maior Prejuízo Acumulado")
        df_top_merchants = con.execute("""
            SELECT merchant_id, qtt_transactions, tt_value_transactions, qtt_cbk, tt_value_cbk, pct_cbk, pct_value_cbk, risk_level
            FROM vw_merchant_risk_profile
            WHERE qtt_cbk > 0
            ORDER BY tt_value_cbk DESC, pct_value_cbk DESC
            LIMIT 15
        """).df()
        st.dataframe(df_top_merchants, use_container_width=True)

    # 2. Dispositivos
    with entity_tab2:
        st.subheader("Devices Involved in Multi-Card Fraud & Emulation" if is_en else "Dispositivos Utilizados para Fraudes e Multi-Contas")
        df_top_devices = con.execute("""
            SELECT device_id_label, qtt_transactions, qtt_users, qtt_cards, qtt_merchants, tt_value_transaction, qtt_cbk, tt_value_cbk, pct_cbk, device_behavior_type
            FROM vw_device_and_card_sharing
            WHERE qtt_cbk > 0 OR qtt_cards > 2 OR qtt_users > 1
            ORDER BY qtt_cbk DESC, qtt_cards DESC
            LIMIT 20
        """).df()
        st.dataframe(df_top_devices, use_container_width=True)

    # 3. Usuários
    with entity_tab3:
        st.subheader("Users with History of Chargebacks and Multi-Cards" if is_en else "Usuários com Histórico de Chargebacks e Multi-Cartão")
        df_top_users = con.execute("""
            SELECT user_id, qtt_transactions, tt_value_transactions, avg_value_transaction, qtt_cards, qtt_devices, qtt_merchants, qtt_cbk, tt_value_cbk, pct_cbk
            FROM vw_user_risk_profile
            WHERE qtt_cbk > 0
            ORDER BY qtt_cbk DESC, tt_value_cbk DESC
            LIMIT 20
        """).df()
        st.dataframe(df_top_users, use_container_width=True)

    # 4. Cartões Compartilhados
    with entity_tab4:
        st.subheader("Cards with Hopping or Distributed Attacks" if is_en else "Cartões com Card Hopping ou Ataques Distribuídos")
        df_top_cards = con.execute("""
            SELECT card_number, qtt_transactions, qtt_users, qtt_devices, qtt_merchants, tt_value_transaction, qtt_cbk, pct_cbk
            FROM vw_card_sharing
            WHERE qtt_cbk > 0 OR qtt_users > 1
            ORDER BY qtt_cbk DESC, qtt_users DESC
            LIMIT 20
        """).df()
        st.dataframe(df_top_cards, use_container_width=True)


# ==============================================================================
# PÁGINA 4: INSIGHTS & PROPOSTA RECOMENDADA / INSIGHTS & POLICY PROPOSAL
# ==============================================================================
elif current_page == "page_4":
    if is_en:
        st.header("Diagnostic Insights & Anti-Fraud Policy Proposal")
        st.markdown("Comprehensive strategy for financial loss mitigation, revenue preservation, and real-time decision engine architecture.")
        tabs_p4_names = [
            "💡 1. Analytical Heuristics & Evidence",
            "🛡️ 2. 3-Path Policy Matrix",
            "⚙️ 3. Real-Time Engine Architecture",
            "🌐 4. Next-Gen Data Enrichment"
        ]
    else:
        st.header("Insights Diagnósticos & Proposta de Solução Antifraude")
        st.markdown("Estratégia completa para mitigação de risco financeiro, preservação de receita legítima e arquitetura do motor de decisão em tempo real.")
        tabs_p4_names = [
            "💡 1. Heurísticas & Diagnóstico Analítico",
            "🛡️ 2. Matriz de Políticas (3 Vias)",
            "⚙️ 3. Arquitetura do Motor de Decisão",
            "🌐 4. Dados para Próxima Geração"
        ]
    
    # KPI Row
    kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
    with kpi_col1:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">{"Fraud Prevention" if is_en else "Prevenção de Fraude"}</div>
                <div class="metric-value">> 85%</div>
                <small style="color:#00d26a">{"+$480k saved" if is_en else "+$ 480 mil salvos"}</small>
            </div>
        """, unsafe_allow_html=True)
    with kpi_col2:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">{"Good Volume Approval" if is_en else "Aprovação Legítima"}</div>
                <div class="metric-value">> 90%</div>
                <small style="color:#00d26a">{"Zero friction" if is_en else "Sem atrito comercial"}</small>
            </div>
        """, unsafe_allow_html=True)
    with kpi_col3:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">{"Target Fraud Rate" if is_en else "Taxa de Fraude Alvo"}</div>
                <div class="metric-value">< 2.5%</div>
                <small class="highlight-red">{"Down from 23.14%" if is_en else "Queda de 23,14% inicial"}</small>
            </div>
        """, unsafe_allow_html=True)
    with kpi_col4:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">{"Engine Latency" if is_en else "Latência do Motor"}</div>
                <div class="metric-value">< 10 ms</div>
                <small style="color:#a0aec0">{"In-memory real-time" if is_en else "Tempo real in-memory"}</small>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    tab_ins1, tab_ins2, tab_ins3, tab_ins4 = st.tabs(tabs_p4_names)

    # --------------------------------------------------------------------------
    # TAB 1: HEURÍSTICAS & DIAGNÓSTICO ANALÍTICO
    # --------------------------------------------------------------------------
    with tab_ins1:
        st.subheader("Quantitative Evidence Supporting Anti-Fraud Rules" if is_en else "Embasamento Estatístico das Heurísticas Antifraude")
        st.markdown("Proven quantitative validations extracted directly from the transactions dataset underpinning each decision rule:" if is_en else "Comprovações quantitativas extraídas diretamente da base transacional real que fundamentam cada regra de decisão:")

        # Heurísticas 1 & 2
        col_h1, col_h2 = st.columns(2)
        with col_h1:
            st.markdown("##### 1. " + ("Amount Deviation vs. User Historical Average" if is_en else "Desvio de Valor vs. Média Histórica do Próprio Usuário"))
            df_dev_amt = con.execute("SELECT * FROM vw_user_amount_deviation").df()
            if is_en:
                df_dev_amt["user_amount_anomaly_group"] = df_dev_amt["user_amount_anomaly_group"].map(LABEL_MAPS["user_amount_anomaly_group"]).fillna(df_dev_amt["user_amount_anomaly_group"])
            
            fig_h1 = px.bar(
                df_dev_amt,
                x="user_amount_anomaly_group",
                y="pct_cbk_vol",
                text="pct_cbk_vol",
                title="% Financial Loss by User Amount Deviation" if is_en else "% Perda Financeira por Grau de Desvio do Padrão do Usuário",
                labels={"user_amount_anomaly_group": "Pattern" if is_en else "Padrão de Compra", "pct_cbk_vol": "% Loss" if is_en else "% Perda Financeira"},
                color="pct_cbk_vol",
                color_continuous_scale="Reds"
            )
            fig_h1.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
            fig_h1.update_layout(template="plotly_dark", height=320, xaxis_tickangle=-15)
            st.plotly_chart(fig_h1, use_container_width=True)
            if is_en:
                st.caption(r"💡 **Rule:** When user exceeds **> 250%** of their historical average ticket, fraud loss jumps to **68.3%**. Trigger **Yellow Path (3DS 2.0)** to verify legitimate cardholder.")
            else:
                st.caption(r"💡 **Regra:** Se o usuário tentar uma compra **> 250%** da sua média histórica, a perda salta para **68,3%**. Ativar **Yellow Path (3DS 2.0)** para verificar se é o titular genuíno.")

        with col_h2:
            st.markdown("##### 2. " + ("Device Consistency per User (1, 2 vs. 3+ Devices)" if is_en else "Constância de Dispositivos por Usuário (1, 2 vs. 3+ Aparelhos)"))
            df_user_dev = con.execute("SELECT * FROM vw_user_device_expansion").df()
            if is_en:
                df_user_dev["user_devices_group"] = df_user_dev["user_devices_group"].map(LABEL_MAPS["user_devices_group"]).fillna(df_user_dev["user_devices_group"])
            
            fig_h2 = px.bar(
                df_user_dev,
                x="user_devices_group",
                y="pct_cbk_vol",
                text="pct_cbk_vol",
                title="% Financial Loss by Linked Devices per User" if is_en else "% Perda Financeira conforme Qtd de Aparelhos do Usuário",
                labels={"user_devices_group": "Devices Linked" if is_en else "Dispositivos Vinculados", "pct_cbk_vol": "% Loss" if is_en else "% Perda Financeira"},
                color="pct_cbk_vol",
                color_continuous_scale="Reds"
            )
            fig_h2.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
            fig_h2.update_layout(template="plotly_dark", height=320)
            st.plotly_chart(fig_h2, use_container_width=True)
            if is_en:
                st.caption(r"💡 **Rule:** Users with 1 device have controlled risk (23.8% loss). When a **3rd device appears on the account**, fraud loss spikes to **81.1%**. Trigger **Yellow Path / Facial Biometrics**.")
            else:
                st.caption(r"💡 **Regra:** Usuários com 1 aparelho têm risco controlado (23,8% vol). Ao surgir um **3º aparelho no mesmo cadastro**, a perda sobe para **81,1%**. Ativar **Yellow Path / Biometria Facial**.")

        st.markdown("---")

        # Heurísticas 3 & 4
        col_h3, col_h4 = st.columns(2)
        with col_h3:
            st.markdown("##### 3. " + ("Card Hopping (Shared Card across Distinct Users)" if is_en else "Migração Repentina de Cartão (Card Hopping entre Usuários)"))
            df_card_hop = con.execute("SELECT * FROM vw_card_hopping_analysis").df()
            if is_en:
                df_card_hop["card_sharing_pattern"] = df_card_hop["card_sharing_pattern"].map(LABEL_MAPS["card_sharing_pattern"]).fillna(df_card_hop["card_sharing_pattern"])
            
            fig_h3 = px.bar(
                df_card_hop,
                x="card_sharing_pattern",
                y="pct_cbk_vol",
                text="pct_cbk_vol",
                title="% Financial Loss by Card Sharing Pattern" if is_en else "% Perda Financeira por Compartilhamento de Cartão",
                labels={"card_sharing_pattern": "Sharing Pattern" if is_en else "Padrão de Uso do Cartão", "pct_cbk_vol": "% Loss" if is_en else "% Perda Financeira"},
                color="pct_cbk_vol",
                color_continuous_scale="Reds"
            )
            fig_h3.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
            fig_h3.update_layout(template="plotly_dark", height=320, xaxis_tickangle=-15)
            st.plotly_chart(fig_h3, use_container_width=True)
            if is_en:
                st.caption(r"💡 **Rule:** A card historically used by one user that suddenly appears on a **second user account** reaches **67.3% fraud loss**. Trigger **Yellow Path**.")
            else:
                st.caption(r"💡 **Regra:** Cartão com histórico em um usuário que surge subitamente em um **segundo usuário/conta** atinge **67,3% de perda**. Ativar **Yellow Path** (ou Red Path se device for farming).")

        with col_h4:
            st.markdown("##### 4. " + ("Velocity Burst Windows (Consecutive Retries)" if is_en else "Janelas Temporais de Velocidade & Rajadas (Burst Windows)"))
            df_vel_win = con.execute("SELECT * FROM vw_velocity_window_risk").df()
            if is_en:
                df_vel_win["velocity_window"] = df_vel_win["velocity_window"].map(LABEL_MAPS["velocity_window"]).fillna(df_vel_win["velocity_window"])
            
            fig_h4 = px.bar(
                df_vel_win,
                x="velocity_window",
                y="pct_cbk_vol",
                text="pct_cbk_vol",
                title="% Financial Loss by Time Interval between Attempts" if is_en else "% Perda Financeira por Intervalo entre Tentativas",
                labels={"velocity_window": "Time Interval" if is_en else "Janela de Tempo", "pct_cbk_vol": "% Loss" if is_en else "% Perda Financeira"},
                color="pct_cbk_vol",
                color_continuous_scale="Reds"
            )
            fig_h4.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
            fig_h4.update_layout(template="plotly_dark", height=320, xaxis_tickangle=-15)
            st.plotly_chart(fig_h4, use_container_width=True)
            if is_en:
                st.caption(r"💡 **Rule:** 1st transaction has 11.5% loss. Retries in short windows (<= 30 min) concentrate over **70% loss**. Trigger **Yellow Path** on 3rd/4th retry and **Red Path** on >= 5th.")
            else:
                st.caption(r"💡 **Regra:** A 1ª transação tem apenas 11,5% de perda. Rajadas em janelas curtas (&le; 30 min) concentram mais de **70% de prejuízo**. Ativar **Yellow Path** na 3ª/4ª tentativa e **Red Path** na &ge; 5ª.")

        st.markdown("---")

        # Heurísticas 5 & 6 (Merchant Hopping & Probe & Scale)
        col_h5, col_h6 = st.columns(2)
        with col_h5:
            st.markdown("##### 5. " + ("Merchant Hopping (User Buying across Multiple Stores)" if is_en else "Merchant Hopping (Dispersão entre Múltiplos Lojistas)"))
            df_m_hop = con.execute("SELECT * FROM vw_merchant_hopping_analysis").df()
            if is_en:
                df_m_hop["merchant_diversity_group"] = df_m_hop["merchant_diversity_group"].map(LABEL_MAPS["merchant_diversity_group"]).fillna(df_m_hop["merchant_diversity_group"])
            
            fig_h5 = px.bar(
                df_m_hop,
                x="merchant_diversity_group",
                y="pct_cbk_vol",
                text="pct_cbk_vol",
                title="% Financial Loss by Merchant Diversity per User" if is_en else "% Perda Financeira por Diversidade de Lojistas no Usuário",
                labels={"merchant_diversity_group": "Merchant Count" if is_en else "Qtd Lojistas Distintos", "pct_cbk_vol": "% Loss" if is_en else "% Perda Financeira"},
                color="pct_cbk_vol",
                color_continuous_scale="Reds"
            )
            fig_h5.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
            fig_h5.update_layout(template="plotly_dark", height=320)
            st.plotly_chart(fig_h5, use_container_width=True)
            if is_en:
                st.caption(r"💡 **Rule:** Users transacting with **3 or more distinct merchants** concentrate **88.4% fraud loss** (vs. 16.5% for single merchant). Trigger **Yellow Path** / Cooldown.")
            else:
                st.caption(r"💡 **Regra:** Usuários que compram em **3 ou mais lojistas distintos** concentram **88,4% de perda financeira** (vs. 16,5% em lojista único). Ativar **Yellow Path**.")

        with col_h6:
            st.markdown("##### 6. " + ("Probe & Scale (Abrupt Amount Escalation post-Trial)" if is_en else "Probe & Scale (Escalação Abrupta de Valor pós-Aprovação)"))
            df_probe = con.execute("SELECT * FROM vw_probe_and_scale_analysis").df()
            if is_en:
                df_probe["amount_progression_group"] = df_probe["amount_progression_group"].map(LABEL_MAPS["amount_progression_group"]).fillna(df_probe["amount_progression_group"])
            
            fig_h6 = px.bar(
                df_probe,
                x="amount_progression_group",
                y="pct_cbk_vol",
                text="pct_cbk_vol",
                title="% Financial Loss by Amount Progression Sequence" if is_en else "% Perda Financeira por Progressão de Valor entre Tentativas",
                labels={"amount_progression_group": "Progression" if is_en else "Progressão de Valor", "pct_cbk_vol": "% Loss" if is_en else "% Perda Financeira"},
                color="pct_cbk_vol",
                color_continuous_scale="Reds"
            )
            fig_h6.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
            fig_h6.update_layout(template="plotly_dark", height=320, xaxis_tickangle=-15)
            st.plotly_chart(fig_h6, use_container_width=True)
            if is_en:
                st.caption(r"💡 **Rule:** When amount abruptly jumps to **> 2x of previous attempt**, fraud loss reaches **64.6%** with high avg ticket (\$ 1,346). Trigger **Yellow Path (3DS)**.")
            else:
                st.caption(r"💡 **Regra:** Quando o valor salta para **> 2x da tentativa anterior**, a perda financeira atinge **64,6%** com ticket médio alto (\$ 1.346). Ativar **Yellow Path (3DS)**.")


    # --------------------------------------------------------------------------
    # TAB 2: MATRIZ DE POLÍTICAS (3 VIAS)
    # --------------------------------------------------------------------------
    with tab_ins2:
        if is_en:
            st.subheader("3-Path Decision Matrix (Green / Yellow / Red Paths)")
            st.markdown("Optimal balance between **frictionless checkout**, **sales conversion** and **fraud defense**.")
        else:
            st.subheader("Matriz de Decisão em 3 Vias (Green / Yellow / Red Paths)")
            st.markdown("Equilíbrio ideal entre **experiência do cliente**, **conversão comercial** e **blindagem contra fraudes**.")
        
        m_col1, m_col2, m_col3 = st.columns(3)
        
        with m_col1:
            if is_en:
                st.markdown(r"""
                    <div class="strategy-card card-green" style="height: 100%;">
                        <h3 style="color:#00d26a; margin-top:0;">🟢 Green Path</h3>
                        <h5 style="color:#a0aec0; margin-top:-5px;">Instant Frictionless Approval</h5>
                        <hr style="border-color:rgba(0, 210, 106, 0.3);">
                        <p><b>Trigger Conditions:</b></p>
                        <ul style="font-size:0.88rem; line-height:1.6; padding-left:18px;">
                            <li>Ticket up to <b>$ 500.00</b></li>
                            <li>Within user historical pattern (&le; 150% avg)</li>
                            <li>Habitual device (1st or 2nd linked device)</li>
                            <li>1st or 2nd spaced attempt</li>
                            <li>Exclusive card ownership</li>
                            <li>Merchant with clean chargeback record</li>
                        </ul>
                        <hr style="border-color:rgba(0, 210, 106, 0.3);">
                        <p style="font-size:0.85rem; color:#00d26a;"><b>Impact:</b> Zero friction and maximum conversion for > 85% of genuine volume.</p>
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(r"""
                    <div class="strategy-card card-green" style="height: 100%;">
                        <h3 style="color:#00d26a; margin-top:0;">🟢 Green Path</h3>
                        <h5 style="color:#a0aec0; margin-top:-5px;">Aprovação Fluida Instantânea</h5>
                        <hr style="border-color:rgba(0, 210, 106, 0.3);">
                        <p><b>Gatilhos de Aplicação:</b></p>
                        <ul style="font-size:0.88rem; line-height:1.6; padding-left:18px;">
                            <li>Ticket até <b>$ 500,00</b></li>
                            <li>Dentro do padrão habitual do usuário (&le; 150% da média)</li>
                            <li>Dispositivo habitual (1º ou 2º aparelho cadastrado)</li>
                            <li>1ª ou 2ª tentativa espaçada</li>
                            <li>Cartão de uso exclusivo do usuário</li>
                            <li>Lojista sem histórico negativo de chargebacks</li>
                        </ul>
                        <hr style="border-color:rgba(0, 210, 106, 0.3);">
                        <p style="font-size:0.85rem; color:#00d26a;"><b>Impacto:</b> Zero atrito e máxima conversão para mais de 85% das vendas genuínas.</p>
                    </div>
                """, unsafe_allow_html=True)
            
        with m_col2:
            if is_en:
                st.markdown(r"""
                    <div class="strategy-card card-yellow" style="height: 100%;">
                        <h3 style="color:#feb019; margin-top:0;">🟡 Yellow Path</h3>
                        <h5 style="color:#a0aec0; margin-top:-5px;">Step-Up Authentication</h5>
                        <hr style="border-color:rgba(254, 176, 25, 0.3);">
                        <p><b>Trigger Conditions:</b></p>
                        <ul style="font-size:0.88rem; line-height:1.6; padding-left:18px;">
                            <li><b>Amount Spike:</b> Ticket <b>> 250%</b> of user historical average</li>
                            <li><b>Device Expansion:</b> <b>3rd device</b> linked to user account</li>
                            <li><b>Card Hopping:</b> Card appearing on a <b>different user account</b></li>
                            <li><b>Merchant Hopping:</b> User transacting on <b>3+ distinct stores</b></li>
                            <li><b>Probe & Scale:</b> Value <b>> 2x</b> of previous immediate attempt</li>
                            <li>Ticket <b>> $ 3,500.00</b> during business hours</li>
                        </ul>
                        <hr style="border-color:rgba(254, 176, 25, 0.3);">
                        <p style="font-size:0.85rem; color:#feb019;"><b>Action:</b> 3D-Secure 2.0 Challenge / Facial Biometrics in App. If authenticated, <b>approve with Liability Shift</b>.</p>
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(r"""
                    <div class="strategy-card card-yellow" style="height: 100%;">
                        <h3 style="color:#feb019; margin-top:0;">🟡 Yellow Path</h3>
                        <h5 style="color:#a0aec0; margin-top:-5px;">Autenticação Reforçada (Step-Up)</h5>
                        <hr style="border-color:rgba(254, 176, 25, 0.3);">
                        <p><b>Gatilhos de Aplicação:</b></p>
                        <ul style="font-size:0.88rem; line-height:1.6; padding-left:18px;">
                            <li><b>Desvio de Valor:</b> Compra <b>> 250%</b> da média histórica do usuário</li>
                            <li><b>Novo Dispositivo:</b> Usuário tentando compra em um <b>3º aparelho</b></li>
                            <li><b>Card Hopping:</b> Cartão de um usuário aparecendo em <b>outra conta</b></li>
                            <li><b>Merchant Hopping:</b> Usuário comprando em <b>3+ lojistas distintos</b></li>
                            <li><b>Probe & Scale:</b> Valor <b>> 2x</b> da tentativa imediatamente anterior</li>
                            <li>Ticket <b>> $ 3.500,00</b> durante o dia / horário comercial</li>
                        </ul>
                        <hr style="border-color:rgba(254, 176, 25, 0.3);">
                        <p style="font-size:0.85rem; color:#feb019;"><b>Ação:</b> Desafio 3D-Secure 2.0 / Biometria Facial no App. Se autenticado, <b>aprova com Liability Shift</b>.</p>
                    </div>
                """, unsafe_allow_html=True)
            
        with m_col3:
            if is_en:
                st.markdown(r"""
                    <div class="strategy-card card-red" style="height: 100%;">
                        <h3 style="color:#f5365c; margin-top:0;">🔴 Red Path</h3>
                        <h5 style="color:#a0aec0; margin-top:-5px;">Hard Decline (Automatic Block)</h5>
                        <hr style="border-color:rgba(245, 54, 92, 0.3);">
                        <p><b>Trigger Conditions:</b></p>
                        <ul style="font-size:0.88rem; line-height:1.6; padding-left:18px;">
                            <li>User or card with <b>confirmed prior chargeback</b></li>
                            <li>Device with <b>> 4 distinct cards</b> (Device Farming)</li>
                            <li>Velocity burst with <b>&ge; 5 consecutive attempts</b></li>
                            <li>24h cumulative volume <b>> $ 5,000.00</b></li>
                            <li>Ticket <b>> $ 3,500 at Midnight (00h-06h)</b> without history</li>
                            <li>Merchant flagged as <b>Established High Risk</b></li>
                        </ul>
                        <hr style="border-color:rgba(245, 54, 92, 0.3);">
                        <p style="font-size:0.85rem; color:#f5365c;"><b>Impact:</b> Immediate decline with audit reason logged for compliance.</p>
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(r"""
                    <div class="strategy-card card-red" style="height: 100%;">
                        <h3 style="color:#f5365c; margin-top:0;">🔴 Red Path</h3>
                        <h5 style="color:#a0aec0; margin-top:-5px;">Hard Decline (Bloqueio Automático)</h5>
                        <hr style="border-color:rgba(245, 54, 92, 0.3);">
                        <p><b>Gatilhos de Aplicação:</b></p>
                        <ul style="font-size:0.88rem; line-height:1.6; padding-left:18px;">
                            <li>Usuário ou cartão com <b>chargeback prévio confirmado</b></li>
                            <li>Dispositivo com <b>> 4 cartões distintos</b> (Device Farming)</li>
                            <li>Disparo massivo com <b>&ge; 5 tentativas consecutivas</b></li>
                            <li>Volume acumulado nas últimas 24h <b>> $ 5.000,00</b></li>
                            <li>Compra <b>> $ 3.500 na Madrugada (00h-06h)</b> sem histórico</li>
                            <li>Lojista classificado como <b>Alto Risco Estabelecido</b></li>
                        </ul>
                        <hr style="border-color:rgba(245, 54, 92, 0.3);">
                        <p style="font-size:0.85rem; color:#f5365c;"><b>Impacto:</b> Bloqueio sumário e imediato com motivo de auditoria registrado no log de segurança.</p>
                    </div>
                """, unsafe_allow_html=True)

    # --------------------------------------------------------------------------
    # TAB 3: ARQUITETURA DO MOTOR EM TEMPO REAL
    # --------------------------------------------------------------------------
    with tab_ins3:
        if is_en:
            st.subheader("Layered Real-Time Decision Engine Architecture (REST API)")
            st.markdown("Deterministic in-memory evaluation in less than **10 milliseconds**.")
            st.markdown(r"""
                <div style="background-color:#151a24; border:1px solid #2d3748; border-radius:10px; padding:20px; font-family:monospace; font-size:0.9rem;">
                    <div style="color:#00d26a; font-weight:bold;">1. REQUEST: POST /transactions/check</div>
                    <div style="margin-left:20px; color:#a0aec0;">Receives payload with transaction_id, merchant_id, user_id, card_number, transaction_amount, device_id.</div>
                    <br>
                    <div style="color:#3b82f6; font-weight:bold;">LAYER 1: Strict Historical Blacklists & Temporal Consistency</div>
                    <div style="margin-left:20px; color:#e2e8f0;">
                        • If user or card has prior confirmed chargeback ➔ <b>DENY (PREVIOUS_CHARGEBACK)</b><br>
                        • If merchant belongs to Established High Risk list (&ge; 4 CBKs) ➔ <b>DENY (HIGH_RISK_MERCHANT)</b>
                    </div>
                    <br>
                    <div style="color:#feb019; font-weight:bold;">LAYER 2: Velocity Bursts, Device Farming, Card Hopping & Limits</div>
                    <div style="margin-left:20px; color:#e2e8f0;">
                        • If device has > 4 linked cards ➔ <b>DENY (DEVICE_FARMING_LIMIT)</b><br>
                        • If user made &ge; 5 consecutive retries ➔ <b>DENY (VELOCITY_BURST_EXCEEDED)</b><br>
                        • If 24h rolling volume for user &gt; $ 5,000.00 ➔ <b>DENY (DAILY_AMOUNT_LIMIT_EXCEEDED)</b><br>
                        • If transaction &gt; $ 3,500.00 at Midnight (00h-06h) without history ➔ <b>DENY (HIGH_TICKET_NIGHT_RISK)</b>
                    </div>
                    <br>
                    <div style="color:#00d26a; font-weight:bold;">LAYER 3: Approval Decision & Response</div>
                    <div style="margin-left:20px; color:#00d26a;">
                        ➔ <b>Response: {"transaction_id": 12345, "recommendation": "approve"}</b>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            st.info("💡 **Zero Data Leakage Guarantee:** The engine exclusively processes historical transactions strictly prior to the timestamp of the evaluated transaction.")
        else:
            st.subheader("Arquitetura em Camadas do Motor Antifraude (API REST)")
            st.markdown("Execução de validações determinísticas de alta velocidade em menos de **10 milissegundos**.")
            st.markdown(r"""
                <div style="background-color:#151a24; border:1px solid #2d3748; border-radius:10px; padding:20px; font-family:monospace; font-size:0.9rem;">
                    <div style="color:#00d26a; font-weight:bold;">1. REQUISIÇÃO: POST /transactions/check</div>
                    <div style="margin-left:20px; color:#a0aec0;">Recebe payload com transaction_id, merchant_id, user_id, card_number, transaction_amount, device_id.</div>
                    <br>
                    <div style="color:#3b82f6; font-weight:bold;">CAMADA 1: Histórico Estrito & Consistência Temporal (Blacklists)</div>
                    <div style="margin-left:20px; color:#e2e8f0;">
                        • Se o usuário ou cartão possui chargeback prévio registrado ➔ <b>DENY (PREVIOUS_CHARGEBACK)</b><br>
                        • Se o lojista pertence à lista de Alto Risco Estabelecido (&ge; 4 CBKs) ➔ <b>DENY (HIGH_RISK_MERCHANT)</b>
                    </div>
                    <br>
                    <div style="color:#feb019; font-weight:bold;">CAMADA 2: Travas de Velocidade, Device Farming, Card Hopping e Limites</div>
                    <div style="margin-left:20px; color:#e2e8f0;">
                        • Se o dispositivo possui mais de 4 cartões vinculados ➔ <b>DENY (DEVICE_FARMING_LIMIT)</b><br>
                        • Se o usuário realizou &ge; 5 tentativas consecutivas ➔ <b>DENY (VELOCITY_BURST_EXCEEDED)</b><br>
                        • Se o volume acumulado pelo usuário nas últimas 24h &gt; $ 5.000,00 ➔ <b>DENY (DAILY_AMOUNT_LIMIT_EXCEEDED)</b><br>
                        • Se transação &gt; $ 3.500,00 na Madrugada (00h-06h) sem histórico prévio ➔ <b>DENY (HIGH_TICKET_NIGHT_RISK)</b>
                    </div>
                    <br>
                    <div style="color:#00d26a; font-weight:bold;">CAMADA 3: Decisão de Aprovação & Resposta</div>
                    <div style="margin-left:20px; color:#00d26a;">
                        ➔ <b>Retorno: {"transaction_id": 12345, "recommendation": "approve"}</b>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            st.info("💡 **Garantia de Não-Vazamento Temporal:** O motor utiliza exclusivamente dados históricos anteriores ao timestamp da transação avaliada, garantindo validade estatística real e sem *data leakage*.")

    # --------------------------------------------------------------------------
    # TAB 4: ENRIQUECIMENTO E PRÓXIMA GERAÇÃO
    # --------------------------------------------------------------------------
    with tab_ins4:
        if is_en:
            st.subheader("Recommended External Attributes (Next-Gen Engine)")
            st.markdown("Key external variables to elevate engine precision at scale of millions of daily transactions:")
            col_e1, col_e2 = st.columns(2)
            with col_e1:
                st.markdown("""
                    <div class="strategy-card card-blue">
                        <h4 style="margin:0 0 8px 0; color:#3b82f6;">📱 1. Advanced Device Fingerprinting</h4>
                        <p style="font-size:0.9rem; line-height:1.5; color:#e2e8f0;">
                            • Android emulator detection (Nox, BlueStacks, LDPlayer)<br>
                            • Root / Jailbreak status checks<br>
                            • App integrity validation via Google Play Protect / App Attest<br>
                            • Persistent hardware IDs (Android ID, IDFA, Canvas Hash)
                        </p>
                    </div>
                """, unsafe_allow_html=True)
                st.markdown("""
                    <div class="strategy-card card-blue">
                        <h4 style="margin:0 0 8px 0; color:#3b82f6;">📍 2. Geolocation & Network Intelligence</h4>
                        <p style="font-size:0.9rem; line-height:1.5; color:#e2e8f0;">
                            • Distance between IP address and smartphone GPS (<i>Geo-IP Mismatch</i>)<br>
                            • Anonymized proxy, VPN, and Tor exit node detection<br>
                            • Impossible travel velocity between successive orders
                        </p>
                    </div>
                """, unsafe_allow_html=True)
            with col_e2:
                st.markdown("""
                    <div class="strategy-card card-blue">
                        <h4 style="margin:0 0 8px 0; color:#3b82f6;">👆 3. Behavioral Biometrics</h4>
                        <p style="font-size:0.9rem; line-height:1.5; color:#e2e8f0;">
                            • Keystroke dynamics and typing cadence on card fields<br>
                            • Touchscreen pressure and swipe patterns<br>
                            • Clipboard pasting detection on sensitive inputs
                        </p>
                    </div>
                """, unsafe_allow_html=True)
                st.markdown("""
                    <div class="strategy-card card-blue">
                        <h4 style="margin:0 0 8px 0; color:#3b82f6;">💳 4. BIN Intelligence & Merchant KYB</h4>
                        <p style="font-size:0.9rem; line-height:1.5; color:#e2e8f0;">
                            • BIN table: Issuer country, card tier (Platinum/Black vs Prepaid)<br>
                            • 3DS status confirmation and Liability Shift with card brand<br>
                            • Merchant Category Code (MCC) and automated tax registration checks (KYB)
                        </p>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.subheader("Atributos Recomendados para Enriquecimento (Next-Gen Engine)")
            st.markdown("Variáveis externas fundamentais para elevar a precisão do motor em escala de milhões de transações diárias:")
            col_e1, col_e2 = st.columns(2)
            with col_e1:
                st.markdown("""
                    <div class="strategy-card card-blue">
                        <h4 style="margin:0 0 8px 0; color:#3b82f6;">📱 1. Device Fingerprint Avançado</h4>
                        <p style="font-size:0.9rem; line-height:1.5; color:#e2e8f0;">
                            • Detecção de emuladores Android (Nox, BlueStacks, LDPlayer)<br>
                            • Identificação de aparelhos com <i>Root</i> ou <i>Jailbreak</i><br>
                            • Integridade do aplicativo via Google Play Protect API / App Attest<br>
                            • Identificadores de hardware persistentes (Android ID, IDFA, Canvas Hash)
                        </p>
                    </div>
                """, unsafe_allow_html=True)
                st.markdown("""
                    <div class="strategy-card card-blue">
                        <h4 style="margin:0 0 8px 0; color:#3b82f6;">📍 2. Geolocalização & Rede</h4>
                        <p style="font-size:0.9rem; line-height:1.5; color:#e2e8f0;">
                            • Distância entre o IP de conexão e as coordenadas de GPS do celular (<i>Geo-IP Mismatch</i>)<br>
                            • Detecção de conexões anonimizadas (VPN comercial, Proxy residencial, rede Tor)<br>
                            • Velocidade impossível de deslocamento entre transações sucessivas
                        </p>
                    </div>
                """, unsafe_allow_html=True)
            with col_e2:
                st.markdown("""
                    <div class="strategy-card card-blue">
                        <h4 style="margin:0 0 8px 0; color:#3b82f6;">👆 3. Biometria Comportamental</h4>
                        <p style="font-size:0.9rem; line-height:1.5; color:#e2e8f0;">
                            • Dinâmica e velocidade de digitação dos dados do cartão (<i>Keystroke Dynamics</i>)<br>
                            • Cadência e pressão de toque na tela do smartphone<br>
                            • Detecção de preenchimento automático via área de transferência (<i>Clipboard Pasting</i>)
                        </p>
                    </div>
                """, unsafe_allow_html=True)
                st.markdown("""
                    <div class="strategy-card card-blue">
                        <h4 style="margin:0 0 8px 0; color:#3b82f6;">💳 4. Inteligência de Cartão (BIN) & KYB</h4>
                        <p style="font-size:0.9rem; line-height:1.5; color:#e2e8f0;">
                            • Tabela BIN: País emissor, tipo de cartão (Crédito vs. Pré-pago) e segmento<br>
                            • Status 3DS e confirmação de <i>Liability Shift</i> com a bandeira<br>
                            • MCC (Merchant Category Code) e validação cadastral automática (KYB/CNPJ)
                        </p>
                    </div>
                """, unsafe_allow_html=True)
