import streamlit as st
import requests
import time

st.set_page_config(page_title="Instagram Reporter", layout="centered")
st.title("📢 Instagram Auto Reporter")

st.markdown("#### 🔐 Enter your Instagram session details")
sessionid = st.text_input("Session ID", type="password")
csrftoken = st.text_input("CSRF Token", type="password")

st.markdown("#### 👤 Usernames to report (one per line)")
usernames_input = st.text_area("Enter usernames", placeholder="user1\nuser2\nuser3")

report_reason = st.selectbox("🚨 Select reason for reporting", {
    "Nudity or sexual activity": "1",
    "Spam": "2",
    "Hate speech or symbols": "5",
    "Violence or dangerous organizations": "6",
    "Scam or fraud": "8"
})

def get_user_id(username, sessionid, csrftoken):
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Cookie": f"sessionid={sessionid}; csrftoken={csrftoken};"
    }
    url = f"https://www.instagram.com/api/v1/users/web_profile_info/?username={username}"
    res = requests.get(url, headers=headers)
    if res.status_code == 200:
        return res.json()["data"]["user"]["id"]
    return None

def report_user(user_id, sessionid, csrftoken, reason_code):
    url = f"https://www.instagram.com/users/{user_id}/report/"
    headers = {
        "User-Agent": "Instagram 275.0.0.27.107 Android",
        "X-CSRFToken": csrftoken,
        "Cookie": f"sessionid={sessionid}; csrftoken={csrftoken};",
    }
    data = {"reason": reason_code}
    res = requests.post(url, headers=headers, data=data)
    return res.status_code

if st.button("🚨 Report Now"):
    if not sessionid or not csrftoken:
        st.error("Please enter valid session details.")
    elif not usernames_input.strip():
        st.error("Please enter at least one username.")
    else:
        usernames = [u.strip() for u in usernames_input.strip().split("\n") if u.strip()]
        with st.spinner("Sending reports..."):
            results = []
            for username in usernames:
                try:
                    user_id = get_user_id(username, sessionid, csrftoken)
                    if user_id:
                        status = report_user(user_id, sessionid, csrftoken, report_reason)
                        if status == 200:
                            results.append(f"✅ Reported @{username} successfully.")
                        elif status == 403:
                            results.append(f"❌ Forbidden: Check session for @{username}.")
                        elif status == 429:
                            results.append(f"❗ Rate limited while reporting @{username}.")
                        else:
                            results.append(f"⚠️ Failed to report @{username}. Status code: {status}")
                    else:
                        results.append(f"❌ Could not fetch ID for @{username}")
                    time.sleep(2)  # to prevent rate-limiting
                except Exception as e:
                    results.append(f"⚠️ Error for @{username}: {str(e)}")
            st.success("Reporting complete.")
            for res in results:
                st.write(res)
