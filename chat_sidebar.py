import streamlit as st
from services.chat_manager import ChatManager

def render_chat_sidebar(chat_manager: ChatManager):
    """Render the chat sidebar with conversation management."""
    
    with st.sidebar:
        st.header(" Conversations")
        
        # New conversation button
        if st.button(" New Chat", use_container_width=True, type="primary"):
            new_id = chat_manager.create_conversation()
            st.session_state.current_conversation_id = new_id
            st.session_state.messages = []
            st.rerun()
        
        # Get all conversations
        conversations = chat_manager.get_all_conversations()
        
        # Display conversations
        if conversations:
            st.subheader("Recent Chats")
            
            for conv in conversations[:10]:  # Show last 10
                # Create container for each conversation
                with st.container():
                    col1, col2 = st.columns([4, 1])
                    
                    with col1:
                        # Conversation button
                        title_display = conv['title'][:25] + "..." if len(conv['title']) > 25 else conv['title']
                        if st.button(
                            title_display,
                            key=f"conv_{conv['id']}",
                            help=f"Messages: {conv['message_count']} | {conv['updated_at'][:10]}",
                            use_container_width=True
                        ):
                            # Load selected conversation
                            conversation_data = chat_manager.load_conversation(conv['id'])
                            if conversation_data:
                                st.session_state.current_conversation_id = conv['id']
                                st.session_state.messages = conversation_data.get('messages', [])
                                st.rerun()
                    
                    with col2:
                        # Delete button
                        if st.button("", key=f"del_{conv['id']}", help="Delete"):
                            if chat_manager.delete_conversation(conv['id']):
                                if st.session_state.get('current_conversation_id') == conv['id']:
                                    st.session_state.current_conversation_id = None
                                    st.session_state.messages = []
                                st.rerun()
        else:
            st.info("No conversations yet. Start a new chat!")

def get_or_create_conversation(chat_manager: ChatManager) -> str:
    """Get current conversation ID or create a new one."""
    if 'current_conversation_id' not in st.session_state or not st.session_state.current_conversation_id:
        conversation_id = chat_manager.create_conversation()
        st.session_state.current_conversation_id = conversation_id
        return conversation_id
    
    return st.session_state.current_conversation_id
