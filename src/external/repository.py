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
        raise ValueError("Uma ou mais variáveis de ambiente do banco de dados não foram definidas.")

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
        raise RuntimeError("A configuração da sessão falhou. Não é possível criar uma sessão.")
    
    return SessionLocal()

def buscar_dados_operacao(session: Session, operacao_id: int = 1):
    """
    Busca os dados de uma operação específica no banco de dados usando uma sessão SQLAlchemy.
    Retorna os dados como um dicionário.
    """
    try:
        print(f"Buscando dados para a operação com ID: {operacao_id}")
        
        sql_query = text("""
            select 
                d.numero, 
                d.EMITENTE_PFJ_CODIGO, 
                d.DESTINATARIO_PFJ_CODIGO, 
                d.ind_entrada_saida, 
                l.Ind_orgao_governamental 
                emit_publico, 
                b.Ind_orgao_governamental 
                dest_publico,
                i.nbm_codigo,
                i.nbs_codigo,
                i.vl_contabil,
                t.cst_codigo_ibs_cbs,
                t.clas_trib_ibs_cbs,
                t.vl_base_ibs_cbs,
                PERC_RED_ALIQ_CBS,
                PERC_RED_ALIQ_IBS_UF,
                VL_CBS,
                VL_IBS_MUN,
                VL_IBS_UF,
                PERC_RED_ALIQ_IBS_MUN
            from
                cor_idf i,
                cor_idf_tributo t,
                cor_dof d,
                cor_pessoa l,
                cor_pessoa b
            where
                i.codigo_do_site = t.codigo_do_site
                and d.codigo_do_site = i.codigo_do_site
                and i.dof_sequence = t.dof_sequence
                and d.dof_sequence = i.dof_sequence
                and d.EMITENTE_PFJ_CODIGO = l.pfj_codigo
                and d.DESTINATARIO_PFJ_CODIGO=b.pfj_codigo
        """) 
        
        result = session.execute(sql_query, {"id": operacao_id}).mappings().first()
        
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

if __name__ == '__main__':
    
    session = None
    try:
        session = get_session()
        
        if session:
            dados = buscar_dados_operacao(session, operacao_id=1)
            if dados:
                print("Dados retornados:", dados)
    except Exception as e:
        print(f"\nOcorreu um erro durante o teste: {e}")
    finally:
        if session:
            session.close()
