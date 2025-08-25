import os
from typing import Optional
from minio import Minio
from minio.error import S3Error
from dotenv import load_dotenv
from io import BytesIO

load_dotenv()

MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY")
MINIO_BUCKET = os.getenv("MINIO_BUCKET")

if not all([MINIO_ENDPOINT, MINIO_ACCESS_KEY, MINIO_SECRET_KEY, MINIO_BUCKET]):
    raise ValueError("Uma ou mais variáveis de ambiente do MinIO não foram definidas.")

try:
    minio_client = Minio(
        MINIO_ENDPOINT,
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
        secure=False,
    )
    print("Cliente MinIO conectado com sucesso.")
except Exception as e:
    print(f"Falha ao conectar com o MinIO: {e}")
    minio_client = None


def salvar_resultado_no_minio(nome_arquivo: str, conteudo: str) -> Optional[str]:
    """
    Salva uma string de conteúdo como um arquivo de texto no bucket do MinIO.
    """
    if not minio_client:
        print("ERRO: Cliente MinIO não está disponível para upload.")
        return False

    try:
        conteudo_bytes = conteudo.encode("utf-8")
        conteudo_stream = BytesIO(conteudo_bytes)
        tamanho_conteudo = len(conteudo_bytes)

        minio_client.put_object(
            bucket_name=MINIO_BUCKET,
            object_name=nome_arquivo,
            data=conteudo_stream,
            length=tamanho_conteudo,
            content_type="text/plain",
        )

        print(
            f"      Resultado salvo com sucesso no MinIO: '{MINIO_BUCKET}/{nome_arquivo}'"
        )

        return minio_client.get_presigned_url("GET", MINIO_BUCKET, nome_arquivo)

    except S3Error as exc:
        print(f"ERRO ao salvar no MinIO: {exc}")
        return None
