# pages/12_Logout.py
import streamlit as st


st.set_page_config(page_title="Logout", layout="centered")

st.title("Logout")

if st.button("Logout from my account"):
    # Clear all session state keys
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    
    st.success("You have been successfully logged out. Redirecting to the main page...")
    # Redirect to the main page
    st.page_link("streamlit_app.py", label="Go to Login Page")
    # Stop the rest of the page from running
    st.stop()

st.info("Click the button above to log out.")