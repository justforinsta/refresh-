import streamlit as st
import requests
import time

st.set_page_config(page_title="Instagram Impersonation Reporter", layout="centered")
st.title("📣 Instagram Multi-Target Impersonation Reporter")

# Input form
with st.form("report_form"):
    sessionid = st.text_input("Session ID", type="password")
    csrftoken = st.text_input("CSRF Token", type="password")
    usernames_input = st.text_area("Target Instagram Usernames (comma or new line)", height=150)
    impersonation_type = st.selectbox("Who are they impersonating?", ["me", "someone_else", "celebrity"])
    refresh_mode = st.checkbox("🔁 Simulate refresh (resend same report to look fresh)")
    submit = st.form_submit_button("🚨 Report All")

# Parse usernames
def parse_usernames(raw):
    return list(set([
        u.strip().lstrip('@')
        for line in raw.splitlines()
        for u in line.split(',') if u.strip()
    ]))

# Setup headers
def build_headers(sessionid, csrftoken):
    return {
        "User-Agent": "Instagram 255.0.0.19.111 Android",
        "X-CSRFToken": csrftoken,
        "Cookie": f"sessionid={sessionid}; csrftoken={csrftoken};",
        "Referer": "https://www.instagram.com/",
        "Content-Type": "application/x-www-form-urlencoded"
    }

# Get Instagram User ID
def get_user_id(username, headers):
    url = f"https://www.instagram.com/api/v1/users/web_profile_info/?username={username}"
    try:
        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            return r.json()['data']['user']['id']
        elif r.status_code == 404:
            st.warning(f"🔍 @{username} not found.")
        elif r.status_code == 403:
            st.error(f"🚫 Forbidden for @{username}. Session might be invalid or blocked.")
        else:
            st.error(f"❌ Error fetching @{username} (status {r.status_code})")
            st.code(r.text)
    except Exception as e:
        st.error(f"⚠️ Error while requesting @{username}: {e}")
    return None

# Submit impersonation report
def report_user(user_id, headers, imp_type, refresh=False):
    url = f"https://www.instagram.com/users/{user_id}/report/"
    meta_json = {
        "impersonation_type": imp_type,
        "details": "Ongoing impersonation. Repeated report." if refresh else "This account is impersonating me."
    }
    payload = {
        "reason_id": "8",  # Impersonation
        "source_name": "profile",
        "meta": str(meta_json).replace("'", '"')  # Make it JSON-safe
    }
    return requests.post(url, headers=headers, data=payload)

# Main action
if submit:
    if not sessionid or not csrftoken or not usernames_input:
        st.warning("⚠️ Please fill in all required fields.")
    else:
        usernames = parse_usernames(usernames_input)
        headers = build_headers(sessionid, csrftoken)

        st.info(f"📤 Starting reports for {len(usernames)} targets...")

        for username in usernames:
            st.markdown(f"---\n### 👤 @{username}")
            user_id = get_user_id(username, headers)
            if user_id:
                response = report_user(user_id, headers, impersonation_type, refresh=refresh_mode)
                if response.status_code == 200:
                    st.success("✅ Report sent successfully.")
                else:
                    st.error("❌ Report failed.")
                    st.code(response.text)
            else:
                st.warning("⚠️ Skipping. Could not get user ID.")
            time.sleep(1.5)  # Delay to mimic human behavior
