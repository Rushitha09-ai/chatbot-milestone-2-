

"""
Main Streamlit app for the LLM Chatbot project.
Handles UI, session state, chat logic, analytics, and error handling.
"""

import streamlit as st
import logging
import json
import os
from datetime import datetime
from services.llm_service import LLMService
from services.chat_manager import ChatManager
from components.chat_sidebar import render_chat_sidebar, get_or_create_conversation
from components.model_selector import render_model_selector
from utils.helpers import sanitize_input, format_response_time
from config import Config

# Configure logging for the app
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def save_chat_history(messages):
    """
    Save the current chat session to a JSON file in data/chat_history/.
    Args:
        messages (list): List of chat messages (dicts)
    Returns:
        bool: True if saved successfully, False otherwise
    """
    if messages:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"data/chat_history/chat_{timestamp}.json"
        os.makedirs("data/chat_history", exist_ok=True)
        try:
            with open(filename, 'w') as f:
                json.dump(messages, f, indent=2, default=str)
            return True
        except Exception as e:
            logger.error(f"Failed to save chat: {e}")
            return False

def show_analytics():







    """
    Enhanced analytics: number of conversations, messages, words, tokens, cost, and charts.
    """
    import pandas as pd
    import glob
    st.header("📊 Chat Analytics")
    history_dir = "data/chat_history"
    files = []
    if os.path.exists(history_dir):
        files = [os.path.join(history_dir, f) for f in os.listdir(history_dir) if f.endswith('.json')]
    st.metric("Saved Conversations", len(files))
    # Aggregate stats
    total_messages = 0
    total_words = 0
    total_tokens = 0
    total_cost = 0.0
    model_usage = {}
    for file in files:
        try:
            with open(file, 'r') as f:
                messages = json.load(f)
            for msg in messages:
                if isinstance(msg, dict) and "content" in msg:
                    total_messages += 1
                    total_words += len(msg["content"].split())
                    if msg.get("metadata") and isinstance(msg["metadata"], dict):
                        total_tokens += int(msg["metadata"].get("tokens_used", 0) or 0)
                        total_cost += float(msg["metadata"].get("estimated_cost", 0) or 0)
                        model = msg["metadata"].get("model_used", "Unknown")
                        model_usage[model] = model_usage.get(model, 0) + 1
        except Exception as e:
            logger.error(f"Error reading {file} for analytics: {e}")
    st.metric("Total Messages", total_messages)
    st.metric("Total Words", total_words)
    st.metric("Total Tokens", total_tokens)
    st.metric("Total Cost ($)", f"{total_cost:.4f}")
    # Model usage bar chart
    if model_usage:
        st.subheader("Model Usage")
        df = pd.DataFrame(list(model_usage.items()), columns=["Model", "Messages"])
        st.bar_chart(df.set_index("Model"))
    # Recent chats
    if files:
        st.subheader("Recent Chats")
        for file in sorted(files)[-5:]:
            st.write(f"💬 {os.path.basename(file)}")
    else:
        st.info("No chat history yet")

def initialize_session_state():
    """
    Initialize Streamlit session state variables for chat, LLM, and settings.
    """
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "llm_service" not in st.session_state:
        try:
            st.session_state.llm_service = LLMService()
        except ValueError as e:
            st.error(f"Configuration Error: {e}")
            st.info("Please check your .env file and ensure all required API keys are set.")
            st.stop()
    if "chat_manager" not in st.session_state:
        st.session_state.chat_manager = ChatManager()
    if "selected_model" not in st.session_state:
        st.session_state.selected_model = "gpt-3.5-turbo"
    if "temperature" not in st.session_state:
        st.session_state.temperature = 0.7
    if "max_tokens" not in st.session_state:
        st.session_state.max_tokens = 1000
    if "system_prompt" not in st.session_state:
        st.session_state.system_prompt = None

def display_messages():
    """
    Render all chat messages in the main UI, including metadata (response time, model, tokens, cost).
    """
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if "metadata" in message and message["metadata"]:
                with st.expander(" Response Details", expanded=False):
                    metadata = message["metadata"]
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric(" Response Time", metadata.get("response_time", "N/A"))
                    with col2:
                        st.metric(" Model", metadata.get("model_used", "N/A"))
                    with col3:
                        st.metric(" Tokens Used", metadata.get("tokens_used", "N/A"))
                    with col4:
                        cost = metadata.get("estimated_cost", 0)
                        if isinstance(cost, (int, float)) and cost > 0:
                            st.metric(" Est. Cost", f"{cost}")
                        else:
                            st.metric(" Est. Cost", "N/A")

