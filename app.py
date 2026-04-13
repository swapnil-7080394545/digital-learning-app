import os
import platform
from datetime import datetime

import pandas as pd
import streamlit as st

# Streamlit page configuration
st.set_page_config(
    page_title="Digital Learning & Student Tracking",
    layout="wide",
    page_icon="🎓",
)

DATA_DIR = os.path.dirname(os.path.abspath(__file__))
STUDENT_XLSX = os.path.join(DATA_DIR, "student.xlsx")
STUDENT_CSV = os.path.join(DATA_DIR, "student.csv")
SESSION_CSV = os.path.join(DATA_DIR, "session.csv")
TRACKING_CSV = os.path.join(DATA_DIR, "tracking.csv")

# ------------------ LOAD DATA ------------------

@st.cache_data
def load_student_data():
    if os.path.exists(STUDENT_XLSX):
        try:
            return pd.read_excel(STUDENT_XLSX, engine="openpyxl", dtype=str)
        except Exception:
            pass
    if os.path.exists(STUDENT_CSV):
        try:
            return pd.read_csv(STUDENT_CSV, dtype=str)
        except Exception:
            pass
    return pd.DataFrame()

@st.cache_data
def load_session_data():
    return pd.read_csv(SESSION_CSV, dtype=str).fillna("")

def save_to_tracking_csv(entry):
    """Append tracking data to tracking.csv."""
    try:
        # Prepare the row
        row = [{
            "student_id": entry.get("student_id", ""),
            "school": entry.get("school", ""),
            "class": entry.get("class", ""),
            "session": entry.get("session", ""),
            "date": entry.get("date", ""),
            "time": entry.get("time", ""),
            "device": entry.get("device", ""),
            "use_time": entry.get("use_time", ""),
            "session_completed": entry.get("session_completed", ""),
            "week": entry.get("week", ""),
            "month": entry.get("month", ""),
            "day": entry.get("day", ""),
        }]
        
        # Read existing data or create new
        if os.path.exists(TRACKING_CSV):
            df = pd.read_csv(TRACKING_CSV, dtype=str)
            df = pd.concat([df, pd.DataFrame(row)], ignore_index=True)
        else:
            df = pd.DataFrame(row)
        
        # Save to CSV
        df.to_csv(TRACKING_CSV, index=False)
        return True
    except Exception as e:
        st.error(f"Failed to save to tracking.csv: {str(e)}")
        return False

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
                        st.rerun()
                    else:
                        st.error("Invalid student ID or password. Please try again.")
                else:
                    st.warning("Please enter both student ID and password.")

    with info_col:
        st.markdown("### Login Tips")
        st.markdown("- Use the registered `student_ID` from your school record.\n- The default password is often `1234` in sample datasets.\n- For a secure experience, always log out after your session.")

# ------------------ MAIN APP ------------------

def main_app(student_df, session_df):
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
    st.markdown("### Digital Learning Platform")

    logout_col = st.columns([1])[0]
    with logout_col:
        if st.button("Logout"):
            st.session_state.clear()
            st.rerun()

    with st.expander("Your selected session details", expanded=True):
        choice_col1, choice_col2, choice_col3 = st.columns(3)
        schools = clean_list(student_df["School"])
        default_school = st.session_state.get("selected_school", student_school if student_school in schools else (schools[0] if schools else ""))
        selected_school = choice_col1.selectbox(
            "Select School",
            schools,
            index=schools.index(default_school) if default_school in schools else 0,
            key="selected_school",
        ) if schools else ""

        classes_for_school = clean_list(student_df[student_df["School"] == selected_school]["Class"])
        if not classes_for_school:
            classes_for_school = clean_list(student_df["Class"])
        default_class = st.session_state.get("selected_class", str(student_class) if str(student_class) in classes_for_school else (classes_for_school[0] if classes_for_school else ""))
        selected_class = choice_col2.selectbox(
            "Select Class",
            classes_for_school,
            index=classes_for_school.index(default_class) if default_class in classes_for_school else 0,
            key="selected_class",
        ) if classes_for_school else ""

        sessions_for_class = session_df[session_df["Class"] == selected_class]
        session_options = clean_list(sessions_for_class["Session"])
        if session_options:
            default_session = st.session_state.get("selected_session", session_options[0])
            selected_session = choice_col3.selectbox(
                "Select Session",
                session_options,
                index=session_options.index(default_session) if default_session in session_options else 0,
                key="selected_session",
            )
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
                
                # Auto-save tracking when video is displayed
                if "tracked_session" not in st.session_state:
                    st.session_state.tracked_session = None
                
                current_session_key = f"{selected_school}_{selected_class}_{selected_session}"
                if st.session_state.tracked_session != current_session_key:
                    entry = {
                        "student_id": str(user.get("student_ID", "")),
                        "school": selected_school,
                        "class": str(selected_class),
                        "session": str(selected_session),
                        "date": datetime.now().strftime("%Y-%m-%d"),
                        "time": datetime.now().strftime("%H:%M:%S.%f"),
                        "device": "web",
                        "use_time": "",
                        "session_completed": "0",
                        "week": datetime.now().strftime("%U"),
                        "month": datetime.now().month,
                        "day": datetime.now().strftime("%A"),
                    }
                    save_to_tracking_csv(entry)
                    st.session_state.tracked_session = current_session_key
                    st.toast("✅ Session tracked", icon="📝")
                
            except Exception as e:
                st.error(f"Unable to load video: {str(e)}")
                st.info("Please check the video link or try again later.")

        with notes_col:
            st.markdown("###  Download Notes")
            notes = session_details.get("Notes") or session_details.get("notes") or session_details.get("Notes Link") or ""
            if notes and str(notes).strip():
                st.markdown(f"[📥 Download Notes]({notes})")
            else:
                st.info("No notes available for this session.")
    else:
        st.info("Choose a session to view the video and notes preview.")


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
        st.session_state.setdefault("login", False)
        st.session_state.setdefault("user", {})
        apply_custom_styles()
        student_df = load_student_data()
        session_df = load_session_data()

        if not st.session_state.login:
            login_page(student_df)
        else:
            main_app(student_df, session_df)
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.info("Please refresh the page or contact support if the issue persists.")

if __name__ == "__main__":
    main()