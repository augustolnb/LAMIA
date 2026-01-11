import os
import boto3
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env
load_dotenv()

# Bibliotecas do LangChain e Qdrant
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

# --- VERIFICAÇÃO DE SEGURANÇA ---
required_vars = [
    "GOOGLE_API_KEY", "QDRANT_URL", "QDRANT_API_KEY", 
    "S3_ENDPOINT", "S3_ACCESS_KEY_ID", "S3_SECRET_ACCESS_KEY", "S3_BUCKET_NAME"
]
missing_vars = [var for var in required_vars if not os.getenv(var)]
if missing_vars:
    raise EnvironmentError(f"❌ Erro: Faltam variáveis no arquivo .env: {', '.join(missing_vars)}")

# --- CONFIGURAÇÕES CARREGADAS ---
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
COLLECTION_NAME = os.getenv("QDRANT_COLLECTION_NAME")

S3_ENDPOINT = os.getenv("S3_ENDPOINT")
S3_ACCESS_KEY = os.getenv("S3_ACCESS_KEY_ID")
S3_SECRET_KEY = os.getenv("S3_SECRET_ACCESS_KEY")
BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
S3_REGION = os.getenv("S3_REGION")

# --- PASSO 1: INGESTÃO (Download S3 -> Qdrant) ---
def ingest_data(file_name_in_bucket):
    print(f"--- 1. Baixando '{file_name_in_bucket}' do Backblaze ---")

    # Configuração do cliente S3 (Boto3)
    s3 = boto3.client('s3', 
                      endpoint_url=S3_ENDPOINT,
                      region_name=S3_REGION,
                      aws_access_key_id=S3_ACCESS_KEY,
                      aws_secret_access_key=S3_SECRET_KEY)

    local_filename = "temp_doc.pdf"
    try:
        s3.download_file(BUCKET_NAME, file_name_in_bucket, local_filename)
    except Exception as e:
        print(f"❌ Erro ao baixar arquivo: {e}")
        return

    print("--- 2. Processando PDF e criando Chunks ---")
    loader = PyPDFLoader(local_filename)
    docs = loader.load()

    # Configuração de Chunking (igual ao n8n)
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100
    )
    splits = text_splitter.split_documents(docs)
    print(f"   -> Documento dividido em {len(splits)} pedaços.")

    print("--- 3. Vetorização e Upload para Qdrant ---")
    embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")

    client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)

    # Verifica/Cria a coleção com dimensão 768
    if not client.collection_exists(COLLECTION_NAME):
        print(f"   -> Criando coleção '{COLLECTION_NAME}'...")
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=768, distance=Distance.COSINE),
        )

    # Envia para o banco
    QdrantVectorStore.from_documents(
        splits,
        embeddings,
        url=QDRANT_URL,
        api_key=QDRANT_API_KEY,
        collection_name=COLLECTION_NAME
    )

    # Limpeza
    if os.path.exists(local_filename):
        os.remove(local_filename)

    print("✅ Ingestão concluída com sucesso!")

# --- PASSO 2: CHAT RAG (Consulta) ---
def chat_with_rag(query):
    print(f"\nPergunta: {query}")

    embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")

    # Conecta ao banco existente
    vector_store = QdrantVectorStore.from_existing_collection(
        embedding=embeddings,
        collection_name=COLLECTION_NAME,
        url=QDRANT_URL,
        api_key=QDRANT_API_KEY
    )

    # Modelo de Chat (Gemini 1.5 Flash)
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)

    # Configura o Retriever (Busca os top 3 contextos)
    retriever = vector_store.as_retriever(search_kwargs={"k": 3})
    docs = retriever.invoke(query)

    if not docs:
        print("⚠️ Nenhuma informação relevante encontrada no banco.")
        return

    # Monta o contexto para o prompt
    context_text = "\n\n".join([d.page_content for d in docs])

    prompt = f"""
    Você é um assistente especialista. Use apenas as informações contidas no banco de dados vetorial para responder a pergunta do usuário.
    Se a resposta não estiver no contexto, diga que não sabe.

    --- Contexto ---
    {context_text}

    --- Pergunta ---
    {query}
    """

    print("Aguarde a resposta...")
    response = llm.invoke(prompt)
    print(f"\nResposta do agente:\n{response.content}")

if __name__ == "__main__":
    # --- MODO 1: INGESTÃO (Rode isso uma vez para popular o banco) ---
    #ingest_data("tcc-lucas-augusto-nunes-de-barros.pdf") 

     # --- MODO 2: CHAT INTERATIVO ---
    print("---------------------------------------------------------")
    print("Chat RAG Iniciado! (Digite 'sair' para encerrar)")
    print("---------------------------------------------------------")

    while True:
        # 1. Aguarda você digitar algo no terminal
        user_input = input("\nPergunte algo ao agente: ")

        # 2. Verifica se você quer sair
        if user_input.lower() in ["sair", "exit", "quit"]:
            print("Encerrando...")
            break
        
        # 3. Evita enviar perguntas vazias (se der apenas Enter)
        if not user_input.strip():
            continue

        # 4. Chama a função de chat com o que você digitou
        chat_with_rag(user_input)