import streamlit as st
import pandas as pd
import requests
import json
import re
from io import BytesIO
from datetime import datetime

# Attempt to import ReportLab for PDF generation (from file 2)
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
    from html.parser import HTMLParser
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    
# ==========================================
# PAGE CONFIG (from file 1)
# ==========================================
st.set_page_config(
    page_title="Unified Streamlit Application",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# CUSTOM CSS (from file 1)
# ==========================================
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        font-weight: 600;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        margin-left: 20%;
    }
    .assistant-message {
        background: #f0f2f6;
        color: #1f1f1f;
        margin-right: 20%;
    }
    .system-message {
        background: #e8f4f8;
        color: #0066cc;
        border-left: 4px solid #0066cc;
    }
    .webhook-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        border: 2px solid #e0e0e0;
        margin-bottom: 1rem;
        transition: all 0.3s;
    }
    .webhook-card:hover {
        border-color: #667eea;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2);
    }
    .metric-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
    }
    .status-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        font-size: 0.85rem;
        font-weight: 600;
    }
    .status-success { background: #d4edda; color: #155724; }
    .status-error { background: #f8d7da; color: #721c24; }
    .status-pending { background: #fff3cd; color: #856404; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# SESSION STATE INITIALIZATION (from file 1)
# ==========================================
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "webhook_history" not in st.session_state:
    st.session_state.webhook_history = []
if "selected_webhook" not in st.session_state:
    st.session_state.selected_webhook = "Newsletter"
if "current_conversation" not in st.session_state:
    st.session_state.current_conversation = []
if "code_data" not in st.session_state:
    st.session_state.code_data = pd.DataFrame()
if "sheet_url" not in st.session_state:
    st.session_state.sheet_url = "https://docs.google.com/spreadsheets/d/1eFZcnDoGT2NJHaEQSgxW5psN5kvlkYx1vtuXGRFTGTk/export?format=csv"
if "selected_code_number" not in st.session_state:
    st.session_state.selected_code_number = None
if "current_code" not in st.session_state:
    st.session_state.current_code = "<h1>Welcome</h1><p>Please load data to begin.</p>"
if "selected_code_row" not in st.session_state:
    st.session_state.selected_code_row = {'Title': 'Welcome', 'Category': 'Info', 'Description': 'Load Google Sheet data to begin'}
if "edit_mode" not in st.session_state:
    st.session_state.edit_mode = False
if "halt_edit" not in st.session_state:
    st.session_state.halt_edit = False
if "show_live_preview" not in st.session_state:
    st.session_state.show_live_preview = True
if "show_code_panel" not in st.session_state:
    st.session_state.show_code_panel = False
if "webhook_simple_history" not in st.session_state:
    st.session_state.webhook_simple_history = []

# ==========================================
# WEBHOOK CONFIGURATIONS (from file 1)
# ==========================================
WEBHOOK_BASE = "https://agentonline-u29564.vm.elestio.app/webhook"
WEBHOOKS = {
    "Newsletter": {
        "url": f"{WEBHOOK_BASE}/newsletter-trigger",
        "icon": "📧",
        "description": "Create engaging newsletters with AI assistance",
        "prompt_template": "Create a professional newsletter about: {topic}",
        "examples": ["Product launch announcement", "Monthly company update", "Industry insights roundup"]
    },
    "Landing Page": {
        "url": f"{WEBHOOK_BASE}/landingpage-trigger",
        "icon": "🌐",
        "description": "Generate high-converting landing pages",
        "prompt_template": "Design a landing page for: {topic}",
        "examples": ["SaaS product launch", "Event registration", "Lead magnet download"]
    },
    "Business Letter": {
        "url": f"{WEBHOOK_BASE}/business-letter-trigger",
        "icon": "📝",
        "description": "Craft professional business correspondence",
        "prompt_template": "Write a business letter regarding: {topic}",
        "examples": ["Partnership proposal", "Client introduction", "Formal complaint"]
    },
    "Email Sequence": {
        "url": f"{WEBHOOK_BASE}/email-sequence-trigger",
        "icon": "📬",
        "description": "Build automated email sequences",
        "prompt_template": "Create an email sequence for: {topic}",
        "examples": ["Onboarding sequence", "Sales nurture campaign", "Re-engagement series"]
    },
    "Invoice": {
        "url": f"{WEBHOOK_BASE}/invoice-trigger",
        "icon": "💰",
        "description": "Generate professional invoices",
        "prompt_template": "Create an invoice for: {topic}",
        "examples": ["Consulting services", "Product sale", "Subscription billing"]
    },
    "Business Contract": {
        "url": f"{WEBHOOK_BASE}/business-contract-trigger",
        "icon": "📄",
        "description": "Draft legal business contracts",
        "prompt_template": "Draft a contract for: {topic}",
        "examples": ["Service agreement", "NDA", "Partnership agreement"]
    }
}

# ==========================================
# HELPER FUNCTIONS (Combined and Refined)
# ==========================================

@st.cache_data(show_spinner="Loading data from Google Sheet...")
def load_data(url):
    """Load data from Google Sheets CSV export (from file 1 & 2)"""
    try:
        df = pd.read_csv(url)
        required_columns = ['Number', 'Code']
        optional_columns = ['Title', 'Category', 'Description']
        
        for col in required_columns:
            if col not in df.columns:
                st.error(f"Google Sheet must have '{col}' column.")
                return pd.DataFrame(columns=required_columns + optional_columns)
        
        for col in optional_columns:
            if col not in df.columns:
                if col == 'Title':
                    df[col] = df['Number'].astype(str) + " - Custom Code"
                elif col == 'Category':
                    df[col] = "Custom"
                elif col == 'Description':
                    df[col] = "Custom HTML/CSS code from Google Sheets"
        
        # Ensure 'Number' is unique and set as index for easy lookup
        df = df.drop_duplicates(subset=['Number'], keep='first')
        df = df.set_index('Number', drop=False)
        
        return df
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return pd.DataFrame(columns=['Number', 'Code', 'Title', 'Category', 'Description'])

def send_webhook(webhook_url, payload):
    """Send webhook request and return response (from file 1)"""
    try:
        resp = requests.post(webhook_url, json=payload, timeout=30)
        return {
            "success": resp.status_code < 300,
            "status_code": resp.status_code,
            "response": resp.text,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            "success": False,
            "status_code": 0,
            "response": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

def add_to_chat_history(role, content, metadata=None):
    """Add message to chat history (from file 1)"""
    st.session_state.chat_history.append({
        "role": role,
        "content": content,
        "timestamp": datetime.utcnow().isoformat(),
        "metadata": metadata or {}
    })

def clean_html_for_download(html_content):
    """Clean HTML content for download - embed CSS properly without showing raw code (from file 1 & 2)"""
    # Extract CSS from style tags
    css_pattern = r'<style[^>]*>(.*?)</style>'
    css_matches = re.findall(css_pattern, html_content, re.DOTALL)
    
    # Remove script tags completely
    html_content = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.DOTALL)
    
    # If CSS found, ensure it's properly embedded in head
    if css_matches:
        combined_css = '\n'.join(css_matches)
        
        # Remove existing style tags
        html_content = re.sub(css_pattern, '', html_content, flags=re.DOTALL)
        
        # Add CSS to head section
        if '<head>' in html_content:
            html_content = html_content.replace('<head>', f'<head>\n<style>\n{combined_css}\n</style>')
        else:
            # Add head section if missing
            html_content = html_content.replace('<html>', f'<html>\n<head>\n<style>\n{combined_css}\n</style>\n</head>')
    
    return html_content

def generate_pdf_from_html(html_content, title="Document"):
    """Generate PDF from HTML with improved formatting (from file 2)"""
    if not REPORTLAB_AVAILABLE:
        st.error("PDF generation requires the 'reportlab' package. Please install it.")
        return None
        
    class EnhancedHTMLParser(HTMLParser):
        # ... (Parser implementation from file 2) ...
        def __init__(self):
            super().__init__()
            self.content = []
            self.current_text = ""
            self.in_title = False
            self.in_header = False
            self.in_paragraph = False
            self.in_list = False
            self.in_table = False
            self.header_level = 1
            self.list_items = []
            self.table_rows = []
            self.current_row = []
            
        def handle_starttag(self, tag, attrs):
            if tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                self.in_header = True
                self.header_level = int(tag[1])
            elif tag == 'p':
                self.in_paragraph = True
            elif tag in ['ul', 'ol']:
                self.in_list = True
                self.list_items = []
            elif tag == 'li':
                self.current_text = ""
            elif tag == 'title':
                self.in_title = True
            elif tag == 'table':
                self.in_table = True
                self.table_rows = []
            elif tag == 'tr':
                self.current_row = []
            elif tag == 'br':
                self.current_text += "\n"
                
        def handle_endtag(self, tag):
            if tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                if self.current_text.strip():
                    self.content.append(('header', self.current_text.strip(), self.header_level))
                self.current_text = ""
                self.in_header = False
            elif tag == 'p':
                if self.current_text.strip():
                    self.content.append(('paragraph', self.current_text.strip()))
                self.current_text = ""
                self.in_paragraph = False
            elif tag in ['ul', 'ol']:
                if self.list_items:
                    self.content.append(('list', self.list_items))
                self.in_list = False
            elif tag == 'li':
                if self.current_text.strip():
                    self.list_items.append(self.current_text.strip())
                self.current_text = ""
            elif tag == 'title':
                self.in_title = False
            elif tag == 'table':
                if self.table_rows:
                    self.content.append(('table', self.table_rows))
                self.in_table = False
            elif tag == 'tr':
                if self.current_row:
                    self.table_rows.append(self.current_row)
            elif tag in ['td', 'th']:
                if self.current_text.strip():
                    self.current_row.append(self.current_text.strip())
                self.current_text = ""
                
        def handle_data(self, data):
            if not self.in_title:  # Skip title content
                self.current_text += data
                
        def get_content(self):
            # Add any remaining text as paragraph
            if self.current_text.strip():
                self.content.append(('paragraph', self.current_text.strip()))
            return self.content

    try:
        # Create PDF buffer
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=1*inch, bottomMargin=1*inch)
        
        # Enhanced styles
        styles = getSampleStyleSheet()
        
        # Custom styles for better formatting
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Title'],
            fontSize=24,
            spaceAfter=30,
            textColor=colors.HexColor('#2c3e50'),
            alignment=TA_CENTER
        )
        
        heading_styles = {
            1: ParagraphStyle('CustomH1', parent=styles['Heading1'], fontSize=20, spaceAfter=20, textColor=colors.HexColor('#34495e')),
            2: ParagraphStyle('CustomH2', parent=styles['Heading2'], fontSize=18, spaceAfter=18, textColor=colors.HexColor('#34495e')),
            3: ParagraphStyle('CustomH3', parent=styles['Heading3'], fontSize=16, spaceAfter=16, textColor=colors.HexColor('#34495e')),
            4: ParagraphStyle('CustomH4', parent=styles['Heading4'], fontSize=14, spaceAfter=14, textColor=colors.HexColor('#34495e')),
            5: ParagraphStyle('CustomH5', parent=styles['Heading5'], fontSize=12, spaceAfter=12, textColor=colors.HexColor('#34495e')),
            6: ParagraphStyle('CustomH6', parent=styles['Heading6'], fontSize=11, spaceAfter=11, textColor=colors.HexColor('#34495e'))
        }
        
        body_style = ParagraphStyle(
            'CustomBody',
            parent=styles['Normal'],
            fontSize=11,
            spaceAfter=12,
            leading=14,
            textColor=colors.HexColor('#2c3e50'),
            alignment=TA_JUSTIFY
        )
        
        list_style = ParagraphStyle(
            'CustomList',
            parent=styles['Normal'],
            fontSize=11,
            leftIndent=20,
            spaceAfter=6,
            leading=14,
            textColor=colors.HexColor('#2c3e50')
        )
        
        # Parse HTML content
        parser = EnhancedHTMLParser()
        parser.feed(html_content)
        content_elements = parser.get_content()
        
        # Build PDF content
        story = []
        
        # Add title
        story.append(Paragraph(title, title_style))
        story.append(Spacer(1, 20))
        
        # Process parsed content
        for element in content_elements:
            if element[0] == 'header':
                level = element[2] if len(element) > 2 else 1
                style = heading_styles.get(level, heading_styles[1])
                story.append(Paragraph(element[1], style))
                
            elif element[0] == 'paragraph':
                # Clean up text and handle special characters
                text = element[1].replace('&nbsp;', ' ').replace('&amp;', '&')
                story.append(Paragraph(text, body_style))
                
            elif element[0] == 'list':
                for item in element[1]:
                    story.append(Paragraph(f"• {item}", list_style))
                story.append(Spacer(1, 10))
                
            elif element[0] == 'table':
                if element[1]:  # If table has rows
                    table_data = element[1]
                    table = Table(table_data)
                    table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f8f9fa')),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
                        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, 0), 10),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                        ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#2c3e50')),
                        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                        ('FONTSIZE', (0, 1), (-1, -1), 9),
                        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#dee2e6'))
                    ]))
                    story.append(table)
                    story.append(Spacer(1, 15))
        
        # If no structured content found, fall back to simple text extraction
        if not story or len(story) <= 2:  # Only title and spacer
            # Simple text extraction as fallback
            clean_text = re.sub(r'<[^>]+>', ' ', html_content)
            clean_text = re.sub(r'\s+', ' ', clean_text).strip()
            
            if clean_text:
                # Split into paragraphs
                paragraphs = [p.strip() for p in clean_text.split('\n') if p.strip()]
                if not paragraphs:
                    paragraphs = [clean_text[:1000] + "..." if len(clean_text) > 1000 else clean_text]
                
                for para in paragraphs:
                    if para:
                        story.append(Paragraph(para, body_style))
                        story.append(Spacer(1, 12))
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
        
    except Exception as e:
        st.error(f"Error generating PDF: {str(e)}")
        return None

