"""The bidirectional Streamlit component that draws The Messenger Wisps (declared here because Streamlit needs a real module)."""
from pathlib import Path

import streamlit.components.v1 as components

_component = components.declare_component("qkd", path=str(Path(__file__).resolve().parent / "assets" / "qkd_component"))


def qkd(payload, key):
    """Show `payload`; returns the latest value the page sent back (an action or a hello), or None."""
    return _component(payload=payload, key=key, default=None)
