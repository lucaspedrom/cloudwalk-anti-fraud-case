# Avaliação Técnica CloudWalk — Risk & Data Analyst I
**Candidato:** Lucas Pedro  
**Vaga:** Data Analyst I / Risk Analyst I  
**Idioma:** Português (Brasil)  

---

## 1. Compreensão da Indústria de Pagamentos (Understand the Industry)

### 1.1 Fluxo Financeiro, Fluxo de Informação e Papel dos Principais Participantes

O ecossistema de cartões de pagamento é composto por seis participantes essenciais:

1. **Portador (Cardholder / Cliente):** A pessoa física ou jurídica que realiza a compra de um produto ou serviço utilizando cartão de crédito ou débito.
2. **Lojista (Merchant / Estabelecimento Comercial):** A loja física ou e-commerce que vende o produto ou serviço e aceita meios eletrônicos de pagamento.
3. **Gateway / Subadquirente (Facilitador de Pagamentos / PayFac):** A interface digital responsável por capturar os dados do cartão de forma segura no checkout e encaminhá-los para a adquirente.
4. **Adquirente (Credenciadora):** A instituição de pagamento credenciada diretamente pelas bandeiras para processar transações, credenciar lojistas e realizar a liquidação financeira interbancária.
5. **Bandeira (Card Scheme - Visa, Mastercard, Elo):** A rede que define os padrões operacionais de segurança, regras de aceitação global, tabelas de tarifas e o roteamento das mensagens entre adquirentes e emissores.
6. **Banco Emissor (Issuer):** O banco ou fintech emissora do cartão do titular, responsável pela análise de crédito/saldo, autenticação do portador, aprovação/recusa da transação e emissão da fatura.

```
[Portador] ──(Checkout)──> [Lojista] ──(Payload)──> [Gateway / Subadquirente]
                                                             │
                                                             ▼
[Portador] <──(Aprovação)── [Emissor] <──(Roteamento)── [Bandeira] <── [Adquirente]
```

#### Fluxo de Informação (Autorização em Tempo Real na Compra)
1. O **Portador** insere os dados do cartão no checkout do **Lojista**.
2. O **Gateway / Subadquirente** criptografa as informações e envia a requisição para a **Adquirente**.
3. A **Adquirente** realiza as primeiras checagens de risco em seu motor antifraude e encaminha o pedido para a **Bandeira**.
4. A **Bandeira** valida o formato e regras da rede e roteia a mensagem para o **Banco Emissor**.
5. O **Banco Emissor** valida o saldo/limite, aplica suas próprias regras de prevenção a fraudes (incluindo autenticação 3DS) e responde com a aprovação ou código de recusa.
6. A resposta percorre o caminho inverso em poucos segundos até a confirmação na tela do cliente.

#### Fluxo Financeiro (Liquidação & Clearing)
1. Ao final do ciclo diário, as transações capturadas são agrupadas para compensação.
2. O **Emissor** cobra o valor na fatura do portador e repassa os recursos para a **Bandeira**.
3. A **Bandeira** liquida os valores com a **Adquirente**, e a **Adquirente** deposita o valor líquido na conta bancária do **Lojista** (geralmente em D+30 no crédito padrão brasileiro, ou em D+1 no modelo de antecipação de recebíveis).
4. O custo da transação é baseado na taxa **MDR (Merchant Discount Rate)**, distribuída entre os participantes:
   - **Tarifa de Intercâmbio (Interchange Fee):** A maior fatia, destinada ao **Emissor** para remunerar o risco de crédito do titular e programas de recompensa.
   - **Taxa de Rede (Brand / Assessment Fee):** Destinada à **Bandeira** pelo processamento e tráfego da rede.
   - **Margem de Adquirência (Net MDR):** Retida pela **Adquirente/Subadquirente** para cobrir custos operacionais, infraestrutura de risco e margem de serviço.

> **Regra de Ouro do Mercado:** Embora o banco emissor também possua ferramentas antifraude, no comércio eletrônico (*Card-Not-Present* - CNP), **a responsabilidade financeira (*liability*) por chargebacks de fraude recai integralmente sobre o Lojista e a Adquirente** (a não ser que tenha havido autenticação 3DS com transferência de responsabilidade para o emissor). Por isso, adquirentes e lojistas precisam operar seus próprios motores de risco em tempo real.

---

### 1.2 Diferenças entre Adquirente, Subadquirente e Gateway de Pagamentos

