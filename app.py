import streamlit as st
import logging
from services.llm_service import LLMService
from utils.helpers import sanitize_input, format_response_time
from config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title=Config.APP_TITLE,
    page_icon="",
    layout="wide"
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

def display_messages():
    """Display chat message history."""
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if "metadata" in message and message["metadata"]:
                with st.expander("Response Details", expanded=False):
                    metadata = message["metadata"]
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Response Time", metadata.get("response_time", "N/A"))
                    with col2:
                        st.metric("Model", metadata.get("model_used", "N/A"))
                    with col3:
                        st.metric("Tokens Used", metadata.get("tokens_used", "N/A"))

def main():
    """Main application function."""
    st.title(" " + Config.APP_TITLE)
    st.markdown("Welcome to your personal AI assistant! Ask me anything.")
    
    # Initialize session state
    initialize_session_state()
    
    # Display existing messages
    display_messages()
    
    # Chat input
    if prompt := st.chat_input("What would you like to know?"):
        # Sanitize input
        sanitized_prompt = sanitize_input(prompt)
        
        if not sanitized_prompt:
            st.error("Please enter a valid message.")
            return
        
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": sanitized_prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(sanitized_prompt)
        
        # Generate assistant response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    result = st.session_state.llm_service.send_message(sanitized_prompt)
                    
                    if result["success"]:
                        response = result["response"]
                        st.markdown(response)
                        
                        # Add assistant message to chat history with metadata
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": response,
                            "metadata": {
                                "response_time": format_response_time(result["response_time"]),
                                "model_used": result.get("model_used", "Unknown"),
                                "tokens_used": result.get("tokens_used", "Unknown")
                            }
                        })
                        
                        # Show success message
                        st.success(f"Response generated in {format_response_time(result['response_time'])}")
                        
                    else:
                        error_msg = result["error"]
                        st.error(f"Error: {error_msg}")
                        
                        # Add error message to chat history
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": f"I apologize, but I encountered an error: {error_msg}",
                            "metadata": None
                        })
                        
                except Exception as e:
                    logger.error(f"Unexpected error in main chat loop: {e}")
                    st.error("An unexpected error occurred. Please try again.")
    
    # Sidebar with controls
    with st.sidebar:
        st.header("Chat Controls")
        
        if st.button("Clear Chat History", type="secondary"):
            st.session_state.messages = []
            st.rerun()
        
        if st.button("Test API Connection", type="secondary"):
            with st.spinner("Testing connection..."):
                try:
                    result = st.session_state.llm_service.test_connection()
                    if result["success"]:
                        st.success(" API connection successful!")
                    else:
                        st.error(f" API connection failed: {result['error']}")
                except Exception as e:
                    st.error(f" Connection test failed: {e}")
        
        # Display configuration info
        st.header("Configuration")
        st.info(f"Max message length: {Config.MAX_MESSAGE_LENGTH}")
        st.info(f"API timeout: {Config.API_TIMEOUT}s")
        st.info(f"Max retries: {Config.MAX_RETRIES}")

if __name__ == "__main__":
    main()
