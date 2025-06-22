import os
from uuid import uuid4

import streamlit as st
from dotenv import load_dotenv

from LifeManager.LM import LifeManager

# Initiate the Life Manager instance and load the env variables.
if "LifeManager" not in st.session_state:
    load_dotenv()
    lm = LifeManager()
    st.session_state.LifeManager = True


def main():
    global lm

    if "LifeManager_main_header" not in st.session_state:
        st.session_state.LifeManager_main_header = True

    if st.session_state.LifeManager_main_header:
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
                label="Select Sub-category:",
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

        # This button 1. disable previous fields 2.lock the drop down menus 3. disappear the main header
        st.button(
            "CLICK...",
            on_click=lambda: (
                st.session_state.update(
                    {
                        "lock_first": True,
                        "show_dropdown": False,
                        "LifeManager_main_header": False,
                    }
                )
            ),
        )

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
    global lm

    st.header("Adding Tasks to the Database.", divider="red")
    st.markdown(
        """
<p style='font-size:25px;color:lightgreen'> In this Section you will add task to the database as a <b>PARENT/CHILD</b>.
The difference between PARENT and CHILD task is as following:</p> 

<p style='font-size:25px;color:aqua'>A Parent task is a main and general task and a Child task is a sub-task.</p>

<p style='font-size:25px'>For example For <font color="red">Learning</font> can be the PARENT task of <font color="red">Udemy</font>.""",
        unsafe_allow_html=True,
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

    def Confirm_add_daily_task():
        global lm
        if lm.add_daily_task(task_name=_task, ref_to=parent_task):
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


def chart_it():
    global lm
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


def show_tasks():
    global lm
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


def DataGuardian():
    global lm

    #! Implemented a state variable to TRACK the readiness of backup
    if "backup_ready" not in st.session_state:
        st.session_state.backup_ready = False

    if st.button("Backup Now"):

        if lm.backup():
            st.session_state.backup_ready = True
            st.success("Generating backup was successful")
        else:
            st.session_state.backup_ready = False
            st.error("An error has occurred during producing a backup file.")

    # ~ When backup created, fetch the last backup from backup folder then upload it.
    if st.session_state.backup_ready:

        last_backup = sorted(os.listdir("backup"))[-1]
        backup_path = os.path.abspath(
            os.path.join(os.environ["BACKUP_PATH"], last_backup)
        )

        with open(backup_path, "rb") as fh:
            file_bytes = fh.read()

        st.download_button(
            label="Download Latest Backup",
            data=file_bytes,
            file_name=last_backup,
            mime="application/octet-stream",
        )

    st.markdown("<hr style='border: 1px solid aqua;'>", unsafe_allow_html=True)
    uploaded_file = st.file_uploader(
        "Upload your backup DATABASE file here or leave is empty for RESTORING THE Latest update."
    )

    if uploaded_file is not None:

        with open("temp_backup_file", "wb") as f:
            f.write(uploaded_file.getbuffer())

        if st.button("Restore Backup"):
            success = lm.restore_backup(backup_path="temp_backup_file")

            if success:
                st.success("Backup restored successfully!")
            else:
                st.error("Failed to restore backup.")
    else:
        if st.button("Restore Backup"):
            success = lm.restore_backup()

            if success:
                st.success("Backup restored successfully!")
            else:
                st.error("Failed to restore backup.")

    st.markdown("<hr style='border: 1px solid red;'>", unsafe_allow_html=True)
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


def insert_task():
    global lm

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


if __name__ == "__main__":
    main()
