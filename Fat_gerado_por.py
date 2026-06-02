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
# from qt_material import apply_stylesheet # (Descomente se estiver usando)

# Define o tema
st.set_page_config(
    page_title="Cobranca",
    page_icon=f"C:\\Users\\matheus.fagundes\\Documents\\Dash_Cobranca\\Imagens\\Logo_aba_navega.png",
    layout="wide",
)

# Faz referencia ao arquivo .css
try:
    with open('styles.css') as f:
        st.markdown(f"<style id=leit>{f.read()}</style>", unsafe_allow_html=True)
except FileNotFoundError:
    pass # Ignora caso o arquivo CSS não esteja na pasta durante testes

# Criando Sidebar de filtros
st.sidebar.image(f"C:\\Users\\matheus.fagundes\\Documents\\Dash_Cobranca\\Imagens\\Group 211.svg", use_container_width=True)

# Lendo o DataFrame a partir do arquivo CSV
df = pd.read_csv("C:\\Users\\matheus.fagundes\\Documents\\Dash_Cobranca\\Bases\\Fat_gerado_por.csv", sep=";", on_bad_lines="skip", dtype={"CONTRATO": str})
df_fa = pd.read_csv(f"C:\\Users\\matheus.fagundes\\Documents\\Dash_Cobranca\\Bases\\FaixaDeAtraso.csv", sep=",")

# Criando seleção de abas
tab1, tab2, tab3 = st.tabs(["Cobranca", "Recebidos", "Faixa de Atraso"])

colors = px.colors.sequential.Blues[::-1]  