# ==========================================
# SIDEBAR - NAVIGATION & CONFIGURATION
# ==========================================
with st.sidebar:
    st.markdown("## 🎯 Navigation")
    
    # Combined navigation (from file 1)
    app_mode = st.radio(
        "Select Mode:",
        ["🎨 Code Viewer", "🤖 AI Webhook Chat", "📤 Simple Webhook Sender"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    # --- Quick Actions (from file 1) ---
    st.markdown("## ⚡ Quick Actions")
    
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.chat_history = []
        st.session_state.current_conversation = []
        st.rerun()
    
    if st.button("🔄 Reset All Data", use_container_width=True):
        st.session_state.chat_history = []
        st.session_state.webhook_history = []
        st.session_state.current_conversation = []
        st.session_state.webhook_simple_history = []
        st.session_state.code_data = pd.DataFrame()
        st.session_state.selected_code_number = None
        st.session_state.current_code = "<h1>Welcome</h1><p>Please load data to begin.</p>"
        st.session_state.selected_code_row = {'Title': 'Welcome', 'Category': 'Info', 'Description': 'Load Google Sheet data to begin'}
        st.rerun()
    
    st.markdown("---")
    
    # --- Statistics (from file 1) ---
    st.markdown("## 📈 Statistics")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Chats", len(st.session_state.chat_history))
    with col2:
        st.metric("Webhooks Sent", len(st.session_state.webhook_history) + len(st.session_state.webhook_simple_history))
    
    if st.session_state.webhook_history or st.session_state.webhook_simple_history:
        total_webhooks = len(st.session_state.webhook_history) + len(st.session_state.webhook_simple_history)
        success_count = sum(1 for w in st.session_state.webhook_history if w.get("success", False))
        success_count += sum(1 for w in st.session_state.webhook_simple_history if w.get("status_code", 500) < 300)
        success_rate = (success_count / total_webhooks) * 100
        st.metric("Success Rate", f"{success_rate:.1f}%")

# ==========================================
# MAIN CONTENT AREA
# ==========================================

if app_mode == "🎨 Code Viewer":
    # ==========================================
    # CODE VIEWER MODE (from file 1 & 2)
    # ==========================================
    
    st.markdown("""
    <div class="main-header">
        <h1>🚀 Professional Code Viewer</h1>
        <p>Load, preview, and download HTML/CSS code from Google Sheets with enhanced features</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Google Sheets Input
    col1, col2 = st.columns([3, 1])
    with col1:
        sheet_url_input = st.text_input(
            "Google Sheet CSV URL:",
            value=st.session_state.sheet_url,
            help="Enter the CSV export URL of your Google Sheet"
        )
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔄 Load Data", use_container_width=True, type="primary"):
            st.session_state.sheet_url = sheet_url_input
            st.session_state.code_data = load_data(st.session_state.sheet_url)
            if not st.session_state.code_data.empty:
                st.session_state.selected_code_number = st.session_state.code_data.index[0]
                st.session_state.current_code = st.session_state.code_data.loc[st.session_state.selected_code_number]['Code']
                st.session_state.selected_code_row = st.session_state.code_data.loc[st.session_state.selected_code_number].to_dict()
            else:
                st.session_state.current_code = "<h1>No Data</h1><p>Please provide a valid Google Sheet URL.</p>"
                st.session_state.selected_code_row = {'Title': 'No Data', 'Category': 'Error', 'Description': 'No data available'}
            st.rerun()

    df = st.session_state.code_data
    
    if not df.empty:
        # Display Controls
        st.markdown("### 🎛️ Display Controls")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.session_state.show_live_preview = st.toggle("🔴 Live Preview", value=st.session_state.show_live_preview)
        with col2:
            st.session_state.show_code_panel = st.toggle("📝 Code Panel", value=st.session_state.show_code_panel)
        with col3:
            st.session_state.edit_mode = st.toggle("✏️ Edit Mode", value=st.session_state.edit_mode)
        with col4:
            st.session_state.halt_edit = st.toggle("🔒 Lock Edit", value=st.session_state.halt_edit)
        
        if st.session_state.halt_edit and st.session_state.edit_mode:
            st.warning("⚠️ Edit mode disabled due to edit lock")
            st.session_state.edit_mode = False
        
        # Category filter
        if 'Category' in df.columns:
            categories = ["All Categories"] + list(df['Category'].unique())
            selected_category = st.selectbox("Filter by Category:", categories)
            
            if selected_category != "All Categories":
                df_filtered = df[df['Category'] == selected_category]
            else:
                df_filtered = df
        else:
            df_filtered = df
        
        # Number selection
        numbers = df_filtered['Number'].tolist()
        
        if numbers:
            selected_number = st.selectbox("Choose Code Entry:", numbers, index=numbers.index(st.session_state.selected_code_number) if st.session_state.selected_code_number in numbers else 0)
            
            if selected_number != st.session_state.selected_code_number:
                st.session_state.selected_code_number = selected_number
                st.session_state.current_code = df_filtered.loc[selected_number]['Code']
                st.session_state.selected_code_row = df_filtered.loc[selected_number].to_dict()
                st.rerun()

            # Get selected row and code
            selected_row = st.session_state.selected_code_row
            current_code = st.session_state.current_code
            
            # Display selected item info
            st.markdown("### 📋 Selected Item Details")
            info_col1, info_col2, info_col3 = st.columns(3)
            with info_col1:
                st.info(f"**Title:** {selected_row.get('Title', 'N/A')}")
            with info_col2:
                st.info(f"**Category:** {selected_row.get('Category', 'N/A')}")
            with info_col3:
                st.info(f"**Number:** {selected_number}")
            
            st.markdown(f"**Description:** {selected_row.get('Description', 'N/A')}")
            
            st.markdown("---")
            
            # Main content display
            if st.session_state.show_live_preview and st.session_state.show_code_panel:
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    st.markdown("### 🔴 Live Preview")
                    if current_code:
                        st.components.v1.html(current_code, height=700, scrolling=True)
                    else:
                        st.info("No code to preview")
                
                with col2:
                    st.markdown("### 📝 Code Editor/Viewer")
                    if st.session_state.edit_mode and not st.session_state.halt_edit:
                        edited_code = st.text_area(
                            "Edit HTML/CSS Code:",
                            value=current_code,
                            height=600,
                            help="Edit the code and see live preview updates"
                        )
                        if edited_code != current_code:
                            st.session_state.current_code = edited_code
                            st.rerun()
                    else:
                        st.code(current_code, language="html", line_numbers=True)
            
            elif st.session_state.show_live_preview:
                st.markdown("### 🔴 Live Preview")
                if current_code:
                    st.components.v1.html(current_code, height=700, scrolling=True)
                else:
                    st.info("No code to preview")
            
            elif st.session_state.show_code_panel:
                st.markdown("### 📝 Code Editor/Viewer")
                if st.session_state.edit_mode and not st.session_state.halt_edit:
                    edited_code = st.text_area(
                        "Edit HTML/CSS Code:",
                        value=current_code,
                        height=600,
                        help="Edit the code and see live preview updates"
                    )
                    if edited_code != current_code:
                        st.session_state.current_code = edited_code
                        st.rerun()
                else:
                    st.code(current_code, language="html", line_numbers=True)
            else:
                st.info("📌 Enable Live Preview or Code Panel to view content")
            
            # Download Section
            st.markdown("---")
            st.markdown("### 📥 Download Options")
            
            col1, col2, col3 = st.columns(3)
            
            if current_code and current_code.strip():
                clean_html = clean_html_for_download(current_code)
                
                with col1:
                    # HTML Download
                    st.download_button(
                        label="🌐 Download HTML",
                        data=clean_html,
                        file_name=f"{selected_row.get('Title', 'document').replace(' ', '_')}.html",
                        mime="text/html",
                        help="Download as HTML file with embedded CSS",
                        use_container_width=True
                    )
                
                with col2:
                    # PDF Download (from file 2)
                    pdf_data = generate_pdf_from_html(current_code, selected_row.get('Title', 'Document'))
                    if pdf_data:
                        st.download_button(
                            label="📄 Download PDF",
                            data=pdf_data,
                            file_name=f"{selected_row.get('Title', 'document').replace(' ', '_')}.pdf",
                            mime="application/pdf",
                            help="Download as formatted PDF document",
                            use_container_width=True
                        )
                    else:
                        st.button("📄 Download PDF", use_container_width=True, disabled=True, help="ReportLab not installed or PDF generation failed.")

                with col3:
                    # Reset Code
                    if st.session_state.edit_mode and not st.session_state.halt_edit:
                        if st.button("🔄 Reset Code", use_container_width=True):
                            # Reset current code to the original from the dataframe
                            st.session_state.current_code = df_filtered.loc[st.session_state.selected_code_number]['Code']
                            st.rerun()
                    else:
                        st.write("") # Placeholder
            else:
                st.info("No code available for download.")

        else:
            st.info("No entries found for the selected category.")
    
    elif st.session_state.sheet_url:
        st.error("❌ No data loaded. Please check your Google Sheet URL and ensure it contains 'Number' and 'Code' columns.")
    else:
        st.warning("⚠️ Please enter a Google Sheet URL and click 'Load Data' to begin.")

elif app_mode == "🤖 AI Webhook Chat":
    # ==========================================
    # AI WEBHOOK CHAT MODE (from file 1)
    # ==========================================
    
    st.markdown("""
    <div class="main-header">
        <h1>🤖 AI Webhook Chat System</h1>
        <p>Intelligent conversation interface for webhook-based AI content generation</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Webhook Selection Section (moved from sidebar in file 1 to main content for this mode)
    st.markdown("## 🔗 Webhook Configuration")
    
    webhook_choice = st.selectbox(
        "Select Webhook Type:",
        list(WEBHOOKS.keys()),
        key="webhook_selector_chat"
    )
    
    webhook_info = WEBHOOKS[webhook_choice]
    st.session_state.selected_webhook = webhook_choice
    
    st.markdown(f"""
    <div class="webhook-card">
        <h3>{webhook_info['icon']} {webhook_choice}</h3>
        <p style='color: #666; font-size: 0.9rem;'>{webhook_info['description']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Custom webhook URL option
    use_custom_url = st.checkbox("Use Custom Webhook URL", value=False, key="chat_custom_url_toggle")
    
    if use_custom_url:
        webhook_url = st.text_input("Custom Webhook URL:", value=webhook_info['url'], key="chat_custom_url_input")
    else:
        webhook_url = webhook_info['url']
        st.text_input("Webhook URL:", value=webhook_url, disabled=True, key="chat_url_display")
    
    st.markdown("---")
    
    # Quick prompt templates
    st.markdown("### 💡 Quick Start Templates")
    template_cols = st.columns(3)
    
    for idx, example in enumerate(webhook_info['examples']):
        with template_cols[idx % 3]:
            if st.button(f"📝 {example}", key=f"template_btn_{idx}", use_container_width=True):
                # Send the template prompt as a user message and trigger the webhook
                prompt = webhook_info['prompt_template'].format(topic=example)
                
                # 1. Add user message to chat
                add_to_chat_history("user", prompt)
                
                # 2. Send webhook
                payload = {
                    "title": f"{webhook_choice} - {example}",
                    "type": "text",
                    "text": prompt,
                    "category": webhook_choice,
                    "timestamp": datetime.utcnow().isoformat()
                }
                
                response_data = send_webhook(webhook_url, payload)
                st.session_state.webhook_history.append(response_data)
                
                # 3. Add system/assistant response to chat
                status = "success" if response_data["success"] else "error"
                system_message = f"Webhook sent to `{webhook_url}`. Status Code: **{response_data['status_code']}**."
                add_to_chat_history("system", system_message, {"status": status})
                
                assistant_response = f"**Webhook Response:**\n\n```json\n{response_data['response'][:500]}...\n```"
                add_to_chat_history("assistant", assistant_response)
                
                st.rerun()
    
    st.markdown("---")
    
    # Chat Interface
    st.markdown("### 💬 Conversation")
    
    # Display chat history
    chat_container = st.container()
    
    with chat_container:
        for message in st.session_state.chat_history:
            role = message['role']
            content = message['content']
            timestamp = message['timestamp']
            
            if role == "user":
                st.markdown(f"""
                <div class="chat-message user-message">
                    <strong>👤 You</strong> <span style='font-size: 0.8rem; opacity: 0.7;'>({timestamp[:19]})</span><br>
                    {content}
                </div>
                """, unsafe_allow_html=True)
            
            elif role == "assistant":
                st.markdown(f"""
                <div class="chat-message assistant-message">
                    <strong>🤖 Assistant</strong> <span style='font-size: 0.8rem; opacity: 0.7;'>({timestamp[:19]})</span><br>
                    {content}
                </div>
                """, unsafe_allow_html=True)
            
            elif role == "system":
                status = message.get('metadata', {}).get('status', 'pending')
                status_class = f"status-{'success' if status == 'success' else 'error' if status == 'error' else 'pending'}"
                st.markdown(f"""
                <div class="chat-message system-message">
                    <strong>⚙️ System</strong> <span class='status-badge {status_class}'>{status.upper()}</span><br>
                    {content}
                </div>
                """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Input Section
    st.markdown("### ✍️ Send Message")
    
    input_col1, input_col2 = st.columns([4, 1])
    
    with input_col1:
        user_input = st.text_area(
            "Your message:",
            height=150,
            placeholder=f"Enter your prompt for the {webhook_choice} webhook...",
            label_visibility="collapsed",
            key="chat_input_area"
        )
    
    with input_col2:
        st.markdown("<br>", unsafe_allow_html=True)
        
        send_as_webhook = st.checkbox("📤 Send to Webhook", value=True, key="send_as_webhook_toggle")
        
        if st.button("🚀 Send", type="primary", use_container_width=True):
            if user_input.strip():
                # 1. Add user message to chat
                add_to_chat_history("user", user_input)
                
                if send_as_webhook:
                    # 2. Send webhook
                    payload = {
                        "title": f"{webhook_choice} - Custom Prompt",
                        "type": "text",
                        "text": user_input,
                        "category": webhook_choice,
                        "timestamp": datetime.utcnow().isoformat()
                    }
                    
                    response_data = send_webhook(webhook_url, payload)
                    st.session_state.webhook_history.append(response_data)
                    
                    # 3. Add system/assistant response to chat
                    status = "success" if response_data["success"] else "error"
                    system_message = f"Webhook sent to `{webhook_url}`. Status Code: **{response_data['status_code']}**."
                    add_to_chat_history("system", system_message, {"status": status})
                    
                    assistant_response = f"**Webhook Response:**\n\n```json\n{response_data['response'][:500]}...\n```"
                    add_to_chat_history("assistant", assistant_response)
                else:
                    # Simple echo/info if not sending to webhook
                    add_to_chat_history("assistant", f"Message received: '{user_input[:50]}...' (Webhook send disabled)")
                
                st.rerun()
            else:
                st.warning("Please enter a message to send.")

elif app_mode == "📤 Simple Webhook Sender":
    # ==========================================
    # SIMPLE WEBHOOK SENDER MODE (from file 2)
    # ==========================================
    
    st.markdown("""
    <div class="main-header">
        <h1>📤 Simple Webhook Text Sender</h1>
        <p>A straightforward interface to send text payloads to a selected webhook URL.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Webhook Selection
    webhook_choice = st.selectbox("Select webhook", list(WEBHOOKS.keys()), key="simple_webhook_select")
    webhook_url = st.text_input("Webhook URL", value=WEBHOOKS[webhook_choice]['url'], key="simple_webhook_url")
    
    title = st.text_input("Title", value=f"{webhook_choice} - {datetime.utcnow().isoformat()[:19]}", key="simple_title")
    
    text_input = st.text_area(
        "Enter the text you want to send",
        height=300,
        key="simple_text_input"
    )
    
    send_button = st.button("Send Webhook", type="primary", use_container_width=True)
    
    # --------------------------
    # SEND REQUEST
    # --------------------------
    if send_button:
        if not text_input.strip():
            st.error("Please enter text to send.")
        else:
            payload = {
                "title": title,
                "type": "text",
                "text": text_input,
                "category": webhook_choice,
            }

            try:
                resp = requests.post(webhook_url, json=payload, timeout=20)

                # raw response text only
                try:
                    resp_body = resp.text
                except:
                    resp_body = ""

                # store in history
                st.session_state.webhook_simple_history.insert(0, {
                    "timestamp": datetime.utcnow().isoformat(),
                    "webhook": webhook_url,
                    "status_code": resp.status_code,
                    "payload": payload,
                    "response": resp_body,
                })

                st.subheader("Response")
                st.code(resp_body)

                if resp.status_code < 300:
                    st.success(f"Sent successfully! Status {resp.status_code}")
                else:
                    st.warning(f"Request failed with status {resp.status_code}")

            except Exception as e:
                st.error(f"Request failed: {e}")

    # --------------------------
    # HISTORY
    # --------------------------
    st.markdown("---")
    st.header("History (Last 10 Simple Webhooks)")
    
    if st.session_state.webhook_simple_history:
        for i, rec in enumerate(st.session_state.webhook_simple_history[:10]):
            with st.expander(f"{i+1}. {rec['timestamp'][:19]} → {rec['webhook']}"):
                st.subheader("Payload")
                st.json(rec["payload"])
                st.subheader("Response")
                st.code(rec["response"])
    else:
        st.info("No simple webhooks sent yet.")
