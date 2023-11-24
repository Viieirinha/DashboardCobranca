import streamlit as st
import folium
import plotly.express as px

# Título do aplicativo

# Criar um mapa com Folium
m = folium.Map(location=[-15.7801, -47.9292], zoom_start=10)

# Adicionar um gráfico com Plotly Express
df = px.data.gapminder()
fig = px.scatter(df, x='gdpPercap', y='lifeExp', size='pop', color='country', log_x=True)
st.plotly_chart(fig)