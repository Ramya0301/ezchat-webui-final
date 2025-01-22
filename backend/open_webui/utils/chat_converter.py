from datetime import datetime
import uuid

def convert_timestamp(iso_string):
    """Convert ISO timestamp string to Unix timestamp"""
    dt = datetime.fromisoformat(iso_string.replace('Z', '+00:00'))
    return int(dt.timestamp())

def convert_message_format(message):
    """Convert a single message from old format to new format"""
    return {
        "id": message["messageId"],
        "parentId": message["parentMessageId"] if message["parentMessageId"] != "00000000-0000-0000-0000-000000000000" else None,
        "childrenIds": [child["messageId"] for child in message.get("children", [])],
        "role": "user" if message["isCreatedByUser"] else "assistant",
        "content": message["text"],
        "timestamp": convert_timestamp(message["createdAt"]),
        "models": [message.get("model", "default-model")]
    }

def convert_legacy_chat_format(input_data):
    """Convert the legacy chat format to the new format"""
    messages_dict = {}
    flat_messages = []
    
    def process_message_tree(message):
        """Recursively process message tree to flatten it"""
        msg_converted = convert_message_format(message)
        messages_dict[message["messageId"]] = msg_converted
        flat_messages.append(msg_converted)
        
        for child in message.get("children", []):
            process_message_tree(child)
    
    # Process the message tree starting from the root message
    process_message_tree(input_data["messages"][0])
    
    return {
        "id": str(uuid.uuid4()),
        "user_id": str(uuid.uuid4()),
        "title": input_data["title"],
        "chat": {
            "id": input_data.get("conversationId", str(uuid.uuid4())),
            "title": input_data["title"],
            "models": [input_data["options"].get("model", "default-model")],
            "params": {
                "temperature": input_data["options"].get("temperature", 0.7),
                "maxContextTokens": input_data["options"].get("maxContextTokens", 4096),
                "max_tokens": input_data["options"].get("max_tokens", 4096)
            },
            "history": {
                "messages": messages_dict,
                "currentId": flat_messages[-1]["id"] if flat_messages else None
            },
            "messages": flat_messages
        },
        "updated_at": int(datetime.utcnow().timestamp()),
        "created_at": int(datetime.utcnow().timestamp()),
        "meta": {},
        "folder_id": None
    } 