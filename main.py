import streamlit as st
import time
import random
import re
from instagrapi import Client
from instagrapi.exceptions import ClientError
from datetime import datetime

def validate_username(username):
    return bool(username and re.match(r'^[A-Za-z0-9._]{1,30}$', username))

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

def parse_targets(input_string):
    targets = [t.strip() for t in input_string.split(",") if validate_username(t.strip())]
    if not targets:
        st.warning("No valid targets found.")
    return targets

def setup_client_with_session(csrf_token, session_id):
    cl = Client()
    cl.sessionid = session_id
    cl.csrf_token = csrf_token
    try:
        cl.get_timeline_feed()
        return cl
    except Exception as e:
        st.error(f"Session invalid: {e}")
        return None

def report_user(cl, target_username, reporter):
    try:
        user_id = cl.user_id_from_username(target_username)
        st.info(f"Simulating report: @{reporter} ➜ @{target_username}")
        time.sleep(random.uniform(1, 2))
        # Real call (commented for safety)
        # cl.report_user(user_id, reason="Impersonation")
        return True
    except Exception as e:
        st.warning(f"Failed report @{target_username} by @{reporter}: {str(e)}")
        return False

# Streamlit UI
st.set_page_config(page_title="Instagram Report Tool", layout="centered")
st.title("📣 Instagram Reporting Tool via Session ID")

with st.form("report_form"):
    session_input = st.text_area("Enter accounts (username:csrf_token:session_id)", height=150,
                                 help="Example: user1:csrf123:sessionid123,user2:csrf456:sessionid456")
    targets_input = st.text_input("Target usernames (comma-separated)", help="Example: spamuser1,scammer2")
    submitted = st.form_submit_button("🚀 Start Reporting")

if submitted:
    with st.spinner("Logging in and sending reports..."):
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
            st.error("No reports were created. Check sessions and targets.")
