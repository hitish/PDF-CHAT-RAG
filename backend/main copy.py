from fastapi import FastAPI, Body
from models import Message, Response
import utils
from starlette.websockets import  WebSocket,WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import logging
import json,os,time

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


@app.post("/chat", response_model=Response)
async def handle_chat_message(message: Message = Body(...)):
  # Access user message from request body
  user_message = message.message
  print(user_message)
  
  # Process user message
  processed_message = "process_message(user_message)"

  return Response(response=processed_message)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
  logger.info("This is an info message")
  logger.debug("This is an info message")
  await websocket.accept()
  #print(websocket.session)
  connected_clients.append(websocket)
  try:
    while True:
      data = await websocket.receive_text()
      
      message = data.text + " response"
      await websocket.send_json({"user":"bot","text":message})
      
  except WebSocketDisconnect:
    print("websocket disconnected")
    logger.info("This is an info message")
    await websocket.close()
    connected_clients.remove(websocket)


@app.websocket("/ws/file")
async def websocket_file_endpoint(websocket: WebSocket):
  logger.info("This is an info message")
  logger.debug("This is an info message")
  await websocket.accept()
  connected_clients.append(websocket)
  try:
     #os.makedirs(os.path.dirname(filepath), exist_ok=True)  # Create directory if needed
    
      while True:
        data = await websocket.receive_bytes()
        if data is not None:
          filename = f"received_file_{int(time.time())}.pdf"  # Generate unique filename
          #print(filename)
          directory_path = "uploads/"+ websocket.user
          filepath = os.path.join(directory_path, filename) 
          os.makedirs(directory_path,exist_ok=True)
          #print(filename)
          with open(filepath, "wb") as f:
            f.write(data)  
            print(f'File saved successfully: {filepath}')
            utils.create_vector_db(directory_path,websocket.user)
            await websocket.close()
            connected_clients.remove(websocket)

      
  except WebSocketDisconnect:
    print("websocket disconnected")
    logger.info("This is an info message")
    await websocket.close()
    connected_clients.remove(websocket)



if __name__ == "__main__":
  import uvicorn
  uvicorn.run("main:app", host="127.0.0.1", port=4000 ,reload=True)