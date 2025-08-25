import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import sys
import os

DIRETORIO_ATUAL = os.path.dirname(os.path.abspath(__file__))
DIRETORIO_RAIZ = os.path.dirname(DIRETORIO_ATUAL)
sys.path.append(DIRETORIO_RAIZ)

from src.utils.constants import PASTA_RESULTADOS
from src.data_loader import load_data
from src.external.repository import buscar_dados_operacao
from src.main import processar_operacao, limpar_pasta_resultados
from src.motor_regras import find_rule

PASTA_RESULTADOS = "results"

# --- Configuração da Página ---
st.set_page_config(
    page_title="Dashboard de Contagem de Cenários",
    page_icon="📊",
    layout="wide"
)

# Inicializa o session_state
if 'dados_dashboard' not in st.session_state:
    st.session_state.dados_dashboard = None

# --- Barra Lateral para Geração de Relatório ---
st.sidebar.image("app/LOGOSYNCHRO.png", use_container_width=True)

pfj_codigo_input = st.sidebar.text_input("Digite o Código PFJ:", "1003A5F4F")

if st.sidebar.button("Gerar Análise", type="primary"):
        pfj_codigo = pfj_codigo_input
        limpar_pasta_resultados()

        with st.spinner(f"Processando PFJ {pfj_codigo}..."):
            regras_df = load_data()
            dados_para_analisar = buscar_dados_operacao(operacao_id=1, pfj_codigo=pfj_codigo)
            sucesso = processar_operacao(dados_para_analisar, regras_df, test_case_id=25630)

        if sucesso:
            st.sidebar.success("Relatório gerado com sucesso!")
            caminho_csv_final = os.path.join(PASTA_RESULTADOS, "resultados.csv")
            if os.path.exists(caminho_csv_final):
                st.session_state.dados_dashboard = pd.read_csv(caminho_csv_final)
            else:
                st.sidebar.error("Arquivo de resultados não foi encontrado.")
                st.session_state.dados_dashboard = None
        else:
            st.sidebar.error("Falha ao processar. Verifique se os códigos estão corretos.")
            st.session_state.dados_dashboard = None


# --- Área Principal do Dashboard (só aparece depois de gerar os dados) ---
if st.session_state.dados_dashboard is not None:
    # --- Título e Descrição ---
    st.title("Dashboard de Cenários")
    st.markdown(
        "Utilize este dashboard para visualizar a quantidade de vezes que um determinado cenário foi enquadrado.")

    df_cenarios_bruto = st.session_state.dados_dashboard.copy()

    # Renomeia colunas para padronizar
    df_cenarios_bruto.rename(columns={
        'lei': 'Cenário',
        'total_ocorrencias': 'Quantidade'
    }, inplace=True)

    # [CORREÇÃO PRINCIPAL] Agrega os dados para obter os totais por cenário
    # Isso resolve a inconsistência entre as métricas e o gráfico.
    df_agregado = df_cenarios_bruto.groupby('Cenário')['Quantidade'].sum().reset_index()

    # --- Barra Lateral com Filtros (aparece junto com o dashboard) ---
    st.sidebar.header("Filtros do Dashboard")
    cenario_selecionado = st.sidebar.selectbox(
        "Selecione um Cenário para destacar:",
        options=df_agregado['Cenário'].unique()  # Usa os cenários únicos do df agregado
    )

    # --- Métricas (calculadas a partir dos dados agregados) ---
    total_enquadramentos = int(df_agregado['Quantidade'].sum())
    cenario_com_maior_volume = df_agregado.loc[df_agregado['Quantidade'].idxmax()]

    col1, col2 = st.columns(2)
    col1.metric("Total de Enquadramentos", f"{total_enquadramentos}")
    col2.metric(f"Principal Cenário: {cenario_com_maior_volume['Cenário']}",
                f"{cenario_com_maior_volume['Quantidade']}")

    st.markdown("---")

    # --- Visualização com Abas ---
    tab1, tab2 = st.tabs(["Gráfico Interativo", "Tabela de Dados Detalhada"])

    with tab1:
        st.markdown("#### Comparativo de Ocorrências por Cenário")

        # Lógica de destaque aplicada ao df agregado
        df_agregado['Destaque'] = np.where(df_agregado['Cenário'] == cenario_selecionado, 'Selecionado', 'Outros')
        mapa_de_cores = {'Selecionado': '#dba112', 'Outros': '#094f80'}

        fig = px.bar(
            df_agregado,  # Usa o dataframe agregado para o gráfico
            x='Cenário',
            y='Quantidade',
            title="Total de Ocorrências por Cenário",
            log_y=False,  # Desativado por padrão para melhor visualização de totais
            text_auto=True,
            color='Destaque',
            color_discrete_map=mapa_de_cores
        )
        fig.update_layout(legend_traceorder="reversed", xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        st.markdown("#### Todos os Dados (Não Agregados)")
        # Mostra os dados brutos para que os detalhes não sejam perdidos
        colunas_para_mostrar = ['Cenário', 'Quantidade', 'nbm_codigo']
        st.dataframe(df_cenarios_bruto[colunas_para_mostrar])

else:
    # Mensagem inicial antes de gerar o relatório
    st.info("⬅️ Por favor, insira o ID da Operação e o Código PFJ na barra lateral para gerar uma análise.")
