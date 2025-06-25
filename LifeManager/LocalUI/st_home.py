import streamlit as st


def main():
    st.header("Home Page", divider="rainbow")
    st.markdown(
        """
        <p style='font-size:24px'><font color='Yellow'><b>Created By :</b></font> Alireza Raad</p>
        <p style='font-size:24px;'><a href="https://raadlearn.com">Website</a> | <a href="https://github.com/AlirezaRaad/LifeManager">Github Page.</a></p>""",
        unsafe_allow_html=True,
    )
