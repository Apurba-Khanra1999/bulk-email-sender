# BulkFlow Pro: Streamlit Bulk HTML Email Sender

BulkFlow Pro is a Streamlit application for running professional bulk email campaigns using your own HTML email templates and a list of recipients. It provides a polished UI, live progress feedback, rendered HTML previews, and safeguards such as HTML minification to avoid message clipping in clients like Gmail.

## Features

- Streamlit UI with professional styling and wide-screen layout
- Sidebar SMTP configuration (server, port, credentials)
- Upload recipients via CSV or XLSX with an `email` column
- Upload HTML template (`.html`/`.htm`) and preview it rendered in-app
- HTML minification to reduce message size and avoid Gmail clipping
- Live progress bar, per-recipient status, and transmission log
- TLS (`STARTTLS`) secure SMTP connection

## Requirements

- Python 3.9+ recommended
- Packages:
  - `streamlit`
  - `pandas`
  - `openpyxl` (for `.xlsx` support)

Install dependencies:

```bash
pip install streamlit pandas openpyxl
```

## Run

```bash
python -m streamlit run main.py
```

The app will be available at:

- Local: `http://localhost:8501/`
- Network: shown in the terminal

## Usage

1. Open the app in a browser.
2. Configure SMTP in the sidebar:
   - `SMTP Server` (e.g., `smtp.gmail.com`)
   - `SMTP Port` (e.g., `587`)
   - `Sender Email`
   - `App Password`
3. Enter a subject line.
4. Upload assets:
   - `HTML Template`: your email design (`.html`/`.htm`)
   - `Recipient List`: CSV/XLSX with an `email` column
5. Review the Overview panel on the right:
   - Total recipients and a preview of the list
   - Rendered HTML preview and source code snippet
6. Click `🚀 Launch Campaign Now` to send.

## Data Formats

- CSV example:

```csv
email
alice@example.com
bob@example.org
```

- XLSX: a single sheet with a column named `email`.

## Important Notes

- Use an **App Password** for Gmail (Google Account → Security → 2-Step Verification → App Passwords).
- BulkFlow Pro uses **STARTTLS** and `server.login()` for authentication.
- Large embedded base64 images in HTML increase size and can still cause Gmail clipping (~102KB limit). Prefer external image URLs.

## Troubleshooting

- "Message clipped" in Gmail:
  - Ensure HTML is minified and avoid large base64 images.
  - Split very long campaigns or simplify template.
- Excel upload fails:
  - Install `openpyxl` and ensure file is `.xlsx`.
- Authentication failures:
  - Verify SMTP server/port and credentials.
  - For Gmail, use app-specific password and ensure SMTP is allowed.
- Nothing sends:
  - Confirm `Subject`, `Template`, and `Recipient List` are provided.

## Security

- Do not hardcode credentials in the code.
- Keep your app password secret; never commit it to version control.
- Use trusted SMTP providers and secure connections.

## License

This project is provided as-is for educational and internal use.
