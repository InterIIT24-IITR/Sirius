import os
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import uvicorn
from pymongo import MongoClient
from dotenv import load_dotenv
from backend.main_backend import QueryRequest
from mongo.general.functions import add_chat_to_conversation, create_conversation
from mongo.general.schema import PyMongoConversation
from agent import run_pipeline

load_dotenv()

try:
    client = MongoClient(os.environ["MONGO_URI"])
    client.admin.command("ping")
    print("MongoDB connected successfully!")
except Exception as e:
    print("Failed to connect to MongoDB:", e)

app = FastAPI()


async def handle_conversation(websocket: WebSocket, request: QueryRequest):
    db = client["conversationdb"]
    conversations_collection = db["conversations"]

    try:
        if not request.id or request.id.strip() == "":
            conversation_data = {
                "title": request.query,
                "chats": [{"message": request.query, "role": "USER", "order": 1}],
            }
            new_conversation = PyMongoConversation.model_validate(conversation_data)
            result = create_conversation(client, new_conversation)
            inserted_conversation = conversations_collection.find_one(
                {"_id": result.inserted_id}
            )

            await websocket.send_json(
                {
                    "type": "request",
                    "conversation": inserted_conversation,
                }
            )

            rag_response = run_pipeline(request.query)

            updated_conversation = add_chat_to_conversation(
                client, str(inserted_conversation["_id"]), rag_response, "RAG"
            )

            await websocket.send_json(
                {
                    "type": "response",
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

            await websocket.send_json(
                {
                    "type": "conversation",
                    "conversation": {
                        "id": request.id,
                        "title": user_conversation["title"],
                        "chats": user_conversation["chats"],
                    },
                }
            )
            rag_response = run_pipeline(request.query)

            updated_conversation = add_chat_to_conversation(
                client, request.id, rag_response, "RAG"
            )

            await websocket.send_json(
                {
                    "type": "response",
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


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=5050)
