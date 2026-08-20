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
├── README.md                                  # Comprehensive bilingual documentation
├── Lucas Pedro - Data Analyst Case Solution.md # Full case solution & executive report (EN)
├── Lucas Pedro - Data Analyst Case Solution (PT).md # Full case solution & executive report (PT)
├── requirements.txt                           # Standard pip package dependencies
├── pyproject.toml                             # Modern Python packaging configuration (uv/pip)
├── run.py                                     # 1-Click launcher script
│
├── data/
│   └── transactions.sqlite                    # Persistent indexed SQLite database
│
├── security-test/
│   ├── transactional-sample.csv               # Raw transaction dataset (3,199 rows)
│   ├── software-engineer-payments.md          # Payment system reference document
│   └── Data_Analyst_I_Case_External.pdf       # Original technical case challenge
│
└── src/
    ├── ingest_data.py                         # Idempotent CSV -> SQLite ingestion + indexing
    ├── views.py                               # 15+ DuckDB analytical VIEW definitions
    ├── dashboard.py                           # Complete Streamlit Dashboard (6 tabs + I18n)
    └── extract_insights.py                    # Terminal-based heuristic validator & insights extractor
```

---

## 📚 Theoretical Payments Answers (Summary)

Complete technical essays and answers are available in [`Lucas Pedro - Data Analyst Case Solution.md`](Lucas%20Pedro%20-%20Data%20Analyst%20Case%20Solution.md) (or the Portuguese version [`Lucas Pedro - Data Analyst Case Solution (PT).md`](Lucas%20Pedro%20-%20Data%20Analyst%20Case%20Solution%20(PT).md)) and inside **Tab 6 of the Dashboard**:

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

Se você utiliza o gerenciador [`uv`](https://github.com/astral-sh/uv):

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

> 💡 **Nota de Automação:** Ao iniciar o dashboard ou qualquer script, o sistema verifica automaticamente a integridade do banco SQLite (`data/transactions.sqlite`). Caso não exista ou esteja vazio, a ingestão e a criação dos índices relacionais ocorrem automaticamente em menos de **1 segundo**.

---

### 📊 Opção D: Relatório de Insights via Terminal (CLI)

Para extrair e exibir todas as tabelas analíticas estruturadas e benchmarks de heurísticas diretamente no terminal:

```bash
python src/extract_insights.py
```

---

## 🎯 Resumo Executivo & Resultados de Negócio

A análise exploratória foi conduzida sobre a base transacional de **3.199 operações mobile** com volume bruto de **$ 2.456.233,48**.

### 📌 Métricas Macro do Portfólio

| Métrica | Volume Legítimo | Volume Fraude (Chargeback) | Total do Portfólio | Taxa de Fraude (%) |
| :--- | :---: | :---: | :---: | :---: |
| **Quantidade de Transações** | 2.808 | 391 | 3.199 | **12,22%** |
| **Volume Financeiro ($)** | $ 1.887.886,86 | $ 568.346,62 | $ 2.456.233,48 | **23,14%** |
| **Ticket Médio** | $ 672,32 | $ 1.453,57 | $ 767,81 | **+116,2% maior ticket em fraude** |

> ⚠️ **Insight Crítico de Negócio:** As perdas financeiras por chargeback (**23,14% da receita total**) representam quase o dobro da taxa volumétrica transacional (**12,22%**). Agentes fraudulentos focam especificamente em transações de **alto valor**, exigindo regras com detecção de anomalia de valor e monitoramento de velocidade.

---

## 💡 Padrões Comportamentais de Fraude Identificados

```
                   PADRÕES DE FRAUDE IDENTIFICADOS
┌─────────────────────────┐         ┌─────────────────────────┐
│     Device Farming      │         │     Velocity Burst      │
│   > 4 cartões / aparelho│         │   Rajadas < 10 min      │
│   Taxa CBK: 89,7%       │         │   Taxa CBK: 71,4%       │
└────────────┬────────────┘         └────────────┬────────────┘
             │                                   │
             └─────────────────┬─────────────────┘
                               │
                ┌──────────────┴──────────────┐
                │      Merchant Hopping       │
                │   >= 3 lojistas em série    │
                │   Taxa CBK: 88,4%           │
                └─────────────────────────────┘
