from io import BytesIO
import streamlit as st
from PIL import Image
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import base64
import streamlit.components.v1 as components
from babel.numbers import format_currency
import locale
from streamlit_javascript import st_javascript
from qt_material import apply_stylesheet

# Define o tema com qt_material
st.set_page_config(
    page_title="Cobranca",
    page_icon=f"C:\\Users\\savio.menezes\\Documents\\Dash_Cobranca\\Imagens\\Logo_aba_navega.png",
    layout="wide",)

#Faz referencia ao arquivo .css
with open('styles.css')as f:
    st.markdown(f"<style id=leit>{f.read()}</style>", unsafe_allow_html = True)

# Criando Sidebar de filtros
st.sidebar.image(f"C:\\Users\\savio.menezes\\Documents\\Dash_Cobranca\\Imagens\\Group 211.svg", use_column_width=True)

# Lendo o DataFrame a partir do arquivo CSV
df = pd.read_csv("C:\\Users\\savio.menezes\\Documents\\Dash_Cobranca\\Bases\\Fat_gerado_por.csv", sep=";", on_bad_lines="skip")
df_fa = pd.read_csv(f"C:\\Users\\savio.menezes\\Documents\\Dash_Cobranca\\Bases\\FaixaDeAtraso.csv", sep=",")

# Criando seleção de abas
tab1, tab2, tab3 = st.tabs(["Cobranca", "Recebidos", "Faixa de Atraso"])

colors = px.colors.sequential.Blues[::-1]  

