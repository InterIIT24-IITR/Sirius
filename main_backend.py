import asyncio
import os
import re
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from agent import run_pipeline
from backend.main_backend import QueryRequest
from mongo.general.functions import add_chat_to_conversation, create_conversation
from mongo.general.schema import PyMongoConversation
from dotenv import load_dotenv

load_dotenv()

try:
    client = MongoClient(os.environ["MONGO_URI"])
    client.admin.command("ping")
    print("MongoDB connected successfully!")
except Exception as e:
    print("Failed to connect to MongoDB:", e)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def monitor_logs(websocket: WebSocket, log_path: str):
    try:
        with open(log_path, "r") as file:
            file.seek(0, 2)
            while True:
                line = file.readline()
                if line:
                    match = re.search(r"Processing tool call: (\w+)", line)
                    if match:
                        tool_name = match.group(1)
                        print(f"Sending log: {tool_name}")
                        await websocket.send_text(f"log:{tool_name}")
                else:
                    await asyncio.sleep(0.5)
    except Exception as e:
        print(f"Log monitoring error: {e}")
        await websocket.close()


async def handle_conversation(websocket: WebSocket, request: QueryRequest):
    db = client["conversationdb"]
    conversations_collection = db["conversations"]

    try:
        if not request.id or request.id.strip() == "":
            conversation_data = {
                "title": request.query[:50],
                "chats": [{"message": request.query, "role": "USER", "order": 1}],
            }
            new_conversation = PyMongoConversation.model_validate(conversation_data)
            result = create_conversation(client, new_conversation)
            inserted_conversation = conversations_collection.find_one(
                {"_id": result.inserted_id}
            )

            await websocket.send_json(
                {
                    "type": request.query,
                    "conversation": inserted_conversation,
                }
            )

            rag_response = run_pipeline(request.query)

            updated_conversation = add_chat_to_conversation(
                client, str(inserted_conversation["_id"]), rag_response, "RAG"
            )

            await websocket.send_json(
                {
                    "type": "rag_response",
                    "conversation": {
                        "id": str(updated_conversation["_id"]),
                        "title": updated_conversation["title"],
                        "chats": updated_conversation["chats"],
                    },
                }
            )

        else:
            user_conversation = add_chat_to_conversation(
                client, request.id, request.query, "USER"
            )

            rag_response = run_pipeline(request.query)

            updated_conversation = add_chat_to_conversation(
                client, request.id, rag_response, "RAG"
            )

            await websocket.send_json(
                {
                    "type": "conversation_update",
                    "conversation": {
                        "id": str(updated_conversation["_id"]),
                        "title": updated_conversation["title"],
                        "chats": updated_conversation["chats"],
                    },
                }
            )

    except Exception as e:
        print(f"Conversation handling error: {e}")
        await websocket.send_json({"type": "error", "message": str(e)})


@app.websocket("/ws/query")
async def query_websocket_handler(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            request = QueryRequest.model_validate_json(data)
            await handle_conversation(websocket, request)
    except WebSocketDisconnect:
        print("Query WebSocket disconnected")
    except Exception as e:
        print(f"Query WebSocket error: {e}")
    finally:
        await websocket.close()


@app.websocket("/ws/logs")
async def logs_websocket_handler(websocket: WebSocket):
    await websocket.accept()
    log_path = os.path.expanduser("~/swarm.log")

    try:
        await monitor_logs(websocket, log_path)
    except WebSocketDisconnect:
        print("Logs WebSocket disconnected")
    except Exception as e:
        print(f"Logs WebSocket error: {e}")
    finally:
        await websocket.close()


# Start Server
def start_server():
    uvicorn.run(app, host="localhost", port=5050)


if __name__ == "__main__":
    start_server()