```

1. **Device Farming & Multi-Card Velocity:** Aparelhos vinculados a mais de 4 cartões distintos exibem taxa de chargeback de **89,7%**, indicando emuladores de hardware e fazendas de teste de credenciais.
2. **Velocity Bursts (Disparos em Rajada):** Usuários com 3 ou mais tentativas em janelas inferiores a 10 minutos concentram probabilidade de chargeback entre **71,4% e 92,8%**.
3. **Merchant Hopping:** Usuários que transitam consecutivamente por 3 ou mais lojistas apresentam **88,4% de taxa de chargeback**, característico de ataques rápidos de varredura de limites.
4. **Anomalia de Valor (Ticket Spike):** Transações que excedem **250% da média histórica** do usuário apresentam taxa de fraude de **68,3%**.

---

## ⚖️ Estratégia de Decisão Antifraude em 4 Camadas (4-Tier Strategy)

Para **maximizar a prevenção de fraudes enquanto protege a receita legítima dos lojistas e a conversão dos clientes**, as decisões são roteadas através de 4 níveis operacionais:

| Nível de Risco | Probabilidade de Fraude | Ação do Motor | Impacto no Cliente & Lojista |
| :--- | :---: | :---: | :--- |
| 🟢 **Green Path** | 0% a 15% | **Aprovação Fluida** | Aprovação instantânea em sub-segundos; zero atrito comercial. |
| 🟡 **Watchlist** | 15% a 40% | **Monitoramento Silencioso** | Aprovada; marcada para observação de velocidade em background. |
| 🟠 **Step-Up Challenge** | 40% a 75% | **Autenticação Reforçada** | Desafio 3DS 2.0 / Biometria Facial / Push no App. Elimina falsos positivos. |
| 🔴 **Hard Decline** | > 75% | **Bloqueio Imediato** | Rejeição direta; cartão e dispositivo bloqueados preventivamente. |

---

## 📊 Módulos do Dashboard Interativo (Interactive Dashboard Modules)

O dashboard executivo possui **Dark Mode nativo**, cartões customizados em CSS e **suporte bilíngue instantâneo (PT-BR / EN)** via barra lateral:

```
[🌐 Seletor de Idioma: 🇧🇷 Português | 🇺🇸 English]
├── 1. 📊 Overview Executivo & KPIs do Portfólio
│   ├── KPIs Macro (Volume, Quantidade, Ticket Médio, Taxas de Perda)
│   ├── Curvas diárias e acumuladas de progressão de chargebacks
│   └── Histogramas comparativos de distribuição de tickets (Legítimo vs Fraude)
├── 2. 🔍 Análise Multidimensional de Riscos
│   ├── Matriz de Device Farming (Cartões por Aparelho)
│   ├── Distribuição de Velocity Bursts e intervalos temporais
│   └── Análise de sensibilidade por faixas de valor
├── 3. 🛡️ Motor de Heurísticas & ROI Financeiro
│   ├── 6 Regras estatísticas com métricas de Precisão, Recall e F1-Score
│   ├── Matrizes de confusão e métricas de prevenção de fraudes
│   └── ROI Financeiro Líquido (Perdas Prevenidas vs Custo de Falso Positivo)
├── 4. 🎛️ Simulador Interativo de Regras
│   ├── Ajuste em tempo real de limiares (Picos de Valor, Janelas de Tempo, Limites de Cartões)
│   └── Recálculo dinâmico da receita protegida e taxas de falsos positivos
├── 5. 🔬 Investigação Forense de Transações & Drill-Down
│   ├── Análise aprofundada por ID de Transação, ID de Usuário, Cartão e ID de Dispositivo
│   └── Linha do tempo cronológica de auditoria de risco para analistas de fraude
└── 6. 📚 Respostas Técnicas & Ecossistema da Indústria de Pagamentos
    ├── Pergunta 1: Fluxo de Autorização, Liquidação (Clearing & Settlement), Composição do MDR
    ├── Pergunta 2: Adquirente vs Subadquirente (PayFac) vs Gateway de Pagamentos
    └── Pergunta 3: Chargeback vs Cancelamento & Risco Adquirente Regulatório
```

---

## 🏗️ Arquitetura Técnica & Stack Tecnológica (Technical Architecture & Stack)

```
┌────────────────────────────────┐
│ security-test/                 │
│ transactional-sample.csv       │
└───────────────┬────────────────┘
                │
                ▼ (src/ingest_data.py)
