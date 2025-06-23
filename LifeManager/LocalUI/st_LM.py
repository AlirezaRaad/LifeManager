import os
from uuid import uuid4
from zipfile import ZipFile

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from LifeManager.LM import LifeManager
from LifeManager.TM import CTimer


def main():
    # Initiate the Life Manager instance and load the env variables.
    if "LifeManager" not in st.session_state:
        load_dotenv()
        st.session_state.LifeManager = LifeManager()

    if "Timer" not in st.session_state:
        st.session_state.Timer = CTimer()

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
        "Show Tasks": None,
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

    # ~ This only when the user clicked the above button will be True and then it redirects.
    # ~ Later when we will back at the main, this will be False again..

    if st.session_state.show_dropdown is False:

        if st.session_state["user_desired_task"][1] == "Add Daily Task":
            add_daily_task()

        if st.session_state["user_desired_task"][1] == "Show Tasks":
            show_tasks()

        if st.session_state["user_desired_task"][1] == "Insert A task to DB":
            insert_task()

        if st.session_state["user_desired_task"][1] == "DataGuardian":
            DataGuardian()

        if st.session_state["user_desired_task"][1] == "Charting":
            chart_it()


def add_daily_task():
    lm: LifeManager = st.session_state.LifeManager

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

    #! Present the user a text input to put something in it; Simultiansly Make the parent_task variable.
    _task = st.text_input(label=f"Please Enter the **Task Name**:")
    parent_task = None

    # $ This Check box indicate that if user want to the `_task` variable be a Parent or a Child.
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
        """This function tries to add the task to the database then we make a flag for after clicking the bellow button."""
        lm: LifeManager = st.session_state.LifeManager
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
    lm: LifeManager = st.session_state.LifeManager

    st.header("Charting Section", divider="rainbow")

    all_weeks = [i for i in lm.show_all_tables() if i.startswith("y")]

    selected_week = st.selectbox(
        label="Please Choose the week that you desire to see your stats: ",
        options=all_weeks,
        index=(len(all_weeks) - 1),
    )
    days_of_week = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]

    selected_default_day = st.selectbox(
        label="Please Enter the day which week starts in you'r region",
        options=days_of_week,
        index=5,
    )

    def show_image():
        """A function that when it activates with a button, it shows the figures."""

        pics = [
            ("line.png", "Line Chart Indicating Your recorded time over weeks"),
            ("pie.png", "Detailed Data on What Hour You Spent On What"),
            (
                "bar.png",
                "Detailed Data on which day of the week you were how many hour productive",
            ),
        ]

        pics_path = [
            (os.path.join(os.environ["FIGURES_PATH"], i[0]), i[1]) for i in pics
        ]

        for image, caption in pics_path:
            st.image(image, caption=caption)

    if st.button("Show the Week's Status", type="primary"):
        # ()  First I create the PNG's using lm.chart_it then send images.
        if lm.chart_it(week=selected_week, start_day=selected_default_day):
            st.success("The Figures Are Ready")
            show_image()
        else:
            st.error("A problem occurred while making the figures")

    st.markdown("<br><br>", unsafe_allow_html=True)
    st.header(body="Download Figures", divider="rainbow")

    desired_chart = st.selectbox(
        label="Please Choose the Chart(s) to Download: ",
        options=["Line Chart", "Pie Chart", "Bar Chart", "All Charts"],
        index=3,
    )

    def binary_pics(chart_type):
        """This Function uniquely designed to send back the binary of 3 files"""

        chart_types = {"line": "line", "pie": "pie", "bar": "bar"}

        filename = f"{chart_types[chart_type]}.png"
        path = os.path.join(os.environ["FIGURES_PATH"], filename)

        with open(path, "rb") as fh:
            return fh.read()

    # % This list will contain 3 boolean values
    flag = [
        os.path.exists(j)
        for j in {
            os.path.join(os.environ["FIGURES_PATH"], i)
            for i in ["line.png", "pie.png", "bar.png"]
        }
    ]

    if flag[0] and flag[1] and flag[2]:
        match desired_chart:
            case _ if desired_chart.startswith("P"):
                st.download_button(
                    label="Line", data=binary_pics("line"), file_name="line.png"
                )

            case _ if desired_chart.startswith("L"):
                st.download_button(
                    label="Pie", data=binary_pics("pie"), file_name="pie.png"
                )

            case _ if desired_chart.startswith("B"):
                st.download_button(
                    label="Bar", data=binary_pics("bar"), file_name="bar.png"
                )

            case _:
                # % For this part, I will first, Zip the 3 pic's then send them.
                zip_path = os.path.join(os.environ["FIGURES_PATH"], "LM_figures.zip")
                with ZipFile(zip_path, "w") as zipfh:
                    paths = {
                        os.path.join(os.environ["FIGURES_PATH"], i)
                        for i in ["line.png", "pie.png", "bar.png"]
                    }
                    for i in paths:
                        zipfh.write(i, arcname=i)

                with open(zip_path, "rb") as fh:
                    zip_content = fh.read()

                st.download_button(
                    label="All", data=zip_content, file_name="all_files.zip"
                )
    st.divider()
    st.info("Click the button bellow to go to the MainPage:")

    def back_to_main():
        st.session_state.update(
            {
                "lock_first": False,
                "show_dropdown": True,
                "LifeManager_main_header": True,
            }
        ),

        #! using list comprehension to remove files and since no variable will point to this list , GC will remove it.

        [
            os.remove(i) if os.path.exists(i) else None
            for i in {
                os.path.join(os.environ["FIGURES_PATH"], i)
                for i in ["line.png", "pie.png", "bar.png", "LM_figures.zip"]
            }
        ]

    st.button("CLICK...", key=str(uuid4()), on_click=back_to_main)


