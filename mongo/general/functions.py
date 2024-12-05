from typing import Literal
from bson import ObjectId
from pymongo import MongoClient

from mongo.general.schema import PyMongoConversation


def create_conversation(client: MongoClient, conversation: PyMongoConversation):
    db = client["conversationdb"]
    conversations_collection = db["conversations"]
    conversation_dict = conversation.model_dump(by_alias=True)
    return conversations_collection.insert_one(conversation_dict)


def add_chat_to_conversation(
    client: MongoClient,
    conversation_id: str,
    message: str,
    role: Literal["USER", "RAG"],
) -> dict:
    db = client["conversationdb"]
    conversations_collection = db["conversations"]

    # Find the current conversation
    conversation = conversations_collection.find_one({"_id": conversation_id})

    if not conversation:
        raise ValueError(f"Conversation with ID {conversation_id} not found")

    # Calculate the next order (last order + 1)
    current_chats = conversation.get("chats", [])
    next_order = max([chat.get("order", 0) for chat in current_chats], default=0) + 1

    # Create new chat
    new_chat = {"message": message, "role": role, "order": next_order}

    # Update the conversation with the new chat
    result = conversations_collection.update_one(
        {"_id": conversation_id}, {"$push": {"chats": new_chat}}
    )

    # Retrieve and return the updated conversation
    updated_conversation = conversations_collection.find_one({"_id": conversation_id})
    return updated_conversation
