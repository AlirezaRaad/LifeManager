from uuid import uuid4

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

        st.info("Click the button bellow to Lock and Proceed")
        if st.button("Double CLICK..."):
            st.session_state.lock_first = True
            st.session_state.show_dropdown = False

    if st.session_state.show_dropdown is False:

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


def add_daily_task():
    st.divider()
    st.info(
        "The difference between **PARENT** and **CHILD** task is as following:\n\nA Parent task is a main and general task and a Child task is a sub-task.\n\nFor example For `Learning` **PARENT** task, The `Udemy` can be a sub-task of **CHILD** task because for me udemy is one of my learning resources."
    )
    st.markdown(
        body="""<p style='font-size:24px;'><b>Please Fill :</b></p>""",
        unsafe_allow_html=True,
    )

    _task = st.text_input(label=f"Please Enter the **Task Name**:")
    parent_task = None

    x = st.checkbox(
        "I want to ad this as a **Child**",
        help="Checking this box means that this task is child of another task.",
    )
    if x:
        parent_task = st.selectbox(
            label="**Please Enter The Parent of your child:**",
            options=lm.get_all_parent_tasks(),
        )
    st.divider()

    st.warning(
        f"""
    **Confirmation Required**

    You are about to add:
    
    - Task: {_task}
    - Type: {"PARENT" if parent_task is None else f"CHILD OF {parent_task.upper()}"}

    Please confirm.
    """
    )
    print(parent_task)
    if st.button("CONFIRM"):

        if lm.add_daily_task(task_name=_task, ref_to=parent_task):

            st.success("Successfully added to the DATABASE!")
        else:
            st.error("There was an error while adding to the DATABASE")

    st.info("Click the button bellow to go to the MainPage:")

    if st.button("Double CLICK.."):
        st.session_state.lock_first = False
        st.session_state.show_dropdown = True


def chart_it():
    st.info("Click the button bellow to go to the MainPage:")

    if st.button("Double CLICK...", key=uuid4()):
        st.session_state.lock_first = False
        st.session_state.show_dropdown = True


def show_tasks():
    st.info("Click the button bellow to go to the MainPage:")

    if st.button("Double CLICK...", key=uuid4()):
        st.session_state.lock_first = False
        st.session_state.show_dropdown = True


def DataGuardian():
    st.info("Click the button bellow to go to the MainPage:")

    if st.button("Double CLICK...", key=uuid4()):
        st.session_state.lock_first = False
        st.session_state.show_dropdown = True


def insert_task():
    st.info("Click the button bellow to go to the MainPage:")

    if st.button("Double CLICK...", key=uuid4()):
        st.session_state.lock_first = False
        st.session_state.show_dropdown = True


if __name__ == "__main__":
    main()
