import streamlit as st
import pandas as pd
import json

def render_file_upload(llm_service):
    """Handle file uploads and analysis"""
    st.header("📁 File Upload & Analysis")
    
    uploaded_file = st.file_uploader(
        "Upload a file for AI analysis",
        type=['txt', 'csv', 'json'],
        help="Upload text, CSV, or JSON files"
    )
    
    if uploaded_file is not None:
        st.success(f"✅ File uploaded: {uploaded_file.name}")
        
        # Show file details
        col1, col2 = st.columns(2)
        with col1:
            st.metric("File Size", f"{uploaded_file.size:,} bytes")
        with col2:
            st.metric("File Type", uploaded_file.type)
        
        # Process file based on type
        if uploaded_file.type == "text/plain":
            content = str(uploaded_file.read(), "utf-8")
            st.text_area("File Content:", content[:500] + "..." if len(content) > 500 else content, height=200)
            
            if st.button("🤖 Analyze with AI"):
                analyze_text_with_ai(content, llm_service)
        
        elif uploaded_file.type == "text/csv":
            df = pd.read_csv(uploaded_file)
            st.subheader("📊 CSV Preview")
            st.dataframe(df.head())
            
            st.write(f"**Rows:** {len(df)}, **Columns:** {len(df.columns)}")
            st.write(f"**Columns:** {', '.join(df.columns)}")
            
            if st.button("🤖 Analyze CSV with AI"):
                analyze_csv_with_ai(df, llm_service)
        
        elif uploaded_file.type == "application/json":
            content = json.load(uploaded_file)
            st.json(content)
            
            if st.button("🤖 Analyze JSON with AI"):
                analyze_json_with_ai(content, llm_service)

def analyze_text_with_ai(content, llm_service):
    """Analyze text content with AI"""
    prompt = f"""
    Please analyze this text content:
    
    {content[:1000]}...
    
    Provide insights about:
    1. Main topics
    2. Key information
    3. Summary
    """
    
    with st.spinner("Analyzing with AI..."):
        response = llm_service.generate_response([{"role": "user", "content": prompt}])
        st.subheader("🤖 AI Analysis Result")
        st.markdown(response)

def analyze_csv_with_ai(df, llm_service):
    """Analyze CSV data with AI"""
    prompt = f"""
    Please analyze this CSV dataset:
    
    - Rows: {len(df)}
    - Columns: {len(df.columns)}
    - Column names: {list(df.columns)}
    
    Sample data:
    {df.head().to_string()}
    
    Provide insights about the data structure and potential analyses.
    """
    
    with st.spinner("Analyzing with AI..."):
        response = llm_service.generate_response([{"role": "user", "content": prompt}])
        st.subheader("🤖 AI Analysis Result")
        st.markdown(response)

def analyze_json_with_ai(content, llm_service):
    """Analyze JSON content with AI"""
    prompt = f"""
    Please analyze this JSON data:
    
    {str(content)[:1000]}...
    
    Provide insights about the data structure and contents.
    """
    
    with st.spinner("Analyzing with AI..."):
        response = llm_service.generate_response([{"role": "user", "content": prompt}])
        st.subheader("🤖 AI Analysis Result")
        st.markdown(response)
