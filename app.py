import streamlit as st
import pandas as pd
from datetime import datetime, date, time
import json

# ==========================================
# PAGE CONFIGURATION & CUSTOM STYLING
# ==========================================
st.set_page_config(
    page_title="Smart Timetable & Lifestyle Platform",
    page_icon="📅",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Tri-Color Status Badges & Modern Card UI
st.markdown("""
<style>
    .main-header { font-size: 26px; font-weight: bold; color: #1E293B; margin-bottom: 12px; }
    .badge-green { background-color: #DCFCE7; color: #15803D; padding: 5px 12px; border-radius: 6px; font-weight: 600; border: 1px solid #86EFAC; display: inline-block; }
    .badge-blue { background-color: #DBEAFE; color: #1D4ED8; padding: 5px 12px; border-radius: 6px; font-weight: 600; border: 1px solid #93C5FD; display: inline-block; }
    .badge-red { background-color: #FEE2E2; color: #B91C1C; padding: 5px 12px; border-radius: 6px; font-weight: 600; border: 1px solid #FCA5A5; display: inline-block; }
    .badge-gray { background-color: #F1F5F9; color: #475569; padding: 5px 12px; border-radius: 6px; font-weight: 600; border: 1px solid #CBD5E1; display: inline-block; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# SESSION STATE INITIALIZATION (PERSISTENCE)
# ==========================================
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

if "selected_clear_tasks" not in st.session_state:
    st.session_state.selected_clear_tasks = []

# ==========================================
# SIDEBAR NAVIGATION & WEEK CONTROLLER
# ==========================================
st.sidebar.title("📌 Smart Schedule App")
menu = st.sidebar.radio(
    "Navigation Menu",
    ["Timetable & Daily Routine", "Weekly History & Analytics", "Islamic Lifestyle & Reminders", "System Settings"]
)

st.sidebar.markdown("---")
st.sidebar.subheader("📅 Week History Selector")
selected_week = st.sidebar.number_input("Select Week (Week 1..N)", min_value=1, max_value=104, value=st.session_state.current_week)

# ==========================================
# MODULE 1: TIMETABLE & DAILY ROUTINE
# ==========================================
if menu == "Timetable & Daily Routine":
    st.markdown(f"<div class='main-header'>🗓️ Weekly Timetable Manager — Week {selected_week}</div>", unsafe_allow_html=True)
    
    # Task Creation Popover / Form
    with st.popover("➕ Add New Planned Task"):
        with st.form("add_task_form", clear_on_submit=True):
            c1, c2, c3 = st.columns(3)
            with c1:
                title = st.text_input("Task Title", placeholder="")
                category = st.selectbox("Category", ["Study", "Work", "Personal", "Health", "Other"])
            with c2:
                day = st.selectbox("Day of Week", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])
                start_t = st.time_input("Start Time", value=time(9, 0))
            with c3:
                end_t = st.time_input("End Time", value=time(10, 0))
                
            submit = st.form_submit_button("Add Task")
            if submit and title:
                new_id = len(st.session_state.tasks) + 1
                st.session_state.tasks.append({
                    "id": new_id,
                    "title": title,
                    "week": selected_week,
                    "day": day,
                    "start_time": str(start_t)[:5],
                    "end_time": str(end_t)[:5],
                    "original_time": f"{day} {str(start_t)[:5]} - {str(end_t)[:5]}",
                    "status": "PENDING",
                    "is_rescheduled": False,
                    "completed": False,
                    "category": category
                })
                st.rerun()

    # Task List Display with Tri-Color Logic
    week_tasks = [t for t in st.session_state.tasks if t["week"] == selected_week]

    if not week_tasks:
        st.info(f"No tasks recorded for Week {selected_week}. Add tasks above to start building your routine.")
    else:
        days_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        
        for d in days_order:
            day_tasks = [t for t in week_tasks if t["day"] == d]
            if day_tasks:
                st.subheader(f"📅 {d}")
                for task in day_tasks:
                    col1, col2, col3 = st.columns([4, 3, 3])
                    
                    with col1:
                        # TRI-COLOR STATUS LOGIC
                        if task["status"] == "COMPLETED" and not task["is_rescheduled"]:
                            st.markdown(f"<span class='badge-green'>🟩 ✓ {task['title']}</span>", unsafe_allow_html=True)
                        elif task["is_rescheduled"]:
                            if task["completed"]:
                                st.markdown(f"<span class='badge-blue'>🟦 ✓ {task['title']} (Rescheduled)</span>", unsafe_allow_html=True)
                            else:
                                st.markdown(f"<span class='badge-blue'>🟦 ↻ {task['title']} (Rescheduled)</span>", unsafe_allow_html=True)
                        elif task["status"] == "SKIPPED":
                            st.markdown(f"<span class='badge-red'>🟥 ✗ {task['title']}</span>", unsafe_allow_html=True)
                        else:
                            st.markdown(f"<span class='badge-gray'>⚪ {task['title']}</span>", unsafe_allow_html=True)
                        
                        st.caption(f"Time: {task['start_time']} - {task['end_time']} | Category: {task['category']}")

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
                                n_start = st.time_input("New Start", key=f"ns_{task['id']}")
                                n_end = st.time_input("New End", key=f"ne_{task['id']}")
                                if st.button("Confirm", key=f"sm_{task['id']}"):
                                    task["day"] = n_day
                                    task["start_time"] = str(n_start)[:5]
                                    task["end_time"] = str(n_end)[:5]
                                    task["is_rescheduled"] = True
                                    task["status"] = "RESCHEDULED"
                                    st.rerun()
                st.divider()

    # Notification Engine Status Section
    st.markdown("---")
    st.subheader("🔔 Notification Engine Status")
    
    if st.session_state.settings["master_notifications"]:
        st.success("🔔 **Notification Enabled:** You will be notified when your task time arrives.")
    else:
        st.warning("⚠️ **Notification Disabled:** Better performance ke liye notification on karein ta ke aap apne task complete kar sakein.")

    # Clear Tasks Options Section
    st.markdown("---")
    st.subheader("🗑️ Clear Tasks Options")
    
    tab1, tab2 = st.tabs(["Clear All Tasks", "Clear Specific Tasks"])
    
    with tab1:
        st.write("Click below to clear all tasks for the current week schedule.")
        if st.button("Clear All Tasks for Week " + str(selected_week), type="primary"):
            st.session_state.tasks = [t for t in st.session_state.tasks if t["week"] != selected_week]
            st.success(f"All tasks for Week {selected_week} have been cleared.")
            st.rerun()

    with tab2:
        if not week_tasks:
            st.info("No tasks available to clear.")
        else:
            st.write("Select specific tasks to remove:")
            selected_to_remove = []
            
            for task in week_tasks:
                chk = st.checkbox(f"[{task['day']}] {task['title']} ({task['start_time']} - {task['end_time']})", key=f"chk_clear_{task['id']}")
                if chk:
                    selected_to_remove.append(task["id"])
            
            if st.button("Clear Selected Tasks", type="primary"):
                if selected_to_remove:
                    st.session_state.tasks = [t for t in st.session_state.tasks if t["id"] not in selected_to_remove]
                    st.success("Selected tasks have been removed.")
                    st.rerun()
                else:
                    st.warning("Please select at least one task to clear.")

# ==========================================
# MODULE 2: WEEKLY HISTORY & ANALYTICS
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
        
        # Performance Formulas
        goal_achievement_pct = round(((direct_completed + rescheduled_completed) / total_planned) * 100, 1)
        on_schedule_pct = round((direct_completed / total_planned) * 100, 1)
        rescheduled_pct = round((rescheduled_completed / total_planned) * 100, 1)
        skipped_pct = round((skipped / total_planned) * 100, 1)

        # High-Level Metrics Display
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Planned Tasks", total_planned)
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

        # Weekly Motivational Summary Evaluation (>= 90% Threshold)
        st.markdown("---")
        st.subheader("🏆 Weekly Motivational Summary")
        if st.session_state.settings["master_notifications"] and st.session_state.settings["weekly_motivation"]:
            if goal_achievement_pct >= 90:
                st.balloons()
                st.success(f"🎉 **Great Work!** You achieved {goal_achievement_pct}% of your weekly goals. You completed most of your planned tasks and successfully managed your rescheduled tasks.")
            else:
                st.info(f"💪 **Keep Going!** You achieved {goal_achievement_pct}% of your weekly goals. Don't worry about missed tasks. Plan your next week better and keep improving!")

# ==========================================
# MODULE 3: ISLAMIC LIFESTYLE & REMINDERS
# ==========================================
elif menu == "Islamic Lifestyle & Reminders":
    st.markdown("<div class='main-header'>🕌 Islamic Lifestyle & Prayer Reminders</div>", unsafe_allow_html=True)

    if not st.session_state.settings["master_notifications"]:
        st.warning("⚠️ All system notifications are currently disabled in Settings. Turn on notifications to activate Prayer Reminders.")
    elif not st.session_state.settings["islamic_reminders"]:
        st.info("Islamic reminders are toggled OFF in App Settings.")
    else:
        st.success(f"📍 Location configured for Prayer Times: **{st.session_state.settings['location']}**")

        st.subheader("🕋 Daily Prayer Schedule (Default Priority)")
        prayer_df = pd.DataFrame({
            "Prayer": ["Fajr", "Dhuhr", "Asr", "Maghrib", "Isha"],
            "Time": ["05:10 AM", "12:15 PM", "03:45 PM", "06:10 PM", "07:30 PM"],
            "System Priority": ["Default Active", "Default Active", "Default Active", "Default Active", "Default Active"]
        })
        st.table(prayer_df)

        st.markdown("---")
        st.subheader("📖 Day-Specific Reminders & Azkar")
        today_str = datetime.now().strftime("%A")
        
        day_reminders = {
            "Friday": "📖 **Friday Sunnah:** Recite Surah Al-Kahf & send abundant Darood Shareef upon Prophet Muhammad (PBUH).",
            "Monday": "✨ **Monday Sunnah:** Voluntary Fasting day & Recite Morning Azkar.",
            "Thursday": "✨ **Thursday Sunnah:** Evening Azkar & Preparation for Friday Jumu'ah.",
            "Saturday": "📿 **Daily Azkar:** SubhanAllah (33x), Alhamdulillah (33x), Allahu Akbar (34x).",
            "Sunday": "📿 **Daily Azkar:** Recite Ayatul Kursi after prayers & Astaghfirullah."
        }
        st.info(day_reminders.get(today_str, "📿 **Daily Reminder:** Maintain daily prayers, Quranic recitation, and morning/evening Azkar."))

# ==========================================
# MODULE 4: SYSTEM SETTINGS
# ==========================================
elif menu == "System Settings":
    st.markdown("<div class='main-header'>⚙️ Application Settings</div>", unsafe_allow_html=True)

    with st.form("settings_form"):
        st.subheader("🔔 Notification Rules Engine")
        master_notif = st.checkbox("Master Notifications Switch (ON/OFF)", value=st.session_state.settings["master_notifications"])
        st.caption("Note: Turning Master Notifications OFF disables all system alerts, including Prayer Notifications.")
        
        daily_mot = st.checkbox("Enable Daily Motivation Alerts (>80% Completion Rule)", value=st.session_state.settings["daily_motivation"])
        weekly_mot = st.checkbox("Enable Weekly Summary Alerts (>=90% Completion Rule)", value=st.session_state.settings["weekly_motivation"])
        
        st.subheader("🕌 Islamic Lifestyle Engine")
        islamic_on = st.checkbox("Enable Prayer Schedules & Verified Reminders", value=st.session_state.settings["islamic_reminders"])
        loc = st.text_input("City / Location", value=st.session_state.settings["location"])

        save = st.form_submit_button("Save Configuration")
        if save:
            st.session_state.settings["master_notifications"] = master_notif
            st.session_state.settings["daily_motivation"] = daily_mot
            st.session_state.settings["weekly_motivation"] = weekly_mot
            st.session_state.settings["islamic_reminders"] = islamic_on
            st.session_state.settings["location"] = loc
            st.success("Settings updated successfully!")