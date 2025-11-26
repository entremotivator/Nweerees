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
    page_title="AI Code & Document Generator Hub",
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
        font-size: 3rem;
        font-weight: 900;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 1.5rem;
        text-align: center;
        letter-spacing: -1px;
    }
    
    .subtitle {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    /* Agent badge styling */
    .agent-badge {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 8px 16px;
        border-radius: 20px;
        font-size: 0.9rem;
        font-weight: 600;
        display: inline-block;
        margin: 5px 5px 5px 0;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    
    .category-badge {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 6px 14px;
        border-radius: 15px;
        font-size: 0.85rem;
        display: inline-block;
        margin: 5px 5px 5px 0;
    }
    
    /* Metric card styling */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 900;
        margin: 10px 0;
    }
    
    .metric-label {
        font-size: 0.9rem;
        opacity: 0.9;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Sidebar styling */
    .sidebar-section {
        background: #f8f9fa;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 15px;
        border-left: 4px solid #667eea;
    }
    
    .sidebar-title {
        font-size: 1.1rem;
        font-weight: 700;
        color: #667eea;
        margin-bottom: 10px;
    }
    
    /* Footer styling */
    .footer {
        text-align: center;
        color: #999;
        padding: 20px;
        margin-top: 40px;
        border-top: 1px solid #e0e0e0;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# CONFIGURATION & CONSTANTS (HIDDEN FROM USER)
# ============================================================================

# Hidden webhook configuration
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
        ("📋 Form App Generator", "Streamlit Form App Generator")
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
        "Build a dashboard to visualize sales data with real-time updates",
        "Generate a contact form with email validation and file upload",
        "Make a Streamlit app for data analysis with CSV upload",
        "Create an ML app for image classification predictions",
    ],
    "Document Generation": [
        "Write a professional newsletter about AI innovations",
        "Create compelling landing page copy for a fitness app",
        "Draft a formal business partnership proposal letter",
        "Generate a 5-email welcome sequence for new subscribers",
        "Create a professional invoice template with payment terms",
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

initialize_session_state()

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def send_to_code_generator(user_input: str) -> Dict[str, Any]:
    """Send request to code generation webhook (hidden endpoint)."""
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
    """Send request to document generation webhook (hidden endpoint)."""
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

def fetch_google_sheets_data() -> Optional[pd.DataFrame]:
    """Fetch data from Google Sheets (placeholder for demo)."""
    try:
        sample_data = {
            "Number": [],
            "Title": [],
            "Category": [],
            "Description": [],
            "Code": [],
            "PDF_Enabled": [],
            "Timestamp": [],
            "Agent_Name": []
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
    """Calculate statistics from all generated content."""
    total_codes = len(st.session_state.generated_codes)
    total_docs = len(st.session_state.generated_documents)
    
    html_count = sum(1 for c in st.session_state.generated_codes if c['code_type'] == 'HTML/CSS/JS')
    python_count = sum(1 for c in st.session_state.generated_codes if c['code_type'] == 'Python/Streamlit')
    
    return {
        "total_codes": total_codes,
        "total_documents": total_docs,
        "total_all": total_codes + total_docs,
        "html": html_count,
        "python": python_count,
    }

# ============================================================================
# SIDEBAR
# ============================================================================

with st.sidebar:
    st.markdown("---")
    st.markdown('<div class="sidebar-section"><div class="sidebar-title">🤖 AI Generator Hub</div></div>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Agent categories section
    st.markdown('<div class="sidebar-title">📚 Available Generators</div>', unsafe_allow_html=True)
    
    for category, agents in AGENT_CATEGORIES.items():
        with st.expander(f"**{category}**", expanded=False):
            for emoji_name, full_name in agents:
                st.markdown(f"- {emoji_name}")
    
    st.markdown("---")
    
    # Statistics section
    st.markdown('<div class="sidebar-title">📊 Statistics</div>', unsafe_allow_html=True)
    
    stats = get_statistics()
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Generated", stats['total_all'])
        st.metric("HTML/CSS", stats['html'])
    with col2:
        st.metric("Documents", stats['total_documents'])
        st.metric("Python", stats['python'])
    
    if st.button("🗑️ Clear All History", use_container_width=True):
        st.session_state.generated_codes = []
        st.session_state.generated_documents = []
        st.session_state.messages = []
        st.session_state.history = []
        st.rerun()
    
    st.markdown("---")
    
    # Connection status (without showing URLs)
    st.markdown('<div class="sidebar-title">🔗 System Status</div>', unsafe_allow_html=True)
    st.success("✅ All systems operational")
    st.caption("Code & Document generators connected")

# ============================================================================
# MAIN CONTENT
# ============================================================================

# Header
st.markdown('<div class="main-header">🚀 AI Generator Hub</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Generate production-ready code and professional documents with AI</div>', unsafe_allow_html=True)

# Create tabs
tab1, tab2, tab3, tab4 = st.tabs(["💬 Code Generator", "📝 Document Generator", "📋 Library", "📊 Analytics"])

# ============================================================================
# TAB 1: CODE GENERATOR
# ============================================================================

with tab1:
    st.markdown("### 💻 AI Code Generation")
    st.markdown("Describe the code you want to generate and our AI agents will create it for you.")
    
    # Example prompts
    st.markdown("#### 💡 Quick Start Examples")
    cols = st.columns(3)
    for idx, prompt in enumerate(EXAMPLE_PROMPTS["Code Generation"][:3]):
        with cols[idx % 3]:
            if st.button(prompt, key=f"code_ex_{idx}", use_container_width=True):
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
                        with st.expander("📝 View Generated Code"):
                            code_lang = "python" if "Streamlit" in message.get("agent", "") else "html"
                            preview = format_code_preview(message["code"], code_lang)
                            st.code(preview, language=code_lang)
    
    # Chat input
    user_input = st.chat_input("Describe the code you want to generate...", key="code_chat_input")
    
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
            with st.spinner("🤖 AI Agent is generating your code..."):
                result = send_to_code_generator(user_input)
                
                if result.get("success", False):
                    agent_name = result.get('agent', 'Unknown Agent')
                    category = result.get('category', 'Unknown Category')
                    generated_code = result.get('code', 'No code generated')
                    
                    st.session_state.current_code = generated_code
                    st.session_state.current_agent = agent_name
                    st.session_state.current_category = category
                    
                    response_msg = f"""
### ✨ Code Generated Successfully!

**Agent Used:** `{agent_name}`  
**Category:** `{category}`  
**Response Time:** `{st.session_state.api_response_time:.2f}s`  
**Generated at:** `{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`
"""
                    
                    st.markdown(response_msg)
                    
                    with st.expander("📝 Code Preview", expanded=True):
                        code_lang = "python" if "Streamlit" in agent_name else "html"
                        preview = format_code_preview(generated_code, code_lang, max_lines=40)
                        st.code(preview, language=code_lang)
                    
                    file_extension = ".py" if "Streamlit" in agent_name else ".html"
                    filename = f"generated_code_{datetime.now().strftime('%Y%m%d_%H%M%S')}{file_extension}"
                    
                    st.download_button(
                        label=f"⬇️ Download {file_extension.upper()} File",
                        data=generated_code,
                        file_name=filename,
                        mime="text/plain",
                        use_container_width=True
                    )
                    
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
                        "code_type": "Python/Streamlit" if "Streamlit" in agent_name else "HTML/CSS/JS"
                    })
                    
                    st.success("✨ Code generation completed!")
                    st.rerun()
                
                else:
                    error_msg = result.get("message", "Unknown error occurred")
                    st.error(f"❌ {error_msg}")
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": f"Error: {error_msg}",
                        "type": "code"
                    })

# ============================================================================
# TAB 2: DOCUMENT GENERATOR
# ============================================================================

with tab2:
    st.markdown("### 📝 AI Document Generation")
    st.markdown("Generate professional documents using AI-powered templates.")
    
    # Document type selection
    col1, col2 = st.columns([2, 1])
    
    with col1:
        doc_type = st.selectbox(
            "Select Document Type",
            list(WEBHOOK_CONFIG["document_generators"]["endpoints"].keys()),
            key="doc_type_select"
        )
    
    with col2:
        auto_title = st.checkbox("Auto-generate title", value=True)
    
    # Title input
    if auto_title:
        title = f"{doc_type} - {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}"
    else:
        title = st.text_input("Document Title", value=f"{doc_type} Document")
    
    # Example prompts for documents
    st.markdown("#### 💡 Example Prompts")
    doc_examples = [p for p in EXAMPLE_PROMPTS["Document Generation"] if doc_type.lower() in p.lower()]
    if doc_examples:
        for idx, prompt in enumerate(doc_examples[:2]):
            if st.button(prompt, key=f"doc_ex_{idx}", use_container_width=True):
                st.session_state.doc_example_text = prompt
    
    # Text input
    default_text = st.session_state.get('doc_example_text', '')
    if default_text:
        del st.session_state.doc_example_text
    
    text_input = st.text_area(
        "Enter your document content or description",
        height=300,
        value=default_text,
        placeholder=f"Describe what you want in your {doc_type}..."
    )
    
    # Generate button
    if st.button("🚀 Generate Document", type="primary", use_container_width=True):
        if not text_input.strip():
            st.warning("⚠️ Please enter some content first!")
        else:
            with st.spinner(f"🤖 Generating your {doc_type}..."):
                result = send_to_document_generator(doc_type, title, text_input)
                
                if result.get("success"):
                    st.success(f"✅ {doc_type} generated successfully!")
                    
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown(f"**Response Time:** {result['response_time']:.2f}s")
                    with col2:
                        st.markdown(f"**Status:** {result['status_code']}")
                    
                    st.markdown("#### 📄 Generated Content")
                    st.code(result['response'])
                    
                    # Download button
                    st.download_button(
                        label="⬇️ Download Document",
                        data=result['response'],
                        file_name=f"{doc_type.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                        mime="text/plain",
                        use_container_width=True
                    )
                    
                    # Store in session state
                    st.session_state.generated_documents.append({
                        "timestamp": datetime.now(),
                        "doc_type": doc_type,
                        "title": title,
                        "input": text_input,
                        "output": result['response'],
                        "response_time": result['response_time']
                    })
                else:
                    st.error(f"❌ {result.get('message', 'Generation failed')}")

# ============================================================================
# TAB 3: LIBRARY
# ============================================================================

with tab3:
    st.markdown("### 📋 Generated Content Library")
    
    # Filter options
    col1, col2 = st.columns(2)
    with col1:
        content_filter = st.selectbox(
            "Filter by type",
            ["All", "Code", "Documents"]
        )
    with col2:
        search_term = st.text_input("🔍 Search", key="library_search")
    
    st.markdown("---")
    
    # Display codes
    if content_filter in ["All", "Code"] and st.session_state.generated_codes:
        st.markdown("#### 💻 Generated Code")
        
        filtered_codes = st.session_state.generated_codes
        if search_term:
            filtered_codes = [
                c for c in filtered_codes
                if search_term.lower() in c['prompt'].lower() or
                   search_term.lower() in c['agent'].lower()
            ]
        
        for idx, code_entry in enumerate(reversed(filtered_codes)):
            with st.expander(f"🔹 {code_entry['category']} - {code_entry['timestamp'].strftime('%Y-%m-%d %H:%M')}"):
                st.markdown(f"**Prompt:** {code_entry['prompt']}")
                st.markdown(f"**Agent:** {code_entry['agent']}")
                st.markdown(f"**Type:** {code_entry['code_type']}")
                
                code_lang = "python" if code_entry['code_type'] == "Python/Streamlit" else "html"
                preview = format_code_preview(code_entry['code'], code_lang, max_lines=50)
                st.code(preview, language=code_lang)
                
                file_ext = ".py" if code_lang == "python" else ".html"
                st.download_button(
                    label="⬇️ Download",
                    data=code_entry['code'],
                    file_name=f"code_{idx}_{code_entry['timestamp'].strftime('%Y%m%d_%H%M%S')}{file_ext}",
                    mime="text/plain",
                    key=f"download_code_{idx}"
                )
    
    # Display documents
    if content_filter in ["All", "Documents"] and st.session_state.generated_documents:
        st.markdown("#### 📝 Generated Documents")
        
        filtered_docs = st.session_state.generated_documents
        if search_term:
            filtered_docs = [
                d for d in filtered_docs
                if search_term.lower() in d['title'].lower() or
                   search_term.lower() in d['doc_type'].lower()
            ]
        
        for idx, doc_entry in enumerate(reversed(filtered_docs)):
            with st.expander(f"📄 {doc_entry['doc_type']} - {doc_entry['timestamp'].strftime('%Y-%m-%d %H:%M')}"):
                st.markdown(f"**Title:** {doc_entry['title']}")
                st.markdown(f"**Input:** {doc_entry['input'][:200]}...")
                st.markdown(f"**Response Time:** {doc_entry['response_time']:.2f}s")
                
                st.markdown("**Generated Content:**")
                st.code(doc_entry['output'])
                
                st.download_button(
                    label="⬇️ Download",
                    data=doc_entry['output'],
                    file_name=f"{doc_entry['doc_type'].lower().replace(' ', '_')}_{idx}.txt",
                    mime="text/plain",
                    key=f"download_doc_{idx}"
                )
    
    if not st.session_state.generated_codes and not st.session_state.generated_documents:
        st.info("📭 No content generated yet. Start creating!")

# ============================================================================
# TAB 4: ANALYTICS
# ============================================================================

with tab4:
    st.markdown("### 📊 Analytics Dashboard")
    
    stats = get_statistics()
    
    # KPI Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f'<div class="metric-card"><div class="metric-label">Total Generated</div><div class="metric-value">{stats["total_all"]}</div></div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown(f'<div class="metric-card"><div class="metric-label">Code Files</div><div class="metric-value">{stats["total_codes"]}</div></div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown(f'<div class="metric-card"><div class="metric-label">Documents</div><div class="metric-value">{stats["total_documents"]}</div></div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown(f'<div class="metric-card"><div class="metric-label">HTML/CSS</div><div class="metric-value">{stats["html"]}</div></div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Document generation history
    if st.session_state.history:
        st.markdown("#### 📜 Recent Document Generations")
        
        for i, rec in enumerate(st.session_state.history[:10]):
            with st.expander(f"{i+1}. {rec['timestamp'][:19]} - {rec['doc_type']} (Status: {rec['status_code']})"):
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**Request:**")
                    st.json(rec["payload"])
                with col2:
                    st.markdown("**Response:**")
                    st.code(rec["response"][:500] + "..." if len(rec["response"]) > 500 else rec["response"])
                st.caption(f"Response time: {rec.get('response_time', 0):.2f}s")

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")
st.markdown("""
<div class="footer">
    <p>🤖 AI-Powered Code & Document Generation Hub</p>
    <p>Built with Streamlit | Secure webhook integration | Real-time generation</p>
</div>
""", unsafe_allow_html=True)
