import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="Dashboard KPIs - Notas Fiscais", page_icon="📊", layout="wide")

@st.cache_data(ttl=3600)
def load_data():
    try:
        df = pd.read_excel("Resultado66.xlsx")
        df['DATA_EMISSAO'] = pd.to_datetime(df['DATA_EMISSAO'], format='%d/%m/%Y')
        df['MES'] = df['DATA_EMISSAO'].dt.strftime('%m/%Y')
        df['MES_NUM'] = df['DATA_EMISSAO'].dt.to_period('M')
        return df
    except Exception as e:
        st.error(f"Erro ao carregar arquivo: {e}")
        return None

st.title("📊 Dashboard - KPIs de Notas Fiscais")
st.markdown(f"🕐 Atualizado em: {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}")

df = load_data()

if df is not None:
    status_labels = {
        'U': 'Utilizada',
        'N': 'Não Utilizada',
        'E': 'Estornada',
        'C': 'Cancelada',
        'B': 'Bloqueada'
    }
    
    df['STATUS_LABEL'] = df['STATUS'].map(status_labels)
    
    st.markdown("### 📈 Indicadores Principais")
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    total_nf = len(df)
    total_valor = df['VALOR_NF'].sum()
    valor_media = df['VALOR_NF'].mean()
    prazo_ok = len(df[df['STATUS_PRAZO'] == 'OK'])
    prazo_divergente = len(df[df['STATUS_PRAZO'] == 'DIVERGENTE'])
    sem_pagamento = len(df[df['SEM_PAGAMENTO'] == 'SIM'])
    
    with col1:
        st.metric("Total NFs", f"{total_nf:,}")
    with col2:
        st.metric("Valor Total", f"R$ {total_valor/1e6:.2f}M")
    with col3:
        st.metric("Valor Médio", f"R$ {valor_media:,.0f}")
    with col4:
        st.metric("Prazos OK", f"{prazo_ok:,}")
    with col5:
        st.metric("Divergentes", f"{prazo_divergente:,}")
    with col6:
        st.metric("Sem Pagamento", f"{sem_pagamento:,}")
    
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        status_data = df['STATUS_LABEL'].value_counts()
        fig1 = px.pie(names=status_data.index, 
