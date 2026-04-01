import streamlit as st
import imaplib
import email
from email.header import decode_header
import io

from services.parsers import parse_vested, parse_indmoney
from services.portfolio_service import get_or_create_account, save_holdings

def sync_latest_reports_from_email():
    """Fetches the latest INDmoney and Vested reports from a specific email label."""
    try:
        email_user = st.secrets.get("EMAIL_USER")
        email_pass = st.secrets.get("EMAIL_PASS")
        email_imap = st.secrets.get("EMAIL_IMAP", "imap.gmail.com")
        email_label = st.secrets.get("EMAIL_LABEL", "holdings") # Use 'holdings' label
        
        if not email_user or not email_pass:
            st.sidebar.error("Email credentials missing in secrets.toml.")
            return

        # Connect to IMAP
        mail = imaplib.IMAP4_SSL(email_imap)
        mail.login(email_user, email_pass)
        
        # Select the specific label/folder
        # Note: In Gmail, labels are treated as folders
        status, _ = mail.select(f'"{email_label}"')
        if status != "OK":
            # Fallback to INBOX if label not found
            status, _ = mail.select("INBOX")
            st.sidebar.warning(f"Label '{email_label}' not found. Searching INBOX instead.")
        
        status, messages = mail.search(None, "ALL")
        if status != "OK" or not messages[0]:
            st.sidebar.info("No new reports found in the 'holdings' label.")
            mail.logout()
            return

        processed_count = 0
        processed_accounts = set() # Track unique broker IDs processed this session
        
        # Get latest 10 message IDs from the label
        email_ids = messages[0].split()
        recent_ids = email_ids[-10:]
        recent_ids.reverse() # Start with newest
        
        for m_id in recent_ids:
            status, data = mail.fetch(m_id, "(RFC822)")
            if status != "OK": continue
            
            raw_email = data[0][1]
            msg = email.message_from_bytes(raw_email)
            
            for part in msg.walk():
                if part.get_content_maintype() == 'multipart': continue
                if part.get('Content-Disposition') is None: continue
                
                filename = part.get_filename()
                if filename:
                    decoded_name, encoding = decode_header(filename)[0]
                    if isinstance(decoded_name, bytes):
                        filename = decoded_name.decode(encoding if encoding else 'utf-8')
                        
                    if any(filename.lower().endswith(ext) for ext in ['.xlsx', '.xls', '.csv']):
                        content = part.get_payload(decode=True)
                        file_obj = io.BytesIO(content)
                        file_obj.name = filename
                        
                        try:
                            # Auto-detect logic
                            if "vested" in filename.lower():
                                df, b_id = parse_vested(file_obj, filename)
                                platform = "Vested"
                            else:
                                df, b_id = parse_indmoney(file_obj, filename)
                                platform = "INDmoney"
                            
                            # Only process if we haven't seen this specific broker ID in this run
                            if b_id not in processed_accounts and not df.empty:
                                acc_id = get_or_create_account(platform, b_id, b_id)
                                save_holdings(df, acc_id)
                                processed_count += 1
                                processed_accounts.add(b_id)
                        except Exception as e:
                            pass # Silently ignore parse errors for older/invalid emails
            
        mail.logout()
        if processed_count > 0:
            st.sidebar.success(f"Synced {processed_count} account(s) from '{email_label}' label!")
            st.rerun()
        else:
            st.sidebar.info("No new reports found in the 'holdings' label.")
            
    except Exception as e:
        st.sidebar.error(f"Email Sync Error: {e}")
