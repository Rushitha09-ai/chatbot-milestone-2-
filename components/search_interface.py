import streamlit as st

def render_search_interface(chat_history_service):
    """Search through conversations"""
    st.header("🔍 Search Conversations")
    
    search_query = st.text_input("Search for messages:", placeholder="Enter keywords...")
    
    if search_query:
        with st.spinner("Searching..."):
            results = chat_history_service.search_conversations(search_query)
        
        if results:
            st.success(f"Found {len(results)} results")
            for i, result in enumerate(results):
                with st.expander(f"Result {i+1}: {result['snippet'][:50]}..."):
                    st.write(f"**Conversation:** {result['conversation_title']}")
                    st.write(f"**Role:** {result['message']['role'].title()}")
                    st.write(f"**Message:** {result['snippet']}")
                    if st.button(f"📂 Open Chat", key=f"open_{i}"):
                        st.session_state.selected_conversation = result['conversation_id']
                        st.success("✅ Conversation loaded!")
                        st.rerun()
        else:
            st.warning("No results found.")
