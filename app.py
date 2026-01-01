import streamlit as st
import time
import os

from backend.sunbeam_agent import get_agent

# --- Page Configuration ---
st.set_page_config(
    page_title="Sunbeam AI - Redefined",
    page_icon="☀️",
    layout="wide",
    initial_sidebar_state="expanded",
)

def local_css(theme, font_size):
    if theme == "Dark":
        bg_gradient = "linear-gradient(135deg, #0A192F 0%, #0A3D62 100%)"
        text_color = "#FFFFFF"
        sidebar_bg = "rgba(10, 25, 47, 0.8)"
        card_bg = "rgba(255, 255, 255, 0.05)"
        assistant_bubble = "rgba(255, 255, 255, 0.08)"
        input_bg = "rgba(255, 255, 255, 0.05)"
        hero_bg = "rgba(255, 255, 255, 0.03)"
        border_color = "rgba(255, 255, 255, 0.1)"
        sub_text = "#A0AEC0"
    else:
        bg_gradient = "linear-gradient(135deg, #F0F2F6 0%, #E0E8F0 100%)"
        text_color = "#1E293B"
        sidebar_bg = "rgba(255, 255, 255, 0.9)"
        card_bg = "rgba(0, 0, 0, 0.03)"
        assistant_bubble = "rgba(255, 255, 255, 1)"
        input_bg = "rgba(255, 255, 255, 1)"
        hero_bg = "rgba(0, 0, 0, 0.02)"
        border_color = "rgba(0, 0, 0, 0.05)"
        sub_text = "#64748B"

    # Map font size labels to rem values
    font_size_map = {
        "Small": "0.9rem",
        "Normal": "1rem",
        "Large": "1.1rem",
        "Extra Large": "1.2rem"
    }
    base_font_size = font_size_map.get(font_size, "1rem")

    st.markdown(f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');
        
        :root {{
            --bg_gradient: {bg_gradient};
            --text-color: {text_color};
            --sub-text: {sub_text};
            --sidebar-bg: {sidebar_bg};
            --card-bg: {card_bg};
            --hero-bg: {hero_bg};
            --border-color: {border_color};
            --input-bg: {input_bg};
            --base-font-size: {base_font_size};
            --primary-accent: #F39C12;
            --secondary-accent: #E67E22;
        }}

        /* Typography & Base */
        html, body, [data-testid="stAppViewContainer"] {{
            font-family: 'Outfit', sans-serif;
            background: var(--bg_gradient) !important;
            color: var(--text-color);
            font-size: var(--base-font-size) !important;
        }}

        [data-testid="stMain"] {{ background: transparent !important; }}
        
        /* Chat Container (Main Area) */
        .block-container {{
            padding: 3rem 1rem 5rem 1rem !important;
            max-width: 1500px !important;
            width: 80% !important;
            margin: auto !important;
        }}

        /* Sidebar Styling */
        [data-testid="stSidebar"] {{
            background-color: var(--sidebar-bg) !important;
            backdrop-filter: blur(10px);
            border-right: 1px solid var(--border-color);
        }}
        
        [data-testid="stSidebar"] * {{ color: var(--text-color) !important; }}

        /* Hero Section */
        .hero-section {{
            text-align: center;
            padding: 3rem 1.5rem;
            background: var(--hero-bg);
            border-radius: 24px;
            border: 1px solid var(--border-color);
            margin-bottom: 2.5rem;
            animation: fadeIn 0.8s ease-out;
        }}
        
        .hero-section h1 {{
            font-size: 3rem !important;
            font-weight: 700 !important;
            background: linear-gradient(90deg, var(--text-color), var(--primary-accent));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 1rem !important;
        }}
        
        .hero-section p {{
            font-size: 1.15rem;
            color: var(--sub-text);
            max-width: 800px;
            margin: 10px auto !important;
            line-height: 1.6;
        }}

        /* Chat Messages (Base Style) */
        [data-testid="stChatMessage"] {{
            background: transparent !important;
            border: none !important;
            margin: 10px 0 !important;
            padding: 0 !important;
            display: flex !important;
            gap: 10px !important;
            font-size: 16px !important;
            line-height: 1.5 !important;
        }}

        /* User Message (Right Aligned) */
        [data-testid="stChatMessageUser"] {{
            justify-content: flex-end !important;
            flex-direction: row-reverse !important;
        }}

        div[data-testid="stChatMessageUser"] > div:nth-child(2) {{
            background: rgba(30, 30, 30, 0.95) !important;
            color: #E2E8F0 !important;
            max-width: 75% !important;
            padding: 8px 12px !important;
            border-radius: 10px !important;
            border: 1px solid #ddd !important;
            margin-right: 0 !important;
            margin-left: 0 !important;
            white-space: pre-wrap !important;
            box-shadow: none !important;
        }}

        /* Assistant Message (Left Aligned) */
        [data-testid="stChatMessageAssistant"] {{
            justify-content: flex-start !important;
            flex-direction: row !important;
        }}
        
        div[data-testid="stChatMessageAssistant"] > div:nth-child(2) {{
            background: transparent !important;
            color: var(--text-color) !important;
            max-width: 75% !important;
            padding: 8px 12px !important;
            border-radius: 10px !important;
            border: 1px solid #ddd !important;
            margin-left: 0 !important;
            white-space: pre-wrap !important;
            box-shadow: none !important;
        }}

        /* Action Icons */
        .chat-actions {{
            display: flex;
            gap: 1.2rem;
            margin-top: 0.8rem;
            opacity: 0.5;
            transition: opacity 0.3s;
        }}
        .chat-actions:hover {{ opacity: 1; }}
        .chat-actions i {{
            font-size: 0.9rem;
            color: var(--sub-text);
            cursor: pointer;
            transition: color 0.2s;
        }}
        .chat-actions i:hover {{ color: var(--primary-accent); }}

        /* Inputs & Buttons */
        [data-testid="stChatInput"] {{
            background: var(--input-bg) !important;
            border: 1px solid var(--border-color) !important;
            border-radius: 100px !important;
            color: var(--text-color) !important;
        }}

        .stButton>button {{
            border-radius: 12px !important;
            background-color: var(--card-bg) !important;
            color: var(--text-color) !important;
            border: 1px solid var(--border-color) !important;
            width: 100%;
        }}
        
        .stButton>button:hover {{
            border-color: #F39C12 !important;
            color: #F39C12 !important;
            background-color: rgba(243, 156, 18, 0.05) !important;
        }}

        /* Selectboxes */
        div[data-baseweb="select"] {{
            background-color: var(--card-bg) !important;
            color: var(--text-color) !important;
        }}

        /* animations */
        @keyframes fadeIn {{ from {{ opacity: 0; transform: translateY(8px); }} to {{ opacity: 1; transform: translateY(0); }} }}
        
        /* Layout Fixes */
        [data-testid="stMarkdownContainer"] p {{ color: var(--text-color); }}
        label[data-testid="stWidgetLabel"] {{ color: var(--text-color) !important; }}

        /* Tables */
        .stMarkdown table {{
            background: var(--hero-bg);
            border-radius: 12px;
            border: 1px solid var(--border-color);
            overflow: hidden;
        }}
        .stMarkdown th {{
            background: var(--card-bg) !important;
            color: #F39C12 !important;
        }}
        .stMarkdown td {{
            color: var(--text-color) !important;
        }}
        
        </style>
        
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    """, unsafe_allow_html=True)

def initialize_state():
    """Initializes all required session state variables."""
    defaults = {
        "messages": [],
        "theme": "Dark",
        "font_size": "Normal",
        "show_lead_form": False,
        "form_submitted": False
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

@st.cache_resource
def load_agent():
    return get_agent()

def get_ai_response(user_input: str):
    """Processes user input and returns AI response metadata."""
    input_lower = user_input.lower()

    # Logic to trigger lead form
    lead_keywords = ["admission", "apply", "contact", "call", "counsellor"]
    if any(k in input_lower for k in lead_keywords):
        st.session_state.show_lead_form = True

    try:
        agent = load_agent()
        
        res = agent.invoke({"input": user_input})
        
        # Check for direct 'output' key
        if "output" in res and res["output"]:
            response = res["output"]
        # Fallback: check for 'messages' list (raw chain output)
        elif "messages" in res and isinstance(res["messages"], list):
            # Get content from the last AIMessage
            last_msg = res["messages"][-1]
            if hasattr(last_msg, "content"):
                response = last_msg.content
            else:
                response = str(last_msg)
        else:
            response = str(res)
            
        source = "Sunbeam AI Agent"
    except Exception as e:
        response = f"I encountered an error: {str(e)}"
        source = "System Error"

    return response, source

# Render Custom CSS
if "theme" in st.session_state and "font_size" in st.session_state:
    local_css(st.session_state.theme, st.session_state.font_size)

def render_sidebar():
    """Renders the sidebar with branding and settings."""
    with st.sidebar:
        # Branding
        _, col_logo, _ = st.columns([1, 2, 1])
        with col_logo:
           # Updated path to assets folder
           logo_path = os.path.join(os.path.dirname(__file__), "assets", "sunbeam_logo.jpg")
           if os.path.exists(logo_path):
               st.image(logo_path, use_container_width=True)
           else:
               st.markdown("<h1 style='text-align: center;'>☀️</h1>", unsafe_allow_html=True)
        st.markdown("<h2 style='text-align: center; color: #F39C12; margin-top: -10px;'>SUNBEAM</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: var(--sub-text); font-size: 0.8rem; margin-top: -15px;'>AI-Powered Assistant</p>", unsafe_allow_html=True)
        st.divider()
        
        st.markdown("### Profile")
        st.markdown("👤 **Guest Student**")
        st.divider()

        st.markdown("### Settings")
        st.radio("Theme Mode", ["Dark", "Light"], key="theme", horizontal=True)
        st.select_slider("Text Size", options=["Small", "Normal", "Large", "Extra Large"], key="font_size")
        st.selectbox("Language", ["English (Primary)", "Hindi", "Marathi"])
        show_src = st.toggle("Show Research Sources", value=True)
        
        st.divider()
        if st.button("🗑️ Clear History", use_container_width=True):
            st.session_state.messages = []
            st.session_state.show_lead_form = False
            st.rerun()

        st.markdown("<br><br><p style='text-align: center; font-size: 0.7rem; color: var(--sub-text);'>System Ready</p>", unsafe_allow_html=True)
    return show_src

def main():
    initialize_state()
    local_css(st.session_state.theme, st.session_state.font_size)
    
    show_src = render_sidebar()

    _, col_main, _ = st.columns([1, 10, 1])
    with col_main:
        # Hero Branding
        st.markdown("""
            <div class="hero-section">
                <h1>Sunbeam Chatbot</h1>
                <p>Welcome to Sunbeam Pune — Delivering Quality Education.</p>
                <p>I’m here to help you with courses, admissions, and training.</p>
            </div>
        """, unsafe_allow_html=True)

        # Message History
        for i, msg in enumerate(st.session_state.messages):
            if msg["role"] == "user":
                with st.chat_message("user"):
                    st.write(msg["content"])
            else:
                with st.chat_message("assistant", avatar="☀️"):
                    st.markdown(msg["content"], unsafe_allow_html=True)
                    
                    st.markdown("""
                        <div class="chat-actions">
                            <i class="far fa-copy" title="Copy"></i>
                            <i class="far fa-thumbs-up" title="Like"></i>
                            <i class="far fa-thumbs-down" title="Dislike"></i>
                            <i class="far fa-share-square" title="Share"></i>
                            <i class="fas fa-sync-alt" title="Regenerate"></i>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    if show_src and "source" in msg:
                        st.markdown(f"<div style='font-size: 0.75rem; color: var(--sub-text); margin-top: 10px; font-style: italic;'>Verified Source: {msg['source']}</div>", unsafe_allow_html=True)

        # Lead Form
        if st.session_state.show_lead_form and not st.session_state.form_submitted:
            st.divider()
            with st.container():
                st.markdown("### 📞 Priority Callback Request")
                st.info("Leave your details and a counsellor will call you within 24 hours.")
                with st.form("lead_form"):
                    name = st.text_input("Name")
                    phone = st.text_input("WhatsApp Number")
                    center = st.selectbox("Preferred Center", ["Pune", "Karad", "Online"])
                    if st.form_submit_button("Submit Request"):
                        if name and phone:
                            st.session_state.form_submitted = True
                            st.session_state.show_lead_form = False
                            st.success("Request logged! We'll contact you soon.")
                            time.sleep(1.5)
                            st.rerun()
                        else:
                            st.error("Please fill required fields.")

        # Chat Input
        if prompt := st.chat_input("Ask Sunbeam AI anything..."):
            if prompt.lower() in ["exit", "quit"]:
                st.warning("Chat session ended. Refresh to start a new session.")
                st.stop()

            st.session_state.messages.append({"role": "user", "content": prompt})
            response, source = get_ai_response(prompt)
            st.session_state.messages.append({"role": "assistant", "content": response, "source": source})
            st.rerun()

    # Footer
    st.markdown("""
        <div style="text-align: center; padding: 40px; color: var(--sub-text); font-size: 0.8rem;">
            &copy; 2025 Sunbeam Institute • Empowering Digital Future • Knowledge is Power
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