# ==========================================
# ABA 1: COBRANCA
# ==========================================
with tab1:
    df_t1 = df.iloc[:-1].copy()
    df_t1["FILTRO_1"] = pd.to_datetime(df_t1["FILTRO_1"])
    df_t1 = df_t1.sort_values("FILTRO_1")
    df_t1["DATA_NEGOCIACAO"] = pd.to_datetime(df_t1["DATA_EMISSAO"])
    df_t1 = df_t1.sort_values("DATA_NEGOCIACAO")
    df_t1["Month"] = df_t1["DATA_NEGOCIACAO"].dt.strftime('%Y-%m')
    df_t1["Quarter"] = df_t1["DATA_NEGOCIACAO"].dt.to_period("Q")
    
    # Criando um contêiner no topo da página para os filtros
    fil1, fil2, fil3, fil4 = st.columns(4)

    # Filtro de datas
    selected_periodo = fil1.selectbox("Período:", ["Mês", "Dia", "Trimestre", "Data Negociação"])
    
    default_month = "2025-10"
    max_allowed_month = "2025-10"
    unique_months = sorted(df_t1["Month"].dropna().unique())

    if selected_periodo == "Mês":
        month = fil2.selectbox("Mês", unique_months, index=unique_months.index(default_month) if default_month in unique_months else 0)
        month = min(month, max_allowed_month)

        df_filtered = df_t1[df_t1["Month"] == month]
        df_filtered_mes = df_t1[df_t1["Month"] == month]

    elif selected_periodo == "Trimestre":
        quarters_with_data = df_t1["Quarter"].unique()
        quarter = fil2.selectbox("Trimestre", quarters_with_data)

        df_filtered = df_t1[df_t1["Quarter"] == quarter]
        df_filtered_mes = df_t1[df_t1["Quarter"] == quarter]

    elif selected_periodo == "Data Negociação":
        date_range = fil2.date_input("Selecione um intervalo de tempo", [df_t1["DATA_NEGOCIACAO"].min(), df_t1["DATA_NEGOCIACAO"].max()])
        if len(date_range) == 1:
            start_date = end_date = pd.Timestamp(date_range[0])
        else:
            start_date = pd.Timestamp(date_range[0])
            end_date = pd.Timestamp(date_range[1])
            
        df_filtered = df_t1[(df_t1["DATA_NEGOCIACAO"] >= start_date) & (df_t1["DATA_NEGOCIACAO"] <= end_date)]
        df_filtered_mes = df_t1[(df_t1["DATA_NEGOCIACAO"] >= start_date) & (df_t1["DATA_NEGOCIACAO"] <= end_date)]

    else:
        date_range = fil2.date_input("Selecione um intervalo de tempo", [df_t1["FILTRO_1"].min(), df_t1["FILTRO_1"].max()])
        if len(date_range) == 1:
            start_date = end_date = pd.Timestamp(date_range[0])
        else:
            start_date = pd.Timestamp(date_range[0])
            end_date = pd.Timestamp(date_range[1])
            
        df_filtered = df_t1[(df_t1["FILTRO_1"] >= start_date) & (df_t1["FILTRO_1"] <= end_date)]
        df_filtered_mes = df_t1[(df_t1["FILTRO_1"] >= start_date) & (df_t1["FILTRO_1"] <= end_date)]

    # Filtro de visão
    filtro_escolha = fil3.selectbox("Visão Por:", ["Geral", "Operador"])

    col1, col2, col8, col9, col10, col11 = st.columns(6)
    col3, col4, col5 = st.columns(3)
    col6 = st.columns(1)
    fat1 = st.columns(1)

    if filtro_escolha == "Geral":
        filtro_selecionado = fil4.selectbox("Operador", ["Todos"]) # Placeholder para manter o layout

    elif selected_periodo == "Mês" and filtro_escolha == 'Operador':
        operadores_mes_selecionado = df_filtered[df_filtered["Month"] == month]["OPERADOR"].unique()
        filtro_selecionado = fil4.multiselect("Operadores", operadores_mes_selecionado)
        df_filtered = df_filtered[df_filtered["OPERADOR"].isin(filtro_selecionado)]	
        
    else:
        filtro_selecionado = [fil4.selectbox("Operador", df_t1["OPERADOR"].unique())]
        df_filtered = df_filtered[df_filtered["OPERADOR"].isin(filtro_selecionado)]
        fat1[0].dataframe(df_filtered, use_container_width=True)	

    # Melhor Recuperador
    df_filtered_pago = df_filtered_mes[df_filtered_mes['STATUS_PAGAMENTO'] == 'PAGO']
    df_grouped2 = df_filtered_pago.groupby('OPERADOR')['VALOR_TOTAL'].sum().reset_index()
    max_row = df_grouped2[df_grouped2['VALOR_TOTAL'] == df_grouped2['VALOR_TOTAL'].max()]

    if not max_row.empty:
        max_operator = max_row['OPERADOR'].values[0]
        max_value = max_row['VALOR_TOTAL'].values[0]
        max_value_formatado = "R$ {:,.2f}".format(max_value)

        st.sidebar.markdown(f"**MELHOR RECUPERADOR DE CRÉDITO**")  
        st.sidebar.image(f"C:\\Users\\matheus.fagundes\\Documents\\Dash_Cobranca\\Imagens\\trofeu.png", use_container_width=True)
        st.sidebar.markdown(f"**Operador:** {max_operator}\n\n**Valor:** {max_value_formatado}")
    else:
        st.sidebar.markdown("Nenhum valor a ser mostrado.")
    
    def download_excel(df_to_download, filename='Download.xlsx'):
        with BytesIO() as b:
            df_to_download.to_excel(b, index=False, engine='openpyxl', header=True)
            b.seek(0)
            href = f"<a href='data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{base64.b64encode(b.read()).decode()}' download='{filename}' style='color: white; background-color: #E05007; padding: 10px; border-radius: 5px; text-decoration: none;'>Download Excel</a>"
        return href

    Total = len(df_filtered)
    Valor = round(sum(df_filtered["VALOR_TOTAL"]), 2)

    df_filtered_pago = df_filtered[df_filtered["STATUS_RECEBIMENTO"].isin(["PAGO"])]
    Valor_Pago = round(sum(df_filtered_pago["Val_last_paid"]), 2)

    df_filtered_atraso = df_filtered[df_filtered["FAIXA_DE_ATRASO"].isin(["1 A 34 DIAS", "35 A 45 DIAS", "46 A 60 DIAS", "61 A 75 DIAS", "76 A 90 DIAS", "91 A 180 DIAS", "181 A 360 DIAS", "(+) 361 DIAS"])]
    count_atraso = df_filtered_atraso["FAIXA_DE_ATRASO"].value_counts()

    df_filtered_a_receber = df_filtered[df_filtered["STATUS_RECEBIMENTO"].isin(["A VENCER"])]
    Valor_a_receber = round(sum(df_filtered_a_receber["VALOR_TOTAL"]), 2)

    # CORREÇÃO PANDAS: Usando assign em vez de loc
    df_filtered = df_filtered.assign(FILTRO_2=pd.to_datetime(df_filtered['FILTRO_2']))
    df_filtered_a_quebras = df_filtered[df_filtered['FILTRO_2'] <= pd.Timestamp('now') - pd.DateOffset(1)]
   
    df_quebras = df_filtered_a_quebras[df_filtered_a_quebras['STATUS_RECEBIMENTO'] == 'VENCIDO']
    total_quebras = df_quebras['FAT'].nunique()
    Valor_quebras = round(sum(df_quebras["VALOR_TOTAL"]), 2)

    try:
        locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
    except locale.Error:
        try:
            locale.setlocale(locale.LC_ALL, 'Portuguese_Brazil.1252')
        except locale.Error:
            pass # Fallback caso o locale não seja encontrado no SO

    Valor_formatado = locale.currency(Valor, grouping=True) if Valor else "R$ 0,00"
    Valor_Pago_formatado = locale.currency(Valor_Pago, grouping=True) if Valor_Pago else "R$ 0,00"
    Valor_a_receber_formatado = locale.currency(Valor_a_receber, grouping=True) if Valor_a_receber else "R$ 0,00"
    Valor_quebras_formatado = locale.currency(Valor_quebras, grouping=True) if Valor_quebras else "R$ 0,00"
    
    count_pagamento = df_filtered["PAGAMENTO"].value_counts()
    count_status = df_filtered["STATUS_PAGAMENTO"].value_counts()
    count_dia = df_filtered["date_last_paid"].value_counts()

    df_filtered_vencimento = df_filtered[df_filtered["STATUS_RECEBIMENTO"].isin(["VENCIDO", "A VENCER"])]
    count_vencimento = df_filtered_vencimento["STATUS_RECEBIMENTO"].value_counts()

    labels_pagamento = count_pagamento.index
    labels_status = count_status.index    
    values_pagamento = count_pagamento.values
    values_status = count_status.values

    # Tratamento para evitar erro se 'pull' for maior que a quantidade de dados
    pull_pagamento = [0.01, 0.03, 0.2, 0.02, 0.02][:len(labels_pagamento)]
    fig_pagamento_pizza = go.Figure(data=[go.Pie(labels=labels_pagamento, values=values_pagamento, pull=pull_pagamento, hole=0.7)])
    fig_pagamento_pizza.update_layout(title="Forma de Pagamento")
    fig_pagamento_pizza.update_traces(marker=dict(colors=colors))

    if len(count_vencimento) == 0:
        fig_vencimento = px.bar(title="Vencimento")
    else:
        fig_vencimento = px.bar(count_vencimento, x=count_vencimento.index, y=count_vencimento.values, color=count_vencimento.index, title="Vencimento", orientation="v", color_discrete_sequence=colors)
    
    for i, value in enumerate(count_vencimento.values):
        fig_vencimento.add_annotation(x=count_vencimento.index[i], y=value, text=str(value), showarrow=False, arrowhead=4, xshift=0, yshift=15)
        
    fig_Pag = go.Figure(data=[go.Pie(labels=labels_status, values=values_status, pull=[0, 0.03][:len(labels_status)], hole=0.7)])
    fig_Pag.update_layout(title="Total por status")
    fig_Pag.update_traces(marker=dict(colors=colors))

    df_grouped = df_filtered.groupby('date_last_paid')['VALOR_TOTAL'].sum().reset_index()
    df_grouped['date_last_paid'] = pd.to_datetime(df_grouped['date_last_paid'])
    df_grouped['Data_Recebimento'] = df_grouped['date_last_paid'].dt.strftime('%d %b').str.upper()

    if len(df_grouped) == 0:
        fig_data = px.bar(title="Negociação por Dia")
    else:
        fig_data = px.line(df_grouped, x='Data_Recebimento', y='VALOR_TOTAL', title="Negociação por Dia", line_shape='linear', render_mode='svg')
        fig_data.update_xaxes(tickangle=25)
        fig_data.add_trace(go.Scatter(x=df_grouped['Data_Recebimento'], y=df_grouped['VALOR_TOTAL'], name='Valor', mode='markers', marker=dict(size=10, line=dict(color='blue', width=2), color='white')))

        for i, value in enumerate(df_grouped['VALOR_TOTAL']):
            value_formatado_graf = format_currency(value, 'BRL', locale='pt_BR.UTF-8').split(',')[0]
            fig_data.add_annotation(x=df_grouped['Data_Recebimento'].iloc[i], y=value, text=f"{value_formatado_graf}", showarrow=False, font=dict(size=10), xshift=0, yshift=20)

    fig_data.update_layout(font=dict(family="Alfa Slab One", size=12, color="#333"), height=400)

    # CORREÇÃO STREAMLIT: Usando markdown para HTML e removendo use_container_width
    col1.markdown(f"""<div id="Info"><center>Total:<br>{Total}</center></div>""", unsafe_allow_html=True)
    col2.markdown(f"""<div id="Info"><center>Valor Renegociado:<br>{Valor_formatado}</center></div>""", unsafe_allow_html=True)
    col8.markdown(f"""<div id="Info"><center>Valor Recebido:<br>{Valor_Pago_formatado}</center></div>""", unsafe_allow_html=True)
    col9.markdown(f"""<div id="Info"><center>Valor A Receber:<br>{Valor_a_receber_formatado}</center></div>""", unsafe_allow_html=True)
    col10.markdown(f"""<div id="Info"><center>Valor Quebras:<br>{Valor_quebras_formatado}</center></div>""", unsafe_allow_html=True)
    col11.markdown(f"""<div id="Info"><center>Total de Quebras:<br>{total_quebras}</center></div>""", unsafe_allow_html=True)

    col4.plotly_chart(fig_Pag, use_container_width=True)
    col3.plotly_chart(fig_vencimento, use_container_width=True)
    col5.plotly_chart(fig_pagamento_pizza, use_container_width=True)
    col6[0].plotly_chart(fig_data, use_container_width=True)

    with st.expander("🔍 Ver detalhes das negociações"):
        tabela_detalhada = df_filtered[["CONTRATO", "OPERADOR", "FAT", "VALOR_TOTAL", "DATA_EMISSAO", "date_last_paid", "STATUS_PAGAMENTO"]].copy()
        tabela_detalhada = tabela_detalhada.sort_values(by="VALOR_TOTAL", ascending=False)
        st.markdown("### 📊 Detalhamento de Negociações")
        st.dataframe(tabela_detalhada, use_container_width=True)

    st.markdown(download_excel(df_filtered, 'Fat_gerado_por.xlsx'), unsafe_allow_html=True)


