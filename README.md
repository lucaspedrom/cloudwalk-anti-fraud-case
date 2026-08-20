<div align="center">

# 🛡️ CloudWalk Anti-Fraud Intelligence & Payments Platform
### Technical Assessment — Data Analyst I & Payments Specialist

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)](https://python.org)
[![DuckDB](https://img.shields.io/badge/DuckDB-0.9%2B-FFF000?logo=duckdb&logoColor=black)](https://duckdb.org)
[![SQLite](https://img.shields.io/badge/SQLite-3-003B57?logo=sqlite&logoColor=white)](https://sqlite.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30%2B-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io)
[![Plotly](https://img.shields.io/badge/Plotly-5.18%2B-3F4F75?logo=plotly&logoColor=white)](https://plotly.com)
[![Status](https://img.shields.io/badge/Status-Completed-success)]()

**An executive end-to-end analytical platform for transaction fraud detection, heuristic risk modeling with ROI estimation, transaction forensics, and payment acquiring ecosystem architecture.**

---

🌐 **Language Navigation / Navegação de Idioma:**  
[🇬🇧 **English Version (Default)**](#-english-version) &nbsp;|&nbsp; [🇧🇷 **Versão em Português**](#-versão-em-português-brazilian-portuguese)

> ℹ️ *Note: This documentation starts in English as the primary assessment language, followed by the complete Brazilian Portuguese version at the end of the page.*

---

</div>

# 🇬🇧 English Version

## ⚡ 1-Click Quickstart (How to Run)

The entire data ingestion, database indexing, and dashboard rendering pipeline is fully automated. You can run the project with **a single command**:

### 🚀 Option A: Standard Automated Setup (Recommended)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the automated launcher (creates database and launches dashboard)
python run.py
```

---

### ⚡ Option B: Using `uv` (Ultra Fast)

If you have [`uv`](https://github.com/astral-sh/uv) installed:

```bash
# Automatically sets up venv, installs dependencies, and runs the launcher
uv run python run.py

# Or launch directly with Streamlit
uv run streamlit run src/dashboard.py
```

---

### 💻 Option C: Direct Streamlit Execution

```bash
streamlit run src/dashboard.py
```

> 💡 **Automated Pipeline Bootstrap:** Upon launching the dashboard or any script, the system automatically checks the integrity of `data/transactions.sqlite`. If not present, the ingestion and relational indexing from `security-test/transactional-sample.csv` execute automatically in less than **1 second**.

---

### 📊 Option D: Terminal CLI Insights Extraction

To extract and print all structured insight tables and heuristic benchmarks directly to your terminal:

```bash
python src/extract_insights.py
```

---

## 🎯 Executive Summary & Business Insights

The exploratory data analysis was conducted on **3,199 mobile transactional records** with a gross volume of **$ 2,456,233.48**.

### 📌 Portfolio Macro Metrics

| Metric | Legitimate Volume | Fraud Volume (Chargeback) | Portfolio Total | Fraud Rate (%) |
| :--- | :---: | :---: | :---: | :---: |
| **Transactions Count** | 2,808 | 391 | 3,199 | **12.22%** |
| **Financial Volume ($)** | $ 1,887,886.86 | $ 568,346.62 | $ 2,456,233.48 | **23.14%** |
| **Average Ticket** | $ 672.32 | $ 1,453.57 | $ 767.81 | **+116.2% higher ticket in fraud** |

> ⚠️ **Key Business Finding:** Financial chargeback losses (**23.14% of total revenue**) represent nearly double the transactional volume rate (**12.22%**). Fraudulent actors specifically target high-ticket items, requiring rules with amount-anomaly detection and velocity tracking.

---

## 💡 Identified Fraud Behavioral Patterns

```
                     IDENTIFIED FRAUD PATTERNS
┌─────────────────────────┐         ┌─────────────────────────┐
│     Device Farming      │         │     Velocity Burst      │
│   > 4 cards / device    │         │  Bursts under 10 min    │
│   CBK Rate: 89.7%       │         │  CBK Rate: 71.4%        │
└────────────┬────────────┘         └────────────┬────────────┘
             │                                   │
             └─────────────────┬─────────────────┘
                               │
                ┌──────────────┴──────────────┐
                │      Merchant Hopping       │
                │   >= 3 merchants in series  │
                │   CBK Rate: 88.4%           │
                └─────────────────────────────┘
```

1. **Device Farming & Multi-Card Velocity:** Devices linked to > 4 distinct cards exhibit an **89.7% chargeback rate**, indicating hardware emulators and credential-testing farms.
2. **Velocity Bursts:** Users attempting 3+ transactions within windows shorter than 10 minutes display a **71.4% to 92.8% chargeback probability**.
3. **Merchant Hopping:** Users jumping across 3 or more merchants consecutively show an **88.4% chargeback rate**, characteristic of rapid limit-testing attacks.
4. **Amount Spike Anomaly:** Transactions exceeding **250% of the user's historical average** present a **68.3% fraud rate**.

---

## ⚖️ 4-Tier Anti-Fraud Decision Strategy

To **maximize fraud prevention while protecting legitimate merchant revenue and customer conversion**, decisions are routed across 4 operational tiers:

| Risk Tier | Fraud Probability | Engine Action | Customer & Merchant Impact |
| :--- | :---: | :---: | :--- |
| 🟢 **Green Path** | 0% – 15% | **Frictionless Approval** | Instant sub-second approval; zero customer friction. |
| 🟡 **Watchlist** | 15% – 40% | **Silent Monitoring** | Approved; flagged for background velocity observation. |
| 🟠 **Step-Up Challenge** | 40% – 75% | **Enhanced Authentication** | 3DS 2.0 / Facial Biometrics / Mobile Push Challenge. Eliminates false positives. |
| 🔴 **Hard Decline** | > 75% | **Immediate Block** | Direct rejection; card & device temporarily blacklisted. |

---

## 📊 Interactive Dashboard Modules

The executive dashboard features **native Dark Mode**, custom CSS cards, and **instant bilingual support (PT-BR / EN)** via the sidebar:

```
[🌐 Language Switcher: 🇧🇷 Português | 🇺🇸 English]
├── 1. 📊 Executive Overview & Portfolio KPIs
│   ├── Macro KPIs (Volume, Count, Average Ticket, Loss Rates)
│   ├── Daily & cumulative chargeback progression curves
│   └── Ticket distribution comparative histograms (Legitimate vs Fraud)
├── 2. 🔍 Multidimensional Risk Analysis
│   ├── Device Farming matrix (Cards per Device)
│   ├── Velocity burst and temporal gap distribution
│   └── Amount range sensitivity analysis
├── 3. 🛡️ Heuristics Engine & Financial ROI
│   ├── 6 Statistical rules with Precision, Recall, and F1-Scores
│   ├── Confusion matrices and fraud prevention metrics
│   └── Net Financial ROI (Fraud Losses Prevented vs False Positive Cost)
├── 4. 🎛️ Interactive Rule Simulator
│   ├── Real-time threshold adjustment (Amount Spikes, Time Windows, Card Limits)
│   └── Dynamic recalculation of protected revenue and false positive rates
├── 5. 🔬 Transaction Forensics & User Drill-Down
│   ├── Deep-dive by Transaction ID, User ID, Card, and Device ID
│   └── Chronological risk audit timeline for fraud analysts
└── 6. 📚 Technical Answers & Payments Industry Ecosystem
    ├── Question 1: Authorization Flow, Clearing & Settlement, MDR Breakdown
    ├── Question 2: Acquirer vs Sub-acquirer (PayFac) vs Payment Gateway
    └── Question 3: Chargeback vs Cancellation & Regulatory Acquirer Risk
```

---

## 🏗️ Technical Architecture & Stack

```
┌────────────────────────────────┐
│ security-test/                 │
│ transactional-sample.csv       │
└───────────────┬────────────────┘
                │
                ▼ (src/ingest_data.py)
┌────────────────────────────────┐
│ data/transactions.sqlite       │  <-- Persistent indexed SQLite storage
│ (Indexed: tx, user, dev, etc.) │
└───────────────┬────────────────┘
                │
                ▼ (src/views.py)
┌────────────────────────────────┐
│ DuckDB In-Memory OLAP Engine   │  <-- 15+ analytical VIEWs (sub-millisecond)
└───────────────┬────────────────┘
                │
        ┌───────┴────────────────┐
        ▼                        ▼
┌──────────────────┐   ┌───────────────────────────┐
│ Streamlit UI     │   │ Terminal CLI Engine       │
│ (src/dashboard.py│   │ (src/extract_insights.py) │
└──────────────────┘   └───────────────────────────┘
```

* **DuckDB (In-Memory OLAP):** High-speed vectorized SQL analytical engine performing aggregations across 15+ custom views.
* **SQLite 3:** Persistent storage layer with B-Tree indexes on `transaction_id`, `user_id`, `merchant_id`, `card_number`, `device_id`, and `transaction_date`.
* **Streamlit + Plotly:** Interactive reactive web application with bespoke CSS design and multi-language support.

---

## 📁 Repository Directory Tree

```
cloudwalk-case/
├── README.md                      # Comprehensive bilingual documentation
├── requirements.txt               # Standard pip package dependencies
├── pyproject.toml                 # Modern Python packaging configuration (uv/pip)
├── run.py                         # 1-Click launcher script
│
├── data/
│   └── transactions.sqlite        # Persistent indexed SQLite database
│
├── security-test/
│   ├── transactional-sample.csv   # Raw transaction dataset (3,199 rows)
│   ├── anti-fraud_report.md       # Comprehensive executive anti-fraud report
│   ├── respostas-payments.md      # Detailed payment ecosystem answers
│   └── Data_Analyst_I_Case_External.pdf # Original technical case challenge
│
└── src/
    ├── ingest_data.py             # Idempotent CSV -> SQLite ingestion + indexing
    ├── views.py                   # 15+ DuckDB analytical VIEW definitions
    ├── dashboard.py               # Complete Streamlit Dashboard (6 tabs + I18n)
    └── extract_insights.py        # Terminal-based heuristic validator & insights extractor
```

---

## 📚 Theoretical Payments Answers (Summary)

Complete technical essays and answers are available in [`security-test/anti-fraud_report.md`](security-test/anti-fraud_report.md), [`security-test/respostas-payments.md`](security-test/respostas-payments.md), and inside **Tab 6 of the Dashboard**:

* **Question 1 (Payment Industry Flow):** Detailed step-by-step description of real-time dual-message authorization (Cardholder $\leftrightarrow$ Merchant $\leftrightarrow$ Gateway/PayFac $\leftrightarrow$ Acquirer $\leftrightarrow$ Scheme $\leftrightarrow$ Issuer) and financial clearing & settlement, including MDR breakdown (*Interchange Fee*, Scheme Assessment, and Acquirer Margin).
* **Question 2 (Acquirer vs Sub-acquirer vs Gateway):** Technical and operational comparison highlighting risk underwriting, centralized settlement (PayFac / Master Merchant model), and cryptographic API routing (Gateways).
* **Question 3 (Chargeback vs Refund & Acquirer Risk):** Formal distinction between commercial mutual refunds and fraud chargebacks, alongside regulatory risks (Visa VAMP / Mastercard ECP programs) and merchant insolvency credit risks.

---
---

# 🇧🇷 Versão em Português (Brazilian Portuguese)

## ⚡ Como Executar em 1 Minuto (Quickstart)

Toda a esteira de ingestão, indexação do banco de dados e renderização do dashboard foi 100% automatizada. Você pode rodar o projeto com **um único comando**:

### 🚀 Opção A: Inicialização Automática Padrão (Recomendada)

```bash
# 1. Instale as dependências
pip install -r requirements.txt

# 2. Inicie o sistema (alimenta o banco e abre o dashboard automaticamente)
python run.py
```

---

### ⚡ Opção B: Utilizando `uv` (Ultra Rápido)

```bash
# Cria o ambiente virtual e inicia o dashboard diretamente
uv run python run.py

# Ou acione diretamente o Streamlit
uv run streamlit run src/dashboard.py
```

---

### 💻 Opção C: Execução Direta via Streamlit

```bash
streamlit run src/dashboard.py
```

> 💡 **Nota de Automação:** Ao iniciar o dashboard ou qualquer script, o sistema verifica automaticamente a integridade do banco SQLite (`data/transactions.sqlite`). Caso não exista ou esteja vazio, a ingestão e a criação dos índices ocorrem automaticamente em menos de **1 segundo**.

---

### 📊 Opção D: Relatório de Insights via Terminal (CLI)

```bash
python src/extract_insights.py
```

---

## 🎯 Visão Geral do Case e Resultados de Negócio

A análise foi conduzida sobre a base transacional de **3.199 operações mobile** totalizando **$ 2.456.233,48** em volume transacionado.

### 📌 Diagnóstico Macro do Portfólio

| Indicador | Volume Legítimo | Volume Fraude (CBK) | Total Geral | % Fraude |
| :--- | :---: | :---: | :---: | :---: |
| **Transações** | 2.808 | 391 | 3.199 | **12,22%** |
| **Volume Financeiro ($)** | $ 1.887.886,86 | $ 568.346,62 | $ 2.456.233,48 | **23,14%** |
| **Ticket Médio** | $ 672,32 | $ 1.453,57 | $ 767,81 | **+116,2% no ticket de fraude** |

> ⚠️ **Insight Crítico:** O prejuízo financeiro do chargeback (**23,14% do faturamento**) é quase o dobro da taxa volumétrica (**12,22%**). Fraudes no ecossistema têm como alvo transações de **alto valor**, demandando regras com sensibilidade monetária e velocidade transacional.

---

## 💡 Padrões Comportamentais de Fraude Identificados

1. **Device Farming & Multi-Card Velocity:** Dispositivos com mais de 4 cartões distintos possuem **89,7% de taxa de chargeback**, indicando emulação e fazendas de teste de cartões clonados.
2. **Velocity Bursts (Disparos Consecutivos):** Usuários com 3 ou mais transações em janelas inferiores a 10 minutos concentram **71,4% a 92,8% de chargeback**.
3. **Merchant Hopping:** Usuários que tentam compras em 3 ou mais lojistas distintos em curto intervalo apresentam **88,4% de taxa de chargeback**, caracterizando varredura de limites.
4. **Anomalia de Valor (Ticket Spike):** Compras que excedem **250% da média histórica** do usuário apresentam salto de taxa de fraude para **68,3%**.

---

## ⚖️ Estratégia de Mitigação: 4 Camadas de Decisão

| Nível de Risco | Faixa de Probabilidade | Ação do Motor | Impacto na Experiência do Cliente |
| :--- | :---: | :---: | :--- |
| 🟢 **Green Path** | 0% a 15% | **Aprovação Automática** | Zero atrito; aprovação instantânea em sub-segundos. |
| 🟡 **Watchlist** | 15% a 40% | **Monitoramento Silencioso** | Compra aprovada com acompanhamento de velocidade. |
| 🟠 **Step-Up Challenge** | 40% a 75% | **Autenticação Reforçada** | Desafio 3DS 2.0 / Biometria Facial / Push no App. Evita falso positivo. |
| 🔴 **Hard Decline** | > 75% | **Bloqueio Imediato** | Recusa da transação e congelamento preventivo de credencial. |

---

## 📊 Módulos do Dashboard Interativo

```
[🌐 Seletor de Idioma: 🇧🇷 Português | 🇺🇸 English]
├── 1. 📊 Overview Executivo & KPIs (Métricas macro, curvas temporais, tickets)
├── 2. 🔍 Análise Multidimensional de Riscos (Device Farming, Velocity Bursts, Faixas de Valor)
├── 3. 🛡️ Motor de Heurísticas & ROI (6 Regras com Precisão, Recall e ROI financeiro)
├── 4. 🎛️ Simulador Interativo de Regras (Ajuste dinâmico de limiares com recálculo em tempo real)
├── 5. 🔬 Investigação Forense de Transações (Drill-down por transação, usuário e dispositivo)
└── 6. 📚 Respostas Teóricas & Ecossistema de Pagamentos (Perguntas 1, 2 e 3 do desafio)
```

---

<div align="center">
Desenvolvido para o <b>Processo Seletivo CloudWalk — Data Analyst I</b>.
</div>
