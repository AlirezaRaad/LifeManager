from uuid import uuid4

import pandas as pd
import streamlit as st

from LifeManager.BM import CBanker


def main():
    if "Banker" not in st.session_state:
        st.session_state.Banker = CBanker()

    if "show_bank_selectbox" not in st.session_state:
        st.session_state.show_bank_selectbox = True

    if st.session_state.show_bank_selectbox:
        st.header("Personal Banker", divider="rainbow")

        opts = {
            "Add Bank": adding_bank,
            "Show All Banks": show_all_banks,
            "Add Expense": show_expenses,
            "Make Transaction": make_transaction,
            "See Banking Records": banking_record,
            "Charting": bnk_charting,
        }

        usr_answer = st.selectbox(
            label="Choose You're Work:", options=list(opts.keys())
        )

        def confirm_selection():
            st.session_state.show_bank_selectbox = False
            st.session_state.selected_function = opts[usr_answer]

        st.button("Confirm", on_click=confirm_selection)

    if not st.session_state.get("show_bank_selectbox", True):
        func = st.session_state.get("selected_function")
        if func:
            func()


def adding_bank():
    bnk: CBanker = st.session_state.Banker

    st.header("Adding a Bank", divider="blue")
    st.markdown(
        """<p style='font-size:24px;color:lightgreen'>In this Section You can add Your Banks that you want to later make transaction.</p>""",
        unsafe_allow_html=True,
    )

    bank_name_input = st.text_input(
        label="Please Enter The Bank Name That You Want To add :", help="eg. PayPal"
    )

    if bank_name_input:

        if st.button(f"Add {bank_name_input} Bank"):
            if bank_name_input == "":
                st.error("Please Enter a valid name for your bank.")

            elif bnk.add_bank(bank_name=bank_name_input):
                st.success("Bank Added Successfully")
            else:
                st.error("There Was an Error in Adding the Bank.")

    st.markdown("<hr style='border: 1px solid purple;'>", unsafe_allow_html=True)
    st.info("Click the button bellow to go to the Main Banking Page:")

    st.button(
        "CLICK...",
        key=str(uuid4()),
        on_click=lambda: st.session_state.update(
            {
                "show_bank_selectbox": True,
            }
        ),
    )


def show_all_banks():
    print(st.session_state)
    bnk: CBanker = st.session_state.Banker

    st.header("All Bankss", divider="rainbow")

    st.dataframe(pd.DataFrame(bnk.show_all_banks(), columns=["All Banks"]))
    st.markdown("<hr style='border: 1px solid crimson;'>", unsafe_allow_html=True)
    st.info("Click the button bellow to go to the Main Banking Page:")

    st.button(
        "CLICK...",
        key=str(uuid4()),
        on_click=lambda: st.session_state.update(
            {
                "show_bank_selectbox": True,
            }
        ),
    )


def show_expenses():
    pass


def make_transaction():
    pass


def banking_record():
    pass


def bnk_charting():
    pass


if __name__ == "__main__":
    main()
