import streamlit as st
import pandas as pd
from datetime import datetime
import time
import os
import csv

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Digital Learning App",
    page_icon=" ",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Hide Streamlit default elements
hide_st_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
.stApp > header {display: none;}
.stDeployButton {display: none;}
.stApp, .block-container, .main, [data-testid="stAppViewContainer"] {
    background: transparent !important;
}
.block-container {
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    padding: 0 !important;
    margin: 0 auto !important;
    width: 100% !important;
    max-width: 380px !important;
    min-height: 100vh;
}
.main {padding: 0 !important; margin: 0 auto !important;}
.st-emotion-cache-1jicfl2 {padding: 0 !important;}
[data-testid="stAppViewContainer"] {padding: 0 !important;}
</style>
"""
st.markdown(hide_st_style, unsafe_allow_html=True)

# ---------------- CUSTOM CSS ----------------
st.markdown("""
<style>
/* Global Styles */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

html, body {
    background-color: #FFF8F0 !important;
}
body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
    background-color: #FFF8F0 !important;
    min-height: 100vh;
    overflow-x: hidden;
}

/* Login Page Styles */
.login-container {
    width: 100%;
    max-width: 380px;
    padding: 20px;
    animation: slideUp 0.55s ease-out;
    background: #FFFFFF;
    border: 1px solid rgba(0, 0, 0, 0.05);
    box-shadow: 0 18px 45px rgba(0, 0, 0, 0.08);
    border-radius: 12px;
    position: relative;
    overflow: hidden;
}

