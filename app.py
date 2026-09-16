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
    
    st.markdown("### 📅 Análise por Mês")
    col1, col2 = st.columns(2)
    
    with col1:
        nf_por_mes = df.groupby('MES').size().reset_index(name='Quantidade')
        nf_por_mes = nf_por_mes.sort_values('MES')
        fig5 = px.bar(nf_por_mes, x='MES', y='Quantidade', title="NFs por Mês", color_discrete_sequence=['#667eea'])
        st.plotly_chart(fig5, use_container_width=True)
    
    with col2:
        valor_por_mes = df.groupby('MES')['VALOR_NF'].sum().reset_index()
        valor_por_mes = valor_por_mes.sort_values('MES')
        fig6 = px.bar(valor_por_mes, x='MES', y='VALOR_NF', title="Valor Total por Mês", color_discrete_sequence=['#764ba2'])
        st.plotly_chart(fig6, use_container_width=True)
    
    col5, col6 = st.columns(2)
    
    with col5:
        status_mes = df.groupby(['MES', 'STATUS_LABEL']).size().reset_index(name='Quantidade')
        status_mes = status_mes.sort_values('MES')
        fig7 = px.bar(status_mes, x='MES', y='Quantidade', color='STATUS_LABEL', title="Status por Mês")
        st.plotly_chart(fig7, use_container_width=True)
    
    with col6:
        prazo_mes = df.groupby(['MES', 'STATUS_PRAZO']).size().reset_index(name='Quantidade')
        prazo_mes = prazo_mes.sort_values('MES')
        fig8 = px.bar(prazo_mes, x='MES', y='Quantidade', color='STATUS_PRAZO', title="Prazo por Mês")
        st.plotly_chart(fig8, use_container_width=True)
    
    st.markdown("---")
    st.markdown("### 📋 Dados Detalhados")
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["RESUMO", "UTILIZADA", "NÃO UTILIZADA", "ESTORNADA", "POR MÊS"])
    
    with tab1:
        resumo = []
        for status, label in status_labels.items():
            dados = df[df['STATUS'] == status]
            resumo.append({
                'Status': label,
                'Quantidade': len(dados),
                'Valor Total': f"R$ {dados['VALOR_NF'].sum():,.2f}",
                'Valor Médio': f"R$ {dados['VALOR_NF'].mean():,.2f}",
                '%': f"{len(dados)/total_nf*100:.1f}%"
            })
        st.dataframe(pd.DataFrame(resumo), use_container_width=True)
    
    with tab2:
        df_u = df[df['STATUS'] == 'U'][['NOTA_FISCAL', 'NMRAZSOCFORN', 'DATA_EMISSAO', 'VALOR_NF', 'ESTADO', 'MES']]
        st.dataframe(df_u, use_container_width=True)
        st.info(f"✓ {len(df_u)} NFs | R$ {df_u['VALOR_NF'].sum():,.2f}")
    
    with tab3:
        df_n = df[df['STATUS'] == 'N'][['NOTA_FISCAL', 'NMRAZSOCFORN', 'DATA_EMISSAO', 'VALOR_NF', 'ESTADO', 'MES']]
        st.dataframe(df_n, use_container_width=True)
        st.warning(f"⚠️ {len(df_n)} NFs")
    
    with tab4:
        df_e = df[df['STATUS'] == 'E'][['NOTA_FISCAL', 'NMRAZSOCFORN', 'DATA_EMISSAO', 'VALOR_NF', 'ESTADO', 'FILIAL', 'MES']]
        st.dataframe(df_e, use_container_width=True)
        st.error(f"❌ {len(df_e)} NFs ESTORNADAS!")
    
    with tab5:
        st.subheader("Consolidação por Mês")
        mes_resumo = df.groupby('MES').agg({
            'NOTA_FISCAL': 'count',
            'VALOR_NF': ['sum', 'mean']
        }).reset_index()
        mes_resumo.columns = ['Mês', 'Quantidade NFs', 'Valor Total', 'Valor Médio']
        mes_resumo['Valor Total'] = mes_resumo['Valor Total'].apply(lambda x: f"R$ {x:,.2f}")
        mes_resumo['Valor Médio'] = mes_resumo['Valor Médio'].apply(lambda x: f"R$ {x:,.2f}")
        st.dataframe(mes_resumo, use_container_width=True)
    
    st.markdown("---")
    st.markdown("Dashboard Streamlit | Atualiza automaticamente ✅")
else:
    st.error("Não foi possível carregar os dados!")
    
    