with tab1:
    df = df.iloc[:-1] 
    df["FILTRO_1"] = pd.to_datetime(df["FILTRO_1"])
    df = df.sort_values("FILTRO_1")
    df["DATA_NEGOCIACAO"] = pd.to_datetime(df["DATA_EMISSAO"])
    df = df.sort_values("DATA_NEGOCIACAO")
    df["Month"] = df["DATA_NEGOCIACAO"].apply(lambda x: str(x.year) + "-" + str(x.month))
    df["Quarter"] = df["DATA_NEGOCIACAO"].dt.to_period("Q")
    
    # Criando um contêiner no topo da página para os filtros
    fil1, fil2, fil3, fil4 = st.columns(4)

    # Filtro de datas
    selected_periodo = fil1.selectbox("Período:", ["Mês", "Dia", "Trimestre", "Data Negociação"])
    
    default_month = "2025-10"
    max_allowed_month = "2025-10"

    unique_months = sorted(df["Month"].unique())

    if selected_periodo == "Mês":
        month = fil2.selectbox("Mês", unique_months, index=unique_months.index(default_month))

        # Ensure selected month does not exceed the maximum allowed month
        month = min(month, max_allowed_month)

        df_filtered = df[df["Month"] == month]
        df_filtered_mes = df[df["Month"] == month]

    elif selected_periodo == "Trimestre":
        quarters_with_data = df["Quarter"].unique()
        quarter = fil2.selectbox("Trimestre", quarters_with_data)

        df_filtered = df[df["Quarter"] == quarter]
        df_filtered_mes = df[df["Quarter"] == quarter]

    elif  selected_periodo == "Data Negociação":
        date_range = fil2.date_input("Selecione um intervalo de tempo", [df["DATA_NEGOCIACAO"].min(), df["DATA_NEGOCIACAO"].max()])
        # Verifica se o intervalo selecionado possui apenas uma data
        if len(date_range) == 1:
            start_date = end_date = pd.Timestamp(date_range[0])
        else:
            start_date = pd.Timestamp(date_range[0])
            end_date = pd.Timestamp(date_range[1])
        df_filtered = df[(df["DATA_NEGOCIACAO"] >= start_date) & (df["DATA_NEGOCIACAO"] <= end_date)]
        df_filtered_mes = df[(df["DATA_NEGOCIACAO"] >= start_date) & (df["DATA_NEGOCIACAO"] <= end_date)]


    else:
        date_range = fil2.date_input("Selecione um intervalo de tempo", [df["FILTRO_1"].min(), df["FILTRO_1"].max()])
        # Verifica se o intervalo selecionado possui apenas uma data
        if len(date_range) == 1:
            start_date = end_date = pd.Timestamp(date_range[0])
        else:
            start_date = pd.Timestamp(date_range[0])
            end_date = pd.Timestamp(date_range[1])
        df_filtered = df[(df["FILTRO_1"] >= start_date) & (df["FILTRO_1"] <= end_date)]
        df_filtered_mes = df[(df["FILTRO_1"] >= start_date) & (df["FILTRO_1"] <= end_date)]


    # Filtro de visão
    filtro_escolha = fil3.selectbox("Visão Por:", ["Geral", "Operador"])

    # Printando os gráficos

    col1, col2, col8, col9, col10, col11 = st.columns(6)
    col3, col4, col5 = st.columns(3)
    col6 = st.columns(1)
    # Tabela
    fat1 = st.columns(1)

    if filtro_escolha == "Geral":
        df_filtered = df_filtered
        filtro_selecionado = fil4.selectbox("Operador", [])

    elif selected_periodo == "Mês" and filtro_escolha == 'Operador':
        operadores_mes_selecionado = df_filtered[df_filtered["Month"] == month]["OPERADOR"].unique()
        filtro_selecionado = fil4.multiselect("Operadores", operadores_mes_selecionado)
        df_filtered = df_filtered[df_filtered["OPERADOR"].isin(filtro_selecionado)]	
        
    else:
        filtro_selecionado = [fil4.selectbox("Operador", df["OPERADOR"].unique())]
        df_filtered = df_filtered[df_filtered["OPERADOR"].isin(filtro_selecionado)]
        fat1[0].write(df_filtered, use_container_width=True)	

    # Filtrar o DataFrame apenas para os registros em que o "STATUS_RECEBIMENTO" seja "PAGO"
    df_filtered_pago = df_filtered_mes[df_filtered_mes['STATUS_PAGAMENTO'] == 'PAGO']

    # Agrupar pelos operadores e calcular a soma dos valores para os registros pagos
    df_grouped2 = df_filtered_pago.groupby('OPERADOR')['VALOR_TOTAL'].sum().reset_index()

    # Encontrar a linha com o valor máximo
    max_row = df_grouped2[df_grouped2['VALOR_TOTAL'] == df_grouped2['VALOR_TOTAL'].max()]

    if not max_row.empty:
        max_operator = max_row['OPERADOR'].values[0]
        max_value = max_row['VALOR_TOTAL'].values[0]

        max_value_formatado = "R$ {:,.2f}".format(max_value)

        # Crie um bloco de informação na barra lateral
        st.sidebar.markdown(f"""**MELHOR RECUPERADOR DE CRÉDITO**""")  

        st.sidebar.image(f"C:\\Users\\savio.menezes\\Documents\\Dash_Cobranca\\Imagens\\trofeu.png", use_column_width=True)

        st.sidebar.markdown(
            f"""
            **Operador:** {max_operator}

            **Valor:** {max_value_formatado}
            """
        )
    else:
        # If max_row is empty, display a message indicating that no maximum value was found
        st.sidebar.markdown("Nenhum valor a ser mostrado.")
    
    
    # Botão de download
    def download_excel(df):
        with BytesIO() as b:
            df_filtered.to_excel(b, index=False, engine='openpyxl', header=True)
            b.seek(0)
            href = f"<a href='data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{base64.b64encode(b.read()).decode()}' download='Fat_gerado_por.xlsx' style='color: white; background-color: #E05007; padding: 10px; border-radius: 5px; text-decoration: none;'>Download Excel</a>"
        return href

    # Criando Graficos

    Total = len(df_filtered)
    Valor = round(sum(df_filtered["VALOR_TOTAL"]), 2)

    df_filtered_pago = df_filtered[df_filtered["STATUS_RECEBIMENTO"].isin(["PAGO"])]
    Valor_Pago = round(sum(df_filtered_pago["Val_last_paid"]), 2)

    df_filtered_atraso = df_filtered[df_filtered["FAIXA_DE_ATRASO"].isin(["1 A 34 DIAS", "35 A 45 DIAS", "46 A 60 DIAS", "61 A 75 DIAS", "76 A 90 DIAS", "91 A 180 DIAS", "181 A 360 DIAS", "(+) 361 DIAS"])]
    count_atraso = df_filtered_atraso["FAIXA_DE_ATRASO"].value_counts()

    df_filtered_a_receber = df_filtered[df_filtered["STATUS_RECEBIMENTO"].isin(["A VENCER"])]
    Valor_a_receber = round(sum(df_filtered_a_receber["VALOR_TOTAL"]), 2)

    df_filtered.loc[:, 'FILTRO_2'] = pd.to_datetime(df_filtered['FILTRO_2'])

    df_filtered_a_quebras = df_filtered[df_filtered['FILTRO_2'] <= pd.Timestamp('now') - pd.DateOffset(1)]
   
    df_quebras = df_filtered_a_quebras[df_filtered_a_quebras['STATUS_RECEBIMENTO'] == 'VENCIDO']
    
    total_quebras = df_quebras['FAT'].nunique()

    Valor_quebras = round(sum(df_quebras["VALOR_TOTAL"]), 2)

    try:
        locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
    except locale.Error:
        locale.setlocale(locale.LC_ALL, 'Portuguese_Brazil.1252')

    # Formatando os valores como moeda
    Valor_formatado = locale.currency(Valor, grouping=True)
    Valor_Pago_formatado = locale.currency(Valor_Pago, grouping=True)
    Valor_a_receber_formatado = locale.currency(Valor_a_receber, grouping=True)
    Valor_quebras_formatado = locale.currency(Valor_quebras, grouping=True)
    
    count_pagamento = df_filtered["PAGAMENTO"].value_counts()
    count_status = df_filtered["STATUS_PAGAMENTO"].value_counts()
    count_dia = df_filtered["date_last_paid"].value_counts()

    df_filtered_vencimento = df_filtered[df_filtered["STATUS_RECEBIMENTO"].isin(["VENCIDO", "A VENCER"])]
    count_vencimento = df_filtered_vencimento["STATUS_RECEBIMENTO"].value_counts()

    labels_pagamento = count_pagamento.index
    labels_status = count_status.index    
    values_pagamento = count_pagamento.values
    values_status = count_status.values
    

    fig_pagamento_pizza = go.Figure(data=[go.Pie(labels=labels_pagamento, values=values_pagamento, pull=[0.01, 0.03, 0.2, 0.02, 0.02], hole=0.7)])
    fig_pagamento_pizza.update_layout(title="Forma de Pagamento")
    fig_pagamento_pizza.update_traces(marker=dict(colors=colors))

    if len(count_vencimento) == 0:
        # Se count_vencimento estiver vazio, criar um gráfico vazio
        fig_vencimento = px.bar(title="Vencimento")
    else:
        # Caso contrário, criar o gráfico normalmente
        fig_vencimento = px.bar(count_vencimento, x=count_vencimento.index, y=count_vencimento.values, color=count_vencimento.index, title="Vencimento", orientation="v",color_discrete_sequence=colors)
    
    for i, value in enumerate(count_vencimento.values):
        fig_vencimento.add_annotation(
            x=count_vencimento.index[i],
            y=value,
            text=str(value),
            showarrow=False,
            arrowhead=4,
            xshift=0,
            yshift=15
        )
        
    if len(count_dia) == 0:
        fig_data = px.bar(title="Vencimento")
    else:
        fig_data = px.bar(count_dia, x=count_dia.index, y=count_dia.values, color=count_dia.index, title="Negociação por Dia", orientation="v")

    fig_Pag = go.Figure(data=[go.Pie(labels=labels_status, values=values_status, pull=[0, 0.03], hole=0.7)])
    fig_Pag.update_layout(title="Total por status")
    fig_Pag.update_traces(marker=dict(colors=colors))

    # Suponha que df_grouped seja o DataFrame que você criou com 'DATA_EMISSAO' e 'VALOR_TOTAL'
    df_grouped = df_filtered.groupby('date_last_paid')['VALOR_TOTAL'].sum().reset_index()

    # Converta a coluna 'DATA_EMISSAO' para o tipo datetime
    df_grouped['date_last_paid'] = pd.to_datetime(df_grouped['date_last_paid'])

    df_grouped['Data_Recebimento'] = df_grouped['date_last_paid'].dt.strftime('%d %b').str.upper()

    # Crie o gráfico de linha
    fig_data = px.line(df_grouped, x='Data_Recebimento', y='VALOR_TOTAL', title="Negociação por Dia", line_shape='linear', render_mode='svg')
    fig_data.update_xaxes(tickangle=25)

    # Adicione pontos para cada valor com tamanho maior
    fig_data.add_trace(go.Scatter(x=df_grouped['Data_Recebimento'], y=df_grouped['VALOR_TOTAL'],name='Valor', mode='markers',marker=dict(size=10, line=dict(color='blue', width=2), color='white')))

    for i, value in enumerate(df_grouped['VALOR_TOTAL']):
        # Formate o valor como moeda usando babel
        value_formatado = format_currency(value, 'BRL', locale='pt_BR.UTF-8').split(',')[0]
        
        fig_data.add_annotation(
            x=df_grouped['Data_Recebimento'][i],
            y=value,
            text=f"{value_formatado}",  # Exibir o valor formatado como moeda
            showarrow=False,
            font=dict(size=10),
            xshift=0,
            yshift=20,
        )

    # Atualize o layout do gráfico
    fig_data.update_layout(
        font=dict(family="Alfa Slab One", size=12, color="#333"),
        height=400)

    col1.write(f"""<div id="Info" > <center>Total: <br>{Total}</br></center> </div>""", unsafe_allow_html=True)

    col2.write(f"""<div id="Info" > <center>Valor Renegociado: <br> {Valor_formatado}</div></center>""", unsafe_allow_html=True, use_container_width=True)

    col8.write(f"""<div id="Info" > <center>Valor Recebido: <br> {Valor_Pago_formatado}</div></center>""", unsafe_allow_html=True, use_container_width=True)

    col9.write(f"""<div id="Info" > <center>Valor A Receber: <br> {Valor_a_receber_formatado}</div></center>""", unsafe_allow_html=True, use_container_width=True)

    col10.write(f"""<div id="Info" > <center>Valor Quebras: <br> {Valor_quebras_formatado}</div></center>""", unsafe_allow_html=True, use_container_width=True)

    col11.write(f"""<div id="Info" > <center>Total de Quebras: <br> {total_quebras}</div></center>""", unsafe_allow_html=True, use_container_width=True)

    col4.plotly_chart(fig_Pag, use_container_width=True)
    col3.plotly_chart(fig_vencimento, use_container_width=True)
    col5.plotly_chart(fig_pagamento_pizza, use_container_width=True)
    col6[0].plotly_chart(fig_data, use_container_width=True,  style={'min-height': '500px'})

    # Agrupando os FATs e somando o VALOR_TOTAL
    tabela_fat_valores = df_filtered.groupby("FAT", as_index=False)["VALOR_TOTAL"].sum()

    # Ordenando do maior para o menor valor
    tabela_fat_valores = tabela_fat_valores.sort_values(by="VALOR_TOTAL", ascending=False)

    with st.expander("🔍 Ver detalhes das negociações"):
        # Seleciona e ordena as colunas desejadas
        tabela_detalhada = df_filtered[[
            "CONTRATO", 
            "OPERADOR", 
            "FAT", 
            "VALOR_TOTAL", 
            "DATA_EMISSAO", 
            "date_last_paid", 
            "STATUS_PAGAMENTO"
        ]].copy()

        # Ordena por VALOR_TOTAL do maior para o menor
        tabela_detalhada = tabela_detalhada.sort_values(by="VALOR_TOTAL", ascending=False)

        st.markdown("### 📊 Detalhamento de Negociações")
        st.dataframe(tabela_detalhada, use_container_width=True)

        # # Botão de download
        # def download_detalhamento(df_detalhe):
        #     with BytesIO() as b:
        #         df_detalhe.to_excel(b, index=False, engine='openpyxl', header=True)
        #         b.seek(0)
        #         href = f"<a href='data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{base64.b64encode(b.read()).decode()}' download='Detalhamento_Negociacoes.xlsx' style='color: white; background-color: #007ACC; padding: 10px; border-radius: 5px; text-decoration: none;'>📥 Baixar Tabela</a>"
        #     return href

    # st.markdown(download_detalhamento(tabela_detalhada), unsafe_allow_html=True)

    st.markdown(download_excel(df_filtered), unsafe_allow_html=True)
    
