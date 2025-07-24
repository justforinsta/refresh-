import streamlit as st
import requests
import time

# ---------------------
# CONSTANTS
# ---------------------
REASON_CODE = "2"  # Self Injury

# ---------------------
# HELPER FUNCTIONS
# ---------------------
def get_user_id(username, sessionid):
    try:
        r = requests.get(
            f"https://i.instagram.com/api/v1/users/web_profile_info/?username={username}",
            headers={
                "User-Agent": "Instagram 155.0.0.37.107",
                "Cookie": f"sessionid={sessionid};",
            }
        )
        return r.json()["data"]["user"]["id"]
    except:
        return None

def send_report(user_id, sessionid, csrftoken):
    res = requests.post(
        f"https://i.instagram.com/users/{user_id}/flag/",
        headers={
            "User-Agent": "Mozilla/5.0",
            "Host": "i.instagram.com",
            "cookie": f"sessionid={sessionid}",
            "X-CSRFToken": csrftoken,
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"
        },
        data=f'source_name=&reason_id={REASON_CODE}&frx_context=',
        allow_redirects=False
    )
    return res.status_code

# ---------------------
# STREAMLIT UI
# ---------------------
st.set_page_config(page_title="Instagram Reporter", layout="centered")
st.title("📢 Instagram Self Injury Reporter")

with st.form("report_form"):
    session_id = st.text_input("🔐 Instagram Session ID", type="password")
    csrf_token = st.text_input("🔑 CSRF Token", type="password")
    targets = st.text_area("🎯 Target Usernames (comma-separated)")
    report_count = st.number_input("🔁 Reports per target", min_value=1, max_value=100, value=5)
    delay = st.slider("⏱️ Delay between reports (seconds)", min_value=1, max_value=30, value=5)
    submit = st.form_submit_button("🚀 Start Reporting")

if submit:
    if not session_id or not csrf_token or not targets:
        st.error("⚠️ Please fill in all required fields.")
    else:
        usernames = [u.strip() for u in targets.split(",") if u.strip()]
        st.info(f"Starting reports for {len(usernames)} user(s)...")
        report_log = st.empty()
        log_lines = []

        for username in usernames:
            user_id = get_user_id(username, session_id)
            if not user_id:
                log_lines.append(f"❌ @{username} not found.")
                report_log.text("\n".join(log_lines))
                continue

            for i in range(1, report_count + 1):
                code = send_report(user_id, session_id, csrf_token)
                if code in [200, 302]:
                    log_lines.append(f"✅ @{username} report {i}/{report_count} (Self Injury)")
                elif code == 429:
                    log_lines.append(f"🚫 @{username} rate limited.")
                    break
                else:
                    log_lines.append(f"⚠️ @{username} unknown response: {code}")
                report_log.text("\n".join(log_lines))
                time.sleep(delay)

        st.success("🎉 Reporting complete!")