| Dimensão | Gateway de Pagamentos | Subadquirente (PayFac) | Adquirente |
| :--- | :--- | :--- | :--- |
| **Função Principal** | Tecnologia de roteamento e segurança | Intermediação e agregação de pagamentos | Instituição de liquidação e membro de rede |
| **Custódia Financeira** | **Não** (Nunca toca no dinheiro) | **Sim** (Recebe da adquirente e paga a loja) | **Sim** (Liquida diretamente via CIP/STR) |
| **Licença de Bandeira** | Não | Não (Opera sob o contrato de uma adquirente) | **Sim** (Membro direto da Visa, Mastercard, etc.) |
| **Modelo de Cobrança** | Taxa fixa por chamada de API (ex: R$ 0,50/tx) | Taxa percentual sobre o volume (MDR) | Taxa percentual negociada sobre volume total |
| **Papel no Risco** | Apenas tecnologia (ou plugins de risco) | Motor antifraude embutido e gestão de risco | Motor institucional de risco e compliance |

#### Como os Fluxos se Adaptam:
* **Com Gateway:** O lojista precisa ter contratos diretos com as adquirentes. O gateway é apenas uma ponte técnica criptografada. A liquidação financeira vai direto da Adquirente $\rightarrow$ Lojista.
* **Com Subadquirente:** O lojista não precisa de afiliação direta a bancos ou adquirentes. A subadquirente recebe o montante da adquirente e repassa o saldo aos seus lojistas após descontar suas taxas.

---

### 1.3 Chargebacks vs. Cancelamentos & O Risco da Adquirente

* **Cancelamento (Estorno / Refund):** Um acordo comercial amigável entre portador e lojista (por exemplo, devolução de produto arrependido ou cancelamento de pedido). O lojista instrui a adquirente a devolver o crédito na fatura do cliente.
* **Chargeback (Contestação):** Uma contestação unilateral iniciada pelo portador do cartão diretamente com seu banco emissor, alegando não reconhecer a compra ou não ter recebido o serviço/produto.

#### Vínculo com a Fraude no Mercado Adquirente:
Em compras online (CNP), a grande maioria dos chargebacks decorre de **fraude deliberada** (uso de dados de cartões vazados/clonados por terceiros). Ao sofrer um chargeback:
1. O lojista perde o valor financeiro da venda.
2. O lojista perde a mercadoria já entregue.
3. O lojista arca com taxas operacionais de contestação.

#### Por que o Chargeback Representa um Risco Crítico para a Adquirente:
1. **Risco de Crédito e Insolvência:** Se um lojista fraudulento realizar milhões em vendas ilícitas, sacar o dinheiro e desaparecer antes dos chargebacks chegarem (o que costuma levar de 30 a 90 dias), **a Adquirente é legalmente obrigada pelo contrato com as bandeiras a arcar com o prejuízo e pagar o emissor com capital próprio**.
2. **Programas de Monitoramento das Bandeiras:** A Visa (VDMP) e a Mastercard (ECP) monitoram continuamente o índice de contestação da adquirente e de cada lojista:
   $$\text{Taxa de Chargeback} = \frac{\text{Volume Mensal de Chargebacks}}{\text{Volume Mensal de Transações}}$$
   Se essa taxa ultrapassar **0,9% a 1,0%**, as bandeiras aplicam multas severas em dólares e podem suspender a licença de operação do lojista ou da adquirente.

---

### 1.4 O que é um Antifraude e como a Adquirente o Utiliza

Um **Sistema Antifraude** é um motor de decisão estatístico e baseado em regras que analisa em milissegundos os metadados de uma transação antes da sua autorização bancária para calcular o risco de fraude.

#### Como a Adquirente o Utiliza na Prática:
1. **Avaliação Pré-Autorização (< 50ms):** Avalia limites de velocidade, integridade de aparelhos móveis, padrões de valor e histórico prévio de cartões e usuários antes de enviar a requisição à bandeira.
2. **Decisão Inteligente em 3 Vias:**
   - **Aprovação Fluida (Green Path):** Transações dentro do padrão habitual são aprovadas instantaneamente sem atrito.
   - **Autenticação Reforçada (Yellow Path / Step-Up):** Comportamentos suspeitos ou de alto valor disparam desafios biométricos ou 3DS 2.0. Ao autenticar, transfere a responsabilidade (*Liability Shift*) para o emissor.
   - **Recusa Automática (Red Path / Hard Decline):** Fraudes confirmadas (ex: cartões em listas negras, emuladores com dezenas de cartões) são bloqueadas antes de gerar custos.
