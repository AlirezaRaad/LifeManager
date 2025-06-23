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
            "Add Expense": add_expenses,
            "Show All Expenses": show_expenses,
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


def add_expenses():
    bnk: CBanker = st.session_state.Banker

    st.header("Adding Expense to the Database.", divider="red")
    st.markdown(
        """
<p style='font-size:25px;color:lightgreen'> In this Section you will add Expenses to the database as a <b>PARENT/CHILD</b>.
The difference between PARENT and CHILD Expense is as differ from one person to another:</p> 

<p style='font-size:25px;color:aqua'>For One person, buying <b>Tobacco</b> is a Child Expense under <b>wasting money</b> Parent Expense, but for other person, it is his/her main expense.</p>""",
        unsafe_allow_html=True,
    )

    st.markdown(
        body="""<p style='font-size:24px;'><b>Please Fill :</b></p>""",
        unsafe_allow_html=True,
    )

    #! Present the user a text input to put something in it; Simultiansly Make the parent_task variable.
    _task = st.text_input(label=f"Please Enter the **Expense Name**:")
    parent_expense = None

    # $ This Check box indicate that if user want to the `_task` variable be a Parent or a Child.
    x = st.checkbox(
        "I want to ad this as a **Child** Expense",
        help="Checking this box means that this task is child of another Expense.",
    )
    if x:
        parent_expense = st.selectbox(
            label="**Please Enter The Parent of your child:**",
            options=bnk._get_all_parent_expenses(),
        )
    st.divider()

    st.warning(
        f"""
    **Confirmation Required**

    You are about to add:
    
    - Expense: {_task}
    - Type: {"PARENT" if parent_expense is None else f"CHILD OF {parent_expense.upper()}"}

    Please confirm.
    """
    )

    def Confirm_add_daily_task():
        """This function tries to add the task to the database then we make a flag for after clicking the bellow button."""

        if bnk.add_expense(expense_name=_task, ref_to=parent_expense):
            st.session_state.feedback = True
        else:
            st.session_state.feedback = False

    st.button(label="CONFIRM", on_click=Confirm_add_daily_task)

    if "feedback" in st.session_state:
        if st.session_state.feedback:
            st.success("Successfully added to the DATABASE!")
        else:
            st.error("There was an error while adding to the DATABASE")

    st.markdown("<hr style='border: 1px solid red;'>", unsafe_allow_html=True)

    st.info("Click the button bellow to go to the Main Page:")

    st.button(
        "CLICK...",
        key=str(uuid4()),
        on_click=lambda: st.session_state.update(
            {
                "lock_first": False,
                "show_dropdown": True,
                "LifeManager_main_header": True,
            }
        ),
    )


def show_expenses():
    bnk: CBanker = st.session_state.Banker

    st.header("All Expenses", divider="green")
    st.markdown(
        """<p style='font-size:24px;color:aqua'>All the Expenses that you added to the DATABASE. </p>""",
        unsafe_allow_html=True,
    )

    parent = pd.DataFrame(bnk._get_all_parent_expenses(), columns=["Parent Expenses"])

    st.header("Parent Expenses", divider="violet")
    st.dataframe(parent)

    st.header("Child of Certain Expenses", divider="orange")
    _task = st.selectbox(label="Select the Parent Expenses:", options=parent)

    st.dataframe(
        pd.DataFrame(
            bnk._get_all_child_expenses(_task), columns=[f"Child Expenses of {_task}"]
        )
    )

    st.info("Click the button bellow to go to the MainPage:")
    st.button(
        "CLICK...",
        key=str(uuid4()),
        on_click=lambda: st.session_state.update(
            {
                "lock_first": False,
                "show_dropdown": True,
                "LifeManager_main_header": True,
            }
        ),
    )


def make_transaction():
    pass


def banking_record():
    pass


def bnk_charting():
    pass


if __name__ == "__main__":
    main()
