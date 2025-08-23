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
            SELECT 1 FROM DUAL
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
