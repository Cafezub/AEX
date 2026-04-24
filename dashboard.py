import streamlit as st
import pandas as pd
import requests
import plotly.express as px

# Coloque aqui a URL do Firebase
FIREBASE_URL = "https://banco-5cf3c-default-rtdb.firebaseio.com"


def carregar_dados():
    endpoint = f"{FIREBASE_URL}/leituras.json"
    response = requests.get(endpoint)

    if response.status_code != 200:
        st.error("Erro ao acessar Firebase.")
        return pd.DataFrame()

    dados = response.json()

    if not dados:
        return pd.DataFrame()

    lista = []
    for key, value in dados.items():
        lista.append(value)

    df = pd.DataFrame(lista)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    return df


def detectar_anomalias(df):
    """
    Regras simples para detectar anomalias.
    """
    df["anomalia"] = False

    # consumo muito alto
    df.loc[df["consumo_kwh"] > 6.0, "anomalia"] = True

    # temperatura alta demais para freezer/geladeira
    df.loc[
        (df["equipamento"] == "Freezer_Industrial") & (df["temperatura"] > -5),
        "anomalia"
    ] = True

    df.loc[
        (df["equipamento"] == "Geladeira") & (df["temperatura"] > 10),
        "anomalia"
    ] = True

    # forno com temperatura muito baixa quando ON (falha)
    df.loc[
        (df["equipamento"] == "Forno_Eletrico") & (df["status"] == "ON") & (df["temperatura"] < 120),
        "anomalia"
    ] = True

    return df


st.set_page_config(page_title="Dashboard IoT - Energia", layout="wide")

st.title("⚡ Dashboard IoT - Monitoramento Energético (Protótipo Indústria 4.0)")
st.write("Dados simulados enviados para Cloud (Firebase) e analisados em Python.")

df = carregar_dados()

if df.empty:
    st.warning("Nenhum dado encontrado ainda. Rode o simulador primeiro.")
    st.stop()

df = detectar_anomalias(df)

# Sidebar filtros
st.sidebar.header("Filtros")
equipamentos = st.sidebar.multiselect(
    "Selecione os equipamentos:",
    options=df["equipamento"].unique(),
    default=df["equipamento"].unique()
)

df_filtrado = df[df["equipamento"].isin(equipamentos)]

# KPIs
col1, col2, col3 = st.columns(3)

col1.metric("Total de Leituras", len(df_filtrado))
col2.metric("Consumo Médio (kWh)", round(df_filtrado["consumo_kwh"].mean(), 2))
col3.metric("Anomalias Detectadas", int(df_filtrado["anomalia"].sum()))

st.divider()

# Gráfico de consumo
st.subheader("📈 Consumo Energético ao Longo do Tempo")

fig_consumo = px.line(
    df_filtrado,
    x="timestamp",
    y="consumo_kwh",
    color="equipamento",
    markers=True,
    title="Consumo (kWh) por Equipamento"
)
st.plotly_chart(fig_consumo, use_container_width=True)

# Gráfico de temperatura
st.subheader("🌡️ Temperatura ao Longo do Tempo")

fig_temp = px.line(
    df_filtrado,
    x="timestamp",
    y="temperatura",
    color="equipamento",
    markers=True,
    title="Temperatura por Equipamento"
)
st.plotly_chart(fig_temp, use_container_width=True)

st.divider()

# Tabela de anomalias
st.subheader("🚨 Registros com Anomalias")

anomalias = df_filtrado[df_filtrado["anomalia"] == True].sort_values("timestamp", ascending=False)

st.dataframe(anomalias, use_container_width=True)

st.divider()

# Consumo acumulado por equipamento
st.subheader("📊 Consumo Total por Equipamento")

consumo_total = df_filtrado.groupby("equipamento")["consumo_kwh"].sum().reset_index()

fig_bar = px.bar(
    consumo_total,
    x="equipamento",
    y="consumo_kwh",
    title="Consumo Total (Somatório kWh)"
)

st.plotly_chart(fig_bar, use_container_width=True)