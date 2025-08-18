import pytest
from services.chat_manager import ChatManager

def test_create_and_load_conversation():
    cm = ChatManager()
    conv_id = cm.create_conversation("Test Chat")
    assert conv_id is not None
    conv = cm.load_conversation(conv_id)
    assert conv is not None
    assert conv["title"] == "Test Chat"
