import streamlit as st
import requests
import time
from datetime import datetime, timedelta

# ---------------------
# CONSTANTS
# ---------------------
REASONS = {
    "Violence": "5",
    "Self Injury": "2",
    "Impersonation (@)": "8",
    "Scam or Fraud": "6",
    "Sales of Illegal Drugs": "3"
}

WEB_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
    'Accept': '*/*',
    'Content-Type': 'application/x-www-form-urlencoded',
    'X-Requested-With': 'XMLHttpRequest',
    'Referer': 'https://www.instagram.com/accounts/login/',
}

# ---------------------
# FUNCTIONS
# ---------------------
def login_instagram(username, password):
    session = requests.Session()
    try:
        session.get('https://www.instagram.com/accounts/login/', headers=WEB_HEADERS)
        csrf_token = session.cookies.get_dict().get('csrftoken')

        data = {
            'username': username,
            'enc_password': f'#PWD_INSTAGRAM_BROWSER:0:&:{password}',
            'queryParams': {},
            'optIntoOneTap': 'false'
        }

        headers = WEB_HEADERS.copy()
        headers['X-CSRFToken'] = csrf_token

        resp = session.post(
            'https://www.instagram.com/accounts/login/ajax/',
            data=data,
            headers=headers
        )

        j = resp.json()
        if j.get('authenticated'):
            cookies = session.cookies.get_dict()
            return session, cookies.get('sessionid'), cookies.get('csrftoken'), None
        elif 'checkpoint_url' in j:
            return None, None, None, "Checkpoint required. Login from browser first."
        else:
            return None, None, None, j.get("message", "Login failed.")
    except Exception as e:
        return None, None, None, str(e)

def get_user_id(username, session):
    try:
        resp = session.get(
            f"https://www.instagram.com/api/v1/users/web_profile_info/?username={username}",
            headers={
                "User-Agent": "Mozilla/5.0",
                "Cookie": f"sessionid={session.cookies.get('sessionid')}",
            }
        )
        return resp.json()["data"]["user"]["id"]
    except:
        return None

def send_report(user_id, session, csrf_token, reason_id):
    headers = {
        "User-Agent": "Mozilla/5.0",
        "X-CSRFToken": csrf_token,
        "Content-Type": "application/x-www-form-urlencoded",
        "Cookie": f"sessionid={session.cookies.get('sessionid')}; csrftoken={csrf_token};",
    }

    data = f"source_name=&reason_id={reason_id}&frx_context="
    try:
        r = session.post(f"https://www.instagram.com/users/{user_id}/flag/", headers=headers, data=data)
        return r.status_code
    except Exception as e:
        return str(e)

# ---------------------
# STREAMLIT UI
# ---------------------
st.set_page_config(page_title="Instagram Web Reporter", layout="centered")
st.title("⏰ Instagram Web Reporter (Scheduled Start)")

with st.form("login_form"):
    st.subheader("🔐 Login with Instagram Web")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    submitted = st.form_submit_button("Login")

if submitted:
    session, sessionid, csrf_token, error = login_instagram(username, password)
    if session:
        st.success("✅ Logged in successfully.")
        st.session_state.session = session
        st.session_state.csrf = csrf_token
        st.session_state.logged_in = True
    else:
        st.error(f"❌ Login failed: {error}")

if st.session_state.get("logged_in"):
    with st.form("report_form"):
        st.subheader("🕒 Schedule Report at Specific Time")
        target_usernames = st.text_area("Usernames (comma-separated)")
        selected_reason = st.selectbox("Reason for report", list(REASONS.keys()))
        report_count = st.slider("Reports per user", 1, 20, 5)
        delay = st.slider("Delay between reports (seconds)", 1, 10, 3)

        scheduled_hour = st.selectbox("Hour (24h format)", list(range(0, 24)), index=0)
        scheduled_minute = st.selectbox("Minute", list(range(0, 60, 5)), index=0)

        start_schedule = st.form_submit_button("📅 Schedule Reports")

    if start_schedule:
        now = datetime.now()
        scheduled_time = now.replace(hour=scheduled_hour, minute=scheduled_minute, second=0, microsecond=0)
        if scheduled_time <= now:
            scheduled_time += timedelta(days=1)

        wait_seconds = (scheduled_time - now).total_seconds()
        st.info(f"⏳ Waiting until {scheduled_time.strftime('%Y-%m-%d %H:%M:%S')} to start...")

        if wait_seconds > 300:
            st.warning("⚠️ Long delays may not work on Streamlit Cloud. Run locally for best results.")
            time.sleep(3)
        else:
            time.sleep(wait_seconds)

        usernames = [u.strip() for u in target_usernames.split(",") if u.strip()]
        reason_id = REASONS[selected_reason]
        log_area = st.empty()
        logs = []

        for username in usernames:
            user_id = get_user_id(username, st.session_state.session)
            if not user_id:
                logs.append(f"❌ @{username} not found.")
                log_area.text("\n".join(logs))
                continue

            for i in range(1, report_count + 1):
                code = send_report(user_id, st.session_state.session, st.session_state.csrf, reason_id)
                if code in [200, 302]:
                    logs.append(f"✅ @{username} report {i}/{report_count}")
                elif code == 429:
                    logs.append(f"⛔ @{username} rate limited.")
                    break
                else:
                    logs.append(f"⚠️ @{username} failed with status: {code}")
                log_area.text("\n".join(logs))
                time.sleep(delay)

        st.success("✅ All scheduled reports completed.")