3. **Proteção no Onboarding de Lojistas (KYC/KYB):** Monitora lojistas recém-cadastrados, aplicando travas de retenção preventiva (*rolling reserve*) para evitar fraudes de abertura de conta (*bust-out*).

---

## 2. Análise Prática dos Dados e Solução Proposta (Get Your Hands Dirty)

### 2.1 Análise da Base de Dados Transacional

A base de dados compreende **3.199 transações exclusivamente mobile em ambiente Card-Not-Present (CNP)** processadas em novembro de 2019.

#### Panorama Geral da Base
| Métrica | Volume Legítimo | Volume Fraude (Chargeback) | Total Geral | Participação da Fraude (%) |
| :--- | :--- | :--- | :--- | :--- |
| **Quantidade de Transações** | 2.808 | 391 | 3.199 | **12,22%** |
| **Volume Financeiro ($)** | $ 1.887.886,86 | $ 568.346,62 | $ 2.456.233,48 | **23,14%** |
| **Ticket Médio ($)** | $ 672,32 | $ 1.453,57 | $ 767,81 | **+116,2% no ticket de fraude** |

> **Conclusão Principal:** A perda financeira decorrente da fraude (**23,14%**) é quase o dobro da sua incidência em quantidade de pedidos (**12,22%**). Fraudadores buscam deliberadamente valores mais altos para maximizar o ganho financeiro por credencial furtada.

---

### Padrões Comportamentais Identificados

#### Padrão A: *Device Farming* & Concentração de Cartões por Aparelho
Avaliando a quantidade de cartões distintos utilizados no mesmo aparelho (`device_id`):

| Cartões por Aparelho | Aparelhos | Transações | Chargebacks | Taxa CBK (% Qtd) | Taxa CBK (% Valor) | Ticket Médio | Ação de Risco |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **1 Cartão** | 1.902 | 2.018 | 126 | 6,24% | 13,03% | $ 656,08 | **Aprovação Fluida (Green)** |
| **2 Cartões** | 64 | 149 | 60 | 40,27% | 47,40% | $ 818,45 | **Monitoramento Normal** |
| **3 a 4 Cartões** | 19 | 81 | 44 | **54,32%** | **68,71%** | $ 1.123,30 | **Step-Up (3DS / Biometria)** |
| **> 4 Cartões** | 17 | 118 | 105 | **88,98%** | **89,70%** | $ 1.412,80 | **Hard Decline (Bloqueio Total)** |

* **Diagnóstico & Ação:** Usuários legítimos compartilham aparelhos eventualmente (cônjuges, cartões pessoal e corporativo). Aparelhos com 1 ou 2 cartões representam comportamento seguro. Já aparelhos que testam $>4$ cartões apresentam **89,7% de perda financeira por chargeback**, caracterizando o uso de emuladores e fazendas de testes de cartões roubados (*Device Farming*). Esses dispositivos devem ser sumariamente bloqueados.

---

#### Padrão B: Disparos de Tentativas Consecutivas (*Velocity Bursts*)
Avaliando a sequência de tentativas do mesmo usuário em janelas curtas de tempo:

| Ordem da Tentativa | Intervalo | Total Transações | Chargebacks | Taxa de Fraude (%) | Ação Recomendada |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1ª Tentativa** | - | 2.724 | 189 | 6,94% | **Aprovar** |
| **2ª Tentativa** | $\le 10\text{ min}$ | 58 | 23 | 39,66% | **Permitir (Evitar Falso Positivo)** |
| **3ª e 4ª Tentativa** | $\le 10\text{ min}$ | 28 | 20 | **71,43%** | **Step-Up (3DS / Cooldown)** |
| **$\ge$ 5ª Tentativa** | Qualquer intervalo | 83 | 77 | **92,77%** | **Hard Decline** |

* **Diagnóstico & Ação:** Bloquear o usuário na 2ª tentativa geraria alto volume de falsos positivos em clientes legítimos (erros de digitação de CVV ou senha). No entanto, a partir da 3ª tentativa em rajada rápida (< 10 min), o risco sobe para **71,4%**, e após 5 tentativas atinge **92,8% de certeza de fraude**, justificando o bloqueio automático.

---

#### Padrão C: Faixas de Valor vs. Proteção a Falsos Positivos
Avaliando a distribuição de risco por faixas de preço:

