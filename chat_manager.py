import json
import os
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path

class ChatManager:
    """Manages chat conversations with persistence."""
    
    def __init__(self, storage_dir: str = "data/chat_history"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
    
    def create_conversation(self, title: str = None) -> str:
        """Create a new conversation."""
        conversation_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        if not title:
            title = f"Chat {datetime.now().strftime('%B %d at %I:%M %p')}"
        
        conversation_data = {
            "id": conversation_id,
            "title": title,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "messages": []
        }
        
        self.save_conversation(conversation_id, conversation_data)
        return conversation_id
    
    def save_conversation(self, conversation_id: str, conversation_data: Dict):
        """Save conversation to file."""
        file_path = self.storage_dir / f"{conversation_id}.json"
        conversation_data["updated_at"] = datetime.now().isoformat()
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(conversation_data, f, indent=2, ensure_ascii=False)
    
    def load_conversation(self, conversation_id: str) -> Optional[Dict]:
        """Load conversation from file."""
        file_path = self.storage_dir / f"{conversation_id}.json"
        if not file_path.exists():
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return None
    
    def get_all_conversations(self) -> List[Dict]:
        """Get list of all conversations."""
        conversations = []
        
        for file_path in self.storage_dir.glob("*.json"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    conversations.append({
                        "id": data["id"],
                        "title": data["title"],
                        "created_at": data["created_at"],
                        "updated_at": data["updated_at"],
                        "message_count": len(data.get("messages", []))
                    })
            except Exception:
                continue
        
        # Sort by updated_at (most recent first)
        conversations.sort(key=lambda x: x["updated_at"], reverse=True)
        return conversations
    
    def add_message(self, conversation_id: str, role: str, content: str, metadata: Dict = None):
        """Add a message to a conversation."""
        conversation = self.load_conversation(conversation_id)
        if not conversation:
            return False
        
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        
        conversation["messages"].append(message)
        self.save_conversation(conversation_id, conversation)
        return True
    
    def delete_conversation(self, conversation_id: str) -> bool:
        """Delete a conversation."""
        file_path = self.storage_dir / f"{conversation_id}.json"
        try:
            if file_path.exists():
                file_path.unlink()
                return True
        except Exception:
            pass
        return False
