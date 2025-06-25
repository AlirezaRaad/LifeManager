"""
This is the main module for streamlit project.
"""

import streamlit as st
from st_BM import main as bnk
from st_home import main as home
from st_log import main as loggs

from LifeManager.LocalUI.st_LM import main as lm


def main():
    PAGES = {"Home": home, "Life Manager": lm, "Banking": bnk, "LOG FILE": loggs}

    # Get the selected page from the sidebar
    selected_page = st.sidebar.radio("Go to", list(PAGES.keys()), index=0)

    # Run the function associated with the selected page
    PAGES[selected_page]()


if __name__ == "__main__":
    main()
