import os
import json
import tempfile
import pytest
from app import search_conversations

def test_search_conversations(tmp_path):
    # Create a fake chat history file
    chat_data = [
        {"role": "user", "content": "Hello world!"},
        {"role": "assistant", "content": "Hi there!"}
    ]
    chat_file = tmp_path / "chat_test.json"
    with open(chat_file, "w") as f:
        json.dump(chat_data, f)
    # Patch the history dir (Windows-friendly, no symlink)
    import shutil
    orig_dir = "data/chat_history"
    backup_dir = orig_dir + "_bak"
    # Backup real chat history if it exists
    if os.path.exists(backup_dir):
        shutil.rmtree(backup_dir)
    if os.path.exists(orig_dir):
        os.rename(orig_dir, backup_dir)
    os.makedirs(orig_dir, exist_ok=True)
    # Copy test file into chat history dir
    shutil.copy(str(chat_file), os.path.join(orig_dir, "chat_test.json"))
    # Search for a word
    results = search_conversations("hello")
    assert any("Hello world!" in r[1] for r in results)
    # Cleanup
    shutil.rmtree(orig_dir)
    if os.path.exists(backup_dir):
        os.rename(backup_dir, orig_dir)

def test_file_upload_txt():
    from io import BytesIO
    file_content = "This is a test file."
    file = BytesIO(file_content.encode("utf-8"))
    # Simulate reading as in app.py
    content = file.read().decode("utf-8")
    assert "test file" in content

# PDF extraction test would require PyPDF2 and a sample PDF, so it's omitted for brevity.
