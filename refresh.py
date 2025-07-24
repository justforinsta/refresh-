import streamlit as st
import requests
import time
import re

st.set_page_config(page_title="Instagram Report Tool", layout="centered")
st.title("📣 Instagram Report Tool")
st.markdown("Lite & App Reporter | For Educational Use Only")

# Session State
if 'reported_users' not in st.session_state:
    st.session_state.reported_users = []

# Input for login
st.subheader("🔐 Instagram Session Credentials")
sessionid = st.text_input("Session ID", type="password")
csrftoken = st.text_input("CSRF Token", type="password")

def get_user_id(username):
    response = requests.post(
        'https://i.instagram.com/api/v1/users/lookup/',
        headers={
            "User-Agent": "Instagram 114.0.0.38.120 Android",
            "Content-Type": "application/x-www-form-urlencoded",
            'cookie': f'sessionid={sessionid}; csrftoken={csrftoken}'
        },
        data={"signed_body": f"sig.{{\"q\":\"{username}\"}}"}
    )
    if "No users found" in response.text:
        return None
    try:
        return str(response.json()['user_id'])
    except:
        return None

def report_lite(target_id):
    r = requests.post(
        f"https://i.instagram.com/users/{target_id}/flag/",
        headers={
            "User-Agent": "Mozilla/5.0",
            "Host": "i.instagram.com",
            'cookie': f'sessionid={sessionid}',
            "X-CSRFToken": csrftoken,
            "Content-Type": "application/x-www-form-urlencoded"
        },
        data='source_name=&reason_id=1&frx_context=',  # Spam
        allow_redirects=False
    )
    return r.status_code in [200, 302]

def report_app(target_id, reason_id, count):
    success = 0
    for i in range(count):
        r = requests.post(
            f"https://i.instagram.com/users/{target_id}/flag/",
            headers={
                "User-Agent": "Mozilla/5.0",
                "Host": "i.instagram.com",
                'cookie': f'sessionid={sessionid}',
                "X-CSRFToken": csrftoken,
                "Content-Type": "application/x-www-form-urlencoded"
            },
            data=f'source_name=&reason_id={reason_id}&frx_context=',
            allow_redirects=False
        )
        if r.status_code in [200, 302]:
            success += 1
        elif r.status_code == 429:
            st.error("❌ Rate limit hit!")
            break
        time.sleep(2)
    return success

# Show previously reported users
if st.session_state.reported_users:
    st.markdown("### 📄 Previously Reported (via Lite)")
    for user in st.session_state.reported_users:
        st.markdown(f"- **{user}**")

st.divider()

# Main input
st.subheader("📌 Target Username or /refresh Command")
user_input = st.text_input("Enter target username or command (e.g., /refresh john_doe)")

if st.button("Submit") and sessionid and csrftoken:
    if user_input.startswith("/refresh"):
        parts = user_input.strip().split()
        if len(parts) == 2:
            username = parts[1]
            target_id = get_user_id(username)
            if target_id:
                st.success(f"✅ Target ID for {username} found: {target_id}")
                reason = st.selectbox("Select report reason", [
                    "1 - Spam", "2 - Self", "3 - Drugs", "4 - Nudity",
                    "5 - Violence", "6 - Hate", "7 - Bullying", "8 - Impersonation"
                ])
                reason_id = reason.split(" - ")[0]
                count = st.slider("Number of reports", 1, 10, 1)
                if st.button("Send Reports (App API)"):
                    total = report_app(target_id, reason_id, count)
                    st.success(f"✅ Sent {total} reports for {username}")
            else:
                st.error("❌ Could not find user ID for refresh.")
        else:
            st.error("❌ Invalid /refresh format. Use /refresh [username]")
    else:
        username = user_input.strip()
        target_id = get_user_id(username)
        if target_id:
            if report_lite(target_id):
                st.success(f"✅ Reported {username} via Instagram Lite.")
                if username not in st.session_state.reported_users:
                    st.session_state.reported_users.append(username)
            else:
                st.error("❌ Report failed.")
        else:
            st.error("❌ Target user not found.")