def main():
    # Sidebar: File Upload
    st.sidebar.markdown("---")
    st.sidebar.subheader("📁 Upload a File")
    uploaded_file = st.sidebar.file_uploader("Choose a .txt or .pdf file", type=["txt", "pdf"])
    uploaded_content = None
    if uploaded_file is not None:
        try:
            if uploaded_file.type == "text/plain":
                uploaded_content = uploaded_file.read().decode("utf-8")
            elif uploaded_file.type == "application/pdf":
                import io
                from PyPDF2 import PdfReader
                pdf_reader = PdfReader(io.BytesIO(uploaded_file.read()))
                uploaded_content = "\n".join(page.extract_text() or "" for page in pdf_reader.pages)
            else:
                st.sidebar.error("Unsupported file type.")
        except Exception as e:
            st.sidebar.error(f"Failed to read file: {e}")

    if uploaded_content:
        st.sidebar.markdown("**File Content Preview:**")
        st.sidebar.text_area("", uploaded_content[:2000], height=200)
        if st.sidebar.button("Send to Chat", key="send_file_to_chat"):
            # Add the uploaded content as a user message to the chat
            user_message = {"role": "user", "content": uploaded_content}
            st.session_state.messages.append(user_message)
            # Generate assistant response as if this was a prompt
            conversation_id = get_or_create_conversation(st.session_state.chat_manager)
            st.session_state.chat_manager.add_message(
                conversation_id, "user", uploaded_content
            )
            selected_model = st.session_state.selected_model if "selected_model" in st.session_state else "gpt-3.5-turbo"
            temperature = st.session_state.temperature if "temperature" in st.session_state else 0.7
            max_tokens = st.session_state.max_tokens if "max_tokens" in st.session_state else 1000
            system_prompt = st.session_state.system_prompt if "system_prompt" in st.session_state else None
            with st.chat_message("assistant"):
                models = st.session_state.llm_service.get_available_models()
                with st.spinner(f" {models[selected_model]['name']} is thinking..."):
                    try:
                        result = st.session_state.llm_service.send_message(
                            uploaded_content,
                            model=selected_model,
                            temperature=temperature,
                            max_tokens=max_tokens,
                            system_prompt=system_prompt
                        )
                        if result["success"]:
                            response = result["response"]
                            st.markdown(response)
                            metadata = {
                                "response_time": format_response_time(result["response_time"]),
                                "model_used": result.get("model_used", "Unknown"),
                                "tokens_used": result.get("tokens_used", "Unknown"),
                                "estimated_cost": result.get("estimated_cost", 0),
                                "temperature": temperature,
                                "max_tokens": max_tokens,
                                "system_prompt_used": bool(system_prompt)
                            }
                            assistant_message = {
                                "role": "assistant",
                                "content": response,
                                "metadata": metadata
                            }
                            st.session_state.messages.append(assistant_message)
                            st.session_state.chat_manager.add_message(
                                conversation_id, "assistant", response, metadata
                            )
                        else:
                            error_msg = result["error"]
                            st.error(f"❗ Error: {error_msg}")
                            error_message = {
                                "role": "assistant",
                                "content": f"I apologize, but I encountered an error: {error_msg}",
                                "metadata": None
                            }
                            st.session_state.messages.append(error_message)
                            st.session_state.chat_manager.add_message(
                                conversation_id, "assistant", error_message["content"]
                            )
                    except Exception as e:
                        logger.error(f"Unexpected error in file upload chat loop: {e}")
                        st.error(f"❗ An unexpected error occurred. Please try again.\nError: {e}")
            st.rerun()  # Refresh to show the new messages in chat

    # Sidebar: Search across conversations
    search_query = st.sidebar.text_input("🔍 Search Conversations", "")
    if search_query:
        st.sidebar.markdown("---")
        st.sidebar.write(f"**Results for:** `{search_query}`")
        matches = search_conversations(search_query)
        if matches:
            for fname, content, role, idx in matches[:10]:
                st.sidebar.write(f"**{role.title()}** in `{fname}`:")
                st.sidebar.caption(content)
        else:
            st.sidebar.info("No matches found.")
    """
    Main entry point for the Streamlit chatbot app.
    Handles UI layout, chat logic, error handling, and sidebar features.
    """
    st.set_page_config(
        page_title=Config.APP_TITLE + " - Enhanced",
        page_icon="",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    try:
        st.title(" " + Config.APP_TITLE + " - Enhanced")
        st.markdown("**Milestone 2**: Multi-model AI chat with conversation management!")

        # Sidebar: Save and Analytics
        if st.sidebar.button("💾 Save Current Chat"):
            # Save chat history to file
            if "messages" in st.session_state and st.session_state.messages:
                if save_chat_history(st.session_state.messages):
                    st.sidebar.success("Chat saved!")
                else:
                    st.sidebar.error("Save failed")
        if st.sidebar.button("📊 Show Analytics"):
            show_analytics()

        # Initialize session state for chat, LLM, and settings
        initialize_session_state()

        # Render chat sidebar (conversations, new chat, etc.)
        render_chat_sidebar(st.session_state.chat_manager)

        # Render model selector and get current settings
        selected_model, temperature, max_tokens, system_prompt = render_model_selector(st.session_state.llm_service)

        # Get or create current conversation
        conversation_id = get_or_create_conversation(st.session_state.chat_manager)

        # Display current conversation and model info
        if conversation_id:
            conversation = st.session_state.chat_manager.load_conversation(conversation_id)
            if conversation:
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.caption(f" **{conversation['title']}** | Messages: {len(st.session_state.messages)}")
                with col2:
                    models = st.session_state.llm_service.get_available_models()
                    model_name = models[selected_model]["name"]
                    st.caption(f" Using: **{model_name}**")

        # Display existing messages in the chat window
        display_messages()

        # Chat input box for user prompt
        if prompt := st.chat_input("What would you like to know?"):
            sanitized_prompt = sanitize_input(prompt)
            if not sanitized_prompt:
                st.error("❗ Please enter a valid message. Empty or invalid input is not allowed.")
                return
            # Show estimated cost before sending
            estimated_cost = st.session_state.llm_service.estimate_cost(sanitized_prompt, selected_model)
            if estimated_cost > 0:
                st.info(f"💸 Estimated cost: {estimated_cost}")
            # Add user message to chat history
            user_message = {"role": "user", "content": sanitized_prompt}
            st.session_state.messages.append(user_message)
            st.session_state.chat_manager.add_message(
                conversation_id, "user", sanitized_prompt
            )
            # Display user message
            with st.chat_message("user"):
                st.markdown(sanitized_prompt)
            # Generate assistant response with selected model and settings
            with st.chat_message("assistant"):
                models = st.session_state.llm_service.get_available_models()
                with st.spinner(f" {models[selected_model]['name']} is thinking..."):
                    try:
                        result = st.session_state.llm_service.send_message(
                            sanitized_prompt,
                            model=selected_model,
                            temperature=temperature,
                            max_tokens=max_tokens,
                            system_prompt=system_prompt
                        )
                        if result["success"]:
                            response = result["response"]
                            st.markdown(response)
                            # Create enhanced response metadata
                            metadata = {
                                "response_time": format_response_time(result["response_time"]),
                                "model_used": result.get("model_used", "Unknown"),
                                "tokens_used": result.get("tokens_used", "Unknown"),
                                "estimated_cost": result.get("estimated_cost", 0),
                                "temperature": temperature,
                                "max_tokens": max_tokens,
                                "system_prompt_used": bool(system_prompt)
                            }
                            # Add assistant message to chat history
                            assistant_message = {
                                "role": "assistant",
                                "content": response,
                                "metadata": metadata
                            }
                            st.session_state.messages.append(assistant_message)
                            st.session_state.chat_manager.add_message(
                                conversation_id, "assistant", response, metadata
                            )
                            cost_info = f" | Cost: {metadata['estimated_cost']}" if metadata['estimated_cost'] > 0 else ""
                            st.success(f"✅ {models[selected_model]['name']} responded in {metadata['response_time']}{cost_info}")
                        else:
                            error_msg = result["error"]
                            # Friendly error banners for common API errors
                            if "insufficient_quota" in str(error_msg) or "quota" in str(error_msg):
                                st.error("🚫 You have exceeded your OpenAI quota. Please check your billing and try again. [OpenAI Billing](https://platform.openai.com/account/billing/overview)")
                            elif "Invalid API key" in str(error_msg):
                                st.error("🔑 Invalid API key. Please check your .env file and restart the app.")
                            elif "Rate limit" in str(error_msg):
                                st.warning("⏳ Rate limit reached. Please wait a moment and try again.")
                            else:
                                st.error(f"❗ Error: {error_msg}")
                            # Add error message to chat history
                            error_message = {
                                "role": "assistant",
                                "content": f"I apologize, but I encountered an error: {error_msg}",
                                "metadata": None
                            }
                            st.session_state.messages.append(error_message)
                            st.session_state.chat_manager.add_message(
                                conversation_id, "assistant", error_message["content"]
                            )
                    except Exception as e:
                        logger.error(f"Unexpected error in main chat loop: {e}")
                        st.error(f"❗ An unexpected error occurred. Please try again.\nError: {e}")
    except Exception as e:
        st.error(f"A fatal error occurred during app execution: {e}")


# --- SEARCH FUNCTIONALITY ---
def search_conversations(query: str):
    """
    Search all saved chat history files for messages containing the query string.
    Returns a list of (filename, message, role, idx) tuples for matches.
    """
    import glob
    results = []
    history_dir = "data/chat_history"
    # Search saved chat history files
    if os.path.exists(history_dir):
        for file in glob.glob(os.path.join(history_dir, '*.json')):
            try:
                with open(file, 'r') as f:
                    messages = json.load(f)
                for idx, msg in enumerate(messages):
                    if isinstance(msg, dict) and "content" in msg:
                        if query.lower() in msg.get("content", "").lower():
                            results.append((os.path.basename(file), msg["content"], msg.get("role", "unknown"), idx))
            except Exception as e:
                logger.error(f"Error searching {file}: {e}")
    # Also search current session's unsaved messages
    if "messages" in st.session_state:
        for idx, msg in enumerate(st.session_state.messages):
            if isinstance(msg, dict) and "content" in msg:
                if query.lower() in msg.get("content", "").lower():
                    results.append(("(Current Session)", msg["content"], msg.get("role", "unknown"), idx))
    return results

if __name__ == "__main__":
    main()