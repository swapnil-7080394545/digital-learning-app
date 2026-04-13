import os
import platform
import random
from datetime import datetime, timedelta

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

# Streamlit page configuration
st.set_page_config(
    page_title="Digital Learning & Student Tracking",
    layout="wide",
    page_icon="🎓",
)

DATA_DIR = os.path.dirname(os.path.abspath(__file__))
STUDENT_XLSX = os.path.join(DATA_DIR, "student.xlsx")
SESSION_CSV = os.path.join(DATA_DIR, "session.csv")
TRACKING_CSV = os.path.join(DATA_DIR, "tracking.csv")

# ------------------ LOAD DATA ------------------

def load_student_data():
    if os.path.exists(STUDENT_XLSX):
        try:
            return pd.read_excel(STUDENT_XLSX, engine="openpyxl", dtype=str)
        except:
            pass
    student_csv = os.path.join(DATA_DIR, "student.csv")
    if os.path.exists(student_csv):
        return pd.read_csv(student_csv, dtype=str)
    return pd.DataFrame()

@st.cache_data
def load_session_data():
    return pd.read_csv(SESSION_CSV, dtype=str).fillna("")

@st.cache_data
def load_tracking_data():
    if os.path.exists(TRACKING_CSV):
        df = pd.read_csv(TRACKING_CSV, dtype=str)
        df["use_time"] = pd.to_numeric(df.get("use_time", 0), errors="coerce").fillna(0)
        return df
    return pd.DataFrame()

def save_tracking(entry):
    df = pd.DataFrame([entry])
    df.to_csv(TRACKING_CSV, mode="a", header=not os.path.exists(TRACKING_CSV), index=False)
    load_tracking_data.clear()

def ensure_dummy_tracking(tracking_df, student_df, session_df):
    if st.session_state.get("dummy_populated"):
        return

    if len(tracking_df) >= 1000:
        st.session_state.dummy_populated = True
        return

    if student_df.empty or session_df.empty:
        return

    needed = max(0, 1000 - len(tracking_df))
    student_ids = student_df["student_ID"].astype(str).unique().tolist()
    schools = student_df["School"].astype(str).unique().tolist()
    student_map = student_df.set_index("student_ID")["School"].to_dict()
    session_options = session_df["Session"].astype(str).tolist()
    classes = session_df["Class"].astype(str).unique().tolist()

    dummy_rows = []
    today = datetime.today()
    for _ in range(needed):
        student_id = random.choice(student_ids)
        school = student_map.get(student_id, random.choice(schools))
        session_item = random.choice(session_options)
        class_item = random.choice(classes)
        date_value = today - timedelta(days=random.randint(0, 35))
        start_time = datetime.combine(date_value.date(), datetime.min.time()) + timedelta(
            hours=random.randint(8, 21), minutes=random.randint(0, 59)
        )
        use_time = round(random.uniform(2.0, 50.0), 2)
        completed = random.choice(["Yes", "No"])

        dummy_rows.append({
            "student_id": str(student_id),
            "school": school,
            "class": class_item,
            "session": session_item,
            "date": date_value.strftime("%Y-%m-%d"),
            "time": start_time.strftime("%H:%M:%S"),
            "device": random.choice(["Mobile", "Desktop"]),
            "use_time": use_time,
            "session_completed": completed,
            "week": date_value.strftime("%U"),
            "month": date_value.month,
            "day": date_value.strftime("%A"),
        })

    if dummy_rows:
        pd.DataFrame(dummy_rows).to_csv(TRACKING_CSV, mode="a", header=not os.path.exists(TRACKING_CSV), index=False)
        load_tracking_data.clear()
    st.session_state.dummy_populated = True

def detect_device_type():
    if "device_type" in st.session_state and st.session_state.device_type:
        return st.session_state.device_type

    try:
        if hasattr(st, "query_params"):
            query_params = dict(st.query_params)
        else:
            query_params = st.experimental_get_query_params()
    except Exception:
        query_params = {}

    device_from_query = query_params.get("device", [None])
    if isinstance(device_from_query, list):
        device_from_query = device_from_query[0] if device_from_query else None

    if device_from_query:
        st.session_state.device_type = device_from_query
        return device_from_query

    js = """
        <script>
        const isMobile = /Mobi|Android|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
        const device = isMobile ? 'Mobile' : 'Desktop';
        const params = new URLSearchParams(window.location.search);
        params.set('device', device);
        window.history.replaceState({}, '', `${window.location.pathname}?${params}`);
        </script>
    """
    components.html(js, height=0)
    fallback = platform.system()
    st.session_state.device_type = "Detecting..." if not device_from_query else fallback
    return st.session_state.device_type