with tab2:
    df = df.iloc[:-1] 
    df["date_last_paid"] = pd.to_datetime(df["date_last_paid"])
    df = df.sort_values("date_last_paid")
    df["date_last_paid"] = pd.to_datetime(df["date_last_paid"])
    df = df.sort_values("date_last_paid")
    df["Month"] = df["date_last_paid"].apply(lambda x: str(x.year) + "-" + str(x.month))
    df["Quarter"] = df["date_last_paid"].dt.to_period("Q")
    
    # Criando um contêiner no topo da página para os filtros
    fil1, fil2, fil3, fil4 = st.columns(4)

    # Filtro de datas
    selected_periodo = fil1.selectbox("Período:", ["Mês", "Dia", "Trimestre", "Data Recebimento"], key="Coutinho")
    
    default_month = "2025-10"
    max_allowed_month = "2025-10"

    unique_months = sorted(df["Month"].unique())

    if selected_periodo == "Mês":
        month = fil2.selectbox("Mês", unique_months, index=unique_months.index(default_month))

        # Ensure selected month does not exceed the maximum allowed month
        month = min(month, max_allowed_month)

        df_filtered = df[df["Month"] == month]
        df_filtered_mes = df[df["Month"] == month]

    elif selected_periodo == "Trimestre":
        quarters_with_data = df["Quarter"].unique()
        quarter = fil2.selectbox("Trimestre", quarters_with_data)

        df_filtered = df[df["Quarter"] == quarter]
        df_filtered_mes = df[df["Quarter"] == quarter]

    elif  selected_periodo == "Data Recebimento":
        date_range = fil2.date_input("Selecione um intervalo de tempo", [df["date_last_paid"].min(), df["date_last_paid"].max()])
        # Verifica se o intervalo selecionado possui apenas uma data
        if len(date_range) == 1:
            start_date = end_date = pd.Timestamp(date_range[0])
        else:
            start_date = pd.Timestamp(date_range[0])
            end_date = pd.Timestamp(date_range[1])
        df_filtered = df[(df["date_last_paid"] >= start_date) & (df["date_last_paid"] <= end_date)]
        df_filtered_mes = df[(df["date_last_paid"] >= start_date) & (df["date_last_paid"] <= end_date)]


    else:
        date_range = fil2.date_input("Selecione um intervalo de tempo", [df["FILTRO_1"].min(), df["FILTRO_1"].max()])
        # Verifica se o intervalo selecionado possui apenas uma data
        if len(date_range) == 1:
            start_date = end_date = pd.Timestamp(date_range[0])
        else:
            start_date = pd.Timestamp(date_range[0])
            end_date = pd.Timestamp(date_range[1])
        df_filtered = df[(df["FILTRO_1"] >= start_date) & (df["FILTRO_1"] <= end_date)]
        df_filtered_mes = df[(df["FILTRO_1"] >= start_date) & (df["FILTRO_1"] <= end_date)]


    # Filtro de visão
    filtro_escolha = fil3.selectbox("Visão Por:", ["Geral", "Operador"], key="Vegetti")

    # Printando os gráficos

    # col1, col2, col8, col9, col10, col11 = st.columns(6)
    col1, col8 = st.columns(2)
    col4, col5 = st.columns(2)
    col6 = st.columns(1)

    # Tabela
    fat1 = st.columns(1)

    if filtro_escolha == "Geral":
        df_filtered = df_filtered
        filtro_selecionado = fil4.selectbox("Operador", [], key="Nuno Moreira")

    elif selected_periodo == "Mês" and filtro_escolha == 'Operador':
        operadores_mes_selecionado = df_filtered[df_filtered["Month"] == month]["OPERADOR"].unique()
        filtro_selecionado = fil4.multiselect("Operadores", operadores_mes_selecionado)
        df_filtered = df_filtered[df_filtered["OPERADOR"].isin(filtro_selecionado)]	
        
    else:
        filtro_selecionado = [fil4.selectbox("Operador", df["OPERADOR"].unique())]
        df_filtered = df_filtered[df_filtered["OPERADOR"].isin(filtro_selecionado)]
        fat1[0].write(df_filtered, use_container_width=True)	

    # Filtrar o DataFrame apenas para os registros em que o "STATUS_RECEBIMENTO" seja "PAGO"
    df_filtered_pago = df_filtered_mes[df_filtered_mes['STATUS_PAGAMENTO'] == 'PAGO']

    # Agrupar pelos operadores e calcular a soma dos valores para os registros pagos
    df_grouped2 = df_filtered_pago.groupby('OPERADOR')['VALOR_TOTAL'].sum().reset_index()

    # Encontrar a linha com o valor máximo
    max_row = df_grouped2[df_grouped2['VALOR_TOTAL'] == df_grouped2['VALOR_TOTAL'].max()]

    if not max_row.empty:
        max_operator = max_row['OPERADOR'].values[0]
        max_value = max_row['VALOR_TOTAL'].values[0]

        max_value_formatado = "R$ {:,.2f}".format(max_value)

        # Crie um bloco de informação na barra lateral
        st.sidebar.markdown(f"""**MELHOR RECUPERADOR DE CRÉDITO**""")  

        st.sidebar.image(f"C:\\Users\\savio.menezes\\Documents\\Dash_Cobranca\\Imagens\\trofeu.png", use_column_width=True)

        st.sidebar.markdown(
            f"""
            **Operador:** {max_operator}

            **Valor:** {max_value_formatado}
            """
        )
    else:
        # If max_row is empty, display a message indicating that no maximum value was found
        st.sidebar.markdown("Nenhum valor a ser mostrado.")
    
    
    # Botão de download
    def download_excel(df):
        with BytesIO() as b:
            df_filtered.to_excel(b, index=False, engine='openpyxl', header=True)
            b.seek(0)
            href = f"<a href='data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{base64.b64encode(b.read()).decode()}' download='Fat_gerado_por.xlsx' style='color: white; background-color: #E05007; padding: 10px; border-radius: 5px; text-decoration: none;'>Download Excel</a>"
        return href

    # Criando Graficos

    Total = len(df_filtered)
    Valor = round(sum(df_filtered["VALOR_TOTAL"]), 2)

    df_filtered_pago = df_filtered[df_filtered["STATUS_RECEBIMENTO"].isin(["PAGO"])]
    Valor_Pago = round(sum(df_filtered_pago["Val_last_paid"]), 2)

    df_filtered_atraso = df_filtered[df_filtered["FAIXA_DE_ATRASO"].isin(["1 A 34 DIAS", "35 A 45 DIAS", "46 A 60 DIAS", "61 A 75 DIAS", "76 A 90 DIAS", "91 A 180 DIAS", "181 A 360 DIAS", "(+) 361 DIAS"])]
    count_atraso = df_filtered_atraso["FAIXA_DE_ATRASO"].value_counts()

    df_filtered_a_receber = df_filtered[df_filtered["STATUS_RECEBIMENTO"].isin(["A VENCER"])]
    Valor_a_receber = round(sum(df_filtered_a_receber["VALOR_TOTAL"]), 2)

    df_filtered.loc[:, 'FILTRO_2'] = pd.to_datetime(df_filtered['FILTRO_2'])

    df_filtered_a_quebras = df_filtered[df_filtered['FILTRO_2'] <= pd.Timestamp('now') - pd.DateOffset(1)]
   
    df_quebras = df_filtered_a_quebras[df_filtered_a_quebras['STATUS_RECEBIMENTO'] == 'VENCIDO']
    
    total_quebras = df_quebras['FAT'].nunique()

    Valor_quebras = round(sum(df_quebras["VALOR_TOTAL"]), 2)

    try:
        locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
    except locale.Error:
        locale.setlocale(locale.LC_ALL, 'Portuguese_Brazil.1252')

    # Formatando os valores como moeda
    Valor_formatado = locale.currency(Valor, grouping=True)
    Valor_Pago_formatado = locale.currency(Valor_Pago, grouping=True)
    Valor_a_receber_formatado = locale.currency(Valor_a_receber, grouping=True)
    Valor_quebras_formatado = locale.currency(Valor_quebras, grouping=True)
    
    count_pagamento = df_filtered["PAGAMENTO"].value_counts()
    count_status = df_filtered["STATUS_PAGAMENTO"].value_counts()
    count_dia = df_filtered["date_last_paid"].value_counts()

    df_filtered_vencimento = df_filtered[df_filtered["STATUS_RECEBIMENTO"].isin(["VENCIDO", "A VENCER"])]
    count_vencimento = df_filtered_vencimento["STATUS_RECEBIMENTO"].value_counts()

    labels_pagamento = count_pagamento.index
    labels_status = count_status.index    
    values_pagamento = count_pagamento.values
    values_status = count_status.values
    

    fig_pagamento_pizza = go.Figure(data=[go.Pie(labels=labels_pagamento, values=values_pagamento, pull=[0.01, 0.03, 0.2, 0.02, 0.02], hole=0.7)])
    fig_pagamento_pizza.update_layout(title="Forma de Pagamento")
    fig_pagamento_pizza.update_traces(marker=dict(colors=colors))

    if len(count_vencimento) == 0:
        # Se count_vencimento estiver vazio, criar um gráfico vazio
        fig_vencimento = px.bar(title="Vencimento")
    else:
        # Caso contrário, criar o gráfico normalmente
        fig_vencimento = px.bar(count_vencimento, x=count_vencimento.index, y=count_vencimento.values, color=count_vencimento.index, title="Vencimento", orientation="v",color_discrete_sequence=colors)
    
    for i, value in enumerate(count_vencimento.values):
        fig_vencimento.add_annotation(
            x=count_vencimento.index[i],
            y=value,
            text=str(value),
            showarrow=False,
            arrowhead=4,
            xshift=0,
            yshift=15
        )
        
    if len(count_dia) == 0:
        fig_data = px.bar(title="Vencimento")
    else:
        fig_data = px.bar(count_dia, x=count_dia.index, y=count_dia.values, color=count_dia.index, title="Negociação por Dia", orientation="v")

    fig_Pag = go.Figure(data=[go.Pie(labels=labels_status, values=values_status, pull=[0, 0.03], hole=0.7)])
    fig_Pag.update_layout(title="Total por status")
    fig_Pag.update_traces(marker=dict(colors=colors))

    # Suponha que df_grouped seja o DataFrame que você criou com 'DATA_EMISSAO' e 'VALOR_TOTAL'
    df_grouped = df_filtered.groupby('date_last_paid')['VALOR_TOTAL'].sum().reset_index()

    # Converta a coluna 'DATA_EMISSAO' para o tipo datetime
    df_grouped['date_last_paid'] = pd.to_datetime(df_grouped['date_last_paid'])

    df_grouped['Data_Recebimento'] = df_grouped['date_last_paid'].dt.strftime('%d %b').str.upper()

    # Crie o gráfico de linha
    fig_data = px.line(df_grouped, x='Data_Recebimento', y='VALOR_TOTAL', title="Negociação por Dia", line_shape='linear', render_mode='svg')
    fig_data.update_xaxes(tickangle=25)

    # Adicione pontos para cada valor com tamanho maior
    fig_data.add_trace(go.Scatter(x=df_grouped['Data_Recebimento'], y=df_grouped['VALOR_TOTAL'],name='Valor', mode='markers',marker=dict(size=10, line=dict(color='blue', width=2), color='white')))

    for i, value in enumerate(df_grouped['VALOR_TOTAL']):
        # Formate o valor como moeda usando babel
        value_formatado = format_currency(value, 'BRL', locale='pt_BR.UTF-8').split(',')[0]
        
        fig_data.add_annotation(
            x=df_grouped['Data_Recebimento'][i],
            y=value,
            text=f"{value_formatado}",  # Exibir o valor formatado como moeda
            showarrow=False,
            font=dict(size=10),
            xshift=0,
            yshift=20,
        )

    # Atualize o layout do gráfico
    fig_data.update_layout(
        font=dict(family="Alfa Slab One", size=12, color="#333"),
        height=400)

    col1.write(f"""<div id="Info" > <center>Total: <br>{Total}</br></center> </div>""", unsafe_allow_html=True)

    # col2.write(f"""<div id="Info" > <center>Valor Renegociado: <br> {Valor_formatado}</div></center>""", unsafe_allow_html=True, use_container_width=True)

    col8.write(f"""<div id="Info" > <center>Valor Recebido: <br> {Valor_Pago_formatado}</div></center>""", unsafe_allow_html=True, use_container_width=True)

    # col9.write(f"""<div id="Info" > <center>Valor A Receber: <br> {Valor_a_receber_formatado}</div></center>""", unsafe_allow_html=True, use_container_width=True)

    # col10.write(f"""<div id="Info" > <center>Valor Quebras: <br> {Valor_quebras_formatado}</div></center>""", unsafe_allow_html=True, use_container_width=True)

    # col11.write(f"""<div id="Info" > <center>Total de Quebras: <br> {total_quebras}</div></center>""", unsafe_allow_html=True, use_container_width=True)

    col4.plotly_chart(fig_Pag, use_container_width=True)
    # col3.plotly_chart(fig_vencimento, use_container_width=True)
    col5.plotly_chart(fig_pagamento_pizza, use_container_width=True)
    col6[0].plotly_chart(fig_data, use_container_width=True,  style={'min-height': '500px'})

    # Agrupando os FATs e somando o VALOR_TOTAL
    tabela_fat_valores = df_filtered.groupby("FAT", as_index=False)["VALOR_TOTAL"].sum()

    # Ordenando do maior para o menor valor
    tabela_fat_valores = tabela_fat_valores.sort_values(by="VALOR_TOTAL", ascending=False)

    with st.expander("🔍 Ver detalhes das negociações"):
        # Seleciona e ordena as colunas desejadas
        tabela_detalhada = df_filtered[[
            "CONTRATO", 
            "CLIENTE",
            "OPERADOR", 
            "FAT", 
            "VALOR_TOTAL", 
            "DATA_EMISSAO", 
            "date_last_paid", 
            "STATUS_PAGAMENTO",
            "FAIXA_DE_ATRASO"
        ]].copy()

        # Ordena por VALOR_TOTAL do maior para o menor
        tabela_detalhada = tabela_detalhada.sort_values(by="VALOR_TOTAL", ascending=False)

        st.markdown("### 📊 Detalhamento de Negociações")
        st.dataframe(tabela_detalhada, use_container_width=True)

        # # Botão de download
        # def download_detalhamento(df_detalhe):
        #     with BytesIO() as b:
        #         df_detalhe.to_excel(b, index=False, engine='openpyxl', header=True)
        #         b.seek(0)
        #         href = f"<a href='data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{base64.b64encode(b.read()).decode()}' download='Detalhamento_Negociacoes.xlsx' style='color: white; background-color: #007ACC; padding: 10px; border-radius: 5px; text-decoration: none;'>📥 Baixar Tabela</a>"
        #     return href

    # st.markdown(download_detalhamento(tabela_detalhada), unsafe_allow_html=True)

    st.markdown(download_excel(df_filtered), unsafe_allow_html=True)

