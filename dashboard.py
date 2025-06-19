# dashboard.py

import streamlit as st
import pandas as pd
from datetime import datetime

# Importa as classes do seu projeto
from irrigation_system.database import AgriculturalDatabase
# A classe de inteligência não é mais necessária para este dashboard simplificado

# Configuração da página do Streamlit
st.set_page_config(
    page_title="Dashboard de Irrigação",
    page_icon="💧",
    layout="wide"
)

# --- Carregamento em Cache do Serviço de Banco de Dados ---
@st.cache_resource
def load_db_service():
    """
    Carrega e retorna uma instância da base de dados.
    Fica em cache para performance.
    """
    db = AgriculturalDatabase(db_name="data/agricultural_system.db")
    return db

# --- Função de busca de dados (com cache) ---
@st.cache_data(ttl=60) # Cache de dados por 60 segundos
def get_dashboard_data(_db):
    """
    Busca dados agregados para a página principal.
    """
    setores = _db.consultar_setores()
    sensores = _db.consultar_sensores()
    irrigacoes = _db.consultar_irrigacoes()
    medicoes = _db.consultar_medicoes()
    return setores, sensores, irrigacoes, medicoes

# --- Função de Renderização da Página Principal ---
def render_overview_page(db):
    """Renderiza a página de Visão Geral."""
    st.title("💧 Dashboard de Monitoramento de Irrigação")
    st.markdown("Status em tempo real da sua plantação e últimas atividades.")
    
    # Busca os dados mais recentes
    setores, sensores, irrigacoes, medicoes = get_dashboard_data(db)

    # Métricas principais na parte superior
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Setores Ativos", f"{len(setores)}")
    col2.metric("Sensores Monitorando", f"{len(sensores)}")
    
    if irrigacoes:
        ultima_irrigacao_dt = max([datetime.fromisoformat(i['data_irrigacao']) for i in irrigacoes])
        col3.metric("Última Irrigação", ultima_irrigacao_dt.strftime("%d/%m/%Y %H:%M"))
    else:
        col3.metric("Última Irrigação", "N/A")

    if medicoes:
        ultima_medicao_dt = max([datetime.fromisoformat(m['data_medicao']) for m in medicoes])
        col4.metric("Última Medição", ultima_medicao_dt.strftime("%d/%m/%Y %H:%M"))
    else:
        col4.metric("Última Medição", "N/A")

    st.divider()

    # Gráfico de umidade de todos os sensores
    st.subheader("Variação da Umidade ao Longo do Tempo (Todos os Setores)")
    if medicoes:
        df_medicoes = pd.DataFrame(medicoes)
        # Filtra apenas por sensores de 'umidade'
        df_umidade = df_medicoes[df_medicoes['tipo_sensor'] == 'umidade'].copy()
        
        if not df_umidade.empty:
            df_umidade['data_medicao'] = pd.to_datetime(df_umidade['data_medicao'])
            
            # Cria uma tabela pivot para ter um sensor por coluna
            chart_data = df_umidade.pivot_table(
                index='data_medicao', 
                columns='id_sensor', 
                values='valor_medicao'
            )
            st.line_chart(chart_data)
        else:
            st.warning("Nenhum dado do sensor de 'umidade' encontrado no banco de dados.")
    else:
        st.info("Aguardando dados de medições para exibir gráficos.")
        
    st.divider()
    
    # Tabela com as últimas irrigações
    st.subheader("Histórico Recente de Irrigações")
    if irrigacoes:
        df_irrigacoes = pd.DataFrame(irrigacoes)
        df_irrigacoes['data_irrigacao'] = pd.to_datetime(df_irrigacoes['data_irrigacao']).dt.strftime('%d/%m/%Y %H:%M')
        st.dataframe(
            df_irrigacoes[['id_setor', 'volume_irrigacao', 'data_irrigacao']].sort_values(by='data_irrigacao', ascending=False).head(10),
            use_container_width=True
        )
    else:
        st.info("Nenhum registro de irrigação encontrado.")


# --- Função Principal do Dashboard ---
def main():
    db = load_db_service()
    render_overview_page(db)

if __name__ == "__main__":
    main()