import streamlit as st
from PIL import Image
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import base64
import streamlit.components.v1 as components
from qt_material import apply_stylesheet
from streamlit_javascript import st_javascript

# Define o tema qt_material
st.markdown("""
    <style>
        .css-1bkhjr6 {
            background-color: #F0F0F0;
            border-radius: 10px;
            padding: 10px;
            margin: 10px;
        }
    </style>
""", unsafe_allow_html=True)

# Criando separador por competência
df = pd.read_csv("Fat_Gerado_Por.csv", sep=",")
df["DATA_EMISSAO"] = pd.to_datetime(df["DATA_EMISSAO"])
df = df.sort_values("DATA_EMISSAO")

df["Competencia"] = df["DATA_EMISSAO"].apply(lambda x: str(x.year) + "-" + str(x.month))

# Criando Sidebar de filtros
st.sidebar.write(f"<div style='font-family: Alfa Slab One, sans-serif; font-size: 25px; color: #E05007;'>Filtros:</div>", unsafe_allow_html=True)

month = st.sidebar.selectbox("Competência", df["Competencia"].unique())

df_filtered = df[df["Competencia"] == month]

filtro_escolha = st.sidebar.selectbox("Visão Por:", ["Geral", "Operador"])

# Printando os gráficos
col1, col2, col8, col9, col10 = st.columns(5)
col3, col4, col5 = st.columns(3)
col6 = st.columns(1)
# Tabela
fat1, fat2, fat3, fat4, fat5, fat6, fat7 = st.columns(7) 

# Criando as Visões
if filtro_escolha == "Geral":
    df_filtered = df_filtered
else: 
    filtro_selecionado = st.sidebar.multiselect("Operador", df["OPERADOR"].unique())
    
if filtro_escolha == "Geral":
    df_filtered = df_filtered
else:
    df_filtered = df_filtered[df_filtered["OPERADOR"].isin(filtro_selecionado)]
    values_to_display = df_filtered["FAT"].tolist()
    values_to_displayII = df_filtered["VALOR_TOTAL"].tolist()
    values_to_displayVI = df_filtered["CLIENTE"].tolist()
    values_to_displayV = df_filtered["VCTO"].tolist()
    values_to_displayVII = df_filtered["FAIXA_DE_ATRASO"].tolist()
    values_to_displayVIII = df_filtered["STATUS_RECEBIMENTO"].tolist()
    values_to_displayIX = df_filtered["CONTATO"].tolist()
    
    formatted_values = [f"<div style='font-family: Alfa Slab One, sans-serif; font-size: 10px;'>{value}</div>" for value in values_to_display]
    formatted_valuesII = [f"<div style='font-family: Alfa Slab One, sans-serif; font-size: 10px;'>{value}</div>" for value in values_to_displayII]
    formatted_valuesV = [f"<div style='font-family: Alfa Slab One, sans-serif; font-size: 10px;'>{value}</div>" for value in values_to_displayV]
    formatted_valuesVI = [f"<div style='font-family: Alfa Slab One, sans-serif; font-size: 10px;'>{value}</div>" for value in values_to_displayVI]
    formatted_valuesVII = [f"<div style='font-family: Alfa Slab One, sans-serif; font-size: 10px;'>{value}</div>" for value in values_to_displayVII]
    formatted_valuesVIII = [f"<div style='font-family: Alfa Slab One, sans-serif; font-size: 10px;'>{value}</div>" for value in values_to_displayVIII]
    formatted_valuesIX = [f"<div style='font-family: Alfa Slab One, sans-serif; font-size: 10px;'>{value}</div>" for value in values_to_displayIX]
    fat1.write("***Fatura***")
    fat2.write("***Valor***")
    fat3.write("***Data Vencimento***")
    fat4.write("***Faixa de Atraso***")
    fat6.write("***Cliente***")
    fat5.write("***Status Pagamento***")
    fat7.write("***Telefone***")
    fat1.write("".join(formatted_values), unsafe_allow_html=True)
    fat2.write("".join(formatted_valuesII), unsafe_allow_html=True)
    fat3.write("".join(formatted_valuesV), unsafe_allow_html=True)
    fat4.write("".join(formatted_valuesVII), unsafe_allow_html=True)
    fat6.write("".join(formatted_valuesVI), unsafe_allow_html=True) 
    fat5.write("".join(formatted_valuesVIII), unsafe_allow_html=True)
    fat7.write("".join(formatted_valuesIX), unsafe_allow_html=True)
    
# Botão de download
def download_csv(df):
    csv_file = df.to_csv(index=False, encoding="utf-8")
    b64 = base64.b64encode(csv_file.encode()).decode()
    href = f"<a href='data:file/csv;base64,{b64}' download='Cobranca.csv' style='color: white; background-color: #E05007; padding: 10px; border-radius: 5px; text-decoration: none;'>Download CSV</a>"
    return href

st.sidebar.markdown(download_csv(df_filtered), unsafe_allow_html=True)

# Criando Graficos
Total = len(df_filtered)
Valor = round(sum(df_filtered["VALOR_TOTAL"]), 2)

df_filtered_pago = df_filtered[df_filtered["STATUS_RECEBIMENTO"].isin(["PAGO"])]
Valor_Pago = round(sum(df_filtered_pago["VALOR_TOTAL"]), 2)

