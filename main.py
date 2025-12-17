# bulk_mail_app.py
# Streamlit web app for sending bulk emails using an HTML template

import streamlit as st
import streamlit.components.v1 as components
import smtplib
import ssl
import re
import pandas as pd
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# ------------------ Page Config & CSS ------------------
st.set_page_config(
    page_title="BulkFlow Pro - Professional Bulk Sender",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    /* Global Styles */
    .stApp {
        background-color: #f8f9fa;
    }
    
    /* Headings */
    h1, h2, h3 {
        color: #2c3e50;
        font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
        font-weight: 600;
    }
    
    /* Metrics */
    div[data-testid="stMetricValue"] {
        color: #3182ce;
    }

    /* Buttons */
    div.stButton > button {
        background-color: #3182ce;
        color: white;
        border-radius: 8px;
        border: none;
        padding: 0.6rem 1.2rem;
        font-weight: 600;
        width: 100%;
        transition: all 0.2s ease-in-out;
    }
    div.stButton > button:hover {
        background-color: #2b6cb0;
        transform: translateY(-2px);
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    div.stButton > button:active {
        transform: translateY(0);
    }
    
    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e2e8f0;
    }
    
    /* Inputs */
    .stTextInput > div > div > input {
        border-radius: 6px;
        border: 1px solid #e2e8f0;
    }
    </style>
""", unsafe_allow_html=True)

# ------------------ Helper Functions ------------------
def load_emails(file):
    if file.name.endswith(".csv"):
        df = pd.read_csv(file)
    else:
        df = pd.read_excel(file)

    if "email" not in df.columns:
        st.error("File must contain a column named 'email'")
        return None

    return df["email"].dropna().unique().tolist()

def minify_html(html_content):
    """
    Minify HTML content to reduce size and avoid clipping by email clients.
    """
    # Remove HTML comments
    html_content = re.sub(r"<!--[\s\S]*?-->", "", html_content)
    # Collapse multiple spaces/newlines into a single space
    html_content = re.sub(r"\s+", " ", html_content)
    # Remove spaces between tags where safe (e.g. > <)
    html_content = re.sub(r">\s+<", "><", html_content)
    return html_content.strip()

# ------------------ Sidebar: Configuration ------------------
with st.sidebar:
    st.title("⚙️ Configuration")
    st.markdown("Configure your SMTP server settings below.")
    
    with st.expander("Server Settings", expanded=True):
        smtp_server = st.text_input("SMTP Server", value="smtp.gmail.com")
        smtp_port = st.number_input("SMTP Port", value=587)
    
    with st.expander("Credentials", expanded=True):
        sender_email = st.text_input("Sender Email")
        sender_password = st.text_input("App Password", type="password", help="Use an App Password for Gmail (Security > 2-Step Verification > App Passwords)")
    
    st.info("💡 **Tip:** Ensure 'Less Secure Apps' is enabled or use an App Password if using Gmail.")
    st.markdown("---")
    st.caption("v2.0 | Built by Apurba")

# ------------------ Main Interface ------------------
col_header_1, col_header_2 = st.columns([1, 6])
with col_header_1:
    st.image("https://cdn-icons-png.flaticon.com/512/2965/2965306.png", width=80)
with col_header_2:
    st.title("BulkFlow Pro Bulk Sender")
    st.markdown("### 🚀 Professional HTML Email Campaigns")

st.markdown("---")

# Layout: Inputs on Left (Narrow), Summary on Right (Wide)
col_left, col_right = st.columns([1, 2], gap="large")

with col_left:
    st.subheader("📝 Campaign Details")
    subject = st.text_input("Subject Line", placeholder="Enter an engaging subject line...")
    
    st.markdown("#### 📂 Assets")
    # Stacked uploaders for narrow column
    template_file = st.file_uploader("HTML Template", type=["html", "htm"], help="Upload your designed HTML email.")
    uploaded_file = st.file_uploader("Recipient List", type=["csv", "xlsx"], help="CSV/Excel must have an 'email' column.")

# Logic variables
email_list = []
html_content = ""

# Process Files
if uploaded_file:
    email_list = load_emails(uploaded_file)

if template_file:
    # Read and reset pointer for potential future reads (though we store in var)
    raw_content = template_file.read().decode("utf-8", errors="replace")
    html_content = minify_html(raw_content)
    template_file.seek(0)

# Right Column: Summary & Preview
with col_right:
    st.subheader("📊 Overview")
    
    if email_list:
        st.metric("Total Recipients", len(email_list))
        with st.expander("View Recipient List"):
            st.dataframe(pd.DataFrame(email_list, columns=["Email"]), height=200, use_container_width=True)
    else:
        st.info("Upload a recipient list to view stats.")
        
    if template_file:
        st.success("✅ HTML Template Ready")
        
        # Rendered Preview
        with st.expander("👁️ Preview Email Design", expanded=True):
            st.caption("This is an approximation of how the email will look.")
            components.html(html_content, height=400, scrolling=True)
            
        # Code Preview
        with st.expander("View Source Code"):
            st.code(html_content[:500] + "...", language="html")
    else:
        st.warning("Upload an HTML template.")

# ------------------ Action Section ------------------
st.markdown("---")

# Centered Button
_, col_btn, _ = st.columns([1, 2, 1])

with col_btn:
    send_btn = st.button("🚀 Launch Campaign Now", type="primary", use_container_width=True)

if send_btn:
    if not all([sender_email, sender_password, subject, template_file, email_list]):
        st.error("❌ Please fill all fields and upload required files.")
    else:
        # Progress UI
        st.markdown("### 📡 Sending Status")
        progress_bar = st.progress(0)
        status_text = st.empty()
        log_box = st.expander("Transmission Log", expanded=True)
        
        # SMTP Session
        try:
            context = ssl.create_default_context()
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                status_text.text("Connecting to SMTP server...")
                server.starttls(context=context)
                server.login(sender_email, sender_password)
                
                success_count = 0
                failed_count = 0
                
                for i, email in enumerate(email_list):
                    try:
                        msg = MIMEMultipart("alternative")
                        msg["From"] = sender_email
                        msg["To"] = email
                        msg["Subject"] = subject
                        msg.attach(MIMEText(html_content, "html"))
                        
                        server.sendmail(sender_email, email, msg.as_string())
                        success_count += 1
                        
                        # Update UI
                        progress = (i + 1) / len(email_list)
                        progress_bar.progress(progress)
                        status_text.text(f"Sending ({i+1}/{len(email_list)}): {email}")
                        
                        # Optional: small delay to be nice to the server
                        # time.sleep(0.1) 
                        
                    except Exception as e:
                        failed_count += 1
                        log_box.write(f"❌ Failed to send to {email}: {e}")
                
                status_text.text("✅ Campaign Completed!")
                progress_bar.progress(1.0)
                
                st.balloons()
                st.success(f"🎉 Sent {success_count} emails successfully. ({failed_count} failed)")
                
        except Exception as e:
            st.error(f"❌ SMTP Connection Error: {e}")
