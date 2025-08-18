import json
import os
from datetime import datetime
import uuid

class ChatHistoryService:
    def __init__(self):
        self.history_dir = "data/chat_history"
        os.makedirs(self.history_dir, exist_ok=True)
    
    def save_conversation(self, conversation_id, messages, title="Chat"):
        """Save conversation to JSON file"""
        conversation_data = {
            'id': conversation_id,
            'title': title,
            'created_at': datetime.now().isoformat(),
            'messages': messages
        }
        
        file_path = os.path.join(self.history_dir, f"{conversation_id}.json")
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(conversation_data, f, indent=2, default=str)
            print(f"✅ Saved conversation: {title}")
        except Exception as e:
            print(f"❌ Error saving conversation: {e}")
    
    def load_conversation(self, conversation_id):
        """Load conversation from JSON file"""
        file_path = os.path.join(self.history_dir, f"{conversation_id}.json")
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"❌ Error loading conversation: {e}")
        return None
    
    def get_all_conversations(self):
        """Get list of all saved conversations"""
        conversations = []
        if os.path.exists(self.history_dir):
            for filename in os.listdir(self.history_dir):
                if filename.endswith('.json'):
                    conv_id = filename[:-5]  # Remove .json
                    conv = self.load_conversation(conv_id)
                    if conv:
                        conversations.append({
                            'id': conv_id,
                            'title': conv.get('title', 'Untitled'),
                            'created_at': conv.get('created_at', ''),
                            'message_count': len(conv.get('messages', []))
                        })
        return sorted(conversations, key=lambda x: x['created_at'], reverse=True)
    
    def search_conversations(self, query):
        """Search for messages containing query"""
        results = []
        conversations = self.get_all_conversations()
        
        for conv in conversations:
            conv_data = self.load_conversation(conv['id'])
            if conv_data:
                for i, message in enumerate(conv_data.get('messages', [])):
                    content = message.get('content', '')
                    if query.lower() in content.lower():
                        results.append({
                            'conversation_id': conv['id'],
                            'conversation_title': conv['title'],
                            'message': message,
                            'snippet': content[:200] + '...' if len(content) > 200 else content
                        })
        return results