df_filtered_atraso = df_filtered[df_filtered["FAIXA_DE_ATRASO"].isin(["1 A 34 DIAS", "35 A 45 DIAS", "46 A 60 DIAS", "61 A 75 DIAS", "76 A 90 DIAS", "91 A 180 DIAS", "181 A 360 DIAS", "(+) 361 DIAS"])]
count_atraso = df_filtered_atraso["FAIXA_DE_ATRASO"].value_counts()

df_filtered_a_receber = df_filtered[df_filtered["FAIXA_DE_ATRASO"].isin(["A VENCER"])]
Valor_a_receber = round(sum(df_filtered_a_receber["VALOR_TOTAL"]), 2)

Valor_quebras = round(sum(df_filtered_atraso["VALOR_TOTAL"]), 2)
 
count_pagamento = df_filtered["PAGAMENTO"].value_counts()
count_status = df_filtered["STATUS_PAGAMENTO"].value_counts()
count_dia = df_filtered["DATA_EMISSA0_2"].value_counts()

df_filtered_vencimento = df_filtered[df_filtered["STATUS_RECEBIMENTO"].isin(["VENCIDO", "A VENCER"])]
count_vencimento = df_filtered_vencimento["STATUS_RECEBIMENTO"].value_counts()

labels_pagamento = count_pagamento.index
labels_status = count_status.index
values_pagamento = count_pagamento.values
values_status = count_status.values

fig_pagamento_pizza = go.Figure(data=[go.Pie(labels=labels_pagamento, values=values_pagamento, pull=[0.01, 0.03, 0.2, 0.02, 0.01], hole= 0.05)])
fig_pagamento_pizza.update_layout(title="Forma de Pagamento")

fig_vencimento = px.bar(count_vencimento, x=count_vencimento.index, y=count_vencimento.values, color=count_vencimento.index, title="Vencimento", orientation="v")
fig_data = px.bar(count_dia, x=count_dia.index, y=count_dia.values, color=count_dia.index, title="Negociação por Dia", orientation="v")

fig_Pag = go.Figure(data=[go.Pie(labels=labels_status, values=values_status, pull=[0, 0.03], hole= 0.04)])
fig_Pag.update_layout(title="Total por status")


fig_data.update_layout(
    margin=dict(l=0, r=0, b=0, t=30),  # Margens para melhor visualização
    paper_bgcolor="#FFFFE1",    # Cor de fundo
    font=dict(family="Alfa Slab One", size=12, color="#333"),  # Estilo de fonte
    title=dict(text="Negociação por Dia", font=dict(size=20, color="#000")),  # Estilo do título com tamanho ajustado
    showlegend=True,
    autosize=True,
    height=400,
    shapes=[
        dict(
            type='rect',
            xref='paper',
            yref='paper',
            x0=0,
            y0=0,
            x1=1,
            y1=1,
            fillcolor='rgba(255,255,255,0)',
            line=dict(color='rgba(255,255,255,0.5)', width=2)
        )
    ]
)

col1.write(f"""<div style='background-color: #FFFFE1; border: 2px solid #EF7900; border-radius: 10px; padding: 15px; margin: 10px 0; color: #EF7900; font-family: "Alfa Slab One", sans-serif; font-size: 25px;
height: 100px; width: 200px; font-weight: bold;'> <center>Total: <br>{Total}</br></center> </div>""", unsafe_allow_html=True)
col2.write(f"""<div style='background-color: #FFFFE1; border: 2px solid #EF7900; border-radius: 10px; padding: 15px; margin: 10px 0; color: #EF7900; font-family: "Alfa Slab One", sans-serif; height: 100px;
width: 200px; font-size: 17.5px; font-weight: bold;'><center>Valor Renegociado: <br>R$ {Valor}</div></center>""", unsafe_allow_html=True, use_container_width=True)
col8.write(f"""<div style='background-color: #FFFFE1; border: 2px solid #EF7900; border-radius: 10px; padding: 15px; margin: 10px 0; color: #EF7900; font-family: "Alfa Slab One", sans-serif; font-size: 20px;
height: 100px; width: 200px; font-weight: bold;'><center>Valor Recebido: <br>R$ {Valor_Pago}</div></center>""", unsafe_allow_html=True, use_container_width=True)
col9.write(f"""<div style='background-color: #FFFFE1; border: 2px solid #EF7900; border-radius: 10px; padding: 15px; margin: 10px 0; color: #EF7900; font-family: "Alfa Slab One", sans-serif; font-size: 20px;
height: 100px; width: 200px; font-weight: bold;'><center>Valor A Receber: <br>R$ {Valor_a_receber}</div></center>""", unsafe_allow_html=True, use_container_width=True)
col10.write(f"""<div style='background-color: #FFFFE1; border: 2px solid #EF7900; border-radius: 10px; padding: 15px; margin: 10px 0; color: #EF7900; font-family: "Alfa Slab One", sans-serif; font-size: 20px;
height: 100px; width: 200px; font-weight: bold;'><center>Valor Quebras: <br>R$ {Valor_quebras}</div></center>""", unsafe_allow_html=True, use_container_width=True)
col3.plotly_chart(fig_Pag, use_container_width=True)
col4.plotly_chart(fig_vencimento, use_container_width=True)
col5.plotly_chart(fig_pagamento_pizza, use_container_width=True)
col6[0].plotly_chart(fig_data, use_container_width=True,  style={'min-height': '500px'})
