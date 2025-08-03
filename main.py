import streamlit as st
import requests
import time

st.set_page_config(page_title="Instagram Multi-Impersonation Reporter", layout="centered")
st.title("👥 Instagram Multi-Impersonation Reporter")

# Input form
with st.form("report_form"):
    sessionid = st.text_input("Session ID", type="password")
    csrftoken = st.text_input("CSRF Token", type="password")
    usernames_input = st.text_area("Target Instagram Usernames (comma or new line)", height=150)
    impersonation_type = st.selectbox("Who are they impersonating?", ["me", "someone_else", "celebrity"])
    refresh_mode = st.checkbox("🔁 Simulate timestamp refresh (send identical report again)")
    submit = st.form_submit_button("🚨 Report All")

# Normalize username input
def parse_usernames(raw):
    return list(set([u.strip().lstrip('@') for line in raw.splitlines() for u in line.split(',') if u.strip()]))

if submit:
    if not sessionid or not csrftoken or not usernames_input:
        st.warning("⚠️ Please fill in all fields.")
    else:
        headers = {
            "User-Agent": "Instagram 255.0.0.19.111 Android",
            "X-CSRFToken": csrftoken,
            "Cookie": f"sessionid={sessionid}; csrftoken={csrftoken};",
            "Referer": "https://www.instagram.com/",
            "Content-Type": "application/x-www-form-urlencoded"
        }

        usernames = parse_usernames(usernames_input)

        def get_user_id(username):
            url = f"https://www.instagram.com/api/v1/users/web_profile_info/?username={username}"
            r = requests.get(url, headers=headers)
            if r.status_code == 200:
                return r.json()["data"]["user"]["id"]
            return None

        def report_user(user_id, imp_type, refresh=False):
            url = f"https://www.instagram.com/users/{user_id}/report/"
            meta_json = {
                "impersonation_type": imp_type,
                "details": "Ongoing impersonation. Report refresh." if refresh else "Impersonating my identity."
            }
            payload = {
                "reason_id": "8",
                "source_name": "profile",
                "meta": str(meta_json).replace("'", '"')
            }
            return requests.post(url, headers=headers, data=payload)

        # Process each target
        for username in usernames:
            st.markdown(f"### 👤 @{username}")
            user_id = get_user_id(username)
            if user_id:
                r = report_user(user_id, impersonation_type, refresh=refresh_mode)
                if r.status_code == 200:
                    st.success(f"✅ Report submitted for @{username}")
                else:
                    st.error(f"❌ Report failed for @{username}")
                    st.code(r.text)
            else:
                st.warning(f"⚠️ Could not fetch ID for @{username}")
            time.sleep(1.5)  # Slight delay to avoid spam detection
