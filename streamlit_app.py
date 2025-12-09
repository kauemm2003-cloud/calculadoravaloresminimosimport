import streamlit as st

st.set_page_config(
    page_title="Calculadora de Importação e Markup",
    layout="centered"
)

# ==== TÍTULO ====
st.title("🧮 Calculadora de Importação e Markup")

st.write(
    "Simulador para operações **importadas ou nacionais**, "
    "calculando custo total, faixa de dólar aceitável e markup real."
)

# ==== CONFIGURAÇÕES LATERAIS ====
st.sidebar.header("Configurações da operação")

tipo_op = st.sidebar.radio("Tipo de operação", ["Importado", "Nacional"])

cotacao = st.sidebar.number_input(
    "Cotação do dólar (R$/US$)",
    value=5.60,
    step=0.01
)

adicional = st.sidebar.number_input(
    "Adicional sobre valor em dólar (tabela %)",
    value=75.0,
    step=0.5
) / 100

# IPI só entra se for importado
ipi_default = 9.75 if tipo_op == "Importado" else 0.0
ipi = st.sidebar.number_input(
    "IPI (%)",
    value=ipi_default,
    step=0.25
) / 100

encargos = st.sidebar.number_input(
    "Encargos adicionais (ICMS/IVA/custo op. etc) (%)",
    value=6.0,
    step=0.5
) / 100

mrkp_min = st.sidebar.number_input(
    "Markup mínimo desejado (%)",
    value=20.0,
    step=0.5
) / 100

mrkp_max = st.sidebar.number_input(
    "Markup máximo desejado (%)",
    value=27.0,
    step=0.5
) / 100

st.sidebar.caption(
    "Dica: use o mínimo como meta de segurança (ex: 20%) "
    "e o máximo como alvo ideal (ex: 27%)."
)

# ==== DADOS DA OPERAÇÃO ====
st.subheader("Dados da operação")

col1, col2 = st.columns(2)

with col1:
    preco_venda = st.number_input(
        "Preço de venda (R$)",
        value=17756.12,
        step=10.0,
        format="%.2f"
    )

with col2:
    preco_dolar = st.number_input(
        "Preço negociado em dólar (US$)",
        value=1300.00,
        step=10.0,
        format="%.2f"
    )

st.caption(
    "Preencha o **preço de venda** que você pratica e o **preço em dólar** "
    "que o fornecedor está oferecendo."
)

# ==== CÁLCULOS ====
# Fator total R$/US$ considerando tudo: cotação, adicional, IPI, encargos
fator_total = cotacao * (1 + adicional) * (1 + ipi) * (1 + encargos)

if preco_dolar > 0 and fator_total > 0:
    custo_total = preco_dolar * fator_total
    mrkp_real = preco_venda / custo_total - 1
else:
    custo_total = 0.0
    mrkp_real = 0.0

# Custos alvo para manter markup dentro da faixa desejada
if (1 + mrkp_max) > 0 and (1 + mrkp_min) > 0:
    custo_min = preco_venda / (1 + mrkp_max)  # custo mais baixo → markup mais alto
    custo_max = preco_venda / (1 + mrkp_min)  # custo mais alto → markup mínimo
else:
    custo_min = 0.0
    custo_max = 0.0

if fator_total > 0:
    usd_min = custo_min / fator_total
    usd_max = custo_max / fator_total
else:
    usd_min = 0.0
    usd_max = 0.0

# ==== RESULTADOS ====
st.markdown("---")
st.subheader("Resultados")

col_a, col_b, col_c = st.columns(3)

with col_a:
    st.metric("Custo total em R$", f"R$ {custo_total:,.2f}")

with col_b:
    st.metric("Markup real", f"{mrkp_real*100:.2f}%")

with col_c:
    st.metric(
        "Faixa de dólar aceitável",
        f"US$ {usd_min:,.2f} a US$ {usd_max:,.2f}"
    )

# Mensagem de status do markup
if custo_total > 0:
    if mrkp_real < mrkp_min:
        st.error("Markup abaixo do mínimo desejado. 🟥")
    elif mrkp_real > mrkp_max:
        st.warning(
            "Markup acima do alvo máximo (lucro alto, mas pode ficar caro demais). 🟨"
        )
    else:
        st.success("Markup dentro da faixa desejada. 🟩")

st.markdown("---")
st.caption(
    "Ferramenta pensada para simulação rápida de operações. "
    "Use sempre com o apoio da legislação vigente e regras internas da empresa."
)
