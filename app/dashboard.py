import streamlit as st
import pandas as pd

# --- Configuração da Página ---
st.set_page_config(
    page_title="Dashboard de Contagem de Cenários",
    page_icon="📊",
    layout="wide"
)

# --- Título e Descrição ---
st.title("📊 Dashboard de Contagem de Cenários")
st.markdown("Utilize este dashboard para visualizar a quantidade de vezes que um determinado cenário foi enquadrado.")

# --- Dados de Exemplo (Simulação) ---
# Em um caso real, estes dados viriam de um banco de dados, arquivo CSV, etc.
dados_cenarios = {
    'Cenário A': 120,
    'Cenário B': 75,
    'Cenário C': 210,
    'Cenário D': 45,
    'Cenário E': 98
}

# Converte o dicionário para um DataFrame do Pandas para melhor manipulação
df_cenarios = pd.DataFrame(list(dados_cenarios.items()), columns=['Cenário', 'Quantidade'])

# --- Barra Lateral com Opções ---
st.sidebar.header("Filtros")
cenario_selecionado = st.sidebar.selectbox(
    "Selecione um Cenário:",
    options=df_cenarios['Cenário'].unique()
)

# --- Painel Principal ---
st.header(f"Análise do Cenário: {cenario_selecionado}")

# Filtra o DataFrame para o cenário selecionado
quantidade_cenario = df_cenarios[df_cenarios['Cenário'] == cenario_selecionado]['Quantidade'].values[0]

# Exibe a métrica de contagem
st.metric(label="Quantidade de Enquadramentos", value=quantidade_cenario)

# --- Visualização Adicional (Opcional) ---
st.subheader("Visão Geral dos Cenários")

# Gráfico de barras para comparar todos os cenários
st.bar_chart(df_cenarios.set_index('Cenário'))

# Tabela com os dados completos
st.dataframe(df_cenarios)