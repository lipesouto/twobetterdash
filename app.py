import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from pathlib import Path
import os

# Configuração da página
st.set_page_config(
    page_title="TwoBetter - Dashboard de Atividades",
    page_icon="📊",
    layout="wide"
)

# CSS customizado
st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .stMetric > div {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    h1 {
        color: #1e3a5f;
    }
</style>
""", unsafe_allow_html=True)

# Função para encontrar o CSV mais recente na pasta data
def get_latest_csv():
    data_dir = Path(__file__).parent / "data"
    
    if not data_dir.exists():
        return None
    
    csv_files = list(data_dir.glob("*.csv"))
    
    if not csv_files:
        return None
    
    # Retorna o mais recente por data de modificação
    latest_file = max(csv_files, key=lambda x: x.stat().st_mtime)
    return latest_file

# Função para carregar e processar dados
@st.cache_data
def load_data(file_path):
    df = pd.read_csv(file_path, encoding='utf-8-sig')
    
    # Renomear colunas para facilitar
    df.columns = ['Tipo', 'Chave', 'ID', 'Resumo', 'Responsavel', 'ID_Responsavel', 
                  'Relator', 'ID_Relator', 'Prioridade', 'Status', 'Resolucao', 
                  'Criado', 'Atualizado', 'Data_Limite']
    
    # Mapeamento de meses PT-BR para EN
    meses_pt_en = {
        'jan': 'Jan', 'fev': 'Feb', 'mar': 'Mar', 'abr': 'Apr',
        'mai': 'May', 'jun': 'Jun', 'jul': 'Jul', 'ago': 'Aug',
        'set': 'Sep', 'out': 'Oct', 'nov': 'Nov', 'dez': 'Dec'
    }
    
    def convert_date_pt(date_str):
        if pd.isna(date_str) or date_str == '':
            return pd.NaT
        try:
            date_str = str(date_str)
            for pt, en in meses_pt_en.items():
                date_str = date_str.replace(f'/{pt}/', f'/{en}/')
            return pd.to_datetime(date_str, format='%d/%b/%y %I:%M %p')
        except:
            return pd.NaT
    
    # Converter datas
    df['Criado'] = df['Criado'].apply(convert_date_pt)
    df['Atualizado'] = df['Atualizado'].apply(convert_date_pt)
    
    # Extrair área do resumo (Backend, Frontend, QA, etc)
    def extract_area(resumo):
        resumo_upper = str(resumo).upper()
        if '[BE]' in resumo_upper or '[BACKEND]' in resumo_upper or 'BACK END' in resumo_upper:
            return 'Backend'
        elif '[FE]' in resumo_upper or '[FRONTEND]' in resumo_upper or 'FRONT END' in resumo_upper:
            return 'Frontend'
        elif '[QA]' in resumo_upper:
            return 'QA'
        elif '[OPS]' in resumo_upper:
            return 'Ops'
        else:
            return 'Outros'
    
    df['Area'] = df['Resumo'].apply(extract_area)
    
    # Limpar responsáveis
    df['Responsavel'] = df['Responsavel'].fillna('Não atribuído')
    
    return df

# Título
st.title("📊 TwoBetter - Dashboard de Atividades")
st.markdown("---")

# Carregar CSV automaticamente da pasta data
csv_file = get_latest_csv()

if csv_file is not None:
    df = load_data(csv_file)
    
    # Mostrar qual arquivo está sendo usado
    st.sidebar.success(f"📁 Arquivo: {csv_file.name}")
    st.sidebar.caption(f"Última atualização: {datetime.fromtimestamp(csv_file.stat().st_mtime).strftime('%d/%m/%Y %H:%M')}")
    
    # Sidebar com filtros
    st.sidebar.markdown("---")
    st.sidebar.header("🔍 Filtros")
    
    # Filtro de período
    min_date = df['Criado'].min().date() if pd.notna(df['Criado'].min()) else datetime.now().date()
    max_date = df['Criado'].max().date() if pd.notna(df['Criado'].max()) else datetime.now().date()
    
    date_range = st.sidebar.date_input(
        "Período",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )
    
    # Filtro de responsável
    responsaveis = ['Todos'] + sorted(df['Responsavel'].unique().tolist())
    selected_responsavel = st.sidebar.selectbox("Responsável", responsaveis)
    
    # Filtro de status
    status_list = ['Todos'] + sorted(df['Status'].unique().tolist())
    selected_status = st.sidebar.selectbox("Status", status_list)
    
    # Filtro de tipo
    tipos = ['Todos'] + sorted(df['Tipo'].unique().tolist())
    selected_tipo = st.sidebar.selectbox("Tipo", tipos)
    
    # Aplicar filtros
    df_filtered = df.copy()
    
    if len(date_range) == 2:
        df_filtered = df_filtered[
            (df_filtered['Criado'].dt.date >= date_range[0]) & 
            (df_filtered['Criado'].dt.date <= date_range[1])
        ]
    
    if selected_responsavel != 'Todos':
        df_filtered = df_filtered[df_filtered['Responsavel'] == selected_responsavel]
    
    if selected_status != 'Todos':
        df_filtered = df_filtered[df_filtered['Status'] == selected_status]
        
    if selected_tipo != 'Todos':
        df_filtered = df_filtered[df_filtered['Tipo'] == selected_tipo]
    
    # KPIs principais
    st.subheader("📈 KPIs Gerais")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    total_tarefas = len(df_filtered)
    concluidas = len(df_filtered[df_filtered['Status'] == 'Concluído'])
    em_andamento = len(df_filtered[df_filtered['Status'] == 'Em andamento'])
    pendentes = len(df_filtered[df_filtered['Status'] == 'Tarefas pendentes'])
    taxa_conclusao = (concluidas / total_tarefas * 100) if total_tarefas > 0 else 0
    
    with col1:
        st.metric("Total de Tarefas", total_tarefas)
    with col2:
        st.metric("Concluídas", concluidas, f"{taxa_conclusao:.1f}%")
    with col3:
        st.metric("Em Andamento", em_andamento)
    with col4:
        st.metric("Pendentes", pendentes)
    with col5:
        devs_ativos = df_filtered['Responsavel'].nunique()
        st.metric("Devs Ativos", devs_ativos)
    
    st.markdown("---")
    
    # Gráficos lado a lado
    col_left, col_right = st.columns(2)
    
    with col_left:
        # Tarefas por Status (Donut)
        st.subheader("📊 Distribuição por Status")
        status_counts = df_filtered['Status'].value_counts()
        
        colors = {
            'Concluído': '#2ecc71',
            'Em andamento': '#f39c12',
            'Tarefas pendentes': '#3498db',
            'TESTE': '#9b59b6'
        }
        
        fig_status = px.pie(
            values=status_counts.values,
            names=status_counts.index,
            hole=0.5,
            color=status_counts.index,
            color_discrete_map=colors
        )
        fig_status.update_traces(textposition='outside', textinfo='percent+label')
        fig_status.update_layout(showlegend=False, height=350)
        st.plotly_chart(fig_status, use_container_width=True)
    
    with col_right:
        # Tarefas por Área
        st.subheader("🏷️ Distribuição por Área")
        area_counts = df_filtered['Area'].value_counts()
        
        fig_area = px.bar(
            x=area_counts.index,
            y=area_counts.values,
            color=area_counts.index,
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig_area.update_layout(
            xaxis_title="Área",
            yaxis_title="Quantidade",
            showlegend=False,
            height=350
        )
        st.plotly_chart(fig_area, use_container_width=True)
    
    st.markdown("---")
    
    # Performance por Dev
    st.subheader("👥 Performance por Desenvolvedor")
    
    dev_stats = df_filtered.groupby('Responsavel').agg({
        'Chave': 'count',
        'Status': lambda x: (x == 'Concluído').sum()
    }).rename(columns={'Chave': 'Total', 'Status': 'Concluidas'})
    
    dev_stats['Pendentes'] = dev_stats['Total'] - dev_stats['Concluidas']
    dev_stats['Taxa_Conclusao'] = (dev_stats['Concluidas'] / dev_stats['Total'] * 100).round(1)
    dev_stats = dev_stats.sort_values('Total', ascending=True)
    
    # Gráfico de barras empilhadas horizontal
    fig_dev = go.Figure()
    
    fig_dev.add_trace(go.Bar(
        name='Concluídas',
        y=dev_stats.index,
        x=dev_stats['Concluidas'],
        orientation='h',
        marker_color='#2ecc71',
        text=dev_stats['Concluidas'],
        textposition='inside'
    ))
    
    fig_dev.add_trace(go.Bar(
        name='Pendentes/Em andamento',
        y=dev_stats.index,
        x=dev_stats['Pendentes'],
        orientation='h',
        marker_color='#e74c3c',
        text=dev_stats['Pendentes'],
        textposition='inside'
    ))
    
    fig_dev.update_layout(
        barmode='stack',
        height=400,
        xaxis_title="Quantidade de Tarefas",
        yaxis_title="",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    st.plotly_chart(fig_dev, use_container_width=True)
    
    # Tabela resumo por dev
    col_table1, col_table2 = st.columns(2)
    
    with col_table1:
        st.subheader("📋 Resumo por Desenvolvedor")
        dev_summary = dev_stats.reset_index()
        dev_summary.columns = ['Desenvolvedor', 'Total', 'Concluídas', 'Pendentes', 'Taxa (%)']
        dev_summary = dev_summary.sort_values('Total', ascending=False)
        st.dataframe(dev_summary, use_container_width=True, hide_index=True)
    
    with col_table2:
        st.subheader("🔥 Atividade Recente (Últimos 7 dias)")
        recent_date = datetime.now() - timedelta(days=7)
        recent_tasks = df_filtered[df_filtered['Atualizado'] >= recent_date]
        recent_summary = recent_tasks.groupby('Responsavel').size().reset_index(name='Tarefas Atualizadas')
        recent_summary = recent_summary.sort_values('Tarefas Atualizadas', ascending=False)
        st.dataframe(recent_summary, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    # Timeline de criação
    st.subheader("📅 Timeline de Criação de Tarefas")
    
    df_timeline = df_filtered.copy()
    df_timeline['Semana'] = df_timeline['Criado'].dt.to_period('W').astype(str)
    timeline_counts = df_timeline.groupby(['Semana', 'Status']).size().reset_index(name='Quantidade')
    
    fig_timeline = px.bar(
        timeline_counts,
        x='Semana',
        y='Quantidade',
        color='Status',
        color_discrete_map={
            'Concluído': '#2ecc71',
            'Em andamento': '#f39c12',
            'Tarefas pendentes': '#3498db',
            'TESTE': '#9b59b6'
        }
    )
    fig_timeline.update_layout(
        xaxis_title="Semana",
        yaxis_title="Quantidade",
        height=400,
        xaxis_tickangle=-45
    )
    st.plotly_chart(fig_timeline, use_container_width=True)
    
    st.markdown("---")
    
    # Detalhes das tarefas
    st.subheader("📝 Detalhes das Tarefas")
    
    # Seletor de colunas
    cols_to_show = st.multiselect(
        "Selecione as colunas para exibir:",
        options=['Chave', 'Tipo', 'Resumo', 'Responsavel', 'Status', 'Area', 'Criado', 'Atualizado'],
        default=['Chave', 'Tipo', 'Resumo', 'Responsavel', 'Status', 'Criado']
    )
    
    if cols_to_show:
        st.dataframe(
            df_filtered[cols_to_show].sort_values('Criado', ascending=False),
            use_container_width=True,
            hide_index=True
        )
    
    # Exportar dados filtrados
    st.sidebar.markdown("---")
    st.sidebar.subheader("📥 Exportar Dados")
    
    csv = df_filtered.to_csv(index=False).encode('utf-8-sig')
    st.sidebar.download_button(
        label="Baixar CSV Filtrado",
        data=csv,
        file_name="jira_filtrado.csv",
        mime="text/csv"
    )

else:
    st.error("⚠️ Nenhum arquivo CSV encontrado na pasta `data/`")
    
    st.markdown("""
    ### Como adicionar dados:
    
    1. Crie uma pasta `data/` no mesmo diretório do `app.py`
    2. Exporte do Jira usando a query JQL:
    ```
    project = TwoBetter AND issuetype in (Task, Subtask) ORDER BY created DESC
    ```
    3. Clique em **Export → CSV (Current fields)**
    4. Coloque o arquivo `.csv` na pasta `data/`
    5. Reinicie o dashboard
    
    O dashboard sempre carrega o arquivo CSV mais recente da pasta.
    """)
