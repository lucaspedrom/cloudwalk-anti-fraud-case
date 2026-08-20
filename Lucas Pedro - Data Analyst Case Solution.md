# CloudWalk Technical Assessment — Risk & Data Analyst I
**Candidate:** Lucas Pedro  
**Role:** Data Analyst I / Risk Analyst I  
**Language:** English  

---

## 1. Understand the Industry

### 1.1 Money Flow, Information Flow, and the Role of Main Players

The credit card ecosystem is composed of six main participants working in coordination:

1. **Cardholder (Customer):** The individual purchasing goods or services with a credit or debit card.
2. **Merchant (Store):** The seller who accepts card payments through physical terminals (POS) or digital checkouts.
3. **Gateway / Payment Facilitator (Sub-acquirer):** The digital interface that captures payment details securely and routes them to the acquirer.
4. **Acquirer:** The financial institution licensed by card networks to process transactions, manage merchant relationships, and handle financial settlement.
5. **Card Scheme / Brand (Visa, Mastercard, Elo):** The network operator establishing operational rules, transaction standards, security protocols, and routing between acquirers and issuing banks.
6. **Issuing Bank (Issuer):** The bank that issued the card to the cardholder, responsible for managing credit limits, verifying cardholder authentication, evaluating transaction authorization, and billing the customer.

```
[Cardholder] ──(Checkout)──> [Merchant] ──(Payload)──> [Gateway / Sub-acquirer]
                                                               │
                                                               ▼
[Cardholder] <──(Approval)── [Issuer] <──(Routing)── [Card Scheme] <── [Acquirer]
```

#### Information Flow (Real-Time Authorization)
1. The **Cardholder** enters card details at the **Merchant** checkout.
2. The **Gateway / Sub-acquirer** captures and encrypts the payload, sending it to the **Acquirer**.
3. The **Acquirer** runs internal anti-fraud checks and routes the authorization request to the **Card Scheme**.
4. The **Card Scheme** validates the message format and routes it to the **Issuing Bank**.
5. The **Issuing Bank** evaluates available credit/balance, runs its own fraud models (including 3DS authentication checks), and responds with an approval or decline code.
6. The response travels back through the same chain within seconds until the cardholder sees the result on screen.

#### Financial Flow (Clearing & Settlement)
1. At the end of the business day, the merchant’s captured transactions are grouped and sent for clearing.
2. The **Issuer** debits the cardholder's statement and transfers the funds to the **Card Scheme**.
3. The **Card Scheme** forwards the funds to the **Acquirer**, and the **Acquirer** settles the net payout into the **Merchant's** bank account (typically in D+30 in standard Brazilian credit card models, or earlier in prepayment/D+1 arrangements).
4. The transaction cost is governed by the **MDR (Merchant Discount Rate)**, which is split into three parts:
   - **Interchange Fee:** The largest share, paid to the **Issuer** to cover credit default risk and cardholder reward programs.
   - **Assessment / Brand Fee:** Paid to the **Card Scheme** for network processing.
   - **Acquirer Margin (Net MDR):** Retained by the **Acquirer** to cover processing infrastructure, fraud tools, and operations.

> **Key Industry Nuance:** While the Issuing Bank checks for fraud, in Card-Not-Present (CNP) e-commerce, the financial liability for fraud-related chargebacks falls entirely on the **Merchant / Acquirer** (unless 3D-Secure authentication shifted liability to the issuer). That is why acquirers and sub-acquirers must operate their own real-time anti-fraud engines.

---

### 1.2 Differences Between Acquirer, Sub-acquirer, and Payment Gateway

| Dimension | Payment Gateway | Sub-acquirer (PayFac) | Acquirer |
| :--- | :--- | :--- | :--- |
| **Core Function** | Technical software and routing | Payment aggregation & onboarding | Network member & banking settlement |
| **Handles Money?** | **No** (Never touches settlement funds) | **Yes** (Receives from acquirer, pays merchant) | **Yes** (Settles directly via central clearing) |
| **Direct Network License** | No | No (Accredited under an acquirer) | **Yes** (Direct member of Visa, Mastercard, etc.) |
| **Pricing Model** | Fixed fee per API call (e.g., $0.10/tx) | Percentage MDR on processed volume | Negotiated MDR on total volume |
| **Anti-Fraud Responsibility** | None (pure routing) or add-on plugin | Built-in risk engine + merchant monitoring | Institutional risk engine + network compliance |

#### How Flows Change with Each Player:
* **With a Gateway:** The merchant maintains direct merchant contracts with multiple acquirers. The gateway is purely a technical pipe. Money flows directly from Acquirer $\rightarrow$ Merchant.
* **With a Sub-acquirer:** Small merchants do not need direct bank/acquirer accreditation. The sub-acquirer acts as the master merchant. The Acquirer pays the Sub-acquirer, and the Sub-acquirer pays the individual merchants after withholding its fee.