def show_tasks():
    """This Function Simple make 3 DataFrames and shows it."""
    lm: LifeManager = st.session_state.LifeManager

    st.header("All Tasks", divider="green")
    st.markdown(
        """<p style='font-size:24px;color:aqua'>All the tasks that you added to the DATABASE. </p>""",
        unsafe_allow_html=True,
    )

    parent = pd.DataFrame(lm.get_all_parent_tasks(), columns=["Parent Tasks"])
    child = pd.DataFrame(lm.fetch_all_non_parent_tasks(), columns=["Child Tasks"])

    st.header("Parent Tasks", divider="violet")
    st.dataframe(parent)

    st.header("Child Tasks", divider="rainbow")

    st.dataframe(child)

    st.header("Child of Certain Tasks", divider="orange")
    _task = st.selectbox(label="Select the Parent Task:", options=parent)

    st.dataframe(
        pd.DataFrame(
            lm.fetch_child_tasks_of(_task), columns=[f"Child Tasks of {_task}"]
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


def DataGuardian():
    lm: LifeManager = st.session_state.LifeManager

    #! Implemented a state variable to TRACK the readiness of backup
    if "backup_ready" not in st.session_state:
        st.session_state.backup_ready = False

    st.header("Backup Now", divider="rainbow")
    if st.button("Backup"):

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

    st.header("Upload your backup DATABASE", divider="red")
    # $ Allows user to upload backups.
    uploaded_file = st.file_uploader(
        " ", type=".backup", help="Just accepts `.backup` files"
    )

    if uploaded_file is not None:
        with open("temp_backup_file", "wb") as fh:
            fh.write(uploaded_file.getbuffer())

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
    """This function corresponds exactly with lm.insert_into_weekly_table"""

    lm: LifeManager = st.session_state.LifeManager
    tm: CTimer = st.session_state.Timer

    st.header("Inserting Task Section", divider="rainbow")

    if "insert_duration" not in st.session_state:
        st.session_state.insert_duration = None

    if st.session_state.insert_duration is None:
        st.error(
            "You need a **Time** to Continue, Enter your time or you Start the Timer?"
        )

    if st.checkbox(label="Custom Duration"):
        custom_time = st.number_input(label="Enter You custom Time :")
        custom_timeframe = st.selectbox(
            label="Choose You'r TimeFrame", options=["Seconds", "Minutes", "Hours"]
        )

    if st.checkbox("Timer Section"):
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            if st.button("Start"):
                tm.start()

        with col2:
            try:
                if st.button("Pause"):
                    tm.pause()
            except:
                st.error("First initiate the start using **start** method")

        with col3:
            try:
                if st.button("Resume"):
                    tm.resume()
            except:
                st.error("Timer has not been paused")
        with col4:

            if st.button("End"):
                kh = tm.time_it()
    try:
        print(kh)
        print(custom_time)
    except:
        pass
    st.markdown("<hr style='border: 1px solid yellow;'>", unsafe_allow_html=True)
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
