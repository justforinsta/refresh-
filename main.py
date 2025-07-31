import streamlit as st
import time
import random
import re
from instagrapi import Client
from datetime import datetime

# ✅ Validate username
def validate_username(username):
    return bool(username and re.match(r'^[A-Za-z0-9._]{1,30}$', username))

# ✅ Parse session format: username:csrf_token:session_id
def parse_sessions(input_string):
    accounts = []
    for entry in input_string.split(","):
        parts = entry.strip().split(":")
        if len(parts) != 3:
            st.warning(f"Invalid format: {entry}")
            continue
        username, csrf_token, session_id = parts
        if not validate_username(username.strip()):
            st.warning(f"Invalid username: {username}")
            continue
        accounts.append({
            "username": username.strip(),
            "csrf_token": csrf_token.strip(),
            "session_id": session_id.strip()
        })
    return accounts

# ✅ Parse target usernames
def parse_targets(input_string):
    targets = [t.strip() for t in input_string.split(",") if validate_username(t.strip())]
    if not targets:
        st.warning("No valid targets found.")
    return targets

# ✅ Safe session loader (no _session, no private, works in latest instagrapi)
def setup_client_with_session(csrf_token, session_id):
    cl = Client()
    
    cl.set_settings({
        "authorization_data": {
            "sessionid": session_id,
            "csrftoken": csrf_token
        }
    })

    try:
        cl.get_timeline_feed()
        return cl
    except Exception as e:
        st.error(f"Session invalid or expired: {e}")
        return None

# ✅ Simulated report
def report_user(cl, target_username, reporter):
    try:
        user_id = cl.user_id_from_username(target_username)
        st.info(f"Simulated report: @{reporter} ➜ @{target_username}")
        time.sleep(random.uniform(1, 2))  # Simulate delay
        # cl.report_user(user_id, reason="Impersonation")  # <-- real call
        return True
    except Exception as e:
        st.warning(f"Failed report @{target_username} by @{reporter}: {str(e)}")
        return False

# ✅ Streamlit UI
st.set_page_config(page_title="Instagram Reporter via Session", layout="centered")
st.title("📣 Instagram Report Tool (Session Login) — Simulated")

with st.form("report_form"):
    session_input = st.text_area(
        "Enter sessions (username:csrf_token:session_id)", height=150,
        help="Example: user1:csrf123:sessionid123,user2:csrf456:sessionid456"
    )
    targets_input = st.text_input(
        "Enter target usernames (comma-separated)",
        help="Example: scammer1,fakeprofile2"
    )
    submitted = st.form_submit_button("🚀 Start Reporting")

if submitted:
    with st.spinner("Logging in and simulating reports..."):
        accounts = parse_sessions(session_input)
        targets = parse_targets(targets_input)
        report_results = []

        for acc in accounts:
            cl = setup_client_with_session(acc["csrf_token"], acc["session_id"])
            if not cl:
                continue

            for target in targets:
                status = report_user(cl, target, acc["username"])
                report_results.append({
                    "target": target,
                    "reporter": acc["username"],
                    "status": "✅ Success" if status else "❌ Failed",
                    "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
                time.sleep(random.uniform(2, 4))

        if report_results:
            st.subheader("📊 Report Summary")
            st.table(report_results)
        else:
            st.error("No reports completed. Check sessions or targets.")