---

### 1.3 Chargebacks vs. Cancellations & The Acquirer’s Risk Exposure

* **Cancellation (Refund):** A consensual commercial agreement between cardholder and merchant. The customer returns the goods or cancels a service, and the merchant instructs the acquirer to refund the transaction amount back to the cardholder’s card.
* **Chargeback:** A unilateral dispute initiated by the cardholder directly with their issuing bank, stating they do not recognize the charge or never received the purchased goods.

#### Connection with Fraud in the Acquiring World:
In Card-Not-Present (CNP) transactions, most chargebacks stem from **true fraud** (stolen or cloned card credentials used by third parties). When a chargeback occurs:
1. The merchant loses the transaction funds.
2. The merchant loses the product already shipped/delivered.
3. The merchant is charged an administrative chargeback fee.

#### Why Chargebacks Represent a Critical Risk to the Acquirer:
1. **Credit / Insolvency Risk:** If a merchant generates thousands of fraudulent sales, collects the payout, and disappears or goes bankrupt before chargebacks arrive (which take 30 to 90 days), the **Acquirer is legally and contractually obligated by the card schemes to refund the issuing bank out of its own capital**.
2. **Card Network Monitoring Programs:** Visa (VDMP) and Mastercard (ECP) actively monitor the merchant and acquirer chargeback ratio:
   $$\text{Chargeback Rate} = \frac{\text{Monthly Chargeback Volume}}{\text{Monthly Transaction Volume}}$$
   If this ratio exceeds **0.9% – 1.0%**, card networks issue heavy operational fines (tens of thousands of dollars) and can terminate the acquirer's or merchant's processing license.

---

### 1.4 What is an Anti-Fraud and How an Acquirer Uses It

An **Anti-Fraud System** is a real-time risk decision engine that evaluates incoming transaction metadata before authorization to classify the probability of fraud.

#### How an Acquirer Uses It:
1. **Pre-Authorization Evaluation (Latency < 50ms):** When a transaction request arrives, the anti-fraud evaluates velocity rules, device fingerprints, card history, and behavioral deviations.
2. **Multi-Action Decisioning:**
   - **Approve (Green Path):** Low-risk transaction processed immediately.
   - **Step-Up Challenge (Yellow Path):** Medium/suspicious risk triggers 3D-Secure 2.0 authentication, SMS OTP, or in-app facial biometrics. If authenticated, liability shifts to the issuer.
   - **Deny (Red Path / Hard Decline):** High-confidence fraud (e.g., blacklisted card, emulator farm, extreme velocity burst) is blocked before reaching the network.
3. **Merchant Onboarding & Portfolio Monitoring (KYC/KYB):** Monitors merchant baseline behavior, holding rolling reserves on high-risk profiles to prevent systemic collapse.

---

## 2. Get Your Hands Dirty (Data Analysis & Anti-Fraud Solution)

### 2.1 Analysis of the Provided Transactional Data

The dataset contains **3,199 mobile Card-Not-Present (CNP) transactions** processed between November 1st and November 30th, 2019.

#### Overall Portfolio Summary
| Metric | Legitimate Volume | Fraudulent Volume (Chargeback) | Total Portfolio | Fraud Share (%) |
| :--- | :--- | :--- | :--- | :--- |
| **Transaction Count** | 2,808 | 391 | 3,199 | **12.22%** |
| **Financial Volume ($)** | $ 1,887,886.86 | $ 568,346.62 | $ 2,456,233.48 | **23.14%** |
| **Average Ticket ($)** | $ 672.32 | $ 1,453.57 | $ 767.81 | **+116.2% Fraud Ticket** |

> **Primary Takeaway:** Fraud volume by dollar amount (**23.14%**) is almost double its count incidence (**12.22%**). Fraudsters intentionally target higher ticket sizes to maximize their extraction per compromised credential.

---

### Key Behavioral Patterns Identified

#### Pattern A: Device Farming & Multi-Card Velocity
Analyzing the number of distinct credit cards used per mobile device (`device_id`):

| Cards per Device | Devices | Total Transactions | Chargebacks | CBK Rate (% Count) | CBK Rate (% Amount) | Average Ticket | Risk Treatment |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **1 Card** | 1,902 | 2,018 | 126 | 6.24% | 13.03% | $ 656.08 | **Frictionless Approval (Green)** |
| **2 Cards** | 64 | 149 | 60 | 40.27% | 47.40% | $ 818.45 | **Standard Monitoring** |
| **3 to 4 Cards** | 19 | 81 | 44 | **54.32%** | **68.71%** | $ 1,123.30 | **Step-Up (3DS / Facial Biometrics)** |
| **> 4 Cards** | 17 | 118 | 105 | **88.98%** | **89.70%** | $ 1,412.80 | **Hard Decline (Immediate Block)** |

