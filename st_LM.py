import streamlit as st

from LifeManager.LM import LifeManager

# Initiate the Life Manager instance
lm = LifeManager()


def main():
    st.header("Life Manager", divider="rainbow")
    st.markdown(
        """
    <p style='font-size:24px;'>In this Part You have access to the all of the <em>LifeManger's tools</em></p>

    """,
        unsafe_allow_html=True,
    )

    #! initiate a lock for user to lock the answers that I can fetch the informationS
    if "lock_first" not in st.session_state:
        st.session_state.lock_first = False

    # * Some Options for drop sown box
    options = {
        "Add Daily Task": None,
        "Show Tasks": ["Parent", "Child", "Child Of", "All"],
        "Insert A task to DB": None,
        "DataGuardian": {"Backup", "Restore"},
        "Charting": None,
    }

    # $ Make a flag to enforce the feeling of disappearing the menu
    if "show_dropdown" not in st.session_state:
        st.session_state.show_dropdown = True

    if st.session_state.show_dropdown:

        # First dropdown
        category = st.selectbox(
            label="Select a category:",
            options=list(options.keys()),
            disabled=st.session_state.lock_first,
            index=3,
        )
        tsk = {1: category}

        if options[category] is not None:

            # Second dropdown: Depends on first selection
            sub_item = st.selectbox(
                label="Select an Calculation Strategy:",
                options=options[category],
                disabled=st.session_state.lock_first,
            )
            tsk[2] = sub_item
            st.session_state["user_desired_task"] = tsk

        else:
            st.session_state["user_desired_task"] = tsk

        # ? If user want's to see the child of certain parent it should write here
        try:
            if st.session_state["user_desired_task"][2] == "Child Of":
                child_of = st.text_input(
                    "Enter The Parent Task That You Want to see its child: "
                )
                st.session_state["user_desired_task"][3] = child_of
        except KeyError:
            pass

        if st.button(label="Lock and Proceed"):
            st.session_state.lock_first = True
            st.session_state.show_dropdown = False

    if st.session_state.show_dropdown is False:
        if st.button(label="UnLock and Change"):

            st.session_state.lock_first = False
            st.session_state.show_dropdown = True

        if st.session_state["user_desired_task"][1] == "Add Daily Task":
            add_daily_task()

        if st.session_state["user_desired_task"][1] == "Show Tasks":
            show_tasks()

        if st.session_state["user_desired_task"][1] == "Insert A task to DB":
            pass

        if st.session_state["user_desired_task"][1] == "DataGuardian":
            DataGuardian()

        if st.session_state["user_desired_task"][1] == "Charting":
            chart_it()


print(st.session_state)


def add_daily_task():

    st.markdown(
        body="""<p style='font-size:24px;'><b>Please Fill :</b></p>""",
        unsafe_allow_html=True,
    )

    _task = st.text_input(label=f"Please Enter the Task Name:")

    if st.checkbox(
        "I want to ad this as a Child<",
        help="Checking this box means that this task is child of another task.",
    ):
        lm.fe


def chart_it():
    pass


def show_tasks():
    pass


def DataGuardian():
    pass


def insert_task():
    pass


if __name__ == "__main__":
    main()