# ==========================================
# ABA 2: RECEBIDOS
# ==========================================
with tab2:
    df_t2 = df.iloc[:-1].copy()
    df_t2["date_last_paid"] = pd.to_datetime(df_t2["date_last_paid"])
    df_t2 = df_t2.sort_values("date_last_paid")
    df_t2["Month"] = df_t2["date_last_paid"].dt.strftime('%Y-%m')
    df_t2["Quarter"] = df_t2["date_last_paid"].dt.to_period("Q")
    
    fil1, fil2, fil3, fil4 = st.columns(4)

    selected_periodo = fil1.selectbox("Período:", ["Mês", "Dia", "Trimestre", "Data Recebimento"], key="Coutinho")
    
    default_month = "2025-10"
    max_allowed_month = "2025-10"
    unique_months = sorted(df_t2["Month"].dropna().unique())

    if selected_periodo == "Mês":
        month = fil2.selectbox("Mês", unique_months, index=unique_months.index(default_month) if default_month in unique_months else 0, key="mes_tab2")
        month = min(month, max_allowed_month)

        df_filtered = df_t2[df_t2["Month"] == month]
        df_filtered_mes = df_t2[df_t2["Month"] == month]

    elif selected_periodo == "Trimestre":
        quarters_with_data = df_t2["Quarter"].unique()
        quarter = fil2.selectbox("Trimestre", quarters_with_data, key="trimestre_tab2")

        df_filtered = df_t2[df_t2["Quarter"] == quarter]
        df_filtered_mes = df_t2[df_t2["Quarter"] == quarter]

    elif selected_periodo == "Data Recebimento":
        date_range = fil2.date_input("Selecione um intervalo de tempo", [df_t2["date_last_paid"].min(), df_t2["date_last_paid"].max()], key="filtro_data_recebimento")
        if len(date_range) == 1:
            start_date = end_date = pd.Timestamp(date_range[0])
        else:
            start_date = pd.Timestamp(date_range[0])
            end_date = pd.Timestamp(date_range[1])
            
        df_filtered = df_t2[(df_t2["date_last_paid"] >= start_date) & (df_t2["date_last_paid"] <= end_date)]
        df_filtered_mes = df_t2[(df_t2["date_last_paid"] >= start_date) & (df_t2["date_last_paid"] <= end_date)]

    else:
        # A referência aqui estava no FILTRO_1. Mantida como no original.
        date_range = fil2.date_input("Selecione um intervalo de tempo", [df_t2["FILTRO_1"].min(), df_t2["FILTRO_1"].max()], key="filtro_data_vencimento_tab2")
        if len(date_range) == 1:
            start_date = end_date = pd.Timestamp(date_range[0])
        else:
            start_date = pd.Timestamp(date_range[0])
            end_date = pd.Timestamp(date_range[1])
            
        df_filtered = df_t2[(df_t2["FILTRO_1"] >= start_date) & (df_t2["FILTRO_1"] <= end_date)]
        df_filtered_mes = df_t2[(df_t2["FILTRO_1"] >= start_date) & (df_t2["FILTRO_1"] <= end_date)]

    filtro_escolha = fil3.selectbox("Visão Por:", ["Geral", "Operador"], key="Vegetti")

    col1, col8 = st.columns(2)
    col4, col5 = st.columns(2)
    col6 = st.columns(1)
    fat1 = st.columns(1)

    if filtro_escolha == "Geral":
        filtro_selecionado = fil4.selectbox("Operador", ["Todos"], key="Nuno Moreira")

    elif selected_periodo == "Mês" and filtro_escolha == 'Operador':
        operadores_mes_selecionado = df_filtered[df_filtered["Month"] == month]["OPERADOR"].unique()
        filtro_selecionado = fil4.multiselect("Operadores", operadores_mes_selecionado, key="multi_op_tab2")
        df_filtered = df_filtered[df_filtered["OPERADOR"].isin(filtro_selecionado)]	
        
    else:
        filtro_selecionado = [fil4.selectbox("Operador", df_t2["OPERADOR"].unique(), key="op_tab2")]
        df_filtered = df_filtered[df_filtered["OPERADOR"].isin(filtro_selecionado)]
        fat1[0].dataframe(df_filtered, use_container_width=True)	

    # CORREÇÃO PANDAS: Usando assign
    df_filtered = df_filtered.assign(FILTRO_2=pd.to_datetime(df_filtered['FILTRO_2']))

    Total = len(df_filtered)
    Valor = round(sum(df_filtered["VALOR_TOTAL"]), 2)

    df_filtered_pago = df_filtered[df_filtered["STATUS_RECEBIMENTO"].isin(["PAGO"])]
    Valor_Pago = round(sum(df_filtered_pago["Val_last_paid"]), 2)

    df_filtered_a_receber = df_filtered[df_filtered["STATUS_RECEBIMENTO"].isin(["A VENCER"])]
    Valor_a_receber = round(sum(df_filtered_a_receber["VALOR_TOTAL"]), 2)

    df_filtered_a_quebras = df_filtered[df_filtered['FILTRO_2'] <= pd.Timestamp('now') - pd.DateOffset(1)]
    df_quebras = df_filtered_a_quebras[df_filtered_a_quebras['STATUS_RECEBIMENTO'] == 'VENCIDO']
    total_quebras = df_quebras['FAT'].nunique()
    Valor_quebras = round(sum(df_quebras["VALOR_TOTAL"]), 2)

    Valor_formatado = locale.currency(Valor, grouping=True) if Valor else "R$ 0,00"
    Valor_Pago_formatado = locale.currency(Valor_Pago, grouping=True) if Valor_Pago else "R$ 0,00"
    
    count_pagamento = df_filtered["PAGAMENTO"].value_counts()
    count_status = df_filtered["STATUS_PAGAMENTO"].value_counts()

    labels_pagamento = count_pagamento.index
    labels_status = count_status.index    
    values_pagamento = count_pagamento.values
    values_status = count_status.values

    pull_pagamento = [0.01, 0.03, 0.2, 0.02, 0.02][:len(labels_pagamento)]
    fig_pagamento_pizza = go.Figure(data=[go.Pie(labels=labels_pagamento, values=values_pagamento, pull=pull_pagamento, hole=0.7)])
    fig_pagamento_pizza.update_layout(title="Forma de Pagamento")
    fig_pagamento_pizza.update_traces(marker=dict(colors=colors))

    fig_Pag = go.Figure(data=[go.Pie(labels=labels_status, values=values_status, pull=[0, 0.03][:len(labels_status)], hole=0.7)])
    fig_Pag.update_layout(title="Total por status")
    fig_Pag.update_traces(marker=dict(colors=colors))

    df_grouped = df_filtered.groupby('date_last_paid')['VALOR_TOTAL'].sum().reset_index()
    df_grouped['date_last_paid'] = pd.to_datetime(df_grouped['date_last_paid'])
    df_grouped['Data_Recebimento'] = df_grouped['date_last_paid'].dt.strftime('%d %b').str.upper()

    if len(df_grouped) == 0:
         fig_data = px.bar(title="Negociação por Dia")
    else:
        fig_data = px.line(df_grouped, x='Data_Recebimento', y='VALOR_TOTAL', title="Negociação por Dia", line_shape='linear', render_mode='svg')
        fig_data.update_xaxes(tickangle=25)
        fig_data.add_trace(go.Scatter(x=df_grouped['Data_Recebimento'], y=df_grouped['VALOR_TOTAL'], name='Valor', mode='markers', marker=dict(size=10, line=dict(color='blue', width=2), color='white')))

        for i, value in enumerate(df_grouped['VALOR_TOTAL']):
            value_formatado_graf = format_currency(value, 'BRL', locale='pt_BR.UTF-8').split(',')[0]
            fig_data.add_annotation(x=df_grouped['Data_Recebimento'].iloc[i], y=value, text=f"{value_formatado_graf}", showarrow=False, font=dict(size=10), xshift=0, yshift=20)

    fig_data.update_layout(font=dict(family="Alfa Slab One", size=12, color="#333"), height=400)

    # CORREÇÃO STREAMLIT: Usando markdown e removendo use_container_width
    col1.markdown(f"""<div id="Info"><center>Total:<br>{Total}</center></div>""", unsafe_allow_html=True)
    col8.markdown(f"""<div id="Info"><center>Valor Recebido:<br>{Valor_Pago_formatado}</center></div>""", unsafe_allow_html=True)

    col4.plotly_chart(fig_Pag, use_container_width=True)
    col5.plotly_chart(fig_pagamento_pizza, use_container_width=True)
    
    # CORREÇÃO STREAMLIT: Removido o argumento style que não existe na função plotly_chart
    col6[0].plotly_chart(fig_data, use_container_width=True)

    with st.expander("🔍 Ver detalhes das negociações"):
        tabela_detalhada = df_filtered[["CONTRATO", "CLIENTE", "ESTÁGIO", "SITUAÇÃO", "OPERADOR", "FAT", "VALOR_TOTAL", "DATA_EMISSAO", "date_last_paid", "STATUS_PAGAMENTO", "FAIXA_DE_ATRASO"]].copy()
        tabela_detalhada = tabela_detalhada.sort_values(by="VALOR_TOTAL", ascending=False)
        st.markdown("### 📊 Detalhamento de Negociações")
        st.dataframe(tabela_detalhada, use_container_width=True)

    st.markdown(download_excel(df_filtered, 'Recebidos.xlsx'), unsafe_allow_html=True)