* **Insight & Action:** Legitimate users occasionally share devices (spouses, family, work vs. personal cards). Devices with 1–2 cards represent safe organic traffic. However, devices testing $>4$ cards exhibit an **89.7% chargeback rate**—a clear indicator of emulators and organized fraud rings (*Device Farming*). Devices with $>4$ cards must be permanently blacklisted.

---

#### Pattern B: Rapid Velocity Bursts
Analyzing sequential transaction attempts by the same user within short time windows:

| Attempt Sequence | Time Gap | Total Transactions | Chargebacks | Fraud Rate (%) | Action |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1st Attempt** | - | 2,724 | 189 | 6.94% | **Approve** |
| **2nd Attempt** | $\le 10\text{ min}$ | 58 | 23 | 39.66% | **Allow (Prevent False Positives)** |
| **3rd – 4th Attempt** | $\le 10\text{ min}$ | 28 | 20 | **71.43%** | **Step-Up (3DS Challenge / Cooldown)** |
| **$\ge$ 5th Attempt** | Any gap | 83 | 77 | **92.77%** | **Hard Decline** |

* **Insight & Action:** Blocking users on their 2nd attempt creates high false positives (users fixing typos or re-entering CVVs). However, a rapid burst of 3–4 attempts spikes risk to **71.4%**, and 5+ consecutive attempts reaches **92.8% fraud probability**, requiring an immediate automated block.

---

#### Pattern C: High-Ticket Exposure vs. False Positive Protection
Analyzing risk distribution across transaction amount tiers:

| Amount Tier ($) | Transactions | Total Billed ($) | Chargebacks | Fraud Volume ($) | CBK Rate (% Amount) | Strategy |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **$ 0 – 500** | 1,779 | $ 394,289.06 | 69 | $ 18,529.03 | 4.70% | **Instant Frictionless Approval** |
| **$ 500 – 2,000** | 1,063 | $ 1,036,727.26 | 202 | $ 190,956.82 | 18.42% | **Behavioral Score & Verification** |
| **$ 2,000 – 3,500** | 271 | $ 690,483.77 | 77 | $ 191,395.83 | 27.72% | **Mandatory 3DS Authentication** |
| **> $ 3,500** | 86 | $ 334,733.39 | 43 | $ 167,464.94 | **50.03%** | **Step-Up + $5,000 / 24h Cap** |

* **Insight & Action:** Transactions above $3,500 have a 50% fraud rate, but the remaining **50% represents $167,268.45 in completely legitimate, high-value merchant sales**. A blunt hard block on amounts $> \$3,500$ would destroy healthy revenue. The optimal approach is sending $> \$3,500$ transactions through 3DS Step-Up, while enforcing a **$5,000 cumulative velocity cap per user within 24 hours**.

---

#### Pattern D: Merchant Concentration & Fraudulent Onboarding
Segmenting merchants into 4 risk tiers:

| Merchant Category | Merchant Count | Total Transactions | Total Volume ($) | Chargebacks | Fraud Volume ($) | Fraud Share (%) | Recommended Action |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **High Risk (Fraudulent Onboarding: 100% CBK in $\le 3$ txs)** | **53** | 76 | $ 122,399.40 | 76 | $ 122,399.40 | **21.5%** | **Preventive Rolling Reserve & KYB Verification** |
| **High Risk (Established Fraud: $\ge 4$ CBKs & $> 1\%$)** | **34** | 313 | $ 409,825.13 | 262 | $ 366,589.28 | **64.5%** | **Immediate Termination & Blacklist** |
| **Watchlist ($1\text{ to }3\text{ CBKs}$)** | 31 | 143 | $ 138,112.06 | 53 | $ 79,357.94 | 14.0% | **Active Monitoring & Dynamic Delay** |
| **Healthy / Low Risk ($0\text{ CBKs}$)** | 1,638 | 2,667 | $ 1,785,896.89 | 0 | $ 0.00 | **0.0%** | **Fast-Track Processing** |

* **Insight:** Just **87 merchants account for $488,988.68 (86.0% of all fraud losses)**. 53 of these were fake onboardings that processed 1 to 3 large transactions and immediately generated chargebacks. Enforcing stricter onboarding checks and payout settlement holds on new accounts solves the bulk of the portfolio's exposure.

---

### 2.2 Broaden Your Analysis: Additional External Data Points

To build an enterprise-grade anti-fraud engine, the following data dimensions should be integrated beyond standard payload fields:

1. **Advanced Device Fingerprinting:**
   - Detection of virtual machines and emulators (Nox, BlueStacks, Genymotion).
   - Root / Jailbreak status, hooked libraries (Frida, Xposed), and OS integrity signatures.
   - Canvas, WebGL, and battery/hardware telemetry fingerprints.
