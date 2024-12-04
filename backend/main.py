from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from func_tracker import FunctionTracker
import pymongo
from pymongo.mongo_client import MongoClient
import datetime
import time

app = FastAPI()
query = None
# uri = ""
# client = MongoClient(uri)
# db = client["chat_database"]
# session_db = db["session"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

##example

async def pipeline(prompt,ws):
    await ws.send_json({"message" : pipeline.__name__, })
    time.sleep(1)
    return "hello world"

@app.websocket("/ws/query")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    
    FunctionTracker.set_websocket(websocket)
    
    try:
        query = await websocket.receive_text()
        prompt = ""
        # all_chats = session_db.find().sort("timestamp", pymongo.ASCENDING)
        # for chat in all_chats:
        #     prompt += "user: " + chat["user_message"] + "\n"
        #     prompt += "chatbot: " + chat["chatbot_response"] + "\n"

        # prompt = prompt + query + "\n"
        # try:
        #     response = await pipeline(prompt)
        #     document = {
        #     "user_message": query,
        #     "chatbot_response": response,
        #     "timestamp": datetime.utcnow(),
        #     }
        #     session_db.insert_one(document)
        response = await pipeline(prompt, websocket)
        await websocket.send_json({"status": "completed", "result": response})
        #except Exception as e:
        #await websocket.send_json({"Error": {str(e)}})
    
    finally:
        await websocket.close()


        
@app.get("/converstaion")
def get_converstaion():
    all_chats = session_db.find().sort("timestamp", pymongo.ASCENDING)
    messages = []
    for chat in all_chats:
        messages.append({
            'userText' : chat['user_message'],
            'responseText' : chat['chatbot_response'],
            'timestamp' : chat['timestamp']
        })
    return ({'messages': messages})



if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8100)
    