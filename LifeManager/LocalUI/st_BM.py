import datetime as dt
import os
from uuid import uuid4
from zipfile import ZipFile

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
    st.markdown(
        "<p style='font-size:24px;'>Click the button bellow to go to the Main Banking Page</p>",
        unsafe_allow_html=True,
    )

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

    st.markdown("<hr style='border: 1px solid yellow;'>", unsafe_allow_html=True)
    st.markdown(
        "<p style='font-size:24px;'>Click the button bellow to go to the Main Banking Page</p>",
        unsafe_allow_html=True,
    )
    st.button(
        "CLICK...",
        key=str(uuid4()),
        on_click=lambda: st.session_state.update(
            {
                "show_bank_selectbox": True,
            }
        ),
    )


def make_transaction():
    bnk: CBanker = st.session_state.Banker
    st.header("Record a Transaction", divider="rainbow")

    usr_bank = st.selectbox(
        label="Please Select you'r Bank: ", options=bnk.show_all_banks()
    )

    usr_amount = st.number_input(label="Enter The Amount of Transaction : ")

    expense = st.selectbox(
        label="Choose the Parent Expense : ", options=bnk._get_all_parent_expenses()
    )

    usr_expense = st.selectbox(
        label="Now Choose You'r Expense: ", options=bnk._get_all_child_expenses(expense)
    )

    user_description = st.text_input(
        label="Enter Description : ", placeholder="Description"
    )

    st.markdown(
        f"""<p style='font-size:24px;'>Conform:
                - <b>Bank : </b> {usr_bank}</br>
                - <b>Amount : </b> {usr_amount}</br>
                - <b>Expense : </b> {usr_expense}</br>
                - <b>Description : </b> {user_description} </p>
""",
        unsafe_allow_html=True,
    )

    if st.button("Confirm Transaction :"):
        if bnk.make_transaction(
            bank_name=usr_bank,
            amount=usr_amount,
            expense_type=usr_expense,
            description="null" if not bool(user_description) else user_description,
        ):
            st.success("Transaction made Successfully.")
        else:
            st.error(
                "Transaction neither failed nor you don't have any credit left to spend."
            )

    st.markdown("<hr style='border: 1px solid yellow;'>", unsafe_allow_html=True)
    st.markdown(
        "<p style='font-size:24px;'>Click the button bellow to go to the Main Banking Page</p>",
        unsafe_allow_html=True,
    )
    st.button(
        "CLICK...",
        key=str(uuid4()),
        on_click=lambda: st.session_state.update(
            {
                "show_bank_selectbox": True,
            }
        ),
    )


def banking_record():
    bnk: CBanker = st.session_state.Banker
    st.header("Banking Records:", divider="rainbow")

    usr_bank = st.selectbox(label="Select Your bank: ", options=bnk.show_all_banks())
    col1, col2 = st.columns(2)

    with col1:
        yesterday = dt.date.today() - dt.timedelta(days=1)
        from_date = st.date_input(label="From : ", value=yesterday, max_value=yesterday)
    with col2:

        to_date = st.date_input(label="To :")

    st.markdown(
        f"<p style='font-size:24px;'>See The transaction of {usr_bank} BANK, From {from_date} To {to_date} </p>",
        unsafe_allow_html=True,
    )

    if st.button(label="Show"):
        if bnk.fetch_records(
            bank_name=usr_bank, start_date=f"{from_date}", end_date=f"{to_date}"
        ):
            st.success("Successful")
            excel_folder = os.environ["BANKING_RECORD_PATH"]

            # Filter files that start with the bank name
            excel_path = [
                os.path.join(excel_folder, i)
                for i in os.listdir(excel_folder)
                if i.lower().startswith(usr_bank.lower())
            ]

            st.dataframe(pd.read_excel(excel_path[0]))

            with open(excel_path[0], "rb") as fh:
                data = fh.read()

            st.markdown(
                f"<p style='font-size:24px;'>Download The Excel File: </p>",
                unsafe_allow_html=True,
            )
            st.download_button(label="Download", file_name=excel_path[0], data=data)
        else:
            st.error("There Was an error!")

    st.markdown("<hr style='border: 1px solid yellow;'>", unsafe_allow_html=True)
    st.markdown(
        "<p style='font-size:24px;'>Click the button bellow to go to the Main Banking Page</p>",
        unsafe_allow_html=True,
    )
    st.button(
        "CLICK...",
        key=str(uuid4()),
        on_click=lambda: st.session_state.update(
            {
                "show_bank_selectbox": True,
            }
        ),
    )


def bnk_charting():
    bnk: CBanker = st.session_state.Banker

    st.header("Charting Section")
    st.markdown("---")
    st.info(
        """
If you **don’t see your bank chart or chart** after clicking the button **Add All**,  
try to **add a transaction** to update the data.
"""
    )

    last_x_days = st.text_input(
        label="Transaction Period (in days):",
        help="Enter a number like 10 to view transactions from the last 10 days.",
        placeholder="e.g., 10",
    )

    try:
        last_x_days_int = int(last_x_days)
    except (ValueError, TypeError):
        last_x_days_int = None
        if last_x_days:
            st.error("Please enter a valid number for days.")

    def show_image():
        figures_dir = os.environ.get("FIGURES_PATH", "figures")

        pics = [i for i in os.listdir(figures_dir) if i.startswith("bank_")]

        pics_path = [
            (
                os.path.join(figures_dir, i),
                f"Bank {i.removeprefix("bank_").removesuffix(".png")}",
            )
            for i in pics
        ]

        for image_path, caption in pics_path:
            st.image(image_path, caption=caption)

        # % For this part, I will first, Zip the pic's then send them.
        zip_path = os.path.join(os.environ["FIGURES_PATH"], "BM_figures.zip")

        with ZipFile(zip_path, "w") as zipfh:
            for i in pics_path:
                zipfh.write(i[0], arcname=os.path.basename(i[0]))

        # Read the ZIP content
        with open(zip_path, "rb") as fh:
            zip_content = fh.read()

            # Download button in Streamlit
            st.download_button(
                label="Download All Figures",
                data=zip_content,
                file_name="BM_figures.zip",
                mime="application/zip",
            )

    if last_x_days_int:
        if st.button("Show the Week's Status", type="primary"):

            if bnk.chart_it(last_x_days=last_x_days_int):
                st.success("The Figures Are Ready")
                show_image()
            else:
                st.error("A problem occurred while making the figures")

    def return_to_main():
        [
            os.remove(i) if os.path.exists(i) else None
            for i in {os.path.join(os.environ["FIGURES_PATH"], "BM_figures.zip")}
        ]
        st.session_state.update(
            {
                "show_bank_selectbox": True,
            }
        ),

    st.markdown("<hr style='border: 1px solid yellow;'>", unsafe_allow_html=True)
    st.markdown(
        "<p style='font-size:24px;'>Click the button bellow to go to the Main Banking Page</p>",
        unsafe_allow_html=True,
    )

    st.button("CLICK...", key=str(uuid4()), on_click=return_to_main)


if __name__ == "__main__":
    main()
