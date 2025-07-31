import streamlit as st
import os
import time
import random
import re
from dotenv import load_dotenv
from instagrapi import Client
from instagrapi.exceptions import ClientError, LoginRequired
from datetime import datetime

load_dotenv()

def validate_username(username):
    return bool(username and re.match(r'^[A-Za-z0-9._]{1,30}$', username))

def parse_credentials(input_string):
    accounts = []
    for cred in input_string.split(","):
        cred = cred.strip()
        if ":" not in cred:
            st.error(f"Invalid credential format: {cred}. Use username:password")
            continue
        username, password = cred.split(":", 1)
        if not validate_username(username.strip()):
            st.error(f"Invalid username format: {username}")
            continue
        accounts.append({"username": username.strip(), "password": password.strip()})
    return accounts

def parse_targets(input_string):
    targets = [t.strip() for t in input_string.split(",") if validate_username(t.strip())]
    if not targets:
        st.error("No valid target usernames provided.")
    return targets

def setup_client(proxy=None):
    cl = Client()
    if proxy:
        cl.set_proxy(proxy)
    return cl

def login_client(cl, username, password):
    try:
        cl.login(username, password)
        csrf_token = cl.last_json.get("csrf_token", "N/A")
        session_id = cl.get_settings().get("sessionid", "N/A")
        return True, csrf_token, session_id
    except (ClientError, LoginRequired) as e:
        st.error(f"Login failed for {username}: {str(e)}")
        return False, None, None

def report_user(cl, target_username, reporting_username, csrf_token, session_id, reason="Impersonation"):
    try:
        user_id = cl.user_id_from_username(target_username)
        # Simulated report
        time.sleep(random.uniform(1, 2))
        return True
    except Exception as e:
        st.warning(f"Report failed for {target_username} by {reporting_username}: {str(e)}")
        return False

st.set_page_config(page_title="Instagram Report Tool", layout="centered")

st.title("📣 Instagram Impersonation Reporter (Simulated)")

with st.form("input_form"):
    creds_input = st.text_area("Enter accounts (username:password, comma-separated)", height=100)
    targets_input = st.text_input("Enter targets to report (comma-separated usernames)")
    submit = st.form_submit_button("Start Reporting")

if submit:
    with st.spinner("Processing..."):
        accounts = parse_credentials(creds_input)
        targets = parse_targets(targets_input)
        proxy = os.getenv("PROXY_URL")
        session_info = []
        report_results = []

        for acc in accounts:
            cl = setup_client(proxy)
            success, csrf, sid = login_client(cl, acc["username"], acc["password"])
            if not success:
                continue
            session_info.append({
                "username": acc["username"],
                "csrf_token": csrf[:10] + "...",
                "session_id": sid[:10] + "..."
            })

            for target in targets:
                status = report_user(cl, target, acc["username"], csrf, sid)
                report_results.append({
                    "target": target,
                    "reporter": acc["username"],
                    "status": "✅ Success" if status else "❌ Failed",
                    "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
                time.sleep(random.uniform(3, 6))  # Simulate delay
            cl.logout()

        if session_info:
            st.subheader("🔐 Session Info")
            st.table(session_info)

        if report_results:
            st.subheader("📊 Report Status")
            st.table(report_results)
        else:
            st.error("No reports were generated.")
