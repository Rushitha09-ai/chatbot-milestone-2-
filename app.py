import streamlit as st
import logging
from services.llm_service import LLMService
from services.chat_manager import ChatManager
from components.chat_sidebar import render_chat_sidebar, get_or_create_conversation
from components.model_selector import render_model_selector
from utils.helpers import sanitize_input, format_response_time
from config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title=Config.APP_TITLE + " - Enhanced",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

def initialize_session_state():
    """Initialize Streamlit session state variables."""
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
    
    # Initialize model settings with defaults
    if "selected_model" not in st.session_state:
        st.session_state.selected_model = "gpt-3.5-turbo"
    if "temperature" not in st.session_state:
        st.session_state.temperature = 0.7
    if "max_tokens" not in st.session_state:
        st.session_state.max_tokens = 1000
    if "system_prompt" not in st.session_state:
        st.session_state.system_prompt = None

def display_messages():
    """Display chat message history with enhanced metadata."""
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
                            st.metric(" Est. Cost", f"")
                        else:
                            st.metric(" Est. Cost", "N/A")

def main():
    """Enhanced main application function with multi-model support."""
    st.title(" " + Config.APP_TITLE + " - Enhanced")
    st.markdown("**Milestone 2**: Multi-model AI chat with conversation management!")
    
    # Initialize session state
    initialize_session_state()
    
    # Render chat sidebar
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
    
    # Display existing messages
    display_messages()
    
    # Chat input
    if prompt := st.chat_input("What would you like to know?"):
        # Sanitize input
        sanitized_prompt = sanitize_input(prompt)
        
        if not sanitized_prompt:
            st.error("Please enter a valid message.")
            return
        
        # Show cost estimation before sending
        estimated_cost = st.session_state.llm_service.estimate_cost(sanitized_prompt, selected_model)
        if estimated_cost > 0:
            st.info(f" Estimated cost: ")
        
        # Add user message to chat history
        user_message = {"role": "user", "content": sanitized_prompt}
        st.session_state.messages.append(user_message)
        
        # Save user message to conversation
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
                        
                        # Save assistant message to conversation
                        st.session_state.chat_manager.add_message(
                            conversation_id, "assistant", response, metadata
                        )
                        
                        # Show enhanced success message
                        cost_info = f" | Cost: " if metadata['estimated_cost'] > 0 else ""
                        st.success(f" {models[selected_model]['name']} responded in {metadata['response_time']}{cost_info}")
                        
                    else:
                        error_msg = result["error"]
                        st.error(f" Error: {error_msg}")
                        
                        # Add error message to chat history
                        error_message = {
                            "role": "assistant",
                            "content": f"I apologize, but I encountered an error: {error_msg}",
                            "metadata": None
                        }
                        st.session_state.messages.append(error_message)
                        
                        # Save error to conversation
                        st.session_state.chat_manager.add_message(
                            conversation_id, "assistant", error_message["content"]
                        )
                        
                except Exception as e:
                    logger.error(f"Unexpected error in main chat loop: {e}")
                    st.error(" An unexpected error occurred. Please try again.")

if __name__ == "__main__":
    main()
