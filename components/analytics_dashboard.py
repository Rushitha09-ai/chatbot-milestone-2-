import streamlit as st
from datetime import datetime, timedelta

def render_analytics_dashboard(chat_history_service):
    """Show usage analytics"""
    st.header("📊 Analytics Dashboard")
    
    # Get all conversations
    conversations = chat_history_service.get_all_conversations()
    
    if not conversations:
        st.info("💬 No conversations yet. Start chatting to see analytics!")
        return
    
    # Calculate metrics
    total_conversations = len(conversations)
    total_messages = sum(conv['message_count'] for conv in conversations)
    avg_messages = round(total_messages / total_conversations, 1) if total_conversations > 0 else 0
    
    # Show metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Conversations", total_conversations)
    
    with col2:
        st.metric("Total Messages", total_messages)
    
    with col3:
        st.metric("Average Messages/Chat", avg_messages)
    
    # Show conversation list
    st.subheader("💬 Recent Conversations")
    for i, conv in enumerate(conversations[:10]):  # Show last 10
        with st.expander(f"📝 {conv['title']} ({conv['message_count']} messages)"):
            st.write(f"**Created:** {conv['created_at'][:19]}")
            st.write(f"**Messages:** {conv['message_count']}")
            if st.button(f"📂 Load This Conversation", key=f"load_{conv['id']}_{i}"):
                st.session_state.selected_conversation = conv['id']
                st.success(f"✅ Loaded: {conv['title']}")
                st.rerun()