def safe_rerun():
    if hasattr(st, "rerun"):
        st.rerun()
    elif hasattr(st, "experimental_rerun"):
        st.experimental_rerun()
    else:
        raise RuntimeError("Streamlit rerun not available in this version.")

# ------------------ SAFE CLEAN ------------------

def clean_list(series):
    return sorted(series.dropna().astype(str).str.strip().unique().tolist())

# ------------------ LOGIN ------------------

def login_page(student_df):
    st.markdown("## Welcome to the Digital Learning Platform")
    st.markdown("Use your `student id` and `password` to sign in and access your learning sessions.")

    login_col, empty_col, info_col = st.columns([2, 1, 2])
    with login_col:
        with st.form("login_form"):
            student_id = st.text_input("Student ID", value="", max_chars=32).strip()
            password = st.text_input("Password", type="password").strip()
            submit = st.form_submit_button("Login")

            if submit:
                if student_id and password:
                    user = student_df[
                        (student_df["student_ID"].astype(str).str.strip() == student_id) &
                        (student_df["password"].astype(str).str.strip() == password)
                    ]
                    if not user.empty:
                        st.session_state.user = user.iloc[0].to_dict()
                        st.session_state.login = True
                        safe_rerun()
                    else:
                        st.error("Invalid student ID or password. Please try again.")
                else:
                    st.warning("Please enter both student ID and password.")

    with info_col:
        st.markdown("### Login Tips")
        st.markdown("- Use the registered `student_ID` from your school record.\n- The default password is often `1234` in sample datasets.\n- For a secure experience, always log out after your session.")

# ------------------ MAIN APP ------------------

def main_app(student_df, session_df, tracking_df):
    if student_df.empty:
        st.error("Student data could not be loaded. Please check the data files.")
        return
    if session_df.empty:
        st.error("Session data could not be loaded. Please check the data files.")
        return

    user = st.session_state.user
    student_name = user.get("student_Name", "Student")
    student_school = user.get("School", "")
    student_class = user.get("Class", "")

    st.markdown(f"## Welcome {student_name}")
    st.markdown("### Digital Learning & Tracking Dashboard")

    logout_col, device_col = st.columns([1, 1])
    with logout_col:
        if st.button("Logout"):
            st.session_state.clear()
            safe_rerun()

    with device_col:
        device_type = detect_device_type()
        st.info(f"Detected device: **{device_type}**")

    with st.expander("Your selected session details", expanded=True):
        choice_col1, choice_col2, choice_col3 = st.columns(3)
        schools = clean_list(student_df["School"])
        if student_school and student_school in schools:
            selected_school = choice_col1.selectbox("Select School", schools, index=schools.index(student_school))
        else:
            selected_school = choice_col1.selectbox("Select School", schools)

        classes_for_school = clean_list(student_df[student_df["School"] == selected_school]["Class"])
        if not classes_for_school:
            classes_for_school = clean_list(student_df["Class"])
        if str(student_class) in classes_for_school:
            selected_class = choice_col2.selectbox("Select Class", classes_for_school, index=classes_for_school.index(str(student_class)))
        else:
            selected_class = choice_col2.selectbox("Select Class", classes_for_school)

        sessions_for_class = session_df[session_df["Class"] == selected_class]
        session_options = clean_list(sessions_for_class["Session"])
        if session_options:
            selected_session = choice_col3.selectbox("Select Session", session_options)
        else:
            selected_session = None
            choice_col3.info("No sessions found for this class.")

    session_details = None
    if selected_session and not sessions_for_class.empty:
        session_details = sessions_for_class[sessions_for_class["Session"] == selected_session].iloc[0]

    video_col, notes_col = st.columns([3, 1])
    if session_details is not None:
        video_url = session_details.get("Video Link", "")
        if video_url:
            try:
                st.video(video_url)
            except Exception as e:
                st.error(f"Unable to load video: {str(e)}")
                st.info("Please check the video link or try again later.")

        with notes_col:
            st.markdown("### 📄 Download Notes")
            notes = session_details.get("Notes") or session_details.get("notes") or session_details.get("Notes Link") or ""
            if notes and str(notes).strip():
                st.markdown(f"[📥 Download Notes]({notes})")
            else:
                st.info("No notes available for this session.")
    else:
        st.info("Choose a session to view the video and notes preview.")

    st.markdown("---")
    tracker_col, stats_col = st.columns([2, 1])
    with tracker_col:
        st.subheader("Session Tracking")
        if "current_session_start" not in st.session_state:
            st.session_state.current_session_start = None
        if "completed_radio" not in st.session_state:
            st.session_state.completed_radio = "Yes"

        completed_option = st.radio("Did you complete the session?", ["Yes", "No"], index=0, key="completed_radio")

        start_button, end_button = st.columns(2)
        if start_button.button("Start Session"):
            st.session_state.current_session_start = datetime.now()
            st.success("Session started. Enjoy your learning!")

        if end_button.button("End Session"):
            if st.session_state.current_session_start is None:
                st.warning("Please start a session before ending it.")
            elif selected_session is None:
                st.warning("Please select a session before ending the tracking.")
            else:
                start_time = st.session_state.current_session_start
                elapsed = datetime.now() - start_time
                elapsed_minutes = round(elapsed.total_seconds() / 60, 2)
                entry = {
                    "student_id": str(user.get("student_ID", "")),
                    "school": selected_school,
                    "class": str(selected_class),
                    "session": str(selected_session),
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "time": datetime.now().strftime("%H:%M:%S"),
                    "device": device_type if device_type not in ["Detecting...", ""] else platform.system(),
                    "use_time": elapsed_minutes,
                    "session_completed": completed_option,
                    "week": datetime.now().strftime("%U"),
                    "month": datetime.now().month,
                    "day": datetime.now().strftime("%A"),
                }
                save_tracking(entry)
                st.success(f"Saved tracking record: {elapsed_minutes} minutes.")
                st.session_state.current_session_start = None
                safe_rerun()

    with stats_col:
        st.subheader("Session Activity")
        st.markdown("Track your learning time, mark completion, and keep progress visible to teachers.")
        st.write("- Start a session when you begin learning.")
        st.write("- End the session when you finish or take a break.")
        st.write("- The dashboard updates with usage and completion statistics.")

    st.markdown("---")
    st.subheader("Tracking Dashboard")
    render_dashboard(tracking_df)

