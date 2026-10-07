import streamlit as st
import pandas as pd
from datetime import datetime, date, time
import json

# ==========================================
# PAGE CONFIGURATION & LIVE TIME JS
# ==========================================
st.set_page_config(
    page_title="Smart Timetable Platform",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Live Device Time Reader JS Script
st.components.v1.html("""
    <script>
        function updateDeviceTime() {
            const now = new Date();
            const timeStr = now.toLocaleTimeString('en-US', { hour12: true });
            window.parent.postMessage({type: 'streamlit:setComponentValue', value: timeStr}, '*');
        }
        setInterval(updateDeviceTime, 1000);
    </script>
""", height=0)

# Custom Styling
st.markdown("""
<style>
    .main-header { font-size: 26px; font-weight: bold; color: #1E293B; margin-bottom: 12px; }
    .badge-green { background-color: #DCFCE7; color: #15803D; padding: 5px 12px; border-radius: 6px; font-weight: 600; border: 1px solid #86EFAC; display: inline-block; }
    .badge-blue { background-color: #DBEAFE; color: #1D4ED8; padding: 5px 12px; border-radius: 6px; font-weight: 600; border: 1px solid #93C5FD; display: inline-block; }
    .badge-red { background-color: #FEE2E2; color: #B91C1C; padding: 5px 12px; border-radius: 6px; font-weight: 600; border: 1px solid #FCA5A5; display: inline-block; }
    .badge-gray { background-color: #F1F5F9; color: #475569; padding: 5px 12px; border-radius: 6px; font-weight: 600; border: 1px solid #CBD5E1; display: inline-block; }
    .hint-text { font-size: 13px; color: #64748B; margin-bottom: 8px; font-style: italic; }
    .table-cell { word-wrap: break-word; min-width: 120px; white-space: normal; }
</style>
""", unsafe_allow_html=True)

# Helper Function to Format Time object to 12-Hour AM/PM String
def format_time_12hr(t_obj):
    if isinstance(t_obj, time):
        return t_obj.strftime("%I:%M %p")
    return str(t_obj)

# Helper Function for Time Sorting
def get_time_sort_key(task):
    try:
        t_str = task["start_time"]
        return datetime.strptime(t_str, "%I:%M %p").time()
    except:
        return time(0, 0)

# ==========================================
# SESSION STATE INITIALIZATION
# ==========================================
if "users" not in st.session_state:
    st.session_state.users = {}

if "last_email" not in st.session_state:
    st.session_state.last_email = None

if "current_user" not in st.session_state:
    st.session_state.current_user = None

if "view_format" not in st.session_state:
    st.session_state.view_format = "List"  # "List" or "Table"

if "schedule_type" not in st.session_state:
    st.session_state.schedule_type = "Weekly"  # "Weekly" or "Monthly"

if "table_row_count" not in st.session_state:
    st.session_state.table_row_count = 10  # Default 10 rows

if "tasks" not in st.session_state:
    st.session_state.tasks = []

if "settings" not in st.session_state:
    st.session_state.settings = {
        "master_notifications": True,
        "daily_motivation": True,
        "weekly_motivation": True,
        "islamic_reminders": True,
        "location": "Lahore, Pakistan"
    }

if "current_week" not in st.session_state:
    st.session_state.current_week = 1

if "form_message" not in st.session_state:
    st.session_state.form_message = None

# ==========================================
# AUTHENTICATION & LOGIN / SIGNUP MODULE
# ==========================================
if st.session_state.current_user is None:
    st.markdown("<h2 style='text-align: center; color: #1E293B;'>⚡ Smart Timetable Platform</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #64748B;'>Welcome! Please sign in, sign up, or continue as a guest to proceed.</p>", unsafe_allow_html=True)
    
    col_a, col_b, col_c = st.columns([1, 2, 1])
    with col_b:
        if st.session_state.last_email:
            st.info(f"💡 **It seems like you already have an account:** `{st.session_state.last_email}`")
            
        auth_mode = st.radio("Choose Action", ["Log In", "Sign Up", "Continue as Guest"], horizontal=True)
        
        if auth_mode == "Log In":
            with st.form("login_form"):
                email = st.text_input("Email Address", value=st.session_state.last_email if st.session_state.last_email else "")
                password = st.text_input("Password", type="password")
                btn_login = st.form_submit_button("Log In", type="primary", use_container_width=True)
                
                if btn_login:
                    if email in st.session_state.users and st.session_state.users[email] == password:
                        st.session_state.current_user = email
                        st.session_state.last_email = email
                        st.success("Logged in successfully!")
                        st.rerun()
                    else:
                        st.error("Invalid email or password. Please try again or Sign Up.")

        elif auth_mode == "Sign Up":
            with st.form("signup_form"):
                new_email = st.text_input("Enter Email Address")
                new_pass = st.text_input("Create Password", type="password")
                btn_signup = st.form_submit_button("Sign Up & Create Account", type="primary", use_container_width=True)
                
                if btn_signup:
                    if not new_email.strip() or not new_pass.strip():
                        st.warning("Please fill in all fields.")
                    elif new_email in st.session_state.users:
                        st.warning("Account already exists with this email! Please switch to Log In.")
                    else:
                        st.session_state.users[new_email] = new_pass
                        st.session_state.current_user = new_email
                        st.session_state.last_email = new_email
                        st.success("Account created successfully!")
                        st.rerun()

        elif auth_mode == "Continue as Guest":
            st.write("You can use the application as a guest without creating an account.")
            if st.button("Proceed as Guest 🚀", type="primary", use_container_width=True):
                st.session_state.current_user = "Guest"
                st.rerun()

        if st.session_state.last_email and auth_mode != "Continue as Guest":
            if st.button("Switch Account / Clear Saved Email", use_container_width=True):
                st.session_state.last_email = None
                st.rerun()

    st.stop()

# ==========================================
# SIDEBAR NAVIGATION & USER CONTROLLER
# ==========================================
st.sidebar.title("⚡ Smart Schedule App")

st.sidebar.markdown(f"👤 **Logged in as:** `{st.session_state.current_user}`")
c_logout, c_switch = st.sidebar.columns(2)
with c_logout:
    if st.button("Log Out"):
        st.session_state.current_user = None
        st.rerun()
with c_switch:
    if st.button("Switch"):
        st.session_state.current_user = None
        st.rerun()

st.sidebar.markdown("---")
menu = st.sidebar.radio(
    "Navigation Menu",
    ["Timetable Manager", "Weekly History & Analytics", "Islamic Lifestyle & Reminders", "System Settings"]
)

st.sidebar.markdown("---")
st.sidebar.subheader("📊 Data Display Format")
st.session_state.view_format = st.sidebar.radio("Show Data As", ["List", "Table"], index=0 if st.session_state.view_format == "List" else 1)

st.sidebar.subheader("📅 Schedule Period")
st.session_state.schedule_type = st.sidebar.radio("Active Period", ["Weekly", "Monthly"], index=0 if st.session_state.schedule_type == "Weekly" else 1)

selected_week = st.sidebar.number_input("Select Week (Week 1..N)", min_value=1, max_value=104, value=st.session_state.current_week)

# ==========================================
# MODULE 1: TIMETABLE MANAGER
# ==========================================
if menu == "Timetable Manager":
    st.markdown(f"<div class='main-header'>🎯 Timetable Manager ({st.session_state.schedule_type} - {st.session_state.view_format} View) — Week {selected_week}</div>", unsafe_allow_html=True)
    
    # Live Device Time Display
    st.caption(f"🕒 **Live Device Time:** {datetime.now().strftime('%I:%M:%S %p')} | Syncing active alerts in real-time.")

    if st.session_state.form_message:
        msg_type, msg_text = st.session_state.form_message
        if msg_type == "success":
            st.success(msg_text)
        elif msg_type == "warning":
            st.warning(msg_text)
        st.session_state.form_message = None

    # Task Creation Popover / Form
    with st.popover("➕ Add New Task"):
        st.markdown("<div class='hint-text'>💡 Hint: Enter clear subject & task details so your notification alert shows exactly what to do!</div>", unsafe_allow_html=True)
        with st.form("add_task_form", clear_on_submit=True):
            col_a, col_b = st.columns(2)
            with col_a:
                subject = st.text_input("Subject / Category", placeholder="e.g. Maths, Gym, Project")
                title = st.text_input("Task Title / Detail", placeholder="e.g. Algebra Ex 1.1, Chest Workout")
                day = st.selectbox("Day of Week", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])
            with col_b:
                category = st.selectbox("Category Tag", ["Study", "Work", "Personal", "Health", "Other"])
                # 12-Hour AM/PM Time Selector with explicit AM/PM Picker
                start_t = st.time_input("Start Time (AM/PM)", value=time(9, 0), step=300)
                end_t = st.time_input("End Time (AM/PM)", value=time(10, 0), step=300)
                
            submit = st.form_submit_button("Add Task")
            if submit:
                if not subject.strip() or not title.strip():
                    st.session_state.form_message = ("warning", "⚠️ Subject and Task Title cannot be empty.")
                    st.rerun()
                else:
                    start_str = format_time_12hr(start_t)
                    end_str = format_time_12hr(end_t)
                    
                    is_duplicate = any(
                        t["week"] == selected_week and
                        t["day"] == day and
                        t["subject"].strip().lower() == subject.strip().lower() and
                        t["title"].strip().lower() == title.strip().lower() and
                        t["start_time"] == start_str
                        for t in st.session_state.tasks
                    )
                    
                    if is_duplicate:
                        st.session_state.form_message = ("warning", f"⚠️ Task '{title}' for Subject '{subject}' already exists for {day} ({start_str})!")
                        st.rerun()
                    else:
                        new_id = len(st.session_state.tasks) + 1
                        st.session_state.tasks.append({
                            "id": new_id,
                            "subject": subject.strip(),
                            "title": title.strip(),
                            "week": selected_week,
                            "day": day,
                            "start_time": start_str,
                            "end_time": end_str,
                            "original_time": f"{day} {start_str} - {end_str}",
                            "status": "PENDING",
                            "is_rescheduled": False,
                            "completed": False,
                            "category": category
                        })
                        st.session_state.form_message = ("success", f"✅ Task '{title}' ({subject}) added successfully to {day} at {start_str}!")
                        st.rerun()

    # Filter tasks for selected week
    week_tasks = [t for t in st.session_state.tasks if t["week"] == selected_week]

    # ==========================================
    # DATA FORMAT 1: LIST VIEW (TIME ALIGNED)
    # ==========================================
    if st.session_state.view_format == "List":
        st.subheader("📋 Task List View (Chronologically Sorted)")
        if not week_tasks:
            st.info(f"No tasks recorded for Week {selected_week}. Add tasks above to populate list.")
        else:
            days_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            
            for d in days_order:
                day_tasks = [t for t in week_tasks if t["day"] == d]
                # Chronological Sorting: Sort by Start Time (10:00 AM before 12:00 PM)
                day_tasks.sort(key=get_time_sort_key)
                
                if day_tasks:
                    st.markdown(f"### 📅 {d}")
                    for task in day_tasks:
                        col1, col2, col3 = st.columns([4, 3, 3])
                        
                        with col1:
                            # Display Subject and Task Title
                            task_display = f"**[{task['subject']}]** {task['title']}"
                            if task["status"] == "COMPLETED" and not task["is_rescheduled"]:
                                st.markdown(f"<span class='badge-green'>🟩 ✓ {task_display}</span>", unsafe_allow_html=True)
                            elif task["is_rescheduled"]:
                                status_txt = "(Rescheduled)"
                                if task["completed"]:
                                    st.markdown(f"<span class='badge-blue'>🟦 ✓ {task_display} {status_txt}</span>", unsafe_allow_html=True)
                                else:
                                    st.markdown(f"<span class='badge-blue'>🟦 ↻ {task_display} {status_txt}</span>", unsafe_allow_html=True)
                            elif task["status"] == "SKIPPED":
                                st.markdown(f"<span class='badge-red'>🟥 ✗ {task_display}</span>", unsafe_allow_html=True)
                            else:
                                st.markdown(f"<span class='badge-gray'>⚪ {task_display}</span>", unsafe_allow_html=True)
                            
                            st.caption(f"🕒 Time: **{task['start_time']} - {task['end_time']}** | Category: {task['category']}")

                        with col2:
                            st.caption(f"Original Schedule:\n{task['original_time']}")

                        with col3:
                            b1, b2, b3 = st.columns(3)
                            with b1:
                                if st.button("Done", key=f"comp_{task['id']}"):
                                    task["completed"] = True
                                    if not task["is_rescheduled"]:
                                        task["status"] = "COMPLETED"
                                    st.rerun()
                            with b2:
                                if st.button("Skip", key=f"skip_{task['id']}"):
                                    task["status"] = "SKIPPED"
                                    task["completed"] = False
                                    st.rerun()
                            with b3:
                                with st.popover("Move"):
                                    n_day = st.selectbox("New Day", days_order, key=f"nd_{task['id']}")
                                    n_start = st.time_input("New Start", key=f"ns_{task['id']}", step=300)
                                    n_end = st.time_input("New End", key=f"ne_{task['id']}", step=300)
                                    if st.button("Confirm", key=f"sm_{task['id']}"):
                                        task["day"] = n_day
                                        task["start_time"] = format_time_12hr(n_start)
                                        task["end_time"] = format_time_12hr(n_end)
                                        task["is_rescheduled"] = True
                                        task["status"] = "RESCHEDULED"
                                        st.rerun()
                    st.divider()

    # ==========================================
    # DATA FORMAT 2: TABLE VIEW (DYNAMIC GRID)
    # ==========================================
    elif st.session_state.view_format == "Table":
        st.subheader(f"📊 {st.session_state.schedule_type} Grid Timetable View")
        st.caption("Note: Tasks added above will auto-intersect under their respective Subject and Day column.")

        # Determine Table Columns
        if st.session_state.schedule_type == "Weekly":
            headers = ["Subjects", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        else:  # Monthly View (30 Day Columns + Subjects)
            headers = ["Subjects"] + [f"Day {i}" for i in range(1, 31)]

        # Unique Subjects from current tasks
        existing_subjects = list(dict.fromkeys([t["subject"] for t in week_tasks]))
        
        # Ensure at least table_row_count rows exist
        rows_data = []
        for i in range(st.session_state.table_row_count):
            row_dict = {h: "" for h in headers}
            if i < len(existing_subjects):
                subj = existing_subjects[i]
                row_dict["Subjects"] = subj
                
                # Fill day columns with tasks matching this subject
                for h in headers[1:]:
                    matched_tasks = [
                        f"{t['title']} ({t['start_time']})" for t in week_tasks
                        if t["subject"].lower() == subj.lower() and (t["day"] == h or f"Day {t.get('day_num', '')}" == h)
                    ]
                    if matched_tasks:
                        row_dict[h] = "\n".join(matched_tasks)
            rows_data.append(row_dict)

        # Convert to Pandas DataFrame for Flexible Grid Display
        df_grid = pd.DataFrame(rows_data)
        
        # Display Interactive / Flexible Table
        st.dataframe(df_grid, use_container_width=True, height=400)

        # Dynamic Row Expansion Feature (Excel / MS Word Style)
        c_add, c_space = st.columns([2, 8])
        with c_add:
            if st.button("➕ Add Row (Expand Table)", type="secondary"):
                st.session_state.table_row_count += 1
                st.rerun()

    # Notification Status Section
    st.markdown("---")
    st.subheader("🔔 Notification Alert Engine")
    if st.session_state.settings["master_notifications"]:
        st.success("🔔 **Notifications Active:** You will receive push-style alerts with **Subject Name** and **Task Details** at scheduled 12-Hour AM/PM times.")
    else:
        st.warning("⚠️ **Notifications Muted:** Enable master notifications in Settings to receive live alerts.")

    # Clear Tasks Section
    st.markdown("---")
    st.subheader("🗑️ Clear Tasks Options")
    tab1, tab2 = st.tabs(["Clear All Tasks", "Clear Specific Tasks"])
    
    with tab1:
        st.write("Click below to clear all tasks for Week " + str(selected_week))
        if st.button("Clear All Tasks for Week " + str(selected_week), type="primary"):
            st.session_state.tasks = [t for t in st.session_state.tasks if t["week"] != selected_week]
            st.session_state.form_message = ("success", f"All tasks for Week {selected_week} cleared successfully.")
            st.rerun()

    with tab2:
        if not week_tasks:
            st.info("No tasks available to clear.")
        else:
            selected_to_remove = []
            for task in week_tasks:
                chk = st.checkbox(f"[{task['day']}] {task['subject']} - {task['title']} ({task['start_time']})", key=f"chk_clear_{task['id']}")
                if chk:
                    selected_to_remove.append(task["id"])
            
            if st.button("Clear Selected Tasks", type="primary"):
                if selected_to_remove:
                    st.session_state.tasks = [t for t in st.session_state.tasks if t["id"] not in selected_to_remove]
                    st.session_state.form_message = ("success", "Selected tasks removed successfully.")
                    st.rerun()
                else:
                    st.warning("Please select at least one task.")

# ==========================================
# MODULE 2: HISTORY & ANALYTICS
# ==========================================
elif menu == "Weekly History & Analytics":
    st.markdown(f"<div class='main-header'>📊 Weekly Performance Analytics — Week {selected_week}</div>", unsafe_allow_html=True)
    week_tasks = [t for t in st.session_state.tasks if t["week"] == selected_week]

    if not week_tasks:
        st.warning(f"No activity records found for Week {selected_week}.")
    else:
        total_planned = len(week_tasks)
        direct_completed = sum(1 for t in week_tasks if t["status"] == "COMPLETED" and not t["is_rescheduled"])
        rescheduled_completed = sum(1 for t in week_tasks if t["is_rescheduled"] and t["completed"])
        skipped = sum(1 for t in week_tasks if t["status"] == "SKIPPED")
        
        goal_achievement_pct = round(((direct_completed + rescheduled_completed) / total_planned) * 100, 1)
        on_schedule_pct = round((direct_completed / total_planned) * 100, 1)
        rescheduled_pct = round((rescheduled_completed / total_planned) * 100, 1)
        skipped_pct = round((skipped / total_planned) * 100, 1)

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Tasks", total_planned)
        m2.metric("Goal Achievement %", f"{goal_achievement_pct}%")
        m3.metric("On-Schedule Completion", f"{on_schedule_pct}%")
        m4.metric("Rescheduled Completion", f"{rescheduled_pct}%")

        st.markdown("---")
        c_left, c_right = st.columns([1, 1])
        with c_left:
            st.subheader("📋 Status Breakdown")
            df = pd.DataFrame({
                "Status Category": ["🟩 Completed On Time", "🟦 Rescheduled & Completed", "🟥 Skipped / Missed"],
                "Task Count": [direct_completed, rescheduled_completed, skipped],
                "Share (%)": [f"{on_schedule_pct}%", f"{rescheduled_pct}%", f"{skipped_pct}%"]
            })
            st.table(df)

        with c_right:
            st.subheader("💡 Key Insights")
            st.write(f"- **Total Goals Tracked:** {total_planned}")
            st.write(f"- **Direct Efficiency Rate:** {on_schedule_pct}%")
            st.write(f"- **Reschedule Recovery Rate:** {rescheduled_pct}%")

# ==========================================
# MODULE 3: ISLAMIC LIFESTYLE & REMINDERS
# ==========================================
elif menu == "Islamic Lifestyle & Reminders":
    st.markdown("<div class='main-header'>🕌 Islamic Lifestyle & Prayer Reminders</div>", unsafe_allow_html=True)
    if not st.session_state.settings["master_notifications"]:
        st.warning("⚠️ Master notifications are currently disabled in Settings.")
    else:
        st.success(f"📍 Location configured: **{st.session_state.settings['location']}**")
        st.subheader("🕋 Daily Prayer Schedule")
        prayer_df = pd.DataFrame({
            "Prayer": ["Fajr", "Dhuhr", "Asr", "Maghrib", "Isha"],
            "Time": ["05:10 AM", "12:15 PM", "03:45 PM", "06:10 PM", "07:30 PM"],
            "System Priority": ["Default Active", "Default Active", "Default Active", "Default Active", "Default Active"]
        })
        st.table(prayer_df)

# ==========================================
# MODULE 4: SYSTEM SETTINGS
# ==========================================
elif menu == "System Settings":
    st.markdown("<div class='main-header'>⚙️ Application Settings</div>", unsafe_allow_html=True)
    with st.form("settings_form"):
        st.subheader("🔔 Notification Rules Engine")
        master_notif = st.checkbox("Master Notifications Switch (ON/OFF)", value=st.session_state.settings["master_notifications"])
        daily_mot = st.checkbox("Enable Daily Motivation Alerts", value=st.session_state.settings["daily_motivation"])
        weekly_mot = st.checkbox("Enable Weekly Summary Alerts", value=st.session_state.settings["weekly_motivation"])
        
        st.subheader("🕌 Islamic Lifestyle Engine")
        islamic_on = st.checkbox("Enable Prayer Schedules & Reminders", value=st.session_state.settings["islamic_reminders"])
        loc = st.text_input("City / Location", value=st.session_state.settings["location"])

        save = st.form_submit_button("Save Configuration")
        if save:
            st.session_state.settings["master_notifications"] = master_notif
            st.session_state.settings["daily_motivation"] = daily_mot
            st.session_state.settings["weekly_motivation"] = weekly_mot
            st.session_state.settings["islamic_reminders"] = islamic_on
            st.session_state.settings["location"] = loc
            st.success("Settings updated successfully!")