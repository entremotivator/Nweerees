import streamlit as st
import pandas as pd
import requests
import json
import re
from io import BytesIO
from datetime import datetime
import time
import altair as alt

# Attempt to import ReportLab for PDF generation
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
# PAGE CONFIG
# ==========================================
st.set_page_config(
    page_title="Ultimate Unified Streamlit Platform v3.0 - Complete Edition",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# CUSTOM CSS
# ==========================================
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        padding: 2.5rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 2.5rem;
        box-shadow: 0 10px 20px rgba(0,0,0,0.15);
    }
    .main-header h1 {
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
        font-weight: 700;
    }
    .main-header p {
        font-size: 1.1rem;
        opacity: 0.95;
    }
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        height: 3.5em;
        font-weight: 700;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .user-message {
        background: linear-gradient(135deg, #4CAF50 0%, #8BC34A 100%);
        color: white;
        margin-left: 20%;
    }
    .assistant-message {
        background: #e3f2fd;
        color: #1f1f1f;
        margin-right: 20%;
        border-left: 5px solid #2196F3;
    }
    .system-message {
        background: #fff3e0;
        color: #ff9800;
        border-left: 4px solid #ff9800;
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
        border-color: #2a5298;
        box-shadow: 0 4px 12px rgba(42, 82, 152, 0.2);
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
    .data-stat-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
    }
    .data-stat-card h3 {
        margin: 0;
        font-size: 2rem;
        font-weight: 700;
    }
    .data-stat-card p {
        margin: 0.5rem 0 0 0;
        font-size: 0.9rem;
        opacity: 0.9;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# SESSION STATE INITIALIZATION
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
if "code_display_mode" not in st.session_state:
    st.session_state.code_display_mode = "Prettify"
if "uploaded_data" not in st.session_state:
    st.session_state.uploaded_data = pd.DataFrame()
if "data_load_stats" not in st.session_state:
    st.session_state.data_load_stats = {"total_rows": 0, "load_time": 0, "duplicates": 0}
if "force_refresh_counter" not in st.session_state:
    st.session_state.force_refresh_counter = 0

# ==========================================
# WEBHOOK CONFIGURATIONS
# ==========================================
WEBHOOK_BASE = "https://agentonline-u29564.vm.elestio.app/webhook"
WEBHOOKS = {
    "Newsletter": {
        "url": f"{WEBHOOK_BASE}/newsletter-trigger",
        "icon": "📧",
        "description": "Create engaging newsletters with AI assistance",
        "prompt_template": "Create a professional newsletter about: {topic} for a target audience of {audience}. The tone should be {tone}.",
        "fields": ["topic", "audience", "tone"],
        "examples": [
            {"topic": "Product launch announcement", "audience": "Tech enthusiasts", "tone": "Excited and informative"},
            {"topic": "Monthly company update", "audience": "Investors", "tone": "Formal and analytical"},
            {"topic": "Industry insights roundup", "audience": "Small business owners", "tone": "Practical and encouraging"}
        ]
    },
    "Landing Page": {
        "url": f"{WEBHOOK_BASE}/landingpage-trigger",
        "icon": "🌐",
        "description": "Generate high-converting landing pages",
        "prompt_template": "Design a landing page for: {product} with a focus on {benefit}. The call-to-action is {cta}.",
        "fields": ["product", "benefit", "cta"],
        "examples": [
            {"product": "SaaS product launch", "benefit": "Saving 50% on cloud costs", "cta": "Start Free Trial"},
            {"product": "Event registration", "benefit": "Networking with industry leaders", "cta": "Register Now"},
            {"product": "Lead magnet download", "benefit": "Mastering Streamlit in 1 hour", "cta": "Download Ebook"}
        ]
    },
    "Business Letter": {
        "url": f"{WEBHOOK_BASE}/business-letter-trigger",
        "icon": "📝",
        "description": "Craft professional business correspondence",
        "prompt_template": "Write a business letter regarding: {subject} to {recipient_type}. The desired outcome is {outcome}.",
        "fields": ["subject", "recipient_type", "outcome"],
        "examples": [
            {"subject": "Partnership proposal", "recipient_type": "CEO of a logistics company", "outcome": "A follow-up meeting"},
            {"subject": "Client introduction", "recipient_type": "New potential client", "outcome": "A positive first impression"},
            {"subject": "Formal complaint", "recipient_type": "Supplier management", "outcome": "A full refund and apology"}
        ]
    },
    "Email Sequence": {
        "url": f"{WEBHOOK_BASE}/email-sequence-trigger",
        "icon": "📬",
        "description": "Build automated email sequences",
        "prompt_template": "Create an email sequence for: {purpose} over {duration} days. The main goal is {goal}.",
        "fields": ["purpose", "duration", "goal"],
        "examples": [
            {"purpose": "Onboarding sequence", "duration": "7", "goal": "First feature usage"},
            {"purpose": "Sales nurture campaign", "duration": "14", "goal": "Book a demo"},
            {"purpose": "Re-engagement series", "duration": "30", "goal": "Active subscription renewal"}
        ]
    },
    "Invoice": {
        "url": f"{WEBHOOK_BASE}/invoice-trigger",
        "icon": "💰",
        "description": "Generate professional invoices",
        "prompt_template": "Create an invoice for: {client} for {service} totaling {amount} USD.",
        "fields": ["client", "service", "amount"],
        "examples": [
            {"client": "Acme Corp", "service": "Consulting services", "amount": "5000"},
            {"client": "Jane Doe", "service": "Product sale (Pro License)", "amount": "999"},
            {"client": "Global Subscriptions", "service": "Subscription billing (Q4)", "amount": "12000"}
        ]
    },
    "Business Contract": {
        "url": f"{WEBHOOK_BASE}/business-contract-trigger",
        "icon": "📄",
        "description": "Draft legal business contracts",
        "prompt_template": "Draft a contract for: {type} between {party_a} and {party_b} with a term of {term}.",
        "fields": ["type", "party_a", "party_b", "term"],
        "examples": [
            {"type": "Service agreement", "party_a": "My Company", "party_b": "Client X", "term": "12 months"},
            {"type": "NDA", "party_a": "Innovator Y", "party_b": "Investor Z", "term": "5 years"},
            {"type": "Partnership agreement", "party_a": "Alpha Partner", "party_b": "Beta Partner", "term": "Indefinite"}
        ]
    },
    "Code Generator": {
        "url": f"{WEBHOOK_BASE}/code-generator-trigger",
        "icon": "💻",
        "description": "Generate code snippets in any language",
        "prompt_template": "Generate a {language} function to {task} and include a brief explanation.",
        "fields": ["language", "task"],
        "examples": [
            {"language": "Python", "task": "read a CSV file into a Pandas DataFrame"},
            {"language": "JavaScript", "task": "validate an email address using a regular expression"},
            {"language": "SQL", "task": "select all users who have placed more than 5 orders"}
        ]
    }
}

# ==========================================
# HELPER FUNCTIONS
# ==========================================

def load_data_with_retry(url, max_retries=3, force_refresh=False):
    """
    Load ALL data from Google Sheets with retry logic and cache busting.
    This ensures complete data retrieval without row limitations.
    """
    start_time = time.time()
    
    for attempt in range(max_retries):
        try:
            # Add timestamp to URL to bypass caching if force_refresh is True
            cache_buster = f"&_cb={int(time.time())}" if force_refresh else ""
            full_url = url + cache_buster
            
            # Use low_memory=False to handle large datasets and ensure all rows are read
            # Set dtype to object for flexibility with mixed data types
            df = pd.read_csv(
                full_url,
                low_memory=False,
                dtype=str,  # Read all as strings to avoid type inference issues
                na_filter=True,
                keep_default_na=True,
                encoding='utf-8'
            )
            
            # Validate required columns
            required_columns = ['Number', 'Code']
            optional_columns = ['Title', 'Category', 'Description']
            
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                error_msg = f"Missing required columns: {', '.join(missing_columns)}"
                st.error(error_msg)
                return pd.DataFrame(columns=required_columns + optional_columns), {
                    "total_rows": 0,
                    "load_time": time.time() - start_time,
                    "duplicates": 0,
                    "error": error_msg
                }
            
            # Add optional columns if missing
            for col in optional_columns:
                if col not in df.columns:
                    if col == 'Title':
                        df[col] = df['Number'].astype(str) + " - Custom Code"
                    elif col == 'Category':
                        df[col] = "Custom"
                    elif col == 'Description':
                        df[col] = "Custom HTML/CSS code from Google Sheets"
            
            # Remove completely empty rows
            df = df.dropna(how='all')
            
            # Check for duplicate Numbers
            duplicates_count = df['Number'].duplicated().sum()
            
            # Keep first occurrence of duplicates
            df = df.drop_duplicates(subset=['Number'], keep='first')
            
            # Convert Number column and set as index
            df['Number'] = pd.to_numeric(df['Number'], errors='coerce')
            df = df.dropna(subset=['Number'])  # Remove rows where Number couldn't be converted
            df['Number'] = df['Number'].astype(int)
            
            # Set Number as index for easy lookup
            df = df.set_index('Number', drop=False)
            
            load_time = time.time() - start_time
            
            stats = {
                "total_rows": len(df),
                "load_time": load_time,
                "duplicates": duplicates_count,
                "columns": list(df.columns),
                "attempt": attempt + 1
            }
            
            return df, stats
            
        except requests.exceptions.RequestException as e:
            if attempt < max_retries - 1:
                wait_time = (attempt + 1) * 2  # Exponential backoff: 2s, 4s, 6s
                st.warning(f"Attempt {attempt + 1} failed. Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                error_msg = f"Failed to load data after {max_retries} attempts: {str(e)}"
                st.error(error_msg)
                return pd.DataFrame(columns=['Number', 'Code', 'Title', 'Category', 'Description']), {
                    "total_rows": 0,
                    "load_time": time.time() - start_time,
                    "duplicates": 0,
                    "error": error_msg
                }
        
        except Exception as e:
            error_msg = f"Unexpected error loading data: {str(e)}"
            st.error(error_msg)
            return pd.DataFrame(columns=['Number', 'Code', 'Title', 'Category', 'Description']), {
                "total_rows": 0,
                "load_time": time.time() - start_time,
                "duplicates": 0,
                "error": error_msg
            }
    
    # Should never reach here
    return pd.DataFrame(columns=['Number', 'Code', 'Title', 'Category', 'Description']), {
        "total_rows": 0,
        "load_time": time.time() - start_time,
        "duplicates": 0,
        "error": "Unknown error"
    }

def send_webhook(webhook_url, payload):
    """Send webhook request and return detailed response"""
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
    """Add message to chat history with timestamp"""
    st.session_state.chat_history.append({
        "role": role,
        "content": content,
        "timestamp": datetime.utcnow().isoformat(),
        "metadata": metadata or {}
    })

def clean_html_for_download(html_content):
    """Clean HTML content for download - embed CSS properly"""
    css_pattern = r'<style[^>]*>(.*?)</style>'
    css_matches = re.findall(css_pattern, html_content, re.DOTALL)
    
    # Remove script tags completely for security
    html_content = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.DOTALL)
    
    # Embed CSS properly in head
    if css_matches:
        combined_css = '\n'.join(css_matches)
        html_content = re.sub(css_pattern, '', html_content, flags=re.DOTALL)
        
        if '<head>' in html_content:
            html_content = html_content.replace('<head>', f'<head>\n<style>\n{combined_css}\n</style>')
        elif '<html>' in html_content:
            html_content = html_content.replace('<html>', f'<html>\n<head>\n<style>\n{combined_css}\n</style>\n</head>')
        else:
            html_content = f'<!DOCTYPE html>\n<html>\n<head>\n<style>\n{combined_css}\n</style>\n</head>\n<body>\n{html_content}\n</body>\n</html>'
    
    return html_content

def prettify_html(html_content):
    """Prettify HTML/CSS content for better readability"""
    html_content = re.sub(r'(?<=>)(<[^/])', r'\n\1', html_content)
    html_content = re.sub(r'(?<=/?>)(<)', r'\n\1', html_content)
    
    lines = html_content.split('\n')
    indent_level = 0
    prettified_lines = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        if line.startswith('</') or line.startswith('}'):
            indent_level = max(0, indent_level - 1)
        
        prettified_lines.append('    ' * indent_level + line)
        
        if not line.startswith('</') and not line.startswith('}') and ('<' in line and '>' in line) and not line.endswith('/>'):
            if not line.startswith('<br') and not line.startswith('<hr'):
                indent_level += 1
    
    return '\n'.join(prettified_lines)

def generate_pdf_from_html(html_content, title="Document"):
    """Generate PDF from HTML with enhanced formatting"""
    if not REPORTLAB_AVAILABLE:
        return None
    
    class EnhancedHTMLParser(HTMLParser):
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
            if not self.in_title:
                self.current_text += data
        
        def get_content(self):
            if self.current_text.strip():
                self.content.append(('paragraph', self.current_text.strip()))
            return self.content
    
    try:
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=1*inch, bottomMargin=1*inch)
        
        styles = getSampleStyleSheet()
        
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
        
        parser = EnhancedHTMLParser()
        parser.feed(html_content)
        content_elements = parser.get_content()
        
        story = []
        story.append(Paragraph(title, title_style))
        story.append(Spacer(1, 20))
        
        for element in content_elements:
            if element[0] == 'header':
                level = element[2] if len(element) > 2 else 1
                style = heading_styles.get(level, heading_styles[1])
                story.append(Paragraph(element[1], style))
            
            elif element[0] == 'paragraph':
                text = element[1].replace('&nbsp;', ' ').replace('&amp;', '&')
                story.append(Paragraph(text, body_style))
            
            elif element[0] == 'list':
                for item in element[1]:
                    story.append(Paragraph(f"• {item}", list_style))
                story.append(Spacer(1, 10))
            
            elif element[0] == 'table':
                if element[1]:
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
        
        if not story or len(story) <= 2:
            clean_text = re.sub(r'<[^>]+>', ' ', html_content)
            clean_text = re.sub(r'\s+', ' ', clean_text).strip()
            
            if clean_text:
                paragraphs = [p.strip() for p in clean_text.split('\n') if p.strip()]
                if not paragraphs:
                    paragraphs = [clean_text[:1000] + "..." if len(clean_text) > 1000 else clean_text]
                
                for para in paragraphs:
                    if para:
                        story.append(Paragraph(para, body_style))
                        story.append(Spacer(1, 12))
        
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
    
    app_mode = st.radio(
        "Select Mode:",
        ["🎨 Code Viewer", "🤖 AI Webhook Chat", "📊 Data Analysis", "📤 Simple Webhook Sender"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
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
        st.session_state.uploaded_data = pd.DataFrame()
        st.session_state.selected_code_number = None
        st.session_state.current_code = "<h1>Welcome</h1><p>Please load data to begin.</p>"
        st.session_state.selected_code_row = {'Title': 'Welcome', 'Category': 'Info', 'Description': 'Load Google Sheet data to begin'}
        st.session_state.data_load_stats = {"total_rows": 0, "load_time": 0, "duplicates": 0}
        st.rerun()
    
    st.markdown("---")
    
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
    
    if st.session_state.data_load_stats.get("total_rows", 0) > 0:
        st.markdown("---")
        st.markdown("### 📊 Data Load Stats")
        st.metric("Rows Loaded", st.session_state.data_load_stats["total_rows"])
        st.metric("Load Time", f"{st.session_state.data_load_stats['load_time']:.2f}s")
        if st.session_state.data_load_stats["duplicates"] > 0:
            st.metric("Duplicates Found", st.session_state.data_load_stats["duplicates"])

# ==========================================
# MAIN CONTENT AREA
# ==========================================

if app_mode == "🎨 Code Viewer":
    st.markdown("""
    <div class="main-header">
        <h1>🚀 Advanced Code Viewer & Editor</h1>
        <p>Load ALL rows from Google Sheets with enhanced data fetching, preview, edit, and download capabilities</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        sheet_url_input = st.text_input(
            "Google Sheet CSV URL:",
            value=st.session_state.sheet_url,
            help="Enter the CSV export URL of your Google Sheet - ALL rows will be loaded"
        )
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔄 Load Data", use_container_width=True, type="primary"):
            st.session_state.sheet_url = sheet_url_input
            with st.spinner("Loading ALL data from Google Sheets..."):
                df, stats = load_data_with_retry(st.session_state.sheet_url, force_refresh=False)
                st.session_state.code_data = df
                st.session_state.data_load_stats = stats
                
                if not df.empty:
                    st.session_state.selected_code_number = df.index[0]
                    st.session_state.current_code = df.loc[st.session_state.selected_code_number]['Code']
                    st.session_state.selected_code_row = df.loc[st.session_state.selected_code_number].to_dict()
                    st.success(f"✅ Successfully loaded {stats['total_rows']} rows in {stats['load_time']:.2f} seconds!")
                else:
                    st.session_state.current_code = "<h1>No Data</h1><p>Please provide a valid Google Sheet URL.</p>"
                    st.session_state.selected_code_row = {'Title': 'No Data', 'Category': 'Error', 'Description': 'No data available'}
            st.rerun()
    
    with col3:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔃 Force Refresh", use_container_width=True):
            st.session_state.force_refresh_counter += 1
            with st.spinner("Force refreshing data (bypassing cache)..."):
                df, stats = load_data_with_retry(st.session_state.sheet_url, force_refresh=True)
                st.session_state.code_data = df
                st.session_state.data_load_stats = stats
                
                if not df.empty:
                    st.session_state.selected_code_number = df.index[0]
                    st.session_state.current_code = df.loc[st.session_state.selected_code_number]['Code']
                    st.session_state.selected_code_row = df.loc[st.session_state.selected_code_number].to_dict()
                    st.success(f"✅ Force refreshed {stats['total_rows']} rows in {stats['load_time']:.2f} seconds!")
            st.rerun()
    
    if st.session_state.data_load_stats.get("total_rows", 0) > 0:
        st.markdown("---")
        st.markdown("### 📊 Data Statistics")
        stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)
        
        with stat_col1:
            st.markdown(f"""
            <div class="data-stat-card">
                <h3>{st.session_state.data_load_stats['total_rows']}</h3>
                <p>Total Rows Loaded</p>
            </div>
            """, unsafe_allow_html=True)
        
        with stat_col2:
            st.markdown(f"""
            <div class="data-stat-card">
                <h3>{st.session_state.data_load_stats['load_time']:.2f}s</h3>
                <p>Load Time</p>
            </div>
            """, unsafe_allow_html=True)
        
        with stat_col3:
            st.markdown(f"""
            <div class="data-stat-card">
                <h3>{st.session_state.data_load_stats.get('duplicates', 0)}</h3>
                <p>Duplicates Removed</p>
            </div>
            """, unsafe_allow_html=True)
        
        with stat_col4:
            st.markdown(f"""
            <div class="data-stat-card">
                <h3>{len(st.session_state.data_load_stats.get('columns', []))}</h3>
                <p>Columns</p>
            </div>
            """, unsafe_allow_html=True)

    df = st.session_state.code_data
    
    if not df.empty:
        st.markdown("---")
        st.markdown("### 🎛️ Display Controls")
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.session_state.show_live_preview = st.toggle("🔴 Live Preview", value=st.session_state.show_live_preview)
        with col2:
            st.session_state.show_code_panel = st.toggle("📝 Code Panel", value=st.session_state.show_code_panel)
        with col3:
            st.session_state.edit_mode = st.toggle("✏️ Edit Mode", value=st.session_state.edit_mode)
        with col4:
            st.session_state.halt_edit = st.toggle("🔒 Lock Edit", value=st.session_state.halt_edit)
        with col5:
            st.session_state.code_display_mode = st.radio("Code View:", ["Prettify", "Raw"], 
                                                          index=0 if st.session_state.code_display_mode == "Prettify" else 1, 
                                                          horizontal=True, label_visibility="collapsed")
        
        if st.session_state.halt_edit and st.session_state.edit_mode:
            st.warning("⚠️ Edit mode disabled due to edit lock")
            st.session_state.edit_mode = False
        
        if 'Category' in df.columns:
            categories = ["All Categories"] + sorted(list(df['Category'].unique()))
            selected_category = st.selectbox("Filter by Category:", categories)
            
            if selected_category != "All Categories":
                df_filtered = df[df['Category'] == selected_category]
            else:
                df_filtered = df
        else:
            df_filtered = df
        
        numbers = sorted(df_filtered['Number'].tolist())
        
        if numbers:
            selected_number = st.selectbox("Choose Code Entry:", numbers, 
                                          index=numbers.index(st.session_state.selected_code_number) if st.session_state.selected_code_number in numbers else 0)
            
            if selected_number != st.session_state.selected_code_number:
                st.session_state.selected_code_number = selected_number
                st.session_state.current_code = df_filtered.loc[selected_number]['Code']
                st.session_state.selected_code_row = df_filtered.loc[selected_number].to_dict()
                st.rerun()
            
            selected_row = st.session_state.selected_code_row
            current_code = st.session_state.current_code
            
            st.markdown("---")
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
            
            code_to_display = current_code
            if st.session_state.code_display_mode == "Prettify":
                code_to_display = prettify_html(current_code)
            
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
                        st.code(code_to_display, language="html", line_numbers=True)
            
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
                    st.code(code_to_display, language="html", line_numbers=True)
            else:
                st.info("📌 Enable Live Preview or Code Panel to view content")
            
            st.markdown("---")
            st.markdown("### 📥 Download Options")
            
            col1, col2, col3, col4 = st.columns(4)
            
            if current_code and current_code.strip():
                clean_html = clean_html_for_download(current_code)
                
                with col1:
                    st.download_button(
                        label="🌐 Download HTML",
                        data=clean_html,
                        file_name=f"{selected_row.get('Title', 'document').replace(' ', '_')}.html",
                        mime="text/html",
                        help="Download as HTML file with embedded CSS",
                        use_container_width=True
                    )
                
                with col2:
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
                        st.button("📄 Download PDF", use_container_width=True, disabled=True, 
                                help="ReportLab not installed or PDF generation failed.")
                
                with col3:
                    st.text_input("Copy Code:", code_to_display, label_visibility="collapsed", key="copy_code_input")
                    st.button("📋 Copy Code", use_container_width=True, help="Copy the displayed code to clipboard.")
                
                with col4:
                    if st.session_state.edit_mode and not st.session_state.halt_edit:
                        if st.button("🔄 Reset Code", use_container_width=True):
                            st.session_state.current_code = df_filtered.loc[st.session_state.selected_code_number]['Code']
                            st.rerun()
                    else:
                        st.write("")
            else:
                st.info("No code available for download.")
        
        else:
            st.info("No entries found for the selected category.")
    
    elif st.session_state.sheet_url:
        st.error("❌ No data loaded. Please check your Google Sheet URL and ensure it contains 'Number' and 'Code' columns.")
        st.markdown("""
        ### 🔍 Troubleshooting Tips:
        - Ensure your Google Sheet is publicly accessible
        - Verify the URL ends with `/export?format=csv`
        - Check that 'Number' and 'Code' columns exist
        - Try the 'Force Refresh' button to bypass caching
        """)
    else:
        st.warning("⚠️ Please enter a Google Sheet URL and click 'Load Data' to begin.")

elif app_mode == "🤖 AI Webhook Chat":
    st.markdown("""
    <div class="main-header">
        <h1>🤖 Advanced AI Webhook Chat System</h1>
        <p>Intelligent conversation interface for webhook-based AI content generation with advanced prompting</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("## 🔗 Webhook Configuration")
    
    webhook_keys = list(WEBHOOKS.keys())
    webhook_choice = st.selectbox(
        "Select Webhook Type:",
        webhook_keys,
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
    
    use_custom_url = st.checkbox("Use Custom Webhook URL", value=False, key="chat_custom_url_toggle")
    
    if use_custom_url:
        webhook_url = st.text_input("Custom Webhook URL:", value=webhook_info['url'], key="chat_custom_url_input")
    else:
        webhook_url = webhook_info['url']
        st.text_input("Webhook URL:", value=webhook_url, disabled=True, key="chat_url_display")
    
    st.markdown("---")
    
    st.markdown("### 💡 Advanced Prompting & Templates")
    
    prompt_fields = webhook_info.get("fields", ["topic"])
    field_values = {}
    
    st.markdown(f"**Template:** `{webhook_info['prompt_template']}`")
    
    col_count = min(len(prompt_fields), 3)
    cols = st.columns(col_count)
    
    for i, field in enumerate(prompt_fields):
        if f"prompt_field_{field}" not in st.session_state:
            st.session_state[f"prompt_field_{field}"] = ""
        
        with cols[i % col_count]:
            field_values[field] = st.text_input(f"Enter value for **{field}**:", 
                                              value=st.session_state[f"prompt_field_{field}"],
                                              key=f"prompt_field_{field}")
    
    st.markdown("#### Quick Examples")
    template_cols = st.columns(3)
    
    for idx, example in enumerate(webhook_info['examples']):
        with template_cols[idx % 3]:
            if st.button(f"📝 {list(example.values())[0][:30]}...", key=f"template_btn_{idx}", use_container_width=True):
                for field, value in example.items():
                    st.session_state[f"prompt_field_{field}"] = value
                st.rerun()
    
    try:
        full_prompt = webhook_info['prompt_template'].format(**field_values)
    except KeyError:
        full_prompt = "Error: Missing values for all required fields in the template."
    
    st.markdown("---")
    
    st.markdown("### 💬 Conversation")
    
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
    
    st.markdown("### ✍️ Send Message")
    
    input_col1, input_col2 = st.columns([4, 1])
    
    with input_col1:
        user_input = st.text_area(
            "Your message (or use the generated prompt above):",
            value=full_prompt,
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
                add_to_chat_history("user", user_input)
                
                if send_as_webhook:
                    payload = {
                        "title": f"{webhook_choice} - Custom Prompt",
                        "type": "text",
                        "text": user_input,
                        "category": webhook_choice,
                        "timestamp": datetime.utcnow().isoformat()
                    }
                    
                    response_data = send_webhook(webhook_url, payload)
                    st.session_state.webhook_history.append(response_data)
                    
                    status = "success" if response_data["success"] else "error"
                    system_message = f"Webhook sent to `{webhook_url}`. Status Code: **{response_data['status_code']}**."
                    add_to_chat_history("system", system_message, {"status": status})
                    
                    assistant_response = f"**Webhook Response:**\n\n```json\n{response_data['response'][:500]}...\n```"
                    add_to_chat_history("assistant", assistant_response)
                else:
                    add_to_chat_history("assistant", f"Message received: '{user_input[:50]}...' (Webhook send disabled)")
                
                st.rerun()
            else:
                st.warning("Please enter a message to send.")

elif app_mode == "📊 Data Analysis":
    st.markdown("""
    <div class="main-header">
        <h1>📊 Data Analysis & Visualization</h1>
        <p>Upload CSV or Excel files for comprehensive data profiling, statistics, and visualization</p>
    </div>
    """, unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader("Upload your CSV or Excel file", type=["csv", "xlsx", "xls"])
    
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file, low_memory=False)
            elif uploaded_file.name.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(uploaded_file)
            
            st.session_state.uploaded_data = df
            st.success(f"✅ Successfully loaded {len(df)} rows and {len(df.columns)} columns from **{uploaded_file.name}**")
            
        except Exception as e:
            st.error(f"Error reading file: {e}")
            st.session_state.uploaded_data = pd.DataFrame()
    
    df = st.session_state.uploaded_data
    
    if not df.empty:
        st.markdown("---")
        st.header("Data Overview")
        
        tab1, tab2, tab3, tab4 = st.tabs(["Raw Data", "Descriptive Statistics", "Column Analysis", "Visualization"])
        
        with tab1:
            st.subheader("Raw Data Table")
            st.dataframe(df, use_container_width=True)
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Rows", len(df))
            with col2:
                st.metric("Total Columns", len(df.columns))
            with col3:
                st.metric("Memory Usage", f"{df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB")
            with col4:
                st.metric("Missing Values", df.isnull().sum().sum())
        
        with tab2:
            st.subheader("Descriptive Statistics")
            st.dataframe(df.describe(include='all'), use_container_width=True)
            
            st.subheader("Data Types Distribution")
            dtype_counts = df.dtypes.value_counts()
            dtype_df = pd.DataFrame({
                'Data Type': dtype_counts.index.astype(str),
                'Count': dtype_counts.values
            })
            st.dataframe(dtype_df)
        
        with tab3:
            st.subheader("Column Information")
            col_info = pd.DataFrame({
                'Data Type': df.dtypes,
                'Non-Null Count': df.count(),
                'Null Count': df.isnull().sum(),
                'Unique Values': df.nunique(),
                'Duplicate Values': df.apply(lambda x: x.duplicated().sum())
            })
            st.dataframe(col_info, use_container_width=True)
            
            st.subheader("Missing Data Heatmap")
            missing_data = df.isnull().sum()
            missing_df = pd.DataFrame({
                'Column': missing_data.index,
                'Missing Count': missing_data.values,
                'Missing Percentage': (missing_data.values / len(df) * 100).round(2)
            })
            missing_df = missing_df[missing_df['Missing Count'] > 0].sort_values('Missing Count', ascending=False)
            
            if not missing_df.empty:
                st.dataframe(missing_df, use_container_width=True)
            else:
                st.success("No missing data found in the dataset!")
        
        with tab4:
            st.subheader("Data Visualization")
            
            numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
            categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
            
            if not numeric_cols and not categorical_cols:
                st.warning("No suitable columns found for visualization.")
            else:
                viz_type = st.selectbox("Select Visualization Type:", 
                                       ["Histogram", "Scatter Plot", "Bar Chart", "Box Plot", "Correlation Heatmap"])
                
                if viz_type == "Histogram":
                    if numeric_cols:
                        col_hist = st.selectbox("Select Column for Histogram:", numeric_cols)
                        
                        if col_hist:
                            chart = alt.Chart(df).mark_bar().encode(
                                x=alt.X(col_hist, bin=alt.Bin(maxbins=30), title=col_hist),
                                y=alt.Y('count()', title='Frequency'),
                                tooltip=[alt.Tooltip(col_hist, bin=alt.Bin(maxbins=30)), 'count()']
                            ).properties(
                                title=f"Distribution of {col_hist}",
                                width=700,
                                height=400
                            ).interactive()
                            st.altair_chart(chart, use_container_width=True)
                    else:
                        st.warning("No numeric columns available for histogram.")
                
                elif viz_type == "Scatter Plot":
                    if len(numeric_cols) >= 2:
                        col_x = st.selectbox("Select X-axis:", numeric_cols, key="scatter_x")
                        col_y = st.selectbox("Select Y-axis:", numeric_cols, key="scatter_y")
                        
                        if col_x and col_y:
                            chart = alt.Chart(df).mark_circle(size=60).encode(
                                x=alt.X(col_x, title=col_x),
                                y=alt.Y(col_y, title=col_y),
                                tooltip=[col_x, col_y]
                            ).properties(
                                title=f"Scatter Plot: {col_x} vs {col_y}",
                                width=700,
                                height=400
                            ).interactive()
                            st.altair_chart(chart, use_container_width=True)
                    else:
                        st.warning("Need at least 2 numeric columns for scatter plot.")
                
                elif viz_type == "Bar Chart":
                    if categorical_cols:
                        col_bar = st.selectbox("Select Categorical Column:", categorical_cols)
                        
                        if col_bar:
                            value_counts = df[col_bar].value_counts().reset_index()
                            value_counts.columns = [col_bar, 'Count']
                            
                            top_n = st.slider("Show top N categories:", 5, min(50, len(value_counts)), 10)
                            value_counts = value_counts.head(top_n)
                            
                            chart = alt.Chart(value_counts).mark_bar().encode(
                                x=alt.X('Count:Q', title='Count'),
                                y=alt.Y(f'{col_bar}:N', sort='-x', title=col_bar),
                                tooltip=[col_bar, 'Count']
                            ).properties(
                                title=f"Top {top_n} Categories in {col_bar}",
                                width=700,
                                height=400
                            ).interactive()
                            st.altair_chart(chart, use_container_width=True)
                    else:
                        st.warning("No categorical columns available for bar chart.")
                
                elif viz_type == "Box Plot":
                    if numeric_cols:
                        col_box = st.selectbox("Select Column for Box Plot:", numeric_cols)
                        
                        if col_box:
                            chart = alt.Chart(df).mark_boxplot().encode(
                                y=alt.Y(col_box, title=col_box)
                            ).properties(
                                title=f"Box Plot of {col_box}",
                                width=700,
                                height=400
                            )
                            st.altair_chart(chart, use_container_width=True)
                    else:
                        st.warning("No numeric columns available for box plot.")
                
                elif viz_type == "Correlation Heatmap":
                    if len(numeric_cols) >= 2:
                        corr_df = df[numeric_cols].corr().reset_index().melt('index')
                        corr_df.columns = ['Variable 1', 'Variable 2', 'Correlation']
                        
                        chart = alt.Chart(corr_df).mark_rect().encode(
                            x='Variable 1:N',
                            y='Variable 2:N',
                            color=alt.Color('Correlation:Q', scale=alt.Scale(scheme='blueorange', domain=[-1, 1])),
                            tooltip=['Variable 1', 'Variable 2', alt.Tooltip('Correlation:Q', format='.3f')]
                        ).properties(
                            title="Correlation Heatmap",
                            width=700,
                            height=700
                        )
                        st.altair_chart(chart, use_container_width=True)
                    else:
                        st.warning("Need at least 2 numeric columns for correlation heatmap.")
    
    else:
        st.info("📁 Upload a CSV or Excel file above to begin comprehensive data analysis.")
        st.markdown("""
        ### Features:
        - View raw data with complete statistics
        - Descriptive statistics and data profiling
        - Column-wise analysis with missing data detection
        - Interactive visualizations (histograms, scatter plots, bar charts, box plots, correlations)
        """)

elif app_mode == "📤 Simple Webhook Sender":
    st.markdown("""
    <div class="main-header">
        <h1>📤 Simple Webhook Text Sender</h1>
        <p>Straightforward interface to send text payloads to selected webhook URLs for quick testing</p>
    </div>
    """, unsafe_allow_html=True)
    
    webhook_choice = st.selectbox("Select webhook type", list(WEBHOOKS.keys()), key="simple_webhook_select")
    webhook_url = st.text_input("Webhook URL", value=WEBHOOKS[webhook_choice]['url'], key="simple_webhook_url")
    
    title = st.text_input("Title", value=f"{webhook_choice} - {datetime.utcnow().isoformat()[:19]}", key="simple_title")
    
    text_input = st.text_area(
        "Enter the text you want to send",
        height=300,
        placeholder="Type your message here...",
        key="simple_text_input"
    )
    
    send_button = st.button("Send Webhook", type="primary", use_container_width=True)
    
    if send_button:
        if not text_input.strip():
            st.error("Please enter text to send.")
        else:
            payload = {
                "title": title,
                "type": "text",
                "text": text_input,
                "category": webhook_choice,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            try:
                with st.spinner("Sending webhook..."):
                    resp = requests.post(webhook_url, json=payload, timeout=20)
                
                try:
                    resp_body = resp.text
                except:
                    resp_body = ""
                
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
                    st.success(f"✅ Sent successfully! Status {resp.status_code}")
                else:
                    st.warning(f"⚠️ Request returned status {resp.status_code}")
            
            except Exception as e:
                st.error(f"❌ Request failed: {e}")
    
    st.markdown("---")
    st.header("📜 Webhook History (Last 10)")
    
    if st.session_state.webhook_simple_history:
        for i, rec in enumerate(st.session_state.webhook_simple_history[:10]):
            status_emoji = "✅" if rec['status_code'] < 300 else "❌"
            with st.expander(f"{status_emoji} {i+1}. {rec['timestamp'][:19]} → Status {rec['status_code']}"):
                st.subheader("Payload Sent")
                st.json(rec["payload"])
                st.subheader("Response Received")
                st.code(rec["response"])
                st.caption(f"Webhook URL: {rec['webhook']}")
    else:
        st.info("No webhooks sent yet. Send your first webhook above!")
