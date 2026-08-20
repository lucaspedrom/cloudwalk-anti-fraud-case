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

## ⚖️ 3-Path Anti-Fraud Decision Strategy

To **maximize fraud prevention while protecting legitimate merchant revenue and customer conversion**, decisions are routed across a 3-tier operational matrix:

| Decision Path | Risk & Trigger Criteria | Engine Action | Customer & Merchant Impact |
| :--- | :--- | :---: | :--- |
| 🟢 **Green Path** | Ticket $\le \$ 500$, habitual user pattern ($\le 150\%$ avg), 1st or 2nd linked device, clean merchant history. | **Frictionless Approval** | Instant sub-second approval; zero customer friction for $> 85\%$ of legitimate volume. |
| 🟡 **Yellow Path** | Amount spike ($> 250\%$ avg), 3rd device on account, card hopping, 3+ merchants, probe & scale ($> 2\text{x}$ prior attempt), ticket $> \$ 3,500$ daytime. | **Enhanced Authentication (Step-Up)** | 3D-Secure 2.0 / Facial Biometrics in App. If authenticated, **approves with Liability Shift**. |
| 🔴 **Red Path** | Prior confirmed chargeback, device with $> 4$ cards (Device Farming), velocity burst with $\ge 5$ consecutive retries, $24\text{h}$ volume $> \$ 5,000$, ticket $> \$ 3,500$ at Midnight (00h-06h) without history. | **Hard Decline (Immediate Block)** | Direct rejection; audit reason logged for security and compliance. |

---

## 📊 Interactive Dashboard Modules

The executive dashboard (*Anti-Fraud Hub*) features **native Dark Mode**, custom CSS cards, and **instant bilingual support (PT-BR / EN)** via the sidebar:

```
[🌐 Language Switcher: 🇧🇷 Português | 🇺🇸 English]
├── 📊 1. Dataset Overview
│   ├── Macro KPIs (Transactions, Volume, Average Ticket, Chargeback Rates)
│   ├── Daily & cumulative chargeback progression curves
│   └── Ticket distribution comparative histograms (Legitimate vs Fraud)
├── 🔍 2. Fraud Patterns & Analysis
│   ├── Amount Range Risk (Fraud sensitivity by transaction value brackets)
│   ├── Temporal Vulnerability (Day period risk & 24h hourly curve)
│   ├── Device Farming & Multi-Card Concentration (Loss % vs cards per device)
│   └── Velocity Bursts (Fraud probability by user attempt sequence order)
├── 🚨 3. Critical Entities
│   ├── 🏪 High-Risk Merchants (Categorization & Top 15 highest loss merchants)
│   ├── 📱 Suspicious Devices (Device farming & multi-account hardware)
│   ├── 👤 Critical Users (Users with prior chargebacks & multi-card patterns)
│   └── 💳 Shared Cards (Card hopping & distributed attack vectors)
└── 🎯 4. Insights & Policy Proposal
    ├── KPI Summary (Fraud Prevention >85%, Good Approval >90%, Target Fraud Rate <2.5%, Latency <10ms)
    ├── 💡 Tab 1: Analytical Heuristics & Evidence (6 proven statistical rules with real data charts)
    ├── 🛡️ Tab 2: 3-Path Policy Matrix (Green / Yellow / Red path interactive cards)
    ├── ⚙️ Tab 3: Real-Time Engine Architecture (Layered REST API check in <10ms)
    └── 🌐 Tab 4: Next-Gen Data Enrichment (Device fingerprinting, Geo-IP, MCC, 3DS telemetry)
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

## ⚖️ Estratégia de Decisão Antifraude em 3 Vias (3-Path Strategy)

Para **maximizar a prevenção de fraudes enquanto protege a receita legítima dos lojistas e a conversão dos clientes**, as decisões são roteadas através de uma matriz operacional em 3 vias:

| Via de Decisão | Critérios de Risco & Gatilhos | Ação do Motor | Impacto no Cliente & Lojista |
| :--- | :--- | :---: | :--- |
| 🟢 **Green Path** | Ticket $\le \$ 500$, padrão habitual ($\le 150\%$ da média), 1º ou 2º aparelho cadastrado, lojista sem histórico negativo. | **Aprovação Fluida** | Aprovação instantânea em sub-segundos; zero atrito comercial para $> 85\%$ do volume genuíno. |
| 🟡 **Yellow Path** | Desvio de valor ($> 250\%$ da média), 3º aparelho no cadastro, card hopping, 3+ lojistas, probe & scale ($> 2\text{x}$ da anterior), ticket $> \$ 3.500$ em horário comercial. | **Autenticação Reforçada (Step-Up)** | Desafio 3D-Secure 2.0 / Biometria Facial no App. Se autenticado, **aprova com Liability Shift**. |
| 🔴 **Red Path** | Chargeback prévio confirmado, aparelho com $> 4$ cartões (Device Farming), rajada com $\ge 5$ tentativas consecutivas, volume em $24\text{h} > \$ 5.000$, compra $> \$ 3.500$ na Madrugada (00h-06h) sem histórico. | **Hard Decline (Bloqueio Imediato)** | Rejeição direta e sumária; motivo de auditoria registrado para conformidade e segurança. |

---

## 📊 Módulos do Dashboard Interativo (Interactive Dashboard Modules)

O dashboard executivo (*Antifraude Hub*) possui **Dark Mode nativo**, cartões customizados em CSS e **suporte bilíngue instantâneo (PT-BR / EN)** via barra lateral:

```
[🌐 Seletor de Idioma: 🇧🇷 Português | 🇺🇸 English]
├── 📊 1. Apresentação da Base (Dataset Overview)
│   ├── KPIs Macro (Transações, Volume, Ticket Médio, Taxas de Chargeback em Qtd e Valor)
│   ├── Curvas diárias e acumuladas de progressão de chargebacks
│   └── Histogramas comparativos de distribuição de tickets (Legítimo vs Fraude)
├── 🔍 2. Padrões & Diagnóstico (Fraud Patterns & Analysis)
│   ├── Sensibilidade por Faixa de Valor (Risco e mitigação por faixas de preço)
│   ├── Vulnerabilidade Temporal (Risco por turnos do dia e curva horária 00h-23h)
│   ├── Device Farming & Concentração de Cartões (Perda % vs cartões por aparelho)
│   └── Velocity Bursts (Probabilidade de fraude pela ordem da tentativa do usuário)
├── 🚨 3. Entidades Críticas (Critical Entities)
│   ├── 🏪 Lojistas de Alto Risco (Categorização e Top 15 lojistas com maior prejuízo)
│   ├── 📱 Dispositivos Suspeitos (Aparelhos de emulação e multi-contas)
│   ├── 👤 Usuários Críticos (Cadastros com histórico de chargeback e multi-cartão)
│   └── 💳 Cartões Compartilhados (Card hopping e ataques distribuídos)
└── 🎯 4. Insights & Proposta (Insights & Policy Proposal)
    ├── Resumo de KPIs (Prevenção >85%, Aprovação Legítima >90%, Fraude Alvo <2,5%, Latência <10ms)
    ├── 💡 Aba 1: Heurísticas & Diagnóstico Analítico (6 regras estatísticas comprovadas com dados reais)
    ├── 🛡️ Aba 2: Matriz de Políticas em 3 Vias (Cartões interativos Green / Yellow / Red Path)
    ├── ⚙️ Aba 3: Arquitetura do Motor em Tempo Real (Validação em camadas REST API <10ms)
    └── 🌐 Aba 4: Dados para Próxima Geração (Device fingerprinting, Geo-IP, MCC, telemetria 3DS)
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
Documentação desenvolvida com auxílio de Inteligência Artificial.
</div>

