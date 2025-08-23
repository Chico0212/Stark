import streamlit as st
import pandas as pd

# --- Configuração da Página ---
st.set_page_config(
    page_title="Dashboard de Contagem de Cenários",
    page_icon="📊",
    layout="wide"
)
st.sidebar.image("app/LOGOSYNCHRO.png", use_container_width=True)
# --- Título e Descrição ---
st.title("Dashboard de Cenários")
st.markdown("Utilize este dashboard para visualizar a quantidade de vezes que um determinado cenário foi enquadrado.")

# --- Dados de Exemplo (Simulação) ---
# Estrutura correta para múltiplas colunas: um dicionário de listas
dados_completos = {
    'Cenário': ['Cenário A', 'Cenário B', 'Cenário C', 'Cenário D', 'Cenário E'],
    'Quantidade': [120, 75, 210, 45, 98],
    'Lei': [
        'Lei nº 8.137/90',
        'Lei nº 9.613/98',
        'LC nº 105/01',
        'Resolução BACEN nº 4.557/17',
        'Lei nº 12.846/13'
    ]
}

# Converte o dicionário para um DataFrame do Pandas
df_cenarios = pd.DataFrame(dados_completos)
# --- Barra Lateral com Opções ---
st.sidebar.header("Filtros")
cenario_selecionado = st.sidebar.selectbox(
    "Selecione um Cenário:",
    options=df_cenarios['Cenário'].unique()
)

# Filtra o DataFrame para o cenário selecionado
quantidade_cenario = df_cenarios[df_cenarios['Cenário'] == cenario_selecionado]['Quantidade'].values[0]

# Exibe a métrica de contagem
#st.metric(label="Quantidade de Enquadramentos", value=quantidade_cenario)

total_enquadramentos = int(df_cenarios['Quantidade'].sum())
cenario_com_maior_volume = df_cenarios.loc[df_cenarios['Quantidade'].idxmax()]
quantidade_do_selecionado = df_cenarios[df_cenarios['Cenário'] == cenario_selecionado]['Quantidade'].iloc[0]

# 2. Criar as colunas
col1, col2 = st.columns(2)

# 3. Exibir as métricas em cada coluna
col1.metric("Total de Enquadramentos", f"{total_enquadramentos}")

# Esta é a métrica que você pediu para adicionar
col2.metric(f"Principal Cenário: {cenario_com_maior_volume['Cenário']}", f"{cenario_com_maior_volume['Quantidade']}")

# --- Painel Principal ---
st.header(f"Análise do Cenário: {cenario_selecionado}")

st.markdown("---") # Adiciona uma linha divisória para organizar

# --- Visualização Adicional (Opcional) ---
st.subheader("Visão Geral dos Cenários")

# Gráfico de barras para comparar todos os cenários
st.bar_chart(df_cenarios.set_index('Cenário'), y='Quantidade', color='#094f80')

# Tabela com os dados completos
st.dataframe(df_cenarios)