"""Central Streamlit page configuration to keep multipage settings consistent."""

from __future__ import annotations

import streamlit as st

from utils.styling import apply_healthcare_theme


def setup_page(page_title: str) -> None:
    """Apply layout, sidebar, and shared CSS once per script run."""
    st.set_page_config(
        page_title=page_title,
        page_icon="🏥",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    apply_healthcare_theme()