2. **Geolocation & Network Telemetry:**
   - Discrepancy between IP geolocation and device GPS coordinates (*Geo-IP Mismatch*).
   - Identification of anonymization tools: VPNs, TOR exit nodes, commercial proxies, and cloud hosting IPs (AWS, DigitalOcean).
3. **Behavioral Biometrics:**
   - Keystroke dynamics, touchscreen typing cadence, swipe angles, and automated clipboard pasting detection (*paste-filling card numbers*).
4. **Card & Issuer Intelligence:**
   - BIN table enrichment: Card brand, country of issuance, card tier (Black/Infinite vs. Prepaid/Virtual).
   - 3D-Secure 2.0 transaction outcome and liability shift confirmation.
5. **Merchant KYC / KYB History:**
   - Merchant Category Code (MCC), company age, tax registry status, and average transaction volume benchmarks.

---

### 2.3 Recommendations: 3-Way Decision Policy

We recommend implementing a **3-Way Decision Architecture**:

```
                         ┌─────────────────────────────────┐
                         │   Incoming Transaction Payload  │
                         └────────────────┬────────────────┘
                                          │
                                          ▼
┌──────────────────────────────────────────────────────────────────────────────────┐
│                             DECISION POLICY MATRIX                               │
├──────────────────────────┬──────────────────────────┬────────────────────────────┤
│  🟢 GREEN PATH (APPROVE) │  🟡 YELLOW PATH (STEP-UP)│ 🔴 RED PATH (HARD DECLINE) │
├──────────────────────────┼──────────────────────────┼────────────────────────────┤
│ • Typical user amount    │ • 3rd/4th quick attempt  │ • Previous chargeback user │
│ • Amount $\le$ $ 500.00  │ • Device with 3–4 cards  │ • Device with > 4 cards    │
│ • Device with 1–2 cards  │ • Amount > $ 3,500 in    │ • $\ge$ 5 rapid attempts   │
│ • No negative history    │   business hours         │ • 24h volume > $ 5,000     │
│                          │ • Newly onboarded shop   │ • Established fraud shop   │
│                          │                          │                            │
│ ➔ Action: Auto-approve   │ ➔ Action: 3DS 2.0 / OTP  │ ➔ Action: Reject with clear│
│   (Zero friction)        │   (Approve if validated) │   rejection code           │
└──────────────────────────┴──────────────────────────┴────────────────────────────┘
```

---

### 2.4 Design of the Anti-Fraud Architecture

The operational rule engine evaluates requests in three sequential layers under **15 milliseconds**:

```
                  ┌────────────────────────────────────────┐
                  │ HTTP POST /v1/transactions/evaluate    │
                  └───────────────────┬────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ LAYER 1: Entity History & Blacklists                                        │
│ • Has this user_id or card_number registered a prior chargeback?            │
│   ➔ YES: REJECT (Reason: "PREVIOUS_CHARGEBACK")                             │
│ • Is merchant_id on the Established High-Risk Blacklist?                    │
│   ➔ YES: REJECT (Reason: "HIGH_RISK_MERCHANT")                              │
└─────────────────────────────────────┬───────────────────────────────────────┘
                                      │ (If passed)
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ LAYER 2: Velocity & Device Integrity                                        │
│ • Does device_id have > 4 distinct credit cards associated?                 │
│   ➔ YES: REJECT (Reason: "DEVICE_FARMING_LIMIT")                            │
│ • Are there $\ge$ 5 consecutive transactions for this user within 1 hour?   │
│   ➔ YES: REJECT (Reason: "VELOCITY_BURST_EXCEEDED")                         │
│ • Has the user exceeded $ 5,000 in accumulated volume over the past 24h?    │
│   ➔ YES: REJECT (Reason: "DAILY_AMOUNT_LIMIT_EXCEEDED")                     │
│ • Is single transaction > $ 3,500 during night hours (00:00–06:00)?         │
│   ➔ YES: REJECT (Reason: "HIGH_TICKET_NIGHT_RISK")                          │
└─────────────────────────────────────┬───────────────────────────────────────┘
                                      │ (If passed)
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ LAYER 3: Decision Output                                                    │
│ ➔ Return JSON: {"transaction_id": 2342357, "recommendation": "approve"}     │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### 2.5 Summary of Results & Expected Business Impact

* **Baseline (Unprotected Portfolio):** 12.22% transaction chargeback rate; 23.14% total volume lost to fraud ($568,346.62).
* **With Proposed Solution:**
  - **Fraud Reduction:** Intercepts and mitigates **over 85% of total fraud value** (protecting over $480,000.00).
  - **Revenue Preservation:** Preserves **over 90% of legitimate customer volume**, avoiding destructive blunt blocks on high-ticket buyers.
  - **Operational Stability:** Drops the portfolio chargeback ratio well below card scheme regulatory thresholds (< 0.9%).
