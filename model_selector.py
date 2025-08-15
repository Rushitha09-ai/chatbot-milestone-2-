import streamlit as st
from services.llm_service import LLMService
from services.theme_service import ThemeService

def render_model_selector(llm_service: LLMService):
    """Render model selection and advanced settings."""
    
    # Initialize theme service
    theme_service = ThemeService()
    
    with st.sidebar:
        # Render theme selector first
        current_theme = theme_service.render_theme_selector()
        
        st.divider()  # Add separator
        
        st.header("🤖 AI Model Settings")
        
        # Get available models
        models = llm_service.get_available_models()
        
        # Model selection
        model_options = list(models.keys())
        model_names = [models[key]["name"] for key in model_options]
        
        selected_model_index = st.selectbox(
            "Choose AI Model:",
            range(len(model_options)),
            format_func=lambda x: model_names[x],
            index=0  # Default to first model (gpt-3.5-turbo)
        )
        
        selected_model = model_options[selected_model_index]
        
        # Display model info
        model_info = models[selected_model]
        st.info(f"""**{model_info['name']}**
{model_info['description']}
 Cost:  per 1K tokens
 Max tokens: {model_info['max_tokens']:,}""")
        
        # Advanced settings
        with st.expander(" Advanced Settings", expanded=False):
            # Temperature slider
            temperature = st.slider(
                "Temperature (Creativity)",
                min_value=0.0,
                max_value=2.0,
                value=0.7,
                step=0.1,
                help="Higher values make output more creative but less focused"
            )
            
            # Max tokens slider
            max_tokens = st.slider(
                "Max Response Length",
                min_value=100,
                max_value=min(2000, model_info['max_tokens']),
                value=1000,
                step=100,
                help="Maximum number of tokens in the response"
            )
            
            # System prompt
            system_prompt = st.text_area(
                "System Prompt (Optional)",
                placeholder="You are a helpful assistant...",
                help="Instructions for how the AI should behave",
                height=100
            )
        
        # Store settings in session state
        st.session_state.selected_model = selected_model
        st.session_state.temperature = temperature
        st.session_state.max_tokens = max_tokens
        st.session_state.system_prompt = system_prompt if system_prompt.strip() else None
        
        return selected_model, temperature, max_tokens, system_prompt if system_prompt.strip() else None