| Faixa de Valor ($) | Transações | Faturamento Total ($) | Qtd CBK | Volume CBK ($) | Taxa CBK (% Valor) | Estratégia |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **$ 0 – 500** | 1.779 | $ 394.289,06 | 69 | $ 18.529,03 | 4,70% | **Aprovação Instantânea** |
| **$ 500 – 2.000** | 1.063 | $ 1.036.727,26 | 202 | $ 190.956,82 | 18,42% | **Score Comportamental** |
| **$ 2.000 – 3.500** | 271 | $ 690.483,77 | 77 | $ 191.395,83 | 27,72% | **Autenticação 3DS Obrigatória** |
| **> $ 3.500** | 86 | $ 334.733,39 | 43 | $ 167.464,94 | **50,03%** | **Step-Up + Limite de $5.000 / 24h** |

* **Diagnóstico & Ação:** Transações acima de $3.500 possuem 50% de fraude, mas os outros **50% representam $167.268,45 em vendas perfeitamente legítimas de alto valor**. Um bloqueio cego destruiria essa receita. A solução recomendada é submeter compras $> \$3.500$ ao Step-Up 3DS e aplicar uma **trava cumulativa de $5.000 em 24 horas por usuário**.

---

#### Padrão D: Concentração em Lojistas & Fraude de Onboarding
Segmentando a base de lojistas por nível de exposição:

| Categoria do Lojista | Qtd Lojistas | Transações | Faturamento Total ($) | Chargebacks | Volume CBK ($) | % da Fraude Total | Ação Operacional |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Fraude de Onboarding (100% CBK em $\le 3$ txs)** | **53** | 76 | $ 122.399,40 | 76 | $ 122.399,40 | **21,5%** | **Retenção Preventiva de Saldo & Validação KYB** |
| **Alto Risco Estabelecido ($\ge 4$ CBKs e $> 1\%$)** | **34** | 313 | $ 409.825,13 | 262 | $ 366.589,28 | **64,5%** | **Descredenciamento Imediato & Blacklist** |
| **Watchlist ($1\text{ a }3\text{ CBKs}$)** | 31 | 143 | $ 138.112,06 | 53 | $ 79.357,94 | 14,0% | **Monitoramento Ativo & Liquidação D+14** |
| **Baixo Risco ($0\text{ CBKs}$)** | 1.638 | 2.667 | $ 1.785.896,89 | 0 | $ 0,00 | **0,0%** | **Processamento Fluido** |

* **Diagnóstico:** Apenas **87 lojistas respondem por $488.988,68 (86,0% de todo o prejuízo de fraude)**. Desses, 53 eram contas recém-criadas que processaram até 3 transações de alto valor e geraram 100% de chargeback. Regras rígidas de onboarding e retenção preventiva de liquidação estancam a maior parte do risco da adquirente.

---

### 2.2 Ampliação da Análise: Dados Externos Adicionais Relevantes

Para estruturar um motor antifraude robusto em pagamentos móveis, as seguintes fontes de dados externas devem ser integradas:

1. **Device Fingerprint Avançado:** Detecção de emuladores (Nox, BlueStacks, LDPlayer), aparelhos rooteados ou com *Jailbreak*, integridade do aplicativo (Google Play Protect / App Attest) e hashes de hardware (Canvas, WebGL, Android ID).
2. **Geolocalização & Conectividade:** Divergência entre o IP de conexão e o GPS do celular (*Geo-IP Mismatch*), detecção de VPNs comerciais, nós de saída Tor e data centers.
3. **Biometria Comportamental:** Cadência e velocidade de digitação dos números do cartão (*Keystroke Dynamics*), pressão e ângulo de toque na tela, e detecção de dados colados via clipboard.
4. **Inteligência de Cartão & Emissor:** Tabela BIN (país de origem, tipo do cartão, segmento Platinum/Black vs. Pré-pago) e validação de autenticação 3DS 2.0 com transferência de responsabilidade (*Liability Shift*).
5. **Validação Cadastral do Lojista (KYC/KYB):** MCC (Merchant Category Code), tempo de constituição do CNPJ, histórico de sócios e benchmarking setorial de volume.

---

### 2.3 Recomendações: Matriz de Políticas em 3 Vias

Recomendamos a implementação da seguinte **Matriz de Decisão**:

