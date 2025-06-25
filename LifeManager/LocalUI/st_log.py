import os

import streamlit as st


def main():
    st.title("📄 Latest Log Viewer")

    log_folder = os.environ["LOG_FILE_PATH"]
    file_path = os.path.join(log_folder, sorted(os.listdir(log_folder))[-1])

    try:
        with open(file_path, "r", encoding="utf-8") as fh:
            content = fh.read()

        with open(file_path, "rb") as file_bytes:
            st.download_button(
                label="📥 Download File",
                data=file_bytes,
                file_name=os.path.basename(file_path),
                mime="text/plain",
            )
        st.text_area("File Content", content, height=400)
    except Exception as e:
        st.error(f"Error reading file: {e}")
