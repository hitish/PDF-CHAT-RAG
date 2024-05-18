from fastapi import FastAPI, Body
from models import Message, Response
import utils
from starlette.websockets import  WebSocket,WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from llama_index.core import VectorStoreIndex,load_index_from_storage,StorageContext
from llama_index.core.llms import ChatMessage, MessageRole
#from llama_index.vector_stores.faiss import FaissVectorStore
import logging
import json,os,time
import base64

from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.core.memory import ChatMemoryBuffer
import qdrant_client

logger = logging.getLogger("main")
logger.setLevel(logging.DEBUG)
app = FastAPI()

connected_clients = []

origins = ["http://localhost:3000", "localhost:3000"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
  await websocket.accept()
  connected_clients.append(websocket)
  chat_engine = None
  chat_hist = []
  chat_hist_copy = []
  try:
    while True:
      data = await websocket.receive_text()
      return_json = {"response":"error"}
      if(data):
        json_data = json.loads(data)
        if chat_engine is None:
          aclient = qdrant_client.AsyncQdrantClient(host="localhost",port=6333)
          client = qdrant_client.QdrantClient( host="localhost", port=6333 )

          vector_store = QdrantVectorStore(client=client,aclient=aclient, collection_name=json_data["chatname"].lower().replace(" ","_"))
          index = VectorStoreIndex.from_vector_store(vector_store=vector_store)
          print(index)
          memory = ChatMemoryBuffer.from_defaults(token_limit=4096)
          chat_engine = index.as_chat_engine(chat_mode="condense_plus_context",memory=memory,  verbose = True, )

        if "text" in json_data:
          chat_hist = chat_hist_copy.copy()
          response_msg = await utils.process_message(json_data,chat_hist,chat_engine)
          chat_hist_copy.append(ChatMessage(role=MessageRole.USER,content=json_data["text"],  ))
          chat_hist_copy.append(ChatMessage(role=MessageRole.ASSISTANT,content=response_msg,  ))
          return_json = {"user":"bot","text":response_msg}
          
        await websocket.send_json(return_json)
        print(return_json)
      
  except WebSocketDisconnect:
    print("websocket disconnected ws")
    print(WebSocketDisconnect)
    await websocket.close()
    connected_clients.remove(websocket)



@app.websocket("/ws/file")
async def websocket_file_endpoint(websoc: WebSocket):
  await websoc.accept()
  connected_clients.append(websoc)
  try:
    while True:
       
      async for data in websoc.iter_bytes():
        #data = await websoc.receive_json()
        if data is not None:
         
          delimiter = data.find(b'\x00')
          chatname = data[:delimiter].decode()
          print(chatname)
          data = data[delimiter + 1:]
          delimiter = data.find(b'\x00')
          fn = data[:delimiter].decode()
          filename =   fn.split(".")[0]+f"{int(time.time())}.pdf"
          file_data = data[delimiter + 1:]
  
          print(filename)
          folder_name = chatname.lower().replace(" ","_")
          directory_path = "uploads/"+folder_name
          filepath = os.path.join(directory_path, filename).replace("\\","/")
          os.makedirs(directory_path,exist_ok=True)
          
          with open(filepath, "wb") as f:
            f.write(file_data)  
            print(f'File saved successfully: {filepath}')
            if(await utils.create_vector_db(directory_path,folder_name)):
              return_json =  {"response":f"{chatname} updated"}
              await websoc.send_json(return_json)
            
  except WebSocketDisconnect:
    print("websocket disconnected ws/file")
    
    await websoc.close()
    connected_clients.remove(websoc)



if __name__ == "__main__":
  import uvicorn
  uvicorn.run("main:app", host="127.0.0.1", port=4000 ,reload=True)