# ==========================================
# ABA 3: FAIXA DE ATRASO
# ==========================================
with tab3:
    df_fa_t3 = df_fa.copy()
    df_fa_t3["date_last_paid"] = pd.to_datetime(df_fa_t3["date_last_paid"])
    df_fa_t3 = df_fa_t3.sort_values("date_last_paid")
    df_fa_t3["Month"] = df_fa_t3["date_last_paid"].dt.strftime('%Y-%m')
    df_fa_t3 = df_fa_t3.dropna(subset=["Month"])  
    
    fil1, fil2 = st.columns(2)

    selected_periodo = fil1.selectbox("Período:", ["Mês", "Dia"], key="periodo_tab3")

    default_month = "2025-10"
    max_allowed_month = "2025-10"

    if selected_periodo == "Mês":
        month_options = df_fa_t3["Month"].unique()
        month_options = [m for m in month_options if m != 'nan-nan']  
        month = fil2.selectbox("Mês", month_options, index=month_options.index(default_month) if default_month in month_options else 0, key="mes_tab3")
        month = min(month, max_allowed_month)

        df_filtered = df_fa_t3[df_fa_t3["Month"] == month]

    else:
        date_range = fil2.date_input("Selecione um intervalo de tempo", [df_fa_t3["date_last_paid"].min(), df_fa_t3["date_last_paid"].max()], key="filtro_tab3_faixa_atraso")
        if len(date_range) == 1:
            start_date = end_date = pd.Timestamp(date_range[0])
        else:
            start_date = pd.Timestamp(date_range[0])
            end_date = pd.Timestamp(date_range[1])
            
        df_filtered = df_fa_t3[(df_fa_t3["date_last_paid"] >= start_date) & (df_fa_t3["date_last_paid"] <= end_date)]

    st.write("### Contagem Faixa de Atraso")
    if 'category' in df_filtered.columns:
        category_counts = df_filtered["category"].value_counts().reset_index()
        category_counts.columns = ["Category", "Count"]
        st.table(category_counts)

        st.write("### Faixa de Atraso por Operador")
        selected_operator = st.selectbox("Selecione o Operador:", df_filtered["OPERADOR"].unique(), key="op_tab3")
        operator_category_count = df_filtered[df_filtered["OPERADOR"] == selected_operator].groupby(["OPERADOR", "category"]).size().reset_index(name="Count")
        st.table(operator_category_count)
    else:
        st.info("A coluna 'category' não foi encontrada na base FaixaDeAtraso.csv")

    st.markdown(download_excel(df_filtered, 'Faixa_De_Atraso.xlsx'), unsafe_allow_html=True)