"""
Enhanced Authentication utility for Streamlit app
"""

import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
from typing import Tuple, Optional


def _load_auth_config(yaml_path: str = "credentials.yaml") -> Optional[dict]:
    """Load authentication configuration from YAML file"""
    try:
        with open(yaml_path) as file:
            return yaml.load(file, Loader=SafeLoader)
    except Exception as e:
        st.error(f"❌ Failed to load credentials: {e}")
        return None


def _create_authenticator(config: dict) -> Optional[stauth.Authenticate]:
    """Create and return authenticator object"""
    try:
        return stauth.Authenticate(
            config["credentials"],
            config["cookie"]["name"],
            config["cookie"]["key"],
            config["cookie"]["expiry_days"],
            config.get("preauthorized"),
        )
    except Exception as e:
        st.error(f"❌ Failed to initialize authenticator: {e}")
        return None


def authenticate(yaml_path: str = "credentials.yaml") -> Tuple[bool, Optional[stauth.Authenticate]]:
    """
    Force a strict login page.
    Until the user is authenticated, nothing else will render.
    """
    config = _load_auth_config(yaml_path)
    if not config:
        st.stop()

    authenticator = _create_authenticator(config)
    if not authenticator:
        st.stop()

    # Reserve full page for login only
    with st.container():
        st.markdown(
            """
            <style>
                .block-container {padding-top: 5%; max-width: 500px;}
                header, footer, .stSidebar {visibility: hidden;}
            </style>
            """,
            unsafe_allow_html=True,
        )

        name, auth_status, username = authenticator.login("Login", "main")

    # Save state
    st.session_state["authentication_status"] = auth_status
    st.session_state["name"] = name
    st.session_state["username"] = username

    # Handle results
    if auth_status is False:
        st.error("❌ Incorrect username or password")
        st.stop()
    elif auth_status is None:
        st.warning("🔐 Please log in to continue")
        st.stop()

    # If authenticated, restore sidebar visibility
    st.markdown(
        """
        <style>
            .stSidebar {visibility: visible;}
        </style>
        """,
        unsafe_allow_html=True,
    )

    return True, authenticator


def show_user_info(authenticator: stauth.Authenticate, location: str = "sidebar") -> None:
    """Show user info + logout"""
    if st.session_state.get("authentication_status"):
        name = st.session_state.get("name", "User")

        if location == "sidebar":
            with st.sidebar:
                st.success(f"👋 Welcome *{name}*")
                authenticator.logout("🚪 Logout", "sidebar")
                st.divider()
        else:
            st.success(f"👋 Welcome *{name}*")
            authenticator.logout("🚪 Logout", "main")
