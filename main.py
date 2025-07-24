import streamlit as st
import requests
import time
from datetime import datetime

# Existing login/session input ...
# (Keep your current sessionid/csrftoken input blocks)

# Add to session state
if 'last_refresh_time' not in st.session_state:
    st.session_state.last_refresh_time = None
if 'auto_refresh_enabled' not in st.session_state:
    st.session_state.auto_refresh_enabled = False

# Target + Refresh Config
st.subheader("📌 Report Target or Auto Refresh")
username = st.text_input("Target Username to report repeatedly")

enable_refresh = st.checkbox("🔁 Enable Auto Refresh Report", value=st.session_state.auto_refresh_enabled)
interval = st.slider("⏱️ Interval in minutes", 1, 60, 10)

if username:
    target_id = get_user_id(username)

    if target_id:
        if enable_refresh:
            st.session_state.auto_refresh_enabled = True

            now = datetime.now()
            if (
                st.session_state.last_refresh_time is None or
                (now - st.session_state.last_refresh_time).total_seconds() > interval * 60
            ):
                st.info("Auto-report triggered...")
                result = report_lite(target_id)  # Or use report_app(target_id, reason_id, 1)
                if result:
                    st.success(f"✅ Report sent at {now.strftime('%H:%M:%S')}")
                    st.session_state.last_refresh_time = now
                    if username not in st.session_state.reported_users:
                        st.session_state.reported_users.append(username)
                else:
                    st.error("❌ Failed to send auto-report.")

                # Wait a few seconds and rerun
                time.sleep(5)
                st.experimental_rerun()
            else:
                remaining = interval * 60 - (now - st.session_state.last_refresh_time).total_seconds()
                st.info(f"⏳ Next auto-report in {int(remaining)} seconds...")
        else:
            st.session_state.auto_refresh_enabled = False
            if st.button("🚨 Manual Report Now"):
                result = report_lite(target_id)
                if result:
                    st.success(f"✅ Report sent at {datetime.now().strftime('%H:%M:%S')}")
                    if username not in st.session_state.reported_users:
                        st.session_state.reported_users.append(username)
                else:
                    st.error("❌ Report failed.")

else:
    st.warning("⚠️ Enter a username to enable auto-refreshing.")
