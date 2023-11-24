import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Dashboard", layout="wide")

#Criando separador por competência
df = pd.read_csv("Dash.csv", sep=",")
df["Dta_Instalacao"] = pd.to_datetime(df["Dta_Instalacao"])
df = df.sort_values("Dta_Instalacao")

df["Month"] = df["Dta_Instalacao"].apply(lambda x: str(x.year) + "-" + str(x.month))

#Criando Sidebar de filtros
st.sidebar.write(f"<div style='font-family: Alfa Slab One, sans-serif; font-size: 25px; color: #DE2207;'>Filtros:</div>", unsafe_allow_html=True)

filtro_escolha = st.sidebar.selectbox("Visão Por:", ["Produtos", "Cidades", "Contato_time_vendas"])

#Criando Filtros
if filtro_escolha == "Produtos":
    filtro_selecionado = st.sidebar.multiselect("Produto", df["Produto"].unique())
elif filtro_escolha == "Contato_time_vendas":
    filtro_selecionado = st.sidebar.multiselect("Contato_time_vendas", df["Contato_time_vendas"].unique())
else:
    filtro_selecionado = st.sidebar.multiselect("Cidades", df["Ciadade"].unique())

month = st.sidebar.selectbox("Competência", df["Month"].unique())

df_filtered = df[df["Month"] == month]

if filtro_escolha == "Produtos":
    df_filtered = df_filtered[df_filtered["Produto"].isin(filtro_selecionado)]
elif filtro_escolha == "Contato_time_vendas":
    df_filtered = df_filtered[df_filtered["Contato_time_vendas"].isin(filtro_selecionado)]
else:
    df_filtered = df_filtered[df_filtered["Ciadade"].isin(filtro_selecionado)]

contagem_bairros = len(df_filtered)

#Printando os gráficos
col1, col2 = st.columns(2)
col3, col5 = st.columns(2)

fig_agendamento = px.bar(df_filtered, x="Ciadade", color="Ciadade", title="Total por Bairro")
fig_prod = px.bar(df_filtered, x="Produto", color="Produto", title="Produto")
fig_ven = px.bar(df_filtered, x="Contato_time_vendas", color="Contato_time_vendas", title="Time de Vendas", orientation="v")

col1.write(f"<div style='font-family: Alfa Slab One, sans-serif; font-size: 50px; color: #DE2207;'>Total:</div>", unsafe_allow_html=True)
col2.write(f"<div style='font-family: Alfa Slab One, sans-serif; font-size: 50px; color: #DE2207;'>{contagem_bairros}</div>", unsafe_allow_html=True)

col3.plotly_chart(fig_agendamento, use_container_width=True)
col5.plotly_chart(fig_ven, use_container_width=True)
st.plotly_chart(fig_prod, use_container_width=True)
