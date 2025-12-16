# bulk_mail_app.py
# Streamlit web app for sending bulk emails using an HTML template

import streamlit as st
import smtplib
import ssl
import re
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import pandas as pd

st.set_page_config(page_title="Bulk Email Sender", layout="centered")

st.title("📧 Bulk Email Sender")
st.write("Send bulk emails using your HTML email template and a list of email IDs.")

# ------------------ Sidebar: SMTP Settings ------------------
st.sidebar.header("SMTP Configuration")
smtp_server = st.sidebar.text_input("SMTP Server", value="smtp.gmail.com")
smtp_port = st.sidebar.number_input("SMTP Port", value=587)
sender_email = st.sidebar.text_input("Sender Email")
sender_password = st.sidebar.text_input("App Password / Email Password", type="password")

# ------------------ Main Inputs ------------------
subject = st.text_input("Email Subject")

template_file = st.file_uploader(
    "Upload HTML Template (.html)",
    type=["html", "htm"]
)

uploaded_file = st.file_uploader(
    "Upload Email List (CSV or Excel with a column named 'email')",
    type=["csv", "xlsx"]
)

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
    - Removes comments
    - Removes excessive whitespace between tags
    """
    # Remove HTML comments
    html_content = re.sub(r"<!--[\s\S]*?-->", "", html_content)
    # Collapse multiple spaces/newlines into a single space
    html_content = re.sub(r"\s+", " ", html_content)
    # Remove spaces between tags where safe (e.g. > <)
    html_content = re.sub(r">\s+<", "><", html_content)
    return html_content.strip()


def send_bulk_email(emails, subject, html_content):
    context = ssl.create_default_context()

    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls(context=context)
        server.login(sender_email, sender_password)

        for email in emails:
            msg = MIMEMultipart("alternative")
            msg["From"] = sender_email
            msg["To"] = email
            msg["Subject"] = subject

            msg.attach(MIMEText(html_content, "html"))
            server.sendmail(sender_email, email, msg.as_string())

# ------------------ Actions ------------------
if uploaded_file:
    email_list = load_emails(uploaded_file)

    if email_list:
        st.success(f"{len(email_list)} email addresses loaded")
        st.dataframe(pd.DataFrame(email_list, columns=["Email IDs"]))

        if st.button("🚀 Send Bulk Email"):
            if not all([sender_email, sender_password, subject, template_file]):
                st.warning("Please fill all required fields")
            else:
                with st.spinner("Sending emails... Please wait"):
                    try:
                        html_content = template_file.read().decode("utf-8", errors="replace")
                        
                        # Minify HTML to avoid clipping
                        html_content = minify_html(html_content)
                        
                        send_bulk_email(email_list, subject, html_content)
                        st.success("✅ Emails sent successfully")
                    except Exception as e:
                        st.error(f"❌ Error: {e}")

# ------------------ Footer ------------------
st.markdown("---")
st.caption("Built with Streamlit & Python")
