import streamlit as st
from pathlib import Path

class ThemeService:
    """Simple service for managing dark/light themes."""
    
    def __init__(self):
        self.themes_dir = Path("themes")
        self.available_themes = {
            "light": "☀️ Light Mode",
            "dark": " Dark Mode"
        }
    
    def load_theme_css(self, theme_name: str) -> str:
        """Load CSS content for a theme."""
        css_file = self.themes_dir / f"{theme_name}.css"
        if css_file.exists():
            try:
                with open(css_file, 'r', encoding='utf-8') as f:
                    return f.read()
            except Exception:
                return ""
        return ""
    
    def apply_theme(self, theme_name: str):
        """Apply a theme to the Streamlit app."""
        css_content = self.load_theme_css(theme_name)
        if css_content:
            st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)
    
    def render_theme_selector(self):
        """Render simple theme selection in sidebar."""
        with st.sidebar:
            st.header(" Theme")
            
            # Get current theme from session state
            if "current_theme" not in st.session_state:
                st.session_state.current_theme = "light"
            
            # Simple theme toggle
            theme_options = ["light", "dark"]
            theme_labels = [" Light Mode", " Dark Mode"]
            
            current_index = 0 if st.session_state.current_theme == "light" else 1
            
            selected_index = st.selectbox(
                "Choose Theme:",
                range(len(theme_options)),
                format_func=lambda x: theme_labels[x],
                index=current_index,
                key="theme_selector"
            )
            
            selected_theme = theme_options[selected_index]
            
            # Update session state if theme changed
            if selected_theme != st.session_state.current_theme:
                st.session_state.current_theme = selected_theme
                st.rerun()
            
            # Apply the current theme
            self.apply_theme(st.session_state.current_theme)
            
            return selected_theme
