"""Shared Streamlit styling for a clean, healthcare-oriented UI."""

import streamlit as st


def apply_healthcare_theme() -> None:
    """
    Inject custom CSS: soft clinical palette, readable typography, and card-like KPI areas.
    Streamlit does not expose full theme APIs for all components; CSS bridges the gap.
    """
    st.markdown(
        """
        <style>
            /* Main app background */
            .stApp {
                background: linear-gradient(180deg, #f6f9fc 0%, #eef4f8 100%);
            }
            /* Sidebar */
            [data-testid="stSidebar"] {
                background: linear-gradient(180deg, #0d3b5c 0%, #0a2d45 100%);
            }
            [data-testid="stSidebar"] * {
                color: #e8f4fc !important;
            }
            [data-testid="stSidebar"] .stMarkdown a {
                color: #7dd3fc !important;
            }
            /* Primary buttons */
            .stButton > button {
                background-color: #0d9488;
                color: white;
                border: none;
                border-radius: 8px;
            }
            /* Metric cards — target the metric container */
            div[data-testid="stMetric"] {
                background: #ffffff;
                border: 1px solid #dbeafe;
                border-radius: 12px;
                padding: 0.75rem 1rem;
                box-shadow: 0 1px 3px rgba(13, 59, 92, 0.08);
            }
            div[data-testid="stMetric"] label {
                color: #64748b !important;
            }
            h1, h2, h3 {
                color: #0f172a;
                font-weight: 600;
            }
            .health-caption {
                color: #475569;
                font-size: 0.95rem;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def page_header(title: str, subtitle: str | None = None) -> None:
    """Consistent page title and optional subtitle."""
    st.markdown(f"## {title}")
    if subtitle:
        st.markdown(f'<p class="health-caption">{subtitle}</p>', unsafe_allow_html=True)
