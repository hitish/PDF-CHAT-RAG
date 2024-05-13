from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Document,Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.faiss import FaissVectorStore
from pypdf import PdfReader
import faiss,time,asyncio
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

transformations = [
    SentenceSplitter(chunk_size=512,chunk_overlap=50),
    #TitleExtractor(nodes=5),
    #QuestionsAnsweredExtractor(questions=3),
    #SummaryExtractor(summaries=["prev", "self"]),
    #KeywordExtractor(keywords=10),
    #EntityExtractor(prediction_threshold=0.5),
]

def process_message(query:str,index:VectorStoreIndex):
  chat_engine = index.as_chat_engine()
  streaming_response = chat_engine.stream_chat("Tell me a joke.")
  for token in streaming_response.response_gen:
    print(token, end="")
  return "streaming_response"

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
    faiss_index = faiss.IndexFlatL2(embedding_dim)
    faiss_vector_store = FaissVectorStore(faiss_index=faiss_index)
    vector_store_index = VectorStoreIndex(nodes=mynodes,vector_store_index=faiss_vector_store)
    vector_store_index.storage_context.persist("./store/"+chatname)
    print("vector store somewhere")
    return True
  except Exception as e:
    print("error is ")
    print(e)
    return False