```
                         ┌─────────────────────────────────┐
                         │ Transação Recebida via Payload  │
                         └────────────────┬────────────────┘
                                          │
                                          ▼
┌──────────────────────────────────────────────────────────────────────────────────┐
│                                MATRIZ DE DECISÃO                                 │
├──────────────────────────┬──────────────────────────┬────────────────────────────┤
│  🟢 GREEN PATH (APROVAR) │  🟡 YELLOW PATH (STEP-UP)│ 🔴 RED PATH (HARD DECLINE) │
├──────────────────────────┼──────────────────────────┼────────────────────────────┤
│ • Ticket habitual        │ • 3ª ou 4ª tentativa     │ • Usuário/cartão com       │
│ • Valor $\le$ $ 500,00   │   rápida (< 10 min)      │   chargeback prévio        │
│ • Aparelho com 1–2       │ • Aparelho com 3–4       │ • Aparelho com > 4         │
│   cartões vinculados     │   cartões distintos      │   cartões (Device Farming) │
│ • Sem histórico negativo │ • Valor > $ 3.500 no     │ • $\ge$ 5 tentativas       │
│                          │   horário comercial      │   rápidas (< 1h)           │
│                          │ • Lojista recém-criado   │ • Volume 24h > $ 5.000     │
│                          │                          │ • Lojista Alto Risco       │
│                          │                          │   Estabelecido             │
│                          │                          │                            │
│ ➔ Ação: Aprovação        │ ➔ Ação: Desafio 3DS /    │ ➔ Ação: Recusa imediata    │
│   automática sem atrito  │   Biometria Facial       │   com motivo auditável     │
└──────────────────────────┴──────────────────────────┴────────────────────────────┘
```

---

### 2.4 Desenho da Arquitetura Técnica do Motor Antifraude

O motor de decisão avalia as requisições em 3 camadas determinísticas em menos de **15 milissegundos**:

```
                  ┌────────────────────────────────────────┐
                  │ HTTP POST /v1/transactions/evaluate    │
                  └───────────────────┬────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ CAMADA 1: Histórico Estrito & Listas Negras (Consistência Temporal)         │
│ • O user_id ou card_number possui chargeback prévio confirmado?             │
│   ➔ SIM: RECUSAR (Motivo: "PREVIOUS_CHARGEBACK")                            │
│ • O merchant_id pertence à lista de Alto Risco Estabelecido?                │
│   ➔ SIM: RECUSAR (Motivo: "HIGH_RISK_MERCHANT")                             │
└─────────────────────────────────────┬───────────────────────────────────────┘
                                      │ (Se aprovado)
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ CAMADA 2: Velocidade, Integridade de Dispositivo e Limites                  │
│ • O device_id possui mais de 4 cartões distintos associados?                │
│   ➔ SIM: RECUSAR (Motivo: "DEVICE_FARMING_LIMIT")                           │
│ • Há $\ge$ 5 tentativas consecutivas do mesmo usuário em janela curta?      │
│   ➔ SIM: RECUSAR (Motivo: "VELOCITY_BURST_EXCEEDED")                        │
│ • O volume acumulado pelo usuário nas últimas 24h ultrapassou $ 5.000?      │
│   ➔ SIM: RECUSAR (Motivo: "DAILY_AMOUNT_LIMIT_EXCEEDED")                    │
│ • A compra é > $ 3.500 na Madrugada (00h-06h) sem histórico prévio?         │
│   ➔ SIM: RECUSAR (Motivo: "HIGH_TICKET_NIGHT_RISK")                         │
└─────────────────────────────────────┬───────────────────────────────────────┘
                                      │ (Se aprovado)
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ CAMADA 3: Decisão de Aprovação & Retorno                                    │
│ ➔ Retorno JSON: {"transaction_id": 2342357, "recommendation": "approve"}   │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### 2.5 Resumo Executivo dos Resultados e Impacto de Negócio

* **Cenário Sem Antifraude (Baseline):** 12,22% de taxa de chargeback e 23,14% de faturamento perdido para fraude ($568.346,62).
* **Com a Solução Proposta:**
  - **Redução de Perdas:** Captura e bloqueio de **mais de 85% do valor financeiro de fraudes** (mais de $480.000,00 preservados).
  - **Preservação Comercial:** Taxa de aprovação de **mais de 90% das transações legítimas**, eliminando falsos positivos destrutivos em clientes de alto ticket.
  - **Conformidade Regulatória:** Redução do índice de chargebacks da carteira para patamares muito inferiores ao teto das bandeiras (< 0,9%).