@keyframes slideUp {
    from {
        opacity: 0;
        transform: translateY(14px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.login-icon {
    width: 44px;
    height: 44px;
    margin: 0 auto 12px;
    border-radius: 50%;
    background: rgba(229, 57, 53, 0.12);
    display: flex;
    align-items: center;
    justify-content: center;
    color: #E53935;
    font-size: 1.2rem;
}

.login-title {
    text-align: center;
    color: #222222;
    font-size: 22px;
    font-weight: 700;
    margin-bottom: 6px;
}

..login-title span {
    display: inline-block;
    animation: floatText 3.5s ease-in-out infinite;
}

@keyframes floatText {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-3px); }
}

.login-subtitle {
    text-align: center;
    color: #5A5A5A;
    font-size: 15px;
    margin-bottom: 10px;
    margin-top: 0;
    font-weight: 600;
    line-height: 1.4;
}

.login-desc {
    text-align: center;
    color: #7A7A7A;
    font-size: 14px;
    margin-bottom: 18px;
    line-height: 1.55;
}

/* Form Elements */
.stTextInput > div > div > input {
    border-radius: 8px;
    border: 1px solid #E8D4B8 !important;
    padding: 0 0.95rem !important;
    font-size: 14px !important;
    transition: all 0.2s ease;
    background: #FFFFFF !important;
    height: 44px !important;
}

.stTextInput > div > div > input:focus {
    border-color: #E53935 !important;
    box-shadow: 0 0 0 2px rgba(229, 57, 53, 0.08) !important;
    transform: translateY(-2px);
}

.stTextInput > div > div > input::placeholder {
    color: #999;
}

/* Button Styles */
.login-btn {
    background: linear-gradient(135deg, #E53935 0%, #D81B60 100%);
    color: white;
    border: none;
    border-radius: 14px;
    padding: 0.95rem 1.2rem;
    font-size: 1rem;
    font-weight: 700;
    cursor: pointer;
    transition: all 0.25s ease;
    width: 100%;
    margin-top: 1.2rem;
    position: relative;
    overflow: hidden;
    height: 48px;
    box-shadow: 0 16px 36px rgba(229, 57, 53, 0.18);
}

.login-btn:hover {
    background: linear-gradient(135deg, #D81B60 0%, #E53935 100%);
    transform: translateY(-2px) scale(1.01);
    box-shadow: 0 18px 42px rgba(229, 57, 53, 0.24);
}

.login-btn:active {
    transform: translateY(0) scale(0.99);
}

.login-btn:active {
    transform: translateY(0px);
}

/* Streamlit Button Override */
.stButton > button {
    background-color: #E53935 !important;
    color: white !important;
    border-radius: 8px !important;
    border: none !important;
    padding: 0 1rem !important;
    font-weight: 700 !important;
    font-size: 14px !important;
    transition: all 0.2s ease !important;
    height: 45px !important;
    width: 100% !important;
    letter-spacing: 0.02em;
}

.stButton > button:hover {
    background-color: #C62828 !important;
    transform: translateY(-1px) !important;
}

.stButton > button:focus {
    background-color: #E53935 !important;
}

/* Dashboard Styles */
.dashboard-container {
    max-width: 380px;
    margin: 0 auto;
    padding: 1rem 0 1.5rem;
    animation: fadeIn 0.45s ease-in;
    background-color: transparent;
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    justify-content: flex-start;
}

@keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
}

.dashboard-heading {
    text-align: center;
    margin-bottom: 10px;
    padding: 0;
.dashboard-title {
    font-size: 1.2rem;
    font-weight: 700;
    color: #222;
    margin-bottom: 4px;
}

.dashboard-subtitle {
    font-size: 0.95rem;
    color: #666;
    margin: 0;
    line-height: 1.5;
}

.dashboard-panel {
    background: transparent;
    border-radius: 0;
    padding: 0;
    box-shadow: none;
    border: none;
}

.field-label {
    font-size: 0.82rem;
    font-weight: 700;
    letter-spacing: 0.11em;
    color: #6F6F6F;
    margin-bottom: 0.25rem;
    text-transform: uppercase;
}

.field-row {
    margin-bottom: 0.72rem;
}

.stSelectbox > div > div > select {
    border-radius: 10px;
    border: 1px solid #E8D4B8;
    padding: 0.72rem 0.85rem;
    font-size: 0.95rem;
    transition: all 0.2s ease;
    background: #FFF8F2;
    min-height: 42px;
}

.stSelectbox > div > div > select:focus {
    border-color: #E53935;
    box-shadow: 0 0 0 2px rgba(229, 57, 53, 0.08);
}

.video-section {
    margin-top: 1rem;
}

..video-section {
    margin-top: 16px;
    padding-top: 16px;
    border-top: 1px solid rgba(0, 0, 0, 0.08);
}

.video-title {
    font-size: 1rem;
    font-weight: 700;
    color: #D32F2F;
    margin-bottom: 0.75rem;
}

.stVideo {
    border-radius: 14px;
    overflow: hidden;
}

/* Logout Button */
.logout-btn {
    position: fixed;
    top: 10px;
    right: 10px;
    background: #E53935;
    color: white;
    border: none;
    border-radius: 8px;
    padding: 0.5rem 1rem;
    font-weight: 600;
    font-size: 0.9rem;
    cursor: pointer;
    transition: all 0.2s ease;
    z-index: 1000;
    height: 32px;
}

.logout-btn:hover {
    background: #C62828;
    transform: translateY(-1px);
    box-shadow: 0 2px 6px rgba(229, 57, 53, 0.2);
}

/* Success/Error Messages */
.stSuccess, .stError {
    border-radius: 8px;
    padding: 0.8rem;
    margin: 0.8rem 0;
    font-size: 0.9rem;
}

.stSuccess {
    background: #E8F5E9;
    border: 1px solid #4CAF50;
    color: #2E7D32;
}

.stError {
    background: #FFEBEE;
    border: 1px solid #E53935;
    color: #C62828;
}

.stInfo {
    background: #E3F2FD;
    border: 1px solid #1976D2;
    color: #0D47A1;
}

/* Responsive Design */
@media (max-width: 768px) {
    .login-container {
        padding: 0;
    }

    .dashboard-container {
        padding: 0.8rem;
    }

    .selection-grid {
        grid-template-columns: 1fr;
        gap: 0.8rem;
    }

    .welcome-title {
        font-size: 1.1rem;
    }

    .video-title {
        font-size: 1.1rem;
    }
}
</style>
""", unsafe_allow_html=True)

# ---------------- UTILITY FUNCTIONS ----------------
@st.cache_data
def load_data():
    try:
        students = pd.read_csv("student.csv")
        sessions = pd.read_csv("session.csv")
        return students, sessions
    except Exception as e:
        st.error(f"Data load error: {e}")
        return None, None

def save_tracking_data(tracking_entry):
    """Save tracking data to CSV with proper error handling"""
    try:
        # Use absolute path
        csv_path = os.path.join(os.getcwd(), "tracking.csv")
        
        # Check if file exists and has data
        file_exists = os.path.exists(csv_path) and os.path.getsize(csv_path) > 0
        
        # Define fieldnames
        fieldnames = list(tracking_entry.keys())
        
        # Write to CSV with proper error handling
        with open(csv_path, 'a', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            # Write header only if file is empty
            if not file_exists:
                writer.writeheader()
            
            writer.writerow(tracking_entry)
        
        st.session_state.tracking_saved = True
    except PermissionError:
        st.error("⚠️ Permission denied: Please close tracking.csv if it's open in Excel or another application.")
        st.session_state.tracking_saved = False
    except Exception as e:
        st.error(f"⚠️ Error saving data: {str(e)}")
        st.session_state.tracking_saved = False

def get_student_name(students_df, student_id):
    """Get student name from student_id"""
    student_row = students_df[students_df['student_id'].astype(str) == str(student_id)]
    if not student_row.empty:
        # Try different possible name columns
        for col in ['name', 'student_name', 'full_name']:
            if col in student_row.columns:
                return student_row.iloc[0][col]
        return f"Student {student_id}"  # Fallback
    return f"Student {student_id}"

def initialize_tracking_file():
    """Initialize tracking.csv with headers if it doesn't exist"""
    try:
        csv_path = os.path.join(os.getcwd(), "tracking.csv")
        
        # If file doesn't exist, create it with headers
        if not os.path.exists(csv_path):
            fieldnames = [
                "student_id", "school", "class", "session", "date", "time", 
                "device", "use_time", "session_completed", "week", "month", "day"
            ]
            
            with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
    except Exception as e:
        st.warning(f"Could not initialize tracking file: {str(e)}")

# ---------------- LOAD DATA ----------------
students, sessions = load_data()

# Initialize tracking file
initialize_tracking_file()

# ---------------- SESSION STATE INITIALIZATION ----------------
if "page" not in st.session_state:
    st.session_state.page = "login"

if "student_data" not in st.session_state:
    st.session_state.student_data = {}

if "selection_data" not in st.session_state:
    st.session_state.selection_data = {
        "school": None,
        "class": None,
        "session": None,
        "video_start_time": None,
        "session_tracked": False
    }

if "tracking_saved" not in st.session_state:
    st.session_state.tracking_saved = False

# ---------------- LOGIN PAGE ----------------
if st.session_state.page == "login":
    # Center login form using columns
    col1, col2, col3 = st.columns([1, 1.2, 1])
    
    with col2:
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        st.markdown('<div class="login-icon">🎓</div>', unsafe_allow_html=True)
        st.markdown('<h1 class="login-title">Digital Learning</h1>', unsafe_allow_html=True)
        st.markdown('<p class="login-subtitle">Secure Student Access</p>', unsafe_allow_html=True)
        st.markdown('<p class="login-desc">Enter your student ID and password to access your learning dashboard.</p>', unsafe_allow_html=True)
        
        with st.form("login_form", clear_on_submit=False):
            student_id = st.text_input("Student ID", placeholder="Enter ID")
            password = st.text_input("Password", type="password", placeholder="Enter Password")
            
            login_submitted = st.form_submit_button("Login", use_container_width=True)

            if login_submitted:
                if student_id and password:
                    # Authenticate user
                    user = students[
                        (students["student_id"].astype(str) == student_id) &
                        (students["password"].astype(str) == password)
                    ]

                    if not user.empty:
                        # Store student data
                        st.session_state.student_data = {
                            "student_id": student_id,
                            "student_name": get_student_name(students, student_id),
                            "school": user.iloc[0]["school"],
                            "class": user.iloc[0]["class"]
                        }

                        # Reset selection data
                        st.session_state.selection_data = {
                            "school": None,
                            "class": None,
                            "session": None,
                            "video_start_time": None,
                            "session_tracked": False
                        }

                        st.session_state.page = "dashboard"
                        st.success("✓ Login successful!")
                        st.rerun()
                    else:
                        st.error("Invalid credentials")
                else:
                    st.error("Please fill all fields")
        
        st.markdown('</div>', unsafe_allow_html=True)

# ---------------- DASHBOARD PAGE ----------------
elif st.session_state.page == "dashboard":
    st.markdown('<div class="dashboard-container">', unsafe_allow_html=True)

    # Logout Button
    if st.button("🚪 Logout", key="logout", help="Logout and return to login"):
        st.session_state.page = "login"
        st.session_state.student_data = {}
        st.session_state.selection_data = {
            "school": None,
            "class": None,
            "session": None,
            "video_start_time": None
        }
        st.rerun()

    # Dashboard Header
    student_name = st.session_state.student_data.get("student_name", "Student")
    st.markdown(f'<div class="dashboard-heading"><div class="dashboard-title">Welcome, {student_name}</div><p class="dashboard-subtitle">Choose your school, class and session to begin.</p></div>', unsafe_allow_html=True)
    st.markdown('<div class="dashboard-panel">', unsafe_allow_html=True)

    # ---------------- CASCADING SELECTION SYSTEM ----------------

    available_schools = sorted(students["school"].unique())
    st.markdown('<div class="field-row"><div class="field-label">School</div></div>', unsafe_allow_html=True)
    selected_school = st.selectbox(
        "School",
        ["Select school"] + available_schools,
        key="school_select",
        label_visibility="collapsed"
    )
    if selected_school == "Select school":
        selected_school = None

    if selected_school != st.session_state.selection_data["school"]:
        st.session_state.selection_data["school"] = selected_school
        st.session_state.selection_data["class"] = None
        st.session_state.selection_data["session"] = None

    if selected_school:
        school_students = students[students["school"] == selected_school]
        available_classes = sorted(school_students["class"].unique())

        st.markdown('<div class="field-row"><div class="field-label">Class</div></div>', unsafe_allow_html=True)
        selected_class = st.selectbox(
            "Class",
            ["Select class"] + available_classes,
            key="class_select",
            label_visibility="collapsed"
        )
        if selected_class == "Select class":
            selected_class = None

        if selected_class != st.session_state.selection_data["class"]:
            st.session_state.selection_data["class"] = selected_class
            st.session_state.selection_data["session"] = None

        if selected_class:
            class_sessions = sessions[sessions["class"] == selected_class]
            available_sessions = sorted(class_sessions["session"].unique())

            st.markdown('<div class="field-row"><div class="field-label">Session</div></div>', unsafe_allow_html=True)
            selected_session = st.selectbox(
                "Session",
                ["Select session"] + available_sessions,
                key="session_select",
                label_visibility="collapsed"
            )
            if selected_session == "Select session":
                selected_session = None

            if selected_session != st.session_state.selection_data["session"]:
                st.session_state.selection_data["session"] = selected_session
                st.session_state.selection_data["video_start_time"] = time.time()
                st.session_state.selection_data["session_tracked"] = False

            if selected_session:
                selected_video = class_sessions[class_sessions["session"] == selected_session].iloc[0]

                if not st.session_state.selection_data.get("session_tracked", False):
                    now = datetime.now()
                    tracking_entry = {
                        "student_id": st.session_state.student_data["student_id"],
                        "school": selected_school,
                        "class": selected_class,
                        "session": selected_session,
                        "date": now.date(),
                        "time": now.time(),
                        "device": "web",
                        "use_time": 0.0,
                        "session_completed": 0,
                        "week": now.isocalendar()[1],
                        "month": now.month,
                        "day": now.strftime('%A')
                    }
                    save_tracking_data(tracking_entry)
                    st.session_state.selection_data["session_tracked"] = True

                st.markdown('<div class="video-section">', unsafe_allow_html=True)
                st.markdown('<div class="field-label">Topic</div>', unsafe_allow_html=True)
                st.markdown(f'<h2 class="video-title">{selected_video["topic"]}</h2>', unsafe_allow_html=True)

                video_url = selected_video["video_link"]
                try:
                    st.video(video_url)
                except Exception as e:
                    st.error(f"Error loading video: {str(e)}")
                st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)