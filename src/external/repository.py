import os
from dotenv import load_dotenv, find_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError

load_dotenv(find_dotenv())


def _build_database_url() -> str:
    """
    Função interna para construir a string de conexão para o Oracle.
    """
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    host = os.getenv("DB_HOST")
    port = os.getenv("DB_PORT")
    service = os.getenv("DB_SERVICE")

    if not all([user, password, host, port, service]):
        raise ValueError(
            "Uma ou mais variáveis de ambiente do banco de dados não foram definidas."
        )

    return f"oracle+oracledb://{user}:{password}@{host}:{port}/?service_name={service}"


try:
    DATABASE_URL = _build_database_url()

    engine = create_engine(DATABASE_URL, pool_pre_ping=True)

    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    print("Engine do SQLAlchemy criado com sucesso.")

except Exception as e:
    print(f"Falha ao configurar o SQLAlchemy: {e}")
    engine = None
    SessionLocal = None


def get_session() -> Session:
    """
    Cria e retorna uma nova sessão com o banco de dados.
    """
    if not SessionLocal:
        raise RuntimeError(
            "A configuração da sessão falhou. Não é possível criar uma sessão."
        )

    return SessionLocal()


def buscar_dados_operacao(operacao_id: int = 1, pfj_codigo: str = "90050238000629"):
    """
    Busca os dados de uma operação específica no banco de dados usando uma sessão SQLAlchemy.
    Retorna os dados como um dicionário.
    """
    with get_session() as session:
        try:
            print(f"Buscando dados para a operação com ID: {operacao_id}")

            sql_query = text(f"""
                                SELECT
                                    dof.EMITENTE_PFJ_CODIGO,
                                    dof.DESTINATARIO_PFJ_CODIGO,
                                    dof.ind_entrada_saida,
                                    pessoa_a.Ind_orgao_governamental AS emit_publico,
                                    pessoa_b.Ind_orgao_governamental AS dest_publico,
                                    idf.nbm_codigo,
                                    tributo.cst_codigo_ibs_cbs,
                                    tributo.clas_trib_ibs_cbs
                                FROM
                                    CSES3_DEV.cor_idf idf,
                                    CSES3_DEV.cor_idf_tributo tributo,
                                    CSES3_DEV.cor_dof dof,
                                    CSES3_DEV.cor_pessoa pessoa_a,
                                    CSES3_DEV.cor_pessoa pessoa_b
                                WHERE
                                    idf.codigo_do_site = tributo.codigo_do_site
                                    AND dof.codigo_do_site = idf.codigo_do_site
                                    AND idf.dof_sequence = tributo.dof_sequence
                                    AND dof.dof_sequence = idf.dof_sequence
                                    AND dof.EMITENTE_PFJ_CODIGO = pessoa_a.pfj_codigo
                                    AND dof.DESTINATARIO_PFJ_CODIGO = pessoa_b.pfj_codigo
                                    AND idf.nbm_codigo IS NOT NULL
                                    AND tributo.cst_codigo_ibs_cbs IS NOT NULL
                                    AND tributo.clas_trib_ibs_cbs IS NOT NULL
                                    AND dof.EMITENTE_PFJ_CODIGO = '{pfj_codigo}'
                                        """)

            result = session.execute(sql_query, {"id": operacao_id}).mappings().all()

            if result:
                dados_operacao = dict(result)
                print("Dados encontrados:", dados_operacao)
                return dados_operacao
            else:
                print(f"Nenhum dado encontrado para a operação com ID: {operacao_id}")
                return None

        except SQLAlchemyError as e:
            print(f"Erro ao buscar dados com SQLAlchemy: {e}")
            return None


if __name__ == "__main__":
    session = None
    try:
        if session:
            dados = buscar_dados_operacao(operacao_id=1)
            if dados:
                print("Dados retornados:", dados)
    except Exception as e:
        print(f"\nOcorreu um erro durante o teste: {e}")
    finally:
        if session:
            session.close()