with tab3:

    df_fa = df_fa 
    df_fa["date_last_paid"] = pd.to_datetime(df_fa["date_last_paid"])
    df_fa = df_fa.sort_values("date_last_paid")
    df_fa["Month"] = df_fa["date_last_paid"].apply(lambda x: str(x.year) + "-" + str(x.month))
    df_fa = df_fa.dropna(subset=["Month"])  
    fil1, fil2 = st.columns(2)

    selected_periodo = fil1.selectbox("Período:", ["Mês", "Dia"])

    default_month = "2025-10"
    max_allowed_month = "2025-10"

    if selected_periodo == "Mês":
        month_options = df_fa["Month"].unique()
        month_options = [month for month in month_options if month != 'nan-nan']  
        month = fil2.selectbox("Mês", month_options, index=month_options.index(default_month))

        month = min(month, max_allowed_month)

        df_filtered = df_fa[df_fa["Month"] == month]
        df_filtered_mes = df_fa[df_fa["Month"] == month]

    else:
        date_range = fil2.date_input("Selecione um intervalo de tempo", [df_fa["date_last_paid"].min(), df_fa["date_last_paid"].max()])
        if len(date_range) == 1:
            start_date = end_date = pd.Timestamp(date_range[0])
        else:
            start_date = pd.Timestamp(date_range[0])
            end_date = pd.Timestamp(date_range[1])
        df_filtered = df_fa[(df_fa["date_last_paid"] >= start_date) & (df_fa["date_last_paid"] <= end_date)]
        df_filtered_mes = df_fa[(df_fa["date_last_paid"] >= start_date) & (df_fa["date_last_paid"] <= end_date)]

    st.write("### Contagem Faixa de Atraso")
    category_counts = df_filtered["category"].value_counts().reset_index()
    category_counts.columns = ["Category", "Count"]
    st.table(category_counts)

    st.write(f"### Faixa de Atraso por Operador")
    selected_operator = st.selectbox("Selecione o Operador:", df_filtered["OPERADOR"].unique())
    operator_category_count = df_filtered[df_filtered["OPERADOR"] == selected_operator].groupby(["OPERADOR", "category"]).size().reset_index(name="Count")
    st.table(operator_category_count)

    def download_excel(df_filtered):
        with BytesIO() as b:
            df_filtered.to_excel(b, index=False, engine='openpyxl', header=True)
            b.seek(0)
            href = f"<a href='data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{base64.b64encode(b.read()).decode()}' download='Faixa_De_Atraso.xlsx' style='color: white; background-color: #E05007; padding: 10px; border-radius: 5px; text-decoration: none;'>Download Excel</a>"
        return href

    st.markdown(download_excel(df_filtered), unsafe_allow_html=True)