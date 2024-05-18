from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Document,Settings,StorageContext
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.openai import OpenAI
from llama_index.llms.llama_api import LlamaAPI

#from llama_index.vector_stores.faiss import FaissVectorStore
#import faiss,time,

import asyncio
from llama_index.vector_stores.qdrant import QdrantVectorStore
import qdrant_client


from pypdf import PdfReader
import nltk
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.extractors import (
    SummaryExtractor,
    QuestionsAnsweredExtractor,
    TitleExtractor,
    KeywordExtractor,
)
from llama_index.core.ingestion import IngestionPipeline
from llama_index.extractors.entity import EntityExtractor


model_name = "all-mpnet-base-v2"  # For text embedding
tokenizer_name = f"{model_name}-tokenizer"  # Corresponding tokenizer
text_embedding_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
Settings.embed_model = text_embedding_model

llm = LlamaAPI(api_key="LL-ZnKQ7YwQEisx0LN9SYDitW3woFEU5p5nuqxm7FBXw3Z8jcc9VebiLPigsE5fcvEe",model="llama-7b-chat",max_tokens=512)

print(llm)
Settings.llm=llm


transformations = [
    SentenceSplitter(chunk_size=128,chunk_overlap=12),
    #TitleExtractor(nodes=5),
    #QuestionsAnsweredExtractor(questions=3),
    #SummaryExtractor(summaries=["prev", "self"]),
    #KeywordExtractor(keywords=10),
    #EntityExtractor(prediction_threshold=0.5),
]

async def process_message(json_data,chat_hist,chat_engine):
  try:
    query = json_data["text"]
    print(query)
    response = await chat_engine.achat(query,chat_history=chat_hist)
    print(response.response)
    return response.response
  except Exception as error:
    print("An exception occurred:", error)
    return "Some error occured please try with other question"


# Define reader function to extract text from PDF
def read_pdf(filepath):
  with open(filepath, 'rb') as f:
    reader = PdfReader(f)
    text = ""
    for page in reader.pages:
      text += page.extract_text()
  return text

# Define function to create document with text and embedding
def create_document(filepath):
  text = read_pdf(filepath)
  embedding = text_embedding_model.encode(text).tolist()
  document = Document(id=filepath, text=text, embedding=embedding)
  return document

async def run_pipeline(documents):
    ingestion_pipeline = IngestionPipeline(transformations=transformations)
    mynodes = await ingestion_pipeline.arun(documents=documents)
    return mynodes

async def create_vector_db(directory_path,chatname):
  try:
    directory_reader = SimpleDirectoryReader(directory_path)
    embedding_dim = 768  # Adjust based on your embedding model
    mydocs = directory_reader.load_data()
    
    #print(mydocs)
    ingestion_pipeline = IngestionPipeline(transformations=transformations)
    mynodes = await ingestion_pipeline.arun(documents=mydocs)

    client = qdrant_client.QdrantClient(
    # you can use :memory: mode for fast and light-weight experiments,
    # it does not require to have Qdrant deployed anywhere
    # but requires qdrant-client >= 1.1.1
    # location=":memory:"
    # otherwise set Qdrant instance address with:
    # url="http://:"
    # otherwise set Qdrant instance with host and port:
    host="localhost",
    port=6333
    # set API KEY for Qdrant Cloud
    # api_key="",
    )

    vector_store = QdrantVectorStore(client=client, collection_name=chatname)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    index = VectorStoreIndex(mynodes, storage_context=storage_context)

    print("vector store somewhere")
    return True
  except Exception as e:
    print("error is ")
    print(e)
    return False