def render_dashboard(tracking_df):
    try:
        if tracking_df.empty:
            st.warning("No tracking data is available yet.")
            return

        tracking_df["is_completed"] = tracking_df["session_completed"].astype(str).str.lower().isin(["yes", "1", "true"])
        total_students = tracking_df["student_id"].nunique()
        total_completed = tracking_df["is_completed"].sum()
        total_hours = tracking_df["use_time"].astype(float).sum()
        completion_rate = round(total_completed / max(len(tracking_df), 1) * 100, 1)

        metric_col1, metric_col2, metric_col3 = st.columns(3)
        metric_col1.metric("Total Students", total_students)
        metric_col2.metric("Sessions Completed", int(total_completed))
        metric_col3.metric("Total Usage Time (mins)", round(total_hours, 1))

        chart_col1, chart_col2 = st.columns(2)
        with chart_col1:
            st.subheader("Class-wise Usage")
            class_usage = tracking_df.groupby("class")["use_time"].sum().sort_values(ascending=False)
            st.bar_chart(class_usage)

        with chart_col2:
            st.subheader("Daily Activity")
            if "date" in tracking_df.columns:
                daily_activity = tracking_df.groupby("date")["use_time"].sum().sort_index()
                st.line_chart(daily_activity)
            else:
                st.info("Daily activity will appear after sessions are tracked.")

        completion_col, recent_col = st.columns([2, 3])
        with completion_col:
            st.subheader("Session Completion Rate")
            completion_by_class = tracking_df.groupby("class").agg(
                completed=("is_completed", "sum"), total=("is_completed", "count")
            )
            completion_by_class["rate"] = (completion_by_class["completed"] / completion_by_class["total"] * 100).round(1)
            st.dataframe(completion_by_class["rate"].rename("Completion %"), use_container_width=True)

        with recent_col:
            st.subheader("Recent Tracking Activity")
            st.dataframe(tracking_df.sort_values(by=["date", "time"], ascending=False).head(12))
    except Exception as e:
        st.error(f"Error loading dashboard: {str(e)}")

