import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="Dashboard KPIs - Notas Fiscais", page_icon="📊", layout="wide")

@st.cache_data(ttl=3600)
def load_data():
    try:
        df = pd.read_excel("Resultado66.xlsx")
        return df
    except:
        st.error("❌ Arquivo Resultado66.xlsx não encontrado!")
        return None

st.title("📊 Dashboard - KPIs de Notas Fiscais")
st.markdown(f"🕐 Atualizado em: {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}")

df = load_data()

if df is not None:
    status_labels = {'U': 'Utilizada', 'N': 'NÃO_Utilizada', 'E': 'Estornada', 'C': 'Cancelada', 'B': 'Bloqueada'}
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
        fig1 = px.pie(names=status_data.index, values=status_data.values, title="Status da NF")
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        prazo_data = df['STATUS_PRAZO'].value_counts()
        fig2 = px.bar(x=prazo_data.index, y=prazo_data.values, title="Status Prazo")
        st.plotly_chart(fig2, use_container_width=True)
    
    col3, col4 = st.columns(2)
    
    with col3:
        valor_status = df.groupby('STATUS_LABEL')['VALOR_NF'].sum().sort_values(ascending=False)
        fig3 = px.bar(x=valor_status.index, y=valor_status.values, title="Valor por Status")
        st.plotly_chart(fig3, use_container_width=True)
    
    with col4:
        pag_data = df['SEM_PAGAMENTO'].value_counts()
        labels = ['Com Pagamento' if x == 'NAO' else 'Sem Pagamento' for x in pag_data.index]
        fig4 = px.pie(names=labels, values=pag_data.values, title="Pagamento")
        st.plotly_chart(fig4, use_container_width=True)
    
    st.markdown("---")
    st.markdown("### 📋 Dados Detalhados")
    
    tab1, tab2, tab3, tab4 = st.tabs(["RESUMO", "UTILIZADA", "NÃO UTILIZADA", "ESTORNADA"])
    
    with tab1:
        resumo = []
        for status, label in status_labels.items():
            dados = df[df['STATUS'] == status]
            resumo.append({'Status': label, 'Quantidade': len(dados), 'Valor Total': f"R$ {dados['VALOR_NF'].sum():,.2f}", 'Valor Médio': f"R$ {dados['VALOR_NF'].mean():,.2f}", '%': f"{len(dados)/total_nf*100:.1f}%"})
        st.dataframe(pd.DataFrame(resumo), use_container_width=True)
    
    with tab2:
        df_u = df[df['STATUS'] == 'U'][['NOTA_FISCAL', 'NMRAZSOCFORN', 'DATA_EMISSAO', 'VALOR_NF', 'ESTADO']]
        st.dataframe(df_u, use_container_width=True)
        st.info(f"✓ {len(df_u)} NFs | R$ {df_u['VALOR_NF'].sum():,.2f}")
    
    with tab3:
        df_n = df[df['STATUS'] == 'N'][['NOTA_FISCAL', 'NMRAZSOCFORN', 'DATA_EMISSAO', 'VALOR_NF', 'ESTADO']]
        st.dataframe(df_n, use_container_width=True)
        st.warning(f"⚠️ {len(df_n)} NFs")
    
    with tab4:
        df_e = df[df['STATUS'] == 'E'][['NOTA_FISCAL', 'NMRAZSOCFORN', 'DATA_EMISSAO', 'VALOR_NF', 'ESTADO', 'FILIAL']]
        st.dataframe(df_e, use_container_width=True)
        st.error(f"❌ {len(df_e)} NFs COM ERRO!")
    
    st.markdown("---")
    st.markdown("Dashboard Streamlit | Atualiza automaticamente ✅")
else:
    st.error("Não foi possível carregar os dados!")
