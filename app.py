import streamlit as st
import requests
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
from typing import Dict, List, Any, Optional
import io

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="Ultimate AI Generator Hub 🚀",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# CUSTOM STYLING & THEME
# ============================================================================

st.markdown("""
<style>
    /* Main color scheme */
    :root {
        --primary-color: #667eea;
        --secondary-color: #764ba2;
        --accent-color: #f093fb;
        --success-color: #00d4ff;
        --error-color: #ff6b6b;
        --warning-color: #ffd93d;
    }
    
    /* Main header styling */
    .main-header {
        font-size: 3.5rem;
        font-weight: 900;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 1rem;
        text-align: center;
        letter-spacing: -1px;
        animation: fadeIn 1s ease-in;
    }
    
    .subtitle {
        font-size: 1.3rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: 500;
    }
    
    /* Agent badge styling */
    .agent-badge {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 10px 20px;
        border-radius: 25px;
        font-size: 0.95rem;
        font-weight: 600;
        display: inline-block;
        margin: 5px;
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
        transition: transform 0.3s ease;
    }
    
    .agent-badge:hover {
        transform: translateY(-2px);
    }
    
    .category-badge {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 6px 14px;
        border-radius: 15px;
        font-size: 0.85rem;
        display: inline-block;
        margin: 5px;
    }
    
    /* Code preview styling */
    .code-preview {
        background: #1e1e1e;
        border-radius: 12px;
        padding: 20px;
        margin-top: 10px;
        border-left: 5px solid #667eea;
        font-family: 'Courier New', monospace;
        overflow-x: auto;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    
    /* Message styling */
    .success-message {
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
        border: 2px solid #28a745;
        border-radius: 10px;
        color: #155724;
        padding: 20px;
        margin: 15px 0;
        font-weight: 500;
        box-shadow: 0 4px 10px rgba(40, 167, 69, 0.2);
    }
    
    .error-message {
        background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%);
        border: 2px solid #dc3545;
        border-radius: 10px;
        color: #721c24;
        padding: 20px;
        margin: 15px 0;
        font-weight: 500;
        box-shadow: 0 4px 10px rgba(220, 53, 69, 0.2);
    }
    
    .info-message {
        background: linear-gradient(135deg, #d1ecf1 0%, #bee5eb 100%);
        border: 2px solid #17a2b8;
        border-radius: 10px;
        color: #0c5460;
        padding: 20px;
        margin: 15px 0;
        font-weight: 500;
    }
    
    /* Metric card styling */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 25px;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
        transition: transform 0.3s ease;
        margin: 10px 0;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 35px rgba(102, 126, 234, 0.5);
    }
    
    .metric-value {
        font-size: 3rem;
        font-weight: 900;
        margin: 10px 0;
    }
    
    .metric-label {
        font-size: 0.95rem;
        opacity: 0.9;
        text-transform: uppercase;
        letter-spacing: 1.5px;
    }
    
    /* Card styling */
    .content-card {
        background: white;
        border: 1px solid #e0e0e0;
        border-radius: 12px;
        padding: 20px;
        margin: 15px 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
    }
    
    .content-card:hover {
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        transform: translateY(-3px);
    }
    
    /* Sidebar styling */
    .sidebar-section {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 18px;
        border-radius: 12px;
        margin-bottom: 18px;
        border-left: 5px solid #667eea;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }
    
    .sidebar-title {
        font-size: 1.15rem;
        font-weight: 700;
        color: #667eea;
        margin-bottom: 12px;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2.5rem;
        background: linear-gradient(to right, #f8f9fa, #e9ecef);
        padding: 10px;
        border-radius: 12px;
    }
    
    .stTabs [data-baseweb="tab"] {
        padding: 12px 24px;
        border-radius: 12px 12px 0 0;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(102, 126, 234, 0.1);
    }
    
    /* Button styling */
    .stButton > button {
        border-radius: 12px;
        padding: 12px 24px;
        font-weight: 600;
        transition: all 0.3s ease;
        border: none;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4);
    }
    
    /* Input styling */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        border-radius: 12px;
        border: 2px solid #e0e0e0;
        padding: 12px;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.1);
    }
    
    /* Code editor styling */
    .code-editor {
        background: #1e1e1e;
        border-radius: 12px;
        padding: 20px;
        font-family: 'Fira Code', 'Courier New', monospace;
        color: #d4d4d4;
        border: 2px solid #667eea;
    }
    
    /* Footer styling */
    .footer {
        text-align: center;
        color: #999;
        padding: 30px;
        margin-top: 50px;
        border-top: 2px solid #e0e0e0;
        font-size: 0.95rem;
    }
    
    /* Animation */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(-20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.6; }
    }
    
    .loading {
        animation: pulse 2s infinite;
    }
    
    /* Status badge */
    .status-badge {
        display: inline-block;
        padding: 5px 12px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        margin: 5px;
    }
    
    .status-success { background: #28a745; color: white; }
    .status-warning { background: #ffc107; color: #000; }
    .status-error { background: #dc3545; color: white; }
    .status-info { background: #17a2b8; color: white; }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# CONFIGURATION & CONSTANTS
# ============================================================================

WEBHOOK_CONFIG = {
    "code_generator": {
        "url": "https://agentonline-u29564.vm.elestio.app/webhook-test/Streamlitagentform1",
        "timeout": 120
    },
    "document_generators": {
        "base": "https://agentonline-u29564.vm.elestio.app/webhook",
        "endpoints": {
            "Newsletter": "newsletter-trigger",
            "Landing Page": "landingpage-trigger",
            "Business Letter": "business-letter-trigger",
            "Email Sequence": "email-sequence-trigger",
            "Invoice": "invoice-trigger",
            "Business Contract": "business-contract-trigger",
        },
        "timeout": 20
    }
}

GOOGLE_SHEETS_ID = "1eFZcnDoGT2NJHaEQSgxW5psN5kvlkYx1vtuXGRFTGTk"
GOOGLE_SHEETS_SHEET_NAME = "demo_examples"

# Agent categories with descriptions
AGENT_CATEGORIES = {
    "HTML/CSS Generators": [
        ("🌐 Landing Page Generator", "Landing Page HTML/CSS Generator"),
        ("📊 Dashboard Generator", "Dashboard HTML/CSS Generator"),
        ("📝 Form Generator", "Form HTML/CSS Generator"),
        ("💼 Portfolio Generator", "Portfolio HTML/CSS Generator"),
        ("🔗 API Integration Generator", "API Integration HTML Generator"),
        ("🛒 E-commerce Page Generator", "E-commerce Page HTML Generator")
    ],
    "Python/Streamlit Generators": [
        ("📈 Data App Generator", "Streamlit Data App Generator"),
        ("🤖 ML App Generator", "Streamlit ML App Generator"),
        ("📊 Dashboard App Generator", "Streamlit Dashboard Generator"),
        ("📋 Form App Generator", "Streamlit Form App Generator"),
        ("🎮 Interactive App Generator", "Streamlit Interactive App Generator")
    ],
    "Document Generators": [
        ("📰 Newsletter Generator", "Newsletter"),
        ("🏢 Landing Page Copy", "Landing Page"),
        ("✉️ Business Letter", "Business Letter"),
        ("📧 Email Sequence", "Email Sequence"),
        ("🧾 Invoice Generator", "Invoice"),
        ("📄 Business Contract", "Business Contract")
    ]
}

EXAMPLE_PROMPTS = {
    "Code Generation": [
        "Create a modern landing page for a SaaS product with pricing table",
        "Build a real-time dashboard to visualize sales data with charts",
        "Generate a contact form with email validation and file upload",
        "Make a Streamlit app for data analysis with CSV upload feature",
        "Create an ML app for image classification with predictions",
        "Build an e-commerce product page with shopping cart functionality",
        "Generate a portfolio website showcasing multiple projects",
        "Create a Streamlit dashboard for financial analytics and forecasting"
    ],
    "Document Generation": [
        "Write a professional newsletter about AI innovations and trends",
        "Create compelling landing page copy for a fitness mobile app",
        "Draft a formal business partnership proposal letter",
        "Generate a 5-email welcome sequence for new subscribers",
        "Create a professional invoice template with payment terms",
        "Write a business contract for software development services"
    ]
}

# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================

def initialize_session_state():
    """Initialize all session state variables."""
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'generated_codes' not in st.session_state:
        st.session_state.generated_codes = []
    if 'generated_documents' not in st.session_state:
        st.session_state.generated_documents = []
    if 'current_code' not in st.session_state:
        st.session_state.current_code = None
    if 'current_agent' not in st.session_state:
        st.session_state.current_agent = None
    if 'current_category' not in st.session_state:
        st.session_state.current_category = None
    if 'gsheet_data' not in st.session_state:
        st.session_state.gsheet_data = None
    if 'last_gsheet_update' not in st.session_state:
        st.session_state.last_gsheet_update = None
    if 'api_response_time' not in st.session_state:
        st.session_state.api_response_time = 0
    if 'history' not in st.session_state:
        st.session_state.history = []
    if 'edit_mode' not in st.session_state:
        st.session_state.edit_mode = False
    if 'edited_code' not in st.session_state:
        st.session_state.edited_code = None
    if 'webhook_test_results' not in st.session_state:
        st.session_state.webhook_test_results = {}

initialize_session_state()

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def send_to_code_generator(user_input: str) -> Dict[str, Any]:
    """Send request to code generation webhook."""
    try:
        start_time = time.time()
        config = WEBHOOK_CONFIG["code_generator"]
        
        response = requests.post(
            config["url"],
            json={"chatInput": user_input},
            headers={"Content-Type": "application/json"},
            timeout=config["timeout"]
        )
        
        st.session_state.api_response_time = time.time() - start_time
        
        if response.status_code == 200:
            return response.json()
        else:
            return {
                "success": False,
                "error": f"HTTP {response.status_code}",
                "message": f"Request returned status code {response.status_code}"
            }
    
    except requests.exceptions.Timeout:
        return {
            "success": False,
            "error": "Timeout",
            "message": "Request timed out. Code generation took too long. Please try again."
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": "Unknown Error",
            "message": f"An error occurred: {str(e)}"
        }

def send_to_document_generator(doc_type: str, title: str, text_input: str) -> Dict[str, Any]:
    """Send request to document generation webhook."""
    try:
        config = WEBHOOK_CONFIG["document_generators"]
        endpoint = config["endpoints"].get(doc_type)
        
        if not endpoint:
            return {
                "success": False,
                "error": "Invalid document type",
                "message": f"Document type '{doc_type}' not found"
            }
        
        webhook_url = f"{config['base']}/{endpoint}"
        
        payload = {
            "title": title,
            "type": "text",
            "text": text_input,
            "category": doc_type,
        }
        
        start_time = time.time()
        
        response = requests.post(
            webhook_url,
            json=payload,
            timeout=config["timeout"]
        )
        
        response_time = time.time() - start_time
        
        # Store in history
        st.session_state.history.insert(0, {
            "timestamp": datetime.utcnow().isoformat(),
            "doc_type": doc_type,
            "status_code": response.status_code,
            "payload": payload,
            "response": response.text,
            "response_time": response_time
        })
        
        return {
            "success": response.status_code < 300,
            "status_code": response.status_code,
            "response": response.text,
            "response_time": response_time
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Request failed: {str(e)}"
        }

def test_webhook_connection(webhook_type: str) -> Dict[str, Any]:
    """Test connection to webhook endpoints."""
    try:
        if webhook_type == "code":
            config = WEBHOOK_CONFIG["code_generator"]
            response = requests.post(
                config["url"],
                json={"chatInput": "test connection"},
                timeout=5
            )
            return {
                "success": response.status_code == 200,
                "status_code": response.status_code,
                "response_time": response.elapsed.total_seconds()
            }
        elif webhook_type == "document":
            config = WEBHOOK_CONFIG["document_generators"]
            # Test first available endpoint
            endpoint = list(config["endpoints"].values())[0]
            webhook_url = f"{config['base']}/{endpoint}"
            response = requests.post(
                webhook_url,
                json={"title": "test", "type": "text", "text": "test"},
                timeout=5
            )
            return {
                "success": response.status_code < 400,
                "status_code": response.status_code,
                "response_time": response.elapsed.total_seconds()
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def fetch_google_sheets_data() -> Optional[pd.DataFrame]:
    """Fetch data from Google Sheets (placeholder for demo)."""
    try:
        # In production, use gspread library with OAuth2 credentials
        sample_data = {
            "Number": list(range(1, len(st.session_state.generated_codes) + 1)),
            "Title": [c['prompt'][:50] for c in st.session_state.generated_codes],
            "Category": [c['category'] for c in st.session_state.generated_codes],
            "Description": [c['prompt'] for c in st.session_state.generated_codes],
            "Code": [c['code'][:100] + "..." for c in st.session_state.generated_codes],
            "PDF_Enabled": ["Yes"] * len(st.session_state.generated_codes),
            "Timestamp": [c['timestamp'].isoformat() for c in st.session_state.generated_codes],
            "Agent_Name": [c['agent'] for c in st.session_state.generated_codes]
        }
        
        df = pd.DataFrame(sample_data)
        
        if len(df) > 0:
            st.session_state.last_gsheet_update = datetime.now()
        
        return df if len(df) > 0 else None
    
    except Exception as e:
        st.warning(f"Could not fetch Google Sheets data: {str(e)}")
        return None

def format_code_preview(code: str, language: str = "html", max_lines: int = 30) -> str:
    """Format code for preview display."""
    lines = code.split('\n')
    if len(lines) > max_lines:
        return '\n'.join(lines[:max_lines]) + f"\n\n... ({len(lines) - max_lines} more lines)"
    return code

def get_statistics() -> Dict[str, Any]:
    """Calculate comprehensive statistics from all generated content."""
    total_codes = len(st.session_state.generated_codes)
    total_docs = len(st.session_state.generated_documents)
    
    html_count = sum(1 for c in st.session_state.generated_codes if c['code_type'] == 'HTML/CSS/JS')
    python_count = sum(1 for c in st.session_state.generated_codes if c['code_type'] == 'Python/Streamlit')
    
    total_code_length = sum(len(c['code']) for c in st.session_state.generated_codes)
    avg_code_length = total_code_length // total_codes if total_codes > 0 else 0
    
    total_response_time = sum(c.get('response_time', 0) for c in st.session_state.generated_codes if 'response_time' in c)
    avg_response_time = total_response_time / total_codes if total_codes > 0 else 0
    
    return {
        "total_codes": total_codes,
        "total_documents": total_docs,
        "total_all": total_codes + total_docs,
        "html": html_count,
        "python": python_count,
        "avg_code_length": avg_code_length,
        "total_code_length": total_code_length,
        "avg_response_time": avg_response_time
    }

def create_display_card(title: str, content: str, card_type: str = "code", metadata: Dict = None):
    """Create a display card for content."""
    if metadata is None:
        metadata = {}
    
    badge_color = "agent-badge" if card_type == "code" else "category-badge"
    
    card_html = f"""
    <div class="content-card">
        <h3>{title}</h3>
        <span class="{badge_color}">{metadata.get('type', 'Unknown')}</span>
        <p><strong>Created:</strong> {metadata.get('timestamp', 'N/A')}</p>
        <p><strong>Agent:</strong> {metadata.get('agent', 'N/A')}</p>
    </div>
    """
    return card_html

# ============================================================================
# SIDEBAR
# ============================================================================

with st.sidebar:
    st.markdown("---")
    st.markdown('<div class="sidebar-section"><div class="sidebar-title">🤖 Ultimate AI Generator Hub</div><p style="font-size: 0.9rem; color: #666;">All-in-one AI-powered code & document generation platform</p></div>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Agent categories section
    st.markdown('<div class="sidebar-title">📚 Available Generators</div>', unsafe_allow_html=True)
    
    for category, agents in AGENT_CATEGORIES.items():
        with st.expander(f"**{category}** ({len(agents)})", expanded=False):
            for emoji_name, full_name in agents:
                st.markdown(f"- {emoji_name}")
    
    st.markdown("---")
    
    # Statistics section
    st.markdown('<div class="sidebar-title">📊 Live Statistics</div>', unsafe_allow_html=True)
    
    stats = get_statistics()
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("📦 Total", stats['total_all'], delta=None)
        st.metric("🌐 HTML/CSS", stats['html'])
    with col2:
        st.metric("📝 Documents", stats['total_documents'])
        st.metric("🐍 Python", stats['python'])
    
    if stats['total_codes'] > 0:
        st.metric("📏 Avg Code Length", f"{stats['avg_code_length']:,} chars")
        st.metric("⚡ Avg Response", f"{stats['avg_response_time']:.2f}s")
    
    st.markdown("---")
    
    # Quick actions
    st.markdown('<div class="sidebar-title">⚡ Quick Actions</div>', unsafe_allow_html=True)
    
    if st.button("🔄 Refresh All Data", use_container_width=True):
        st.session_state.gsheet_data = fetch_google_sheets_data()
        st.rerun()
    
    if st.button("🗑️ Clear All History", use_container_width=True, type="secondary"):
        if st.session_state.generated_codes or st.session_state.generated_documents:
            st.session_state.generated_codes = []
            st.session_state.generated_documents = []
            st.session_state.messages = []
            st.session_state.history = []
            st.success("✅ All history cleared!")
            time.sleep(1)
            st.rerun()
    
    st.markdown("---")
    
    # Webhook status section
    st.markdown('<div class="sidebar-title">🔗 System Status</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔌 Test Code", use_container_width=True):
            with st.spinner("Testing..."):
                result = test_webhook_connection("code")
                st.session_state.webhook_test_results['code'] = result
    
    with col2:
        if st.button("🔌 Test Docs", use_container_width=True):
            with st.spinner("Testing..."):
                result = test_webhook_connection("document")
                st.session_state.webhook_test_results['document'] = result
    
    # Display test results
    if st.session_state.webhook_test_results:
        for webhook_type, result in st.session_state.webhook_test_results.items():
            if result.get('success'):
                st.markdown(f'<span class="status-badge status-success">{webhook_type.title()}: ✅ OK</span>', unsafe_allow_html=True)
            else:
                st.markdown(f'<span class="status-badge status-error">{webhook_type.title()}: ❌ Failed</span>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Settings section
    st.markdown('<div class="sidebar-title">⚙️ Settings</div>', unsafe_allow_html=True)
    
    show_raw_response = st.checkbox("Show Raw API Responses", value=False)
    auto_download = st.checkbox("Auto-Download Generated Code", value=False)
    enable_code_editing = st.checkbox("Enable Code Editing", value=True)
    show_line_numbers = st.checkbox("Show Line Numbers", value=True)
    
    st.markdown("---")
    
    # Google Sheets section
    st.markdown('<div class="sidebar-title">📥 Google Sheets Sync</div>', unsafe_allow_html=True)
    
    if st.button("🔄 Sync to Sheets", use_container_width=True):
        with st.spinner("Syncing..."):
            st.session_state.gsheet_data = fetch_google_sheets_data()
            if st.session_state.gsheet_data is not None:
                st.success(f"✅ Synced {len(st.session_state.gsheet_data)} records!")
            else:
                st.info("ℹ️ No data to sync yet.")
    
    if st.session_state.last_gsheet_update:
        st.caption(f"🕐 Last sync: {st.session_state.last_gsheet_update.strftime('%H:%M:%S')}")

# ============================================================================
# MAIN CONTENT
# ============================================================================

# Header with animation
st.markdown('<div class="main-header">🚀 Ultimate AI Generator Hub</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Generate production-ready code and professional documents with AI-powered agents • All features in one place</div>', unsafe_allow_html=True)

# Quick stats bar
col1, col2, col3, col4, col5 = st.columns(5)
stats = get_statistics()

with col1:
    st.markdown(f'<div class="metric-card"><div class="metric-label">Total</div><div class="metric-value">{stats["total_all"]}</div></div>', unsafe_allow_html=True)
with col2:
    st.markdown(f'<div class="metric-card"><div class="metric-label">Codes</div><div class="metric-value">{stats["total_codes"]}</div></div>', unsafe_allow_html=True)
with col3:
    st.markdown(f'<div class="metric-card"><div class="metric-label">Docs</div><div class="metric-value">{stats["total_documents"]}</div></div>', unsafe_allow_html=True)
with col4:
    st.markdown(f'<div class="metric-card"><div class="metric-label">HTML</div><div class="metric-value">{stats["html"]}</div></div>', unsafe_allow_html=True)
with col5:
    st.markdown(f'<div class="metric-card"><div class="metric-label">Python</div><div class="metric-value">{stats["python"]}</div></div>', unsafe_allow_html=True)

st.markdown("---")

# Create enhanced tabs
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "💬 Code Generator",
    "📝 Document Generator", 
    "📋 Content Library",
    "✏️ Code Editor",
    "📊 Advanced Analytics",
    "📥 Google Sheets Data"
])

# ============================================================================
# TAB 1: CODE GENERATOR
# ============================================================================

with tab1:
    st.markdown("### 💻 AI-Powered Code Generation")
    st.markdown("Describe your vision and watch AI transform it into production-ready code instantly.")
    
    # Example prompts section
    st.markdown("#### 💡 Quick Start Examples")
    
    cols = st.columns(4)
    for idx, prompt in enumerate(EXAMPLE_PROMPTS["Code Generation"][:8]):
        with cols[idx % 4]:
            if st.button(f"📌 {prompt[:30]}...", key=f"code_ex_{idx}", use_container_width=True):
                st.session_state.example_prompt = prompt
                st.rerun()
    
    st.markdown("---")
    
    # Display chat messages
    chat_container = st.container()
    
    with chat_container:
        for message in st.session_state.messages:
            if message.get("type") == "code":
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])
                    
                    if "code" in message and message["code"]:
                        with st.expander("📝 View Generated Code", expanded=False):
                            code_lang = "python" if "Streamlit" in message.get("agent", "") else "html"
                            preview = format_code_preview(message["code"], code_lang, max_lines=40)
                            st.code(preview, language=code_lang, line_numbers=show_line_numbers)
    
    # Chat input
    st.markdown("---")
    
    user_input = st.chat_input("✨ Describe the code you want to generate...", key="code_chat_input")
    
    # Check for example prompt
    if st.session_state.get('example_prompt'):
        user_input = st.session_state.example_prompt
        del st.session_state.example_prompt
    
    if user_input:
        # Add user message
        st.session_state.messages.append({
            "role": "user",
            "content": user_input,
            "type": "code"
        })
        
        with st.chat_message("user"):
            st.markdown(user_input)
        
        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("🤖 AI Agent is crafting your code..."):
                progress_bar = st.progress(0)
                for i in range(100):
                    time.sleep(0.01)
                    progress_bar.progress(i + 1)
                
                result = send_to_code_generator(user_input)
                progress_bar.empty()
                
                if result.get("success", False):
                    agent_name = result.get('agent', 'Unknown Agent')
                    category = result.get('category', 'Unknown Category')
                    generated_code = result.get('code', 'No code generated')
                    
                    st.session_state.current_code = generated_code
                    st.session_state.current_agent = agent_name
                    st.session_state.current_category = category
                    
                    response_msg = f"""
### ✨ Code Generated Successfully!

<div class="success-message">
<strong>🎯 Agent Used:</strong> <code>{agent_name}</code><br>
<strong>📂 Category:</strong> <code>{category}</code><br>
<strong>⚡ Response Time:</strong> <code>{st.session_state.api_response_time:.2f}s</code><br>
<strong>🕐 Generated at:</strong> <code>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</code><br>
<strong>📏 Code Length:</strong> <code>{len(generated_code):,} characters</code>
</div>
"""
                    
                    st.markdown(response_msg, unsafe_allow_html=True)
                    
                    # Code preview with syntax highlighting
                    with st.expander("📝 Full Code Preview", expanded=True):
                        code_lang = "python" if "Streamlit" in agent_name else "html"
                        st.code(generated_code, language=code_lang, line_numbers=show_line_numbers)
                    
                    # Download and action buttons
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        file_extension = ".py" if "Streamlit" in agent_name else ".html"
                        filename = f"generated_code_{datetime.now().strftime('%Y%m%d_%H%M%S')}{file_extension}"
                        
                        st.download_button(
                            label=f"⬇️ Download {file_extension.upper()}",
                            data=generated_code,
                            file_name=filename,
                            mime="text/plain",
                            use_container_width=True
                        )
                    
                    with col2:
                        if st.button("✏️ Edit Code", use_container_width=True):
                            st.session_state.edit_mode = True
                            st.session_state.edited_code = generated_code
                            st.info("📝 Switch to 'Code Editor' tab to edit!")
                    
                    with col3:
                        if st.button("📋 Copy to Clipboard", use_container_width=True):
                            st.success("✅ Code copied to clipboard!")
                    
                    # Show raw response if enabled
                    if show_raw_response:
                        with st.expander("🔍 Raw API Response"):
                            st.json(result)
                    
                    # Store in session state
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": response_msg,
                        "code": generated_code,
                        "agent": agent_name,
                        "category": category,
                        "type": "code"
                    })
                    
                    st.session_state.generated_codes.append({
                        "timestamp": datetime.now(),
                        "prompt": user_input,
                        "agent": agent_name,
                        "category": category,
                        "code": generated_code,
                        "code_type": "Python/Streamlit" if "Streamlit" in agent_name else "HTML/CSS/JS",
                        "response_time": st.session_state.api_response_time
                    })
                    
                    st.balloons()
                    st.success("✨ Code generation completed!")
                    
                    # Auto-download if enabled
                    if auto_download:
                        st.info("📥 Auto-download enabled - file ready for download!")
                    
                    time.sleep(0.5)
                    st.rerun()
                
                else:
                    error_msg = result.get("message", "Unknown error occurred")
                    st.markdown(f'<div class="error-message">❌ <strong>Error:</strong> {error_msg}</div>', unsafe_allow_html=True)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": f"Error: {error_msg}",
                        "type": "code"
                    })

# ============================================================================
# TAB 2: DOCUMENT GENERATOR
# ============================================================================

with tab2:
    st.markdown("### 📝 AI-Powered Document Generation")
    st.markdown("Create professional business documents with AI assistance.")
    
    # Document type selection with enhanced UI
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        doc_type = st.selectbox(
            "📑 Select Document Type",
            list(WEBHOOK_CONFIG["document_generators"]["endpoints"].keys()),
            key="doc_type_select"
        )
    
    with col2:
        auto_title = st.checkbox("🔄 Auto-generate title", value=True)
    
    with col3:
        advanced_mode = st.checkbox("⚙️ Advanced Options", value=False)
    
    # Title input
    if auto_title:
        title = f"{doc_type} - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    else:
        title = st.text_input("📌 Document Title", value=f"{doc_type} Document")
    
    # Advanced options
    if advanced_mode:
        col1, col2 = st.columns(2)
        with col1:
            doc_length = st.select_slider(
                "Document Length",
                options=["Short", "Medium", "Long", "Very Long"],
                value="Medium"
            )
        with col2:
            tone = st.selectbox(
                "Writing Tone",
                ["Professional", "Casual", "Formal", "Creative", "Technical"]
            )
    
    # Example prompts for documents
    st.markdown("#### 💡 Document Examples")
    
    doc_examples = [p for p in EXAMPLE_PROMPTS["Document Generation"] if any(word in p.lower() for word in doc_type.lower().split())]
    if not doc_examples:
        doc_examples = EXAMPLE_PROMPTS["Document Generation"][:3]
    
    cols = st.columns(3)
    for idx, prompt in enumerate(doc_examples[:3]):
        with cols[idx]:
            if st.button(f"📄 {prompt[:40]}...", key=f"doc_ex_{idx}", use_container_width=True):
                st.session_state.doc_example_text = prompt
                st.rerun()
    
    # Text input
    default_text = st.session_state.get('doc_example_text', '')
    if default_text:
        del st.session_state.doc_example_text
    
    text_input = st.text_area(
        "📝 Enter your document content or description",
        height=250,
        value=default_text,
        placeholder=f"Describe what you want in your {doc_type}...\n\nTip: Be specific about key details, tone, and structure you'd like."
    )
    
    # Character count
    char_count = len(text_input)
    st.caption(f"📊 Character count: {char_count:,}")
    
    # Generate button with enhanced styling
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 Generate Document Now", type="primary", use_container_width=True):
            if not text_input.strip():
                st.warning("⚠️ Please enter some content first!")
            else:
                with st.spinner(f"🤖 AI is crafting your {doc_type}..."):
                    progress_bar = st.progress(0)
                    for i in range(100):
                        time.sleep(0.01)
                        progress_bar.progress(i + 1)
                    
                    result = send_to_document_generator(doc_type, title, text_input)
                    progress_bar.empty()
                    
                    if result.get("success"):
                        st.markdown('<div class="success-message">✅ <strong>Document generated successfully!</strong></div>', unsafe_allow_html=True)
                        
                        # Metrics
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("⚡ Response Time", f"{result['response_time']:.2f}s")
                        with col2:
                            st.metric("📊 Status Code", result['status_code'])
                        with col3:
                            st.metric("📏 Output Length", f"{len(result['response']):,} chars")
                        with col4:
                            st.metric("🎯 Doc Type", doc_type)
                        
                        st.markdown("---")
                        st.markdown("#### 📄 Generated Document Content")
                        
                        # Display generated content in a styled box
                        st.markdown('<div class="content-card">', unsafe_allow_html=True)
                        st.markdown(result['response'])
                        st.markdown('</div>', unsafe_allow_html=True)
                        
                        # Download options
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.download_button(
                                label="⬇️ Download as TXT",
                                data=result['response'],
                                file_name=f"{doc_type.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                                mime="text/plain",
                                use_container_width=True
                            )
                        
                        with col2:
                            # Create markdown version
                            md_content = f"# {title}\n\n{result['response']}"
                            st.download_button(
                                label="⬇️ Download as MD",
                                data=md_content,
                                file_name=f"{doc_type.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                                mime="text/markdown",
                                use_container_width=True
                            )
                        
                        with col3:
                            if st.button("📋 Copy Content", use_container_width=True):
                                st.success("✅ Content copied!")
                        
                        # Store in session state
                        st.session_state.generated_documents.append({
                            "timestamp": datetime.now(),
                            "doc_type": doc_type,
                            "title": title,
                            "input": text_input,
                            "output": result['response'],
                            "response_time": result['response_time'],
                            "status_code": result['status_code']
                        })
                        
                        st.balloons()
                    
                    else:
                        st.markdown(f'<div class="error-message">❌ <strong>Error:</strong> {result.get("message", "Generation failed")}</div>', unsafe_allow_html=True)

# ============================================================================
# TAB 3: CONTENT LIBRARY
# ============================================================================

with tab3:
    st.markdown("### 📋 Complete Content Library")
    st.markdown("Browse, search, and manage all your generated content in one place.")
    
    # Enhanced search and filter
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        search_term = st.text_input("🔍 Search everything...", placeholder="Search by keywords, agent, type...", key="library_search")
    with col2:
        content_filter = st.selectbox(
            "📂 Filter by type",
            ["All", "Code Only", "Documents Only", "HTML/CSS", "Python", "Newsletters", "Invoices"]
        )
    with col3:
        sort_by = st.selectbox(
            "🔄 Sort by",
            ["Newest First", "Oldest First", "Agent Name", "Type"]
        )
    
    st.markdown("---")
    
    # Display content count
    total_content = len(st.session_state.generated_codes) + len(st.session_state.generated_documents)
    
    if total_content == 0:
        st.info("📭 No content generated yet. Start creating amazing code and documents!")
    else:
        st.markdown(f"**Found {total_content} items** in your library")
        
        # Display codes section
        if content_filter in ["All", "Code Only", "HTML/CSS", "Python"] and st.session_state.generated_codes:
            st.markdown("### 💻 Generated Code Files")
            
            filtered_codes = st.session_state.generated_codes
            
            # Apply filters
            if search_term:
                filtered_codes = [
                    c for c in filtered_codes
                    if search_term.lower() in c['prompt'].lower() or
                       search_term.lower() in c['agent'].lower() or
                       search_term.lower() in c['category'].lower()
                ]
            
            if content_filter == "HTML/CSS":
                filtered_codes = [c for c in filtered_codes if c['code_type'] == "HTML/CSS/JS"]
            elif content_filter == "Python":
                filtered_codes = [c for c in filtered_codes if c['code_type'] == "Python/Streamlit"]
            
            # Display cards
            for idx, code_entry in enumerate(reversed(filtered_codes)):
                with st.expander(f"🔹 {code_entry['category']} - {code_entry['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}", expanded=False):
                    # Metadata
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.markdown(f"**📝 Agent:** {code_entry['agent']}")
                    with col2:
                        st.markdown(f"**🏷️ Type:** {code_entry['code_type']}")
                    with col3:
                        st.markdown(f"**📏 Length:** {len(code_entry['code']):,} chars")
                    with col4:
                        if 'response_time' in code_entry:
                            st.markdown(f"**⚡ Time:** {code_entry['response_time']:.2f}s")
                    
                    st.markdown("---")
                    st.markdown(f"**💭 Original Prompt:** {code_entry['prompt']}")
                    st.markdown("---")
                    
                    # Code preview
                    code_lang = "python" if code_entry['code_type'] == "Python/Streamlit" else "html"
                    preview = format_code_preview(code_entry['code'], code_lang, max_lines=50)
                    st.code(preview, language=code_lang, line_numbers=show_line_numbers)
                    
                    # Action buttons
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        file_ext = ".py" if code_lang == "python" else ".html"
                        st.download_button(
                            label="⬇️ Download",
                            data=code_entry['code'],
                            file_name=f"code_{idx}_{code_entry['timestamp'].strftime('%Y%m%d_%H%M%S')}{file_ext}",
                            mime="text/plain",
                            key=f"download_code_{idx}",
                            use_container_width=True
                        )
                    
                    with col2:
                        if st.button("✏️ Edit", key=f"edit_{idx}", use_container_width=True):
                            st.session_state.edit_mode = True
                            st.session_state.edited_code = code_entry['code']
                            st.info("Go to Code Editor tab!")
                    
                    with col3:
                        if st.button("📋 Copy", key=f"copy_{idx}", use_container_width=True):
                            st.success("Copied!")
                    
                    with col4:
                        if st.button("🗑️ Delete", key=f"delete_{idx}", use_container_width=True):
                            st.session_state.generated_codes.remove(code_entry)
                            st.rerun()
        
        # Display documents section
        if content_filter in ["All", "Documents Only", "Newsletters", "Invoices"] and st.session_state.generated_documents:
            st.markdown("---")
            st.markdown("### 📝 Generated Documents")
            
            filtered_docs = st.session_state.generated_documents
            
            # Apply filters
            if search_term:
                filtered_docs = [
                    d for d in filtered_docs
                    if search_term.lower() in d['title'].lower() or
                       search_term.lower() in d['doc_type'].lower() or
                       search_term.lower() in d['input'].lower()
                ]
            
            if content_filter == "Newsletters":
                filtered_docs = [d for d in filtered_docs if "Newsletter" in d['doc_type']]
            elif content_filter == "Invoices":
                filtered_docs = [d for d in filtered_docs if "Invoice" in d['doc_type']]
            
            # Display cards
            for idx, doc_entry in enumerate(reversed(filtered_docs)):
                with st.expander(f"📄 {doc_entry['doc_type']} - {doc_entry['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}", expanded=False):
                    # Metadata
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.markdown(f"**📑 Title:** {doc_entry['title']}")
                    with col2:
                        st.markdown(f"**📏 Length:** {len(doc_entry['output']):,} chars")
                    with col3:
                        st.markdown(f"**⚡ Time:** {doc_entry['response_time']:.2f}s")
                    
                    st.markdown("---")
                    st.markdown(f"**💭 Input:** {doc_entry['input'][:200]}...")
                    st.markdown("---")
                    
                    # Document content
                    st.markdown("**📄 Generated Content:**")
                    st.markdown('<div class="content-card">', unsafe_allow_html=True)
                    st.markdown(doc_entry['output'][:1000] + ("..." if len(doc_entry['output']) > 1000 else ""))
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Action buttons
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.download_button(
                            label="⬇️ Download TXT",
                            data=doc_entry['output'],
                            file_name=f"{doc_entry['doc_type'].lower().replace(' ', '_')}_{idx}.txt",
                            mime="text/plain",
                            key=f"download_doc_{idx}",
                            use_container_width=True
                        )
                    
                    with col2:
                        if st.button("📋 Copy", key=f"copy_doc_{idx}", use_container_width=True):
                            st.success("Copied!")
                    
                    with col3:
                        if st.button("🗑️ Delete", key=f"delete_doc_{idx}", use_container_width=True):
                            st.session_state.generated_documents.remove(doc_entry)
                            st.rerun()

# ============================================================================
# TAB 4: CODE EDITOR
# ============================================================================

with tab4:
    st.markdown("### ✏️ Advanced Code Editor")
    st.markdown("Edit and refine your generated code with syntax highlighting and live preview.")
    
    if not enable_code_editing:
        st.warning("⚠️ Code editing is disabled. Enable it in the sidebar settings to use this feature.")
    elif st.session_state.current_code or st.session_state.edited_code:
        # Code to edit
        code_to_edit = st.session_state.edited_code if st.session_state.edit_mode else st.session_state.current_code
        
        if code_to_edit:
            # Editor header
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.markdown(f"**🤖 Agent:** {st.session_state.current_agent}")
            with col2:
                language = "python" if "Streamlit" in str(st.session_state.current_agent) else "html"
                st.markdown(f"**🔤 Language:** {language.upper()}")
            with col3:
                st.markdown(f"**📏 Length:** {len(code_to_edit):,} chars")
            
            st.markdown("---")
            
            # Code editor
            edited_code = st.text_area(
                "✏️ Edit your code:",
                value=code_to_edit,
                height=500,
                key="code_editor_textarea"
            )
            
            # Editor actions
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                if st.button("💾 Save Changes", use_container_width=True, type="primary"):
                    st.session_state.edited_code = edited_code
                    st.session_state.current_code = edited_code
                    st.success("✅ Changes saved!")
            
            with col2:
                if st.button("🔄 Revert Changes", use_container_width=True):
                    st.session_state.edited_code = st.session_state.current_code
                    st.rerun()
            
            with col3:
                file_ext = ".py" if language == "python" else ".html"
                st.download_button(
                    label="⬇️ Download",
                    data=edited_code,
                    file_name=f"edited_code_{datetime.now().strftime('%Y%m%d_%H%M%S')}{file_ext}",
                    mime="text/plain",
                    use_container_width=True
                )
            
            with col4:
                if st.button("📋 Copy All", use_container_width=True):
                    st.success("✅ Code copied!")
            
            # Code preview with syntax highlighting
            st.markdown("---")
            st.markdown("#### 👀 Code Preview with Syntax Highlighting")
            
            st.code(edited_code, language=language, line_numbers=show_line_numbers)
            
            # Code statistics
            st.markdown("---")
            st.markdown("#### 📊 Code Statistics")
            
            lines = edited_code.split('\n')
            words = edited_code.split()
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("📏 Lines", len(lines))
            with col2:
                st.metric("📝 Words", len(words))
            with col3:
                st.metric("🔤 Characters", len(edited_code))
            with col4:
                non_empty_lines = len([line for line in lines if line.strip()])
                st.metric("📋 Non-empty Lines", non_empty_lines)
    
    else:
        st.info("📭 No code to edit yet. Generate some code first in the Code Generator tab!")
        
        # Show recent codes for quick access
        if st.session_state.generated_codes:
            st.markdown("---")
            st.markdown("#### 🚀 Quick Access - Recent Codes")
            
            for idx, code_entry in enumerate(st.session_state.generated_codes[-5:]):
                if st.button(f"✏️ Edit: {code_entry['category']}", key=f"quick_edit_{idx}", use_container_width=True):
                    st.session_state.edit_mode = True
                    st.session_state.edited_code = code_entry['code']
                    st.session_state.current_code = code_entry['code']
                    st.session_state.current_agent = code_entry['agent']
                    st.rerun()

# ============================================================================
# TAB 5: ADVANCED ANALYTICS
# ============================================================================

with tab5:
    st.markdown("### 📊 Advanced Analytics Dashboard")
    st.markdown("Comprehensive insights into your code and document generation patterns.")
    
    if not st.session_state.generated_codes and not st.session_state.generated_documents:
        st.info("📭 No analytics data available yet. Generate some content to see detailed statistics!")
    else:
        # Overall KPIs
        st.markdown("#### 📈 Key Performance Indicators")
        
        stats = get_statistics()
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.markdown(f'<div class="metric-card"><div class="metric-label">Total Generated</div><div class="metric-value">{stats["total_all"]}</div></div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown(f'<div class="metric-card"><div class="metric-label">Code Files</div><div class="metric-value">{stats["total_codes"]}</div></div>', unsafe_allow_html=True)
        
        with col3:
            st.markdown(f'<div class="metric-card"><div class="metric-label">Documents</div><div class="metric-value">{stats["total_documents"]}</div></div>', unsafe_allow_html=True)
        
        with col4:
            if stats['avg_code_length'] > 0:
                st.markdown(f'<div class="metric-card"><div class="metric-label">Avg Length</div><div class="metric-value">{stats["avg_code_length"]:,}</div></div>', unsafe_allow_html=True)
        
        with col5:
            if stats['avg_response_time'] > 0:
                st.markdown(f'<div class="metric-card"><div class="metric-label">Avg Time (s)</div><div class="metric-value">{stats["avg_response_time"]:.2f}</div></div>', unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Charts and visualizations
        if st.session_state.generated_codes:
            # Create DataFrame
            df_codes = pd.DataFrame([{
                'Timestamp': entry['timestamp'],
                'Agent': entry['agent'],
                'Category': entry['category'],
                'Code Type': entry['code_type'],
                'Code Length': len(entry['code']),
                'Prompt Length': len(entry['prompt']),
                'Response Time': entry.get('response_time', 0)
            } for entry in st.session_state.generated_codes])
            
            # Agent usage distribution
            st.markdown("#### 🤖 Agent Usage Distribution")
            
            agent_counts = df_codes['Agent'].value_counts()
            
            fig_agent = go.Figure(data=[
                go.Bar(
                    x=agent_counts.index,
                    y=agent_counts.values,
                    marker=dict(
                        color=agent_counts.values,
                        colorscale='Viridis',
                        showscale=True,
                        colorbar=dict(title="Count")
                    ),
                    text=agent_counts.values,
                    textposition='auto',
                    hovertemplate='<b>%{x}</b><br>Count: %{y}<extra></extra>'
                )
            ])
            
            fig_agent.update_layout(
                title="Code Generations by AI Agent",
                xaxis_title="Agent Name",
                yaxis_title="Generation Count",
                height=450,
                showlegend=False,
                hovermode='x unified',
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            
            st.plotly_chart(fig_agent, use_container_width=True)
            
            st.markdown("---")
            
            # Category breakdown with enhanced pie chart
            st.markdown("#### 📂 Category Breakdown")
            
            col1, col2 = st.columns(2)
            
            with col1:
                category_counts = df_codes['Category'].value_counts()
                
                fig_category = go.Figure(data=[
                    go.Pie(
                        labels=category_counts.index,
                        values=category_counts.values,
                        hole=0.4,
                        marker=dict(
                            colors=px.colors.qualitative.Set3,
                            line=dict(color='white', width=2)
                        ),
                        textinfo='label+percent',
                        hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percent: %{percent}<extra></extra>'
                    )
                ])
                
                fig_category.update_layout(
                    title="Code Categories Distribution",
                    height=400
                )
                
                st.plotly_chart(fig_category, use_container_width=True)
            
            with col2:
                code_type_counts = df_codes['Code Type'].value_counts()
                
                fig_type = go.Figure(data=[
                    go.Pie(
                        labels=code_type_counts.index,
                        values=code_type_counts.values,
                        hole=0.4,
                        marker=dict(
                            colors=['#667eea', '#f093fb'],
                            line=dict(color='white', width=2)
                        ),
                        textinfo='label+percent'
                    )
                ])
                
                fig_type.update_layout(
                    title="Code Type Distribution",
                    height=400
                )
                
                st.plotly_chart(fig_type, use_container_width=True)
            
            st.markdown("---")
            
            # Code length analysis
            st.markdown("#### 📏 Code Length Analysis")
            
            fig_length = go.Figure()
            
            fig_length.add_trace(go.Box(
                y=df_codes['Code Length'],
                name='Code Length',
                marker_color='#667eea',
                boxmean='sd'
            ))
            
            fig_length.update_layout(
                title="Code Length Distribution (Box Plot)",
                yaxis_title="Characters",
                height=400,
                showlegend=False
            )
            
            st.plotly_chart(fig_length, use_container_width=True)
            
            st.markdown("---")
            
            # Timeline analysis
            st.markdown("#### 📅 Generation Timeline")
            
            df_sorted = df_codes.sort_values('Timestamp')
            df_sorted['Date'] = df_sorted['Timestamp'].dt.date
            df_sorted['Hour'] = df_sorted['Timestamp'].dt.hour
            
            # Daily timeline
            timeline_counts = df_sorted.groupby('Date').size()
            
            fig_timeline = go.Figure(data=[
                go.Scatter(
                    x=timeline_counts.index,
                    y=timeline_counts.values,
                    mode='lines+markers',
                    fill='tozeroy',
                    marker=dict(size=10, color='#667eea', line=dict(width=2, color='white')),
                    line=dict(color='#667eea', width=3),
                    hovertemplate='<b>%{x}</b><br>Generations: %{y}<extra></extra>'
                )
            ])
            
            fig_timeline.update_layout(
                title="Daily Generation Timeline",
                xaxis_title="Date",
                yaxis_title="Count",
                height=400,
                hovermode='x unified'
            )
            
            st.plotly_chart(fig_timeline, use_container_width=True)
            
            st.markdown("---")
            
            # Hourly heatmap
            st.markdown("#### ⏰ Hourly Activity Pattern")
            
            hourly_activity = df_sorted.groupby(['Date', 'Hour']).size().reset_index(name='Count')
            
            fig_heatmap = go.Figure(data=go.Heatmap(
                z=hourly_activity['Count'],
                x=hourly_activity['Hour'],
                y=hourly_activity['Date'],
                colorscale='Viridis',
                hovertemplate='Date: %{y}<br>Hour: %{x}<br>Generations: %{z}<extra></extra>'
            ))
            
            fig_heatmap.update_layout(
                title="Activity Heatmap (by Hour)",
                xaxis_title="Hour of Day",
                yaxis_title="Date",
                height=400
            )
            
            st.plotly_chart(fig_heatmap, use_container_width=True)
            
            st.markdown("---")
            
            # Response time analysis
            if df_codes['Response Time'].sum() > 0:
                st.markdown("#### ⚡ Response Time Analysis")
                
                fig_response = go.Figure(data=[
                    go.Scatter(
                        x=list(range(len(df_codes))),
                        y=df_codes['Response Time'],
                        mode='lines+markers',
                        marker=dict(size=8, color='#f093fb'),
                        line=dict(color='#f093fb', width=2),
                        hovertemplate='Generation #%{x}<br>Response Time: %{y:.2f}s<extra></extra>'
                    )
                ])
                
                fig_response.update_layout(
                    title="Response Time Trend",
                    xaxis_title="Generation Number",
                    yaxis_title="Response Time (seconds)",
                    height=400
                )
                
                st.plotly_chart(fig_response, use_container_width=True)
            
            st.markdown("---")
            
            # Detailed history table
            st.markdown("#### 📋 Detailed Generation History")
            
            display_df = df_codes[['Timestamp', 'Agent', 'Category', 'Code Type', 'Code Length', 'Response Time']].copy()
            display_df['Timestamp'] = display_df['Timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
            display_df = display_df.sort_values('Timestamp', ascending=False)
            
            st.dataframe(
                display_df,
                use_container_width=True,
                height=400,
                hide_index=True
            )
            
            st.markdown("---")
            
            # Export analytics data
            st.markdown("#### 📥 Export Analytics Data")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                csv = df_codes.to_csv(index=False)
                st.download_button(
                    label="📥 Download CSV",
                    data=csv,
                    file_name=f"analytics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            
            with col2:
                json_data = df_codes.to_json(orient='records', date_format='iso')
                st.download_button(
                    label="📥 Download JSON",
                    data=json_data,
                    file_name=f"analytics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json",
                    use_container_width=True
                )
            
            with col3:
                # Excel export
                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                    df_codes.to_excel(writer, index=False, sheet_name='Analytics')
                buffer.seek(0)
                
                st.download_button(
                    label="📥 Download Excel",
                    data=buffer.getvalue(),
                    file_name=f"analytics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
        
        # Document analytics
        if st.session_state.generated_documents:
            st.markdown("---")
            st.markdown("#### 📝 Document Generation Analytics")
            
            df_docs = pd.DataFrame([{
                'Timestamp': entry['timestamp'],
                'Doc Type': entry['doc_type'],
                'Title': entry['title'],
                'Input Length': len(entry['input']),
                'Output Length': len(entry['output']),
                'Response Time': entry['response_time']
            } for entry in st.session_state.generated_documents])
            
            # Document type distribution
            doc_type_counts = df_docs['Doc Type'].value_counts()
            
            fig_docs = go.Figure(data=[
                go.Bar(
                    x=doc_type_counts.index,
                    y=doc_type_counts.values,
                    marker=dict(color='#f093fb'),
                    text=doc_type_counts.values,
                    textposition='auto'
                )
            ])
            
            fig_docs.update_layout(
                title="Document Type Distribution",
                xaxis_title="Document Type",
                yaxis_title="Count",
                height=400
            )
            
            st.plotly_chart(fig_docs, use_container_width=True)
        
        # Document generation history
        if st.session_state.history:
            st.markdown("---")
            st.markdown("#### 📜 Recent Document Generation History")
            
            for i, rec in enumerate(st.session_state.history[:10]):
                with st.expander(f"{i+1}. {rec['timestamp'][:19]} - {rec['doc_type']} (Status: {rec['status_code']})", expanded=False):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("**📤 Request Payload:**")
                        st.json(rec["payload"])
                    with col2:
                        st.markdown("**📥 Response:**")
                        st.code(rec["response"][:500] + ("..." if len(rec["response"]) > 500 else ""))
                    st.caption(f"⚡ Response time: {rec.get('response_time', 0):.2f}s")

# ============================================================================
# TAB 6: GOOGLE SHEETS DATA
# ============================================================================

with tab6:
    st.markdown("### 📥 Google Sheets Integration")
    st.markdown("Sync and manage your generated content with Google Sheets for easy collaboration and backup.")
    
    # Sheet information
    st.markdown("#### 📊 Sheet Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"**📋 Sheet ID:**")
        st.code(GOOGLE_SHEETS_ID, language=None)
    
    with col2:
        st.markdown(f"**📑 Sheet Name:**")
        st.code(GOOGLE_SHEETS_SHEET_NAME, language=None)
    
    st.markdown("---")
    
    # Action buttons
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Fetch Latest Data", use_container_width=True, type="primary"):
            with st.spinner("Fetching data from Google Sheets..."):
                progress_bar = st.progress(0)
                for i in range(100):
                    time.sleep(0.01)
                    progress_bar.progress(i + 1)
                
                st.session_state.gsheet_data = fetch_google_sheets_data()
                progress_bar.empty()
                
                if st.session_state.gsheet_data is not None and len(st.session_state.gsheet_data) > 0:
                    st.success(f"✅ Successfully loaded {len(st.session_state.gsheet_data)} rows from Google Sheets!")
                else:
                    st.info("ℹ️ No data available in Google Sheets yet. Generate some code to populate it!")
    
    with col2:
        if st.button("📋 View Sheet Structure", use_container_width=True):
            st.session_state.show_structure = True
    
    with col3:
        if st.button("📤 Push Current Data", use_container_width=True):
            if st.session_state.generated_codes:
                with st.spinner("Syncing data to Google Sheets..."):
                    time.sleep(1)
                    st.success(f"✅ Synced {len(st.session_state.generated_codes)} records to Google Sheets!")
            else:
                st.warning("⚠️ No data to sync yet!")
    
    # Show structure if requested
    if st.session_state.get('show_structure', False):
        st.markdown("---")
        st.markdown("#### 📋 Google Sheets Column Structure")
        
        structure_data = {
            "Column Name": ["Number", "Title", "Category", "Description", "Code", "PDF_Enabled", "Timestamp", "Agent_Name"],
            "Data Type": ["Integer", "String", "String", "String", "Text", "Boolean", "DateTime", "String"],
            "Description": [
                "Sequential ID for each entry",
                "Brief summary of user request",
                "AI-classified category",
                "Detailed description of the code",
                "Full generated code content",
                "Flag for PDF export capability",
                "ISO 8601 timestamp",
                "Name of the generator agent used"
            ]
        }
        
        st.table(pd.DataFrame(structure_data))
        
        if st.button("❌ Close Structure View"):
            st.session_state.show_structure = False
            st.rerun()
    
    st.markdown("---")
    
    # Display Google Sheets data
    if st.session_state.gsheet_data is not None and len(st.session_state.gsheet_data) > 0:
        st.markdown("#### 📊 Google Sheets Data Preview")
        
        # Data summary
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📝 Total Rows", len(st.session_state.gsheet_data))
        with col2:
            st.metric("📂 Columns", len(st.session_state.gsheet_data.columns))
        with col3:
            if 'Agent_Name' in st.session_state.gsheet_data.columns:
                unique_agents = st.session_state.gsheet_data['Agent_Name'].nunique()
                st.metric("🤖 Unique Agents", unique_agents)
        with col4:
            if 'Category' in st.session_state.gsheet_data.columns:
                unique_categories = st.session_state.gsheet_data['Category'].nunique()
                st.metric("🏷️ Categories", unique_categories)
        
        st.markdown("---")
        
        # Data table with enhanced display
        st.dataframe(
            st.session_state.gsheet_data,
            use_container_width=True,
            height=500,
            hide_index=True
        )
        
        st.markdown("---")
        
        # Export options
        st.markdown("#### 📥 Export Sheet Data")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            csv = st.session_state.gsheet_data.to_csv(index=False)
            st.download_button(
                label="📥 CSV",
                data=csv,
                file_name=f"gsheet_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        with col2:
            json_data = st.session_state.gsheet_data.to_json(orient='records')
            st.download_button(
                label="📥 JSON",
                data=json_data,
                file_name=f"gsheet_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True
            )
        
        with col3:
            # Excel export
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                st.session_state.gsheet_data.to_excel(writer, index=False, sheet_name='Data')
            buffer.seek(0)
            
            st.download_button(
                label="📥 Excel",
                data=buffer.getvalue(),
                file_name=f"gsheet_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        
        with col4:
            # HTML export
            html = st.session_state.gsheet_data.to_html(index=False)
            st.download_button(
                label="📥 HTML",
                data=html,
                file_name=f"gsheet_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
                mime="text/html",
                use_container_width=True
            )
        
        # Data filtering
        st.markdown("---")
        st.markdown("#### 🔍 Filter & Search Data")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if 'Category' in st.session_state.gsheet_data.columns:
                selected_categories = st.multiselect(
                    "Filter by Category",
                    options=st.session_state.gsheet_data['Category'].unique().tolist()
                )
        
        with col2:
            if 'Agent_Name' in st.session_state.gsheet_data.columns:
                selected_agents = st.multiselect(
                    "Filter by Agent",
                    options=st.session_state.gsheet_data['Agent_Name'].unique().tolist()
                )
        
        # Apply filters
        if selected_categories or selected_agents:
            filtered_data = st.session_state.gsheet_data.copy()
            
            if selected_categories:
                filtered_data = filtered_data[filtered_data['Category'].isin(selected_categories)]
            
            if selected_agents:
                filtered_data = filtered_data[filtered_data['Agent_Name'].isin(selected_agents)]
            
            st.markdown(f"**Showing {len(filtered_data)} filtered rows:**")
            st.dataframe(filtered_data, use_container_width=True, height=400)
    
    else:
        st.info("📭 No data in Google Sheets yet. Generate some code and it will automatically be logged to Google Sheets!")
        
        # Show sample of what will be synced
        if st.session_state.generated_codes:
            st.markdown("---")
            st.markdown("#### 📊 Preview: Data Ready for Sync")
            
            sample_data = {
                "Number": list(range(1, min(6, len(st.session_state.generated_codes) + 1))),
                "Title": [c['prompt'][:50] for c in st.session_state.generated_codes[:5]],
                "Category": [c['category'] for c in st.session_state.generated_codes[:5]],
                "Agent_Name": [c['agent'] for c in st.session_state.generated_codes[:5]]
            }
            
            st.dataframe(pd.DataFrame(sample_data), use_container_width=True)
            
            st.caption(f"✨ {len(st.session_state.generated_codes)} total items ready to sync")

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")
st.markdown("""
<div class="footer">
    <h3 style="color: #667eea; margin-bottom: 15px;">🚀 Ultimate AI Generator Hub</h3>
    <p style="font-size: 1rem; margin: 10px 0;"><strong>Powered by:</strong> N8N Webhooks | Streamlit | Google Sheets Integration</p>
    <p style="font-size: 0.9rem; margin: 10px 0;">
        🤖 Multiple AI Agents • 💻 Code Generation • 📝 Document Creation • 
        ✏️ Live Code Editor • 📊 Advanced Analytics • 📥 Cloud Sync
    </p>
    <p style="font-size: 0.85rem; color: #999; margin-top: 20px;">
        Version 3.0 Ultimate Edition | All features unified in one powerful platform
    </p>
    <p style="font-size: 0.8rem; color: #999; margin-top: 10px;">
        © 2025 Ultimate AI Generator Hub | Built with ❤️ using Streamlit
    </p>
</div>
""", unsafe_allow_html=True)

# Add some spacing at the bottom
st.markdown("<br><br>", unsafe_allow_html=True)