┌────────────────────────────────┐
│ data/transactions.sqlite       │  <-- Armazenamento SQLite persistente indexado
│ (Indexado: tx, user, dev, etc.)│
└───────────────┬────────────────┘
                │
                ▼ (src/views.py)
┌────────────────────────────────┐
│ DuckDB In-Memory OLAP Engine   │  <-- 15+ VIEWs analíticas (sub-milissegundo)
└───────────────┬────────────────┘
                │
        ┌───────┴────────────────┐
        ▼                        ▼
┌──────────────────┐   ┌───────────────────────────┐
│ Streamlit UI     │   │ Terminal CLI Engine       │
│ (src/dashboard.py│   │ (src/extract_insights.py) │
└──────────────────┘   └───────────────────────────┘
```

* **DuckDB (In-Memory OLAP Engine):** Motor analítico SQL colunar de altíssima velocidade em memória, executando agregações em mais de 15 views personalizadas.
* **SQLite 3:** Camada de persistência relacional com índices em árvore B (*B-Tree*) em `transaction_id`, `user_id`, `merchant_id`, `card_number`, `device_id` e `transaction_date`.
* **Streamlit + Plotly:** Interface web reativa interativa com design CSS refinado e suporte a múltiplos idiomas.

---

## 📁 Estrutura de Arquivos do Repositório

```
cloudwalk-case/
├── README.md                                  # Documentação bilíngue completa
├── Lucas Pedro - Data Analyst Case Solution.md # Resolução completa do case e relatório executivo (EN)
├── Lucas Pedro - Data Analyst Case Solution (PT).md # Resolução completa do case e relatório executivo (PT)
├── requirements.txt                           # Dependências de pacotes padrão pip
├── pyproject.toml                             # Configuração moderna de empacotamento Python (uv/pip)
├── run.py                                     # Script de inicialização automática 1-clique
│
├── data/
│   └── transactions.sqlite                    # Banco de dados SQLite persistente indexado
│
├── security-test/
│   ├── transactional-sample.csv               # Base de dados transacional bruta (3.199 linhas)
│   ├── software-engineer-payments.md          # Documento de referência do sistema de pagamentos
│   └── Data_Analyst_I_Case_External.pdf       # Documento original com o desafio técnico
│
└── src/
    ├── ingest_data.py                         # Ingestão idempotente CSV -> SQLite + Indexação
    ├── views.py                               # Definição de 15+ VIEWs analíticas em DuckDB
    ├── dashboard.py                           # Dashboard Streamlit completo (6 abas + I18n)
    └── extract_insights.py                    # Validador de heurísticas e extrator de insights em CLI
```

---

## 📚 Resumo das Respostas Teóricas de Pagamentos

As análises técnicas completas e relatórios executivos estão documentados em [`Lucas Pedro - Data Analyst Case Solution (PT).md`](Lucas%20Pedro%20-%20Data%20Analyst%20Case%20Solution%20(PT).md) (ou versão em inglês [`Lucas Pedro - Data Analyst Case Solution.md`](Lucas%20Pedro%20-%20Data%20Analyst%20Case%20Solution.md)) e na **Aba 6 do Dashboard**:

* **Pergunta 1 (Fluxo da Indústria de Pagamentos):** Descrição detalhada da autorização em tempo real (*dual-message*) entre Portador $\leftrightarrow$ Lojista $\leftrightarrow$ Gateway/PayFac $\leftrightarrow$ Adquirente $\leftrightarrow$ Bandeira $\leftrightarrow$ Emissor e do processo de liquidação (*Clearing & Settlement*), incluindo o detalhamento e repartição do MDR (*Taxa de Intercâmbio*, Taxa da Bandeira e Margem de Adquirência).
* **Pergunta 2 (Adquirente vs Subadquirente vs Gateway):** Comparação técnica e operacional enfatizando subscrição de risco, liquidação centralizada (*modelo PayFac / Master Merchant*) e roteamento de APIs criptografadas (*Gateways*).
* **Pergunta 3 (Chargeback vs Cancelamento & Risco da Adquirente):** Distinção formal entre cancelamento comercial voluntário e disputa por fraude (*Chargeback*), além dos riscos regulatórios (Programas Visa VAMP / Mastercard ECP) e risco de crédito por insolvência de lojistas.

---

<div align="center">
Desenvolvido para o <b>Processo Seletivo CloudWalk — Data Analyst I</b>.
</div>