def apply_custom_styles():
    st.markdown(
        """
        <style>
        /* Global Styles */
        body {
            background-color: #fff9f2 !important;
            color: #2b0a0a;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            font-size: 14px !important;
            line-height: 1.5 !important;
        }

        .stApp {
            background-color: #fff9f2 !important;
        }

        .block-container {
            max-width: 1000px;
            margin: 0 auto;
            padding-top: 1rem;
            padding-bottom: 1rem;
            background-color: #fff9f2 !important;
        }

        /* Headings */
        h1, h2, h3, h4, h5, h6 {
            color: #a80c0c !important;
            text-align: center;
            margin-bottom: 1rem;
            font-weight: 600;
            font-size: 1.2rem !important;
        }

        h1 { font-size: 1.8rem !important; }
        h2 { font-size: 1.5rem !important; }
        h3 { font-size: 1.3rem !important; }

        /* Buttons */
        .stButton button {
            background-color: #c1121f !important;
            color: white !important;
            border: none !important;
            border-radius: 8px !important;
            padding: 0.5rem 1rem !important;
            font-size: 0.85rem !important;
            font-weight: 500 !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 2px 4px rgba(193, 18, 31, 0.2) !important;
        }

        .stButton button:hover {
            background-color: #a80c0c !important;
            transform: translateY(-1px) !important;
            box-shadow: 0 4px 8px rgba(193, 18, 31, 0.3) !important;
        }

        /* Inputs and Dropdowns */
        .stTextInput input, .stSelectbox select, .stRadio div {
            border: 2px solid #f5c2b2 !important;
            border-radius: 8px !important;
            padding: 0.5rem !important;
            background-color: white !important;
            transition: border-color 0.3s ease !important;
        }

        .stTextInput input:focus, .stSelectbox select:focus {
            border-color: #c1121f !important;
            box-shadow: 0 0 0 2px rgba(193, 18, 31, 0.1) !important;
        }

        /* Cards and Sections */
        .stExpander, .stAlert, .stInfo {
            border-radius: 12px !important;
            border: 1px solid #f5c2b2 !important;
            background-color: white !important;
            box-shadow: 0 4px 12px rgba(0,0,0,0.05) !important;
            margin-bottom: 1rem !important;
        }

        /* Video and Notes Layout */
        .stColumns {
            gap: 1rem !important;
        }

        /* Links */
        a, .stMarkdown a {
            color: #c1121f !important;
            text-decoration: none !important;
            font-weight: 500 !important;
        }

        a:hover, .stMarkdown a:hover {
            color: #a80c0c !important;
            text-decoration: underline !important;
        }

        /* Metrics */
        .stMetric {
            background-color: white !important;
            border-radius: 12px !important;
            padding: 1rem !important;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05) !important;
            border: 1px solid #f5c2b2 !important;
        }

        /* Charts */
        .stBarChart, .stLineChart {
            background-color: white !important;
            border-radius: 12px !important;
            padding: 1rem !important;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05) !important;
            border: 1px solid #f5c2b2 !important;
        }

        /* DataFrames */
        .stDataFrame {
            border-radius: 12px !important;
            overflow: hidden !important;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05) !important;
        }

        /* Mobile Responsiveness */
        @media (max-width: 768px) {
            .block-container {
                padding-left: 1rem !important;
                padding-right: 1rem !important;
            }

            h1, h2, h3, h4, h5, h6 {
                font-size: 1.2rem !important;
                text-align: left !important;
            }

            .stButton button {
                width: 100% !important;
                margin-bottom: 0.5rem !important;
            }

            .stColumns {
                flex-direction: column !important;
                gap: 0.5rem !important;
            }

            .stMetric {
                margin-bottom: 1rem !important;
            }
        }

        /* Sidebar (if used) */
        .stSidebar {
            background-color: #fff9f2 !important;
            border-right: 2px solid #f5c2b2 !important;
        }

        /* Form Styling */
        .stForm {
            background-color: white !important;
            border-radius: 12px !important;
            padding: 2rem !important;
            box-shadow: 0 4px 12px rgba(0,0,0,0.05) !important;
            border: 1px solid #f5c2b2 !important;
        }

        /* Success/Warning/Error Messages */
        .stSuccess, .stWarning, .stError, .stInfo {
            border-radius: 8px !important;
            border: none !important;
        }

        .stSuccess {
            background-color: #d4edda !important;
            color: #155724 !important;
        }

        .stWarning {
            background-color: #fff3cd !important;
            color: #856404 !important;
        }

        .stError {
            background-color: #f8d7da !important;
            color: #721c24 !important;
        }

        .stInfo {
            background-color: #d1ecf1 !important;
            color: #0c5460 !important;
        }

        /* Radio Buttons */
        .stRadio label {
            font-weight: 500 !important;
            color: #2b0a0a !important;
        }

        /* Expander */
        .stExpander summary {
            background-color: #f8f9fa !important;
            border-radius: 8px !important;
            padding: 0.5rem 1rem !important;
            font-weight: 600 !important;
            color: #a80c0c !important;
        }

        .stExpander .stExpanderContent {
            padding: 1rem !important;
            background-color: white !important;
            border-radius: 0 0 12px 12px !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

# ------------------ MAIN ------------------

def main():
    try:
        apply_custom_styles()
        student_df = load_student_data()
        session_df = load_session_data()
        tracking_df = load_tracking_data()

        ensure_dummy_tracking(tracking_df, student_df, session_df)

        if not st.session_state.get("login"):
            login_page(student_df)
        else:
            main_app(student_df, session_df, tracking_df)
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.info("Please refresh the page or contact support if the issue persists.")

if __name__ == "__main__":
    main()