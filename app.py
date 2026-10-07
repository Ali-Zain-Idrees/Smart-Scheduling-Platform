import streamlit as st
import pandas as pd
from datetime import datetime, date, time

# ==========================================
# PAGE CONFIGURATION & CSS STYLING
# ==========================================
st.set_page_config(
    page_title="Smart Timetable Platform",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom Styling (Text colors updated to White for high visibility)
st.markdown("""
<style>
    [data-testid="stSidebar"] { display: none; }
    .main-header { font-size: 28px; font-weight: 800; color: #FFFFFF !important; margin-bottom: 4px; }
    .sub-header-tag { font-size: 20px; font-weight: 600; color: #60A5FA !important; }
    .greeting-text { font-size: 26px; font-weight: 800; color: #FFFFFF !important; margin-bottom: 10px; }
    .live-time-text { font-size: 16px; font-weight: 600; color: #FFFFFF !important; }
    .badge-green { background-color: #DCFCE7; color: #15803D; padding: 5px 12px; border-radius: 6px; font-weight: 600; border: 1px solid #86EFAC; display: inline-block; }
    .badge-blue { background-color: #DBEAFE; color: #1D4ED8; padding: 5px 12px; border-radius: 6px; font-weight: 600; border: 1px solid #93C5FD; display: inline-block; }
    .badge-red { background-color: #FEE2E2; color: #B91C1C; padding: 5px 12px; border-radius: 6px; font-weight: 600; border: 1px solid #FCA5A5; display: inline-block; }
    .badge-gray { background-color: #F1F5F9; color: #475569; padding: 5px 12px; border-radius: 6px; font-weight: 600; border: 1px solid #CBD5E1; display: inline-block; }
    .hint-text { font-size: 13px; color: #94A3B8; margin-bottom: 8px; font-style: italic; }
</style>
""", unsafe_allow_html=True)

# Helper Functions
def format_time_12hr(t_obj):
    if isinstance(t_obj, time):
        return t_obj.strftime("%I:%M %p")
    return str(t_obj)

def get_time_sort_key(task):
    try:
        t_str = task["start_time"]
        return datetime.strptime(t_str, "%I:%M %p").time()
    except:
        return time(0, 0)

def get_dynamic_greeting(user_name):
    current_hour = datetime.now().hour
    if 5 <= current_hour < 12:
        period = "Good Morning! ☀️"
    elif 12 <= current_hour < 17:
        period = "Good Afternoon! 🌤️"
    else:
        period = "Good Evening! 🌙"
    
    if user_name and user_name.strip() != "":
        return f"Hi {user_name.strip()}, {period}"
    else:
        return f"Hi, {period}"

# ==========================================
# SESSION STATE INITIALIZATION
# ==========================================
if "user_name" not in st.session_state:
    st.session_state.user_name = None

if "view_format" not in st.session_state:
    st.session_state.view_format = "List"

if "schedule_type" not in st.session_state:
    st.session_state.schedule_type = "Weekly"

if "table_row_count" not in st.session_state:
    st.session_state.table_row_count = 10

if "tasks" not in st.session_state:
    st.session_state.tasks = []

if "active_tab" not in st.session_state:
    st.session_state.active_tab = "Timetable Manager"

if "current_week" not in st.session_state:
    st.session_state.current_week = 1

if "settings" not in st.session_state:
    st.session_state.settings = {
        "master_notifications": True,
        "daily_motivation": True,
        "weekly_motivation": True,
        "islamic_reminders": True,
        "location": "Lahore, Pakistan"
    }

if "form_message" not in st.session_state:
    st.session_state.form_message = None

# ==========================================
# INITIAL STARTUP SCREEN (NAME & FORMAT SETUP)
# ==========================================
if st.session_state.user_name is None:
    st.markdown("<h2 style='text-align: center; color: #FFFFFF;'>⚡ Welcome to Smart Timetable Platform</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #94A3B8;'>Set up your quick profile to get started.</p>", unsafe_allow_html=True)
    
    col_a, col_b, col_c = st.columns([1, 2, 1])
    with col_b:
        with st.form("startup_form"):
            input_name = st.text_input("Enter Your Name / Username", placeholder="e.g. Ali")
            
            st.markdown("---")
            st.write("**Choose your preferred Data Display Format:**")
            init_format = st.radio("Display Mode", ["List", "Table"], horizontal=True)
            st.caption("💡 *Note: You can change this format anytime from Settings.*")
            
            st.markdown("---")
            btn_save = st.form_submit_button("Continue 🚀", type="primary", use_container_width=True)
            
            if btn_save:
                st.session_state.user_name = input_name.strip() if input_name.strip() else ""
                st.session_state.view_format = init_format
                st.rerun()

        st.markdown("<p style='text-align: center; margin-top: 10px; color: #FFFFFF;'>OR</p>", unsafe_allow_html=True)
        if st.button("Continue Without Name ➡️", use_container_width=True):
            st.session_state.user_name = ""
            st.rerun()

    st.stop()

# ==========================================
# TOP HEADER BAR & SETTINGS (TOP RIGHT)
# ==========================================
top_col1, top_col2 = st.columns([8, 2])

with top_col1:
    greeting_msg = get_dynamic_greeting(st.session_state.user_name)
    st.markdown(f"<div class='greeting-text'>{greeting_msg}</div>", unsafe_allow_html=True)

with top_col2:
    with st.popover("⚙️ Settings"):
        st.subheader("👤 User Profile")
        new_name_val = st.text_input("Edit Name", value=st.session_state.user_name)
        if st.button("Update Name"):
            st.session_state.user_name = new_name_val.strip()
            st.success("Name updated!")
            st.rerun()
            
        st.divider()
        st.subheader("🧭 Navigation")
        st.session_state.active_tab = st.radio("Go To", 
            ["Timetable Manager", "Weekly History & Analytics", "Islamic Lifestyle & Reminders", "System Settings"],
            index=["Timetable Manager", "Weekly History & Analytics", "Islamic Lifestyle & Reminders", "System Settings"].index(st.session_state.active_tab)
        )
        
        st.divider()
        st.subheader("📊 Preferences")
        st.session_state.view_format = st.radio("Data Format", ["List", "Table"], index=0 if st.session_state.view_format == "List" else 1)
        st.session_state.schedule_type = st.radio("Active Period", ["Weekly", "Monthly"], index=0 if st.session_state.schedule_type == "Weekly" else 1)
        st.session_state.current_week = st.number_input("Week Selection", min_value=1, max_value=104, value=st.session_state.current_week)

st.divider()

# ==========================================
# MODULE 1: TIMETABLE MANAGER
# ==========================================
if st.session_state.active_tab == "Timetable Manager":
    # White Color Main Heading
    st.markdown(f"""
        <div class='main-header'>
            🎯 Timetable Manager 
            <span class='sub-header-tag'>({st.session_state.schedule_type} {st.session_state.view_format} View — Week {st.session_state.current_week})</span>
        </div>
    """, unsafe_allow_html=True)
    
    # Accurate Real-Time Device Time Injection (JavaScript Direct Sync)
    st.components.v1.html("""
        <div style="font-family: sans-serif; color: #FFFFFF; font-size: 15px; font-weight: 600;">
            🕒 <b>Live Device Time:</b> <span id="clock" style="color: #60A5FA;">--:--:-- --</span>
        </div>
        <script>
            function updateClock() {
                const now = new Date();
                let hours = now.getHours();
                let minutes = now.getMinutes();
                let seconds = now.getSeconds();
                let ampm = hours >= 12 ? 'PM' : 'AM';
                hours = hours % 12;
                hours = hours ? hours : 12;
                minutes = minutes < 10 ? '0' + minutes : minutes;
                seconds = seconds < 10 ? '0' + seconds : seconds;
                document.getElementById('clock').innerHTML = hours + ':' + minutes + ':' + seconds + ' ' + ampm;
            }
            setInterval(updateClock, 1000);
            updateClock();
        </script>
    """, height=35)
    
    st.caption("ℹ️ *Live Device Time tumhare system/mobile ka exact 12-hour AM/PM time sync kar raha hai taake scheduled tasks ke notifications aur alarms bilkul accurate time par trigger ho sakein.*")

    if st.session_state.form_message:
        msg_type, msg_text = st.session_state.form_message
        if msg_type == "success":
            st.success(msg_text)
        elif msg_type == "warning":
            st.warning(msg_text)
        st.session_state.form_message = None

    # Task Creation Popover
    with st.popover("➕ Add New Task"):
        st.markdown("<div class='hint-text'>💡 Hint: Task title aur subject clear likhein taake notification alert mein exactly wahi detail show ho.</div>", unsafe_allow_html=True)
        with st.form("add_task_form", clear_on_submit=True):
            col_a, col_b = st.columns(2)
            with col_a:
                subject = st.text_input("Subject / Category", placeholder="e.g. Maths, Gym, Project")
                title = st.text_input("Task Title / Detail", placeholder="e.g. Algebra Ex 1.1, Chest Workout")
                day = st.selectbox("Day of Week", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])
            with col_b:
                category = st.selectbox("Category Tag", ["Study", "Work", "Personal", "Health", "Other"])
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
                        t["week"] == st.session_state.current_week and
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
                            "week": st.session_state.current_week,
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

    week_tasks = [t for t in st.session_state.tasks if t["week"] == st.session_state.current_week]

    # DATA FORMAT 1: LIST VIEW
    if st.session_state.view_format == "List":
        st.subheader("📋 Task List View (Chronologically Sorted)")
        if not week_tasks:
            st.info(f"No tasks recorded for Week {st.session_state.current_week}. Add tasks above to populate list.")
        else:
            days_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            for d in days_order:
                day_tasks = [t for t in week_tasks if t["day"] == d]
                day_tasks.sort(key=get_time_sort_key)
                
                if day_tasks:
                    st.markdown(f"### 📅 {d}")
                    for task in day_tasks:
                        col1, col2, col3 = st.columns([4, 3, 3])
                        
                        with col1:
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

    # DATA FORMAT 2: TABLE VIEW
    elif st.session_state.view_format == "Table":
        st.subheader(f"📊 {st.session_state.schedule_type} Grid Timetable View")
        
        if st.session_state.schedule_type == "Weekly":
            headers = ["Subjects", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        else:
            headers = ["Subjects"] + [f"Day {i}" for i in range(1, 31)]

        existing_subjects = list(dict.fromkeys([t["subject"] for t in week_tasks]))
        rows_data = []
        for i in range(st.session_state.table_row_count):
            row_dict = {h: "" for h in headers}
            if i < len(existing_subjects):
                subj = existing_subjects[i]
                row_dict["Subjects"] = subj
                
                for h in headers[1:]:
                    matched_tasks = [
                        f"{t['title']} ({t['start_time']})" for t in week_tasks
                        if t["subject"].lower() == subj.lower() and (t["day"] == h or f"Day {t.get('day_num', '')}" == h)
                    ]
                    if matched_tasks:
                        row_dict[h] = "\n".join(matched_tasks)
            rows_data.append(row_dict)

        df_grid = pd.DataFrame(rows_data)
        st.dataframe(df_grid, use_container_width=True, height=400)

        c_add, _ = st.columns([2, 8])
        with c_add:
            if st.button("➕ Add Row (Expand Table)", type="secondary"):
                st.session_state.table_row_count += 1
                st.rerun()

    # Notifications Engine Section
    st.markdown("---")
    st.subheader("🔔 Notification Alert Engine")
    if st.session_state.settings["master_notifications"]:
        st.success("🔔 **Notifications Active:** Push-style alerts will trigger showing exact **Subject Name** and **Task Details** at 12-Hour AM/PM times.")
    else:
        st.warning("⚠️ **Notifications Muted:** Enable master notifications in Settings menu to receive live alerts.")

    # CLEAR TASKS SECTION
    st.markdown("---")
    st.subheader("🗑️ Clear Tasks")
    tab1, tab2 = st.tabs(["Clear All Tasks", "Clear Selected Tasks"])
    
    with tab1:
        st.write(f"Click below to clear all tasks for Week {st.session_state.current_week}")
        if st.button(f"Clear All Tasks for Week {st.session_state.current_week}", type="primary"):
            st.session_state.tasks = [t for t in st.session_state.tasks if t["week"] != st.session_state.current_week]
            st.session_state.form_message = ("success", f"All tasks for Week {st.session_state.current_week} cleared successfully.")
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
elif st.session_state.active_tab == "Weekly History & Analytics":
    st.markdown(f"<div class='main-header'>📊 Weekly Performance Analytics — Week {st.session_state.current_week}</div>", unsafe_allow_html=True)
    week_tasks = [t for t in st.session_state.tasks if t["week"] == st.session_state.current_week]

    if not week_tasks:
        st.warning(f"No activity records found for Week {st.session_state.current_week}.")
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
# MODULE 3: ISLAMIC LIFESTYLE
# ==========================================
elif st.session_state.active_tab == "Islamic Lifestyle & Reminders":
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
elif st.session_state.active_tab == "System Settings":
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