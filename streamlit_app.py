import streamlit as st

st.set_page_config(
    page_title="Calculadora de Importação e Markup",
    layout="centered"
)

# ==== TÍTULO ====
st.title("🧮 Calculadora de Importação e Markup")

st.write(
    "Simulador para descobrir **quanto você pode pagar em dólar** "
    "mantendo uma faixa de markup mínima e máxima."
)

# ==== SIDEBAR: CONFIGURAÇÕES GERAIS ====
st.sidebar.header("Configurações da operação")

tipo_op = st.sidebar.radio("Tipo de operação", ["Importado", "Nacional"], index=0)

cotacao = st.sidebar.number_input(
    "Cotação do dólar (R$/US$)",
    value=5.60,
    step=0.01,
    format="%.4f"
)

adicional = st.sidebar.number_input(
    "Adicional sobre valor em dólar (tabela %)",
    value=75.0,
    step=0.5,
    help="Percentual aplicado sobre o valor em dólar (ex: +75% direto na tabela)."
) / 100

ipi = st.sidebar.number_input(
    "IPI (%)",
    value=9.75 if tipo_op == "Importado" else 0.0,
    step=0.25,
    help="IPI incidente na operação considerada."
) / 100

st.sidebar.markdown("---")

st.sidebar.subheader("Tributos e custos internos (equivalentes sobre a base)")

icms = st.sidebar.number_input(
    "ICMS equivalente (%)",
    value=18.0,
    step=0.5,
    help="Percentual efetivo médio de ICMS sobre o custo (não necessariamente a alíquota cheia legal)."
)

iva = st.sidebar.number_input(
    "IVA / MVA equivalente (%)",
    value=0.0,
    step=0.5,
    help="Use um valor equivalente médio se quiser considerar impacto de IVA/MVA/ST."
)

custo_op = st.sidebar.number_input(
    "Custo operacional (%)",
    value=6.0,
    step=0.5,
    help="Percentual de custo operacional sobre o custo (frete, rateios, etc)."
)

outros_enc = st.sidebar.number_input(
    "Outros encargos (%)",
    value=0.0,
    step=0.5,
    help="Qualquer outro custo/encargo médio que queira embutir."
)

# converte para fração
encargos_total = (icms + iva + custo_op + outros_enc) / 100.0

st.sidebar.markdown(
    f"**Encargos equivalentes totais:** ~{encargos_total*100:.2f}%"
)

st.sidebar.markdown("---")

mrkp_min = st.sidebar.number_input(
    "Markup mínimo desejado (%)",
    value=20.0,
    step=0.5
) / 100

mrkp_max = st.sidebar.number_input(
    "Markup máximo alvo (%)",
    value=27.0,
    step=0.5
) / 100

st.sidebar.caption(
    "O mínimo é seu piso de segurança.\n"
    "O máximo é o alvo ideal para essa linha de produto."
)

# ==== DADOS DA OPERAÇÃO ====
st.subheader("Dados da operação")

col1, col2 = st.columns(2)

with col1:
    preco_venda = st.number_input(
        "Preço de venda (R$)",
        value=8.82,
        step=0.10,
        format="%.2f",
        help="Preço final que você pretende praticar para o cliente."
    )

with col2:
    preco_dolar = st.number_input(
        "Preço negociado em dólar (US$) (opcional)",
        value=0.00,
        step=10.0,
        format="%.2f",
        help="Preencha apenas se já tiver uma oferta do fornecedor em dólar.\n"
             "Se não tiver ainda, deixe 0 para ver só o mínimo/máximo que você poderia pagar."
    )

st.caption(
    "Use primeiro sem preencher o valor em dólar para descobrir o **mínimo e o máximo** que você pode pagar.\n"
    "Depois, quando tiver uma cotação em US$, você pode testar se ela respeita sua faixa de markup."
)

# ==== CÁLCULO DO FATOR TOTAL R$/US$ ====
# Aqui consideramos: dólar → cotação → adicional → IPI → encargos internos equivalentes
fator_total = cotacao * (1 + adicional) * (1 + ipi) * (1 + encargos_total)



# ==== FAIXA DE CUSTO E FAIXA DE DÓLAR (SEM PRECISAR TER O PREÇO EM US$) ====
st.markdown("---")
st.subheader("Faixa de custo e faixa de dólar aceitável")

if preco_venda > 0 and fator_total > 0 and mrkp_min >= 0 and mrkp_max > mrkp_min:
    # custo alvo em R$ para os limites de markup
    custo_min_r = preco_venda / (1 + mrkp_max)  # menor custo = markup mais alto
    custo_max_r = preco_venda / (1 + mrkp_min)  # maior custo = markup mais baixo

    usd_min = custo_min_r / fator_total
    usd_max = custo_max_r / fator_total

    col_a, col_b = st.columns(2)
    with col_a:
        st.metric("Custo MÍNIMO em R$ (markup máximo)", f"R$ {custo_min_r:,.4f}")
        st.metric("Preço MÍNIMO em dólar (US$)", f"US$ {usd_min:,.4f}")
    with col_b:
        st.metric("Custo MÁXIMO em R$ (markup mínimo)", f"R$ {custo_max_r:,.4f}")
        st.metric("Preço MÁXIMO em dólar (US$)", f"US$ {usd_max:,.4f}")

    st.info(
        "Se o fornecedor vier **abaixo do preço mínimo em dólar**, seu markup fica **acima do alvo máximo**.\n"
        "Se vier **acima do preço máximo em dólar**, seu markup cai **abaixo do mínimo desejado**."
    )
else:
    st.warning("Preencha um preço de venda válido e configure a faixa de markup corretamente para ver a faixa de dólar.")

# ==== ANÁLISE DE UM PREÇO EM DÓLAR ESPECÍFICO (OPCIONAL) ====
st.markdown("---")
st.subheader("Analisar um valor específico em dólar (opcional)")

if preco_dolar > 0 and fator_total > 0 and preco_venda > 0:
    custo_total_r = preco_dolar * fator_total
    mrkp_real = preco_venda / custo_total_r - 1

    col_x, col_y, col_z = st.columns(3)
    with col_x:
        st.metric("Custo total em R$", f"R$ {custo_total_r:,.4f}")
    with col_y:
        st.metric("Markup real", f"{mrkp_real*100:.2f}%")
    with col_z:
        st.metric("Preço em dólar testado", f"US$ {preco_dolar:,.2f}")

    # comparação com faixa desejada
    if mrkp_real < mrkp_min:
        st.error("Markup abaixo do **mínimo desejado**. 🟥")
    elif mrkp_real > mrkp_max:
        st.warning("Markup **acima do alvo máximo** (lucro maior, mas pode ficar caro demais). 🟨")
    else:
        st.success("Markup **dentro da faixa desejada**. 🟩")
else:
    st.caption(
        "Quando você tiver uma cotação real em dólar, preencha o campo acima para ver "
        "o custo total em R$ e o markup real dessa oferta."
    )

st.markdown("---")
st.caption(
    "Simulador de apoio à decisão. Ajuste os percentuais de encargos para refletirem a "
    "realidade da sua empresa (ICMS, IVA/MVA, custos operacionais, etc.)."
)
