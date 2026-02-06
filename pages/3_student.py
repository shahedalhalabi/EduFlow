# pages/3_student.py

import streamlit as st
from googleapiclient.discovery import build
import pickle
import os
from datetime import datetime
from streamlit_lottie import st_lottie
import json
from streamlit_extras.stylable_container import stylable_container

# ===== BACKEND FUNCTIONS =====
TOKEN_FILE = "token.json"

def get_credentials():
    """Load saved credentials from pickle file"""
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "rb") as token:
            return pickle.load(token)
    return None

def get_classroom_service():
    """Build Classroom API service"""
    creds = get_credentials()
    if creds:
        return build("classroom", "v1", credentials=creds)
    return None

def list_courses(service):
    """List all courses where user is student"""
    results = service.courses().list(studentId="me").execute()
    return results.get("courses", [])

def list_announcements(service, course_id):
    """List announcements for a course"""
    results = service.courses().announcements().list(
        courseId=course_id,
        orderBy="updateTime desc"
    ).execute()
    return results.get("announcements", [])

def list_assignments(service, course_id):
    """List assignments for a course"""
    results = service.courses().courseWork().list(
        courseId=course_id,
        orderBy="dueDate asc"
    ).execute()
    return results.get("courseWork", [])

def get_assignment_submission(service, course_id, assignment_id):
    """Get student's submission for an assignment"""
    try:
        submission = service.courses().courseWork().studentSubmissions().list(
            courseId=course_id,
            courseWorkId=assignment_id,
            userId="me"
        ).execute()
        return submission.get("studentSubmissions", [{}])[0]
    except Exception:
        return {}
    
def list_course_materials(service, course_id):
    """List all course materials"""
    results = service.courses().courseWorkMaterials().list(
        courseId=course_id,
        orderBy="updateTime desc"
    ).execute()
    return results.get('courseWorkMaterial', [])

def get_material_details(material):
    """Extract material details for display"""
    material_type = ""
    content = ""
    
    if 'driveFile' in material:
        material_type = "📄 Google Drive File"
        content = f"[Open File](https://drive.google.com/file/d/{material['driveFile']['driveFile']['id']}/view)"
    elif 'link' in material:
        material_type = "🌐 External Link"
        content = f"[{material['link'].get('title', 'Link')}]({material['link']['url']})"
    elif 'youtubeVideo' in material:
        material_type = "▶️ YouTube Video"
        content = f"[Watch Video](https://youtu.be/{material['youtubeVideo']['id']})"
    
    return material_type, content

# ===== UI FUNCTIONS =====
def load_lottie(url):
    """Load Lottie animation from URL or local JSON"""
    if url.startswith('http'):
        import requests
        return requests.get(url).json()
    return json.loads(url)

def course_card(course):
    """Display a course as a styled card"""
    with stylable_container(
        key=f"course_{course['id']}",
        css_styles="""
        {
            background: white;
            border-radius: 10px;
            padding: 1rem;
            margin: 0.5rem 0;
            border: 1px solid #e0e0e0;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        """
    ):
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"### {course.get('name', 'Untitled Course')}")
            st.caption(f"Section: {course.get('section', 'N/A')} • Room: {course.get('room', 'N/A')}")
            if course.get('description'):
                st.markdown(f"<div style='color: #555; font-size: 0.9rem;'>{course['description']}</div>", 
                          unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"**ID:** `{course['id']}`")
            if st.button("View Course", key=f"view_{course['id']}"):
                st.session_state.current_course = course

def assignment_card(assignment, submission):
    """Display an assignment with submission status"""
    with stylable_container(
        key=f"assignment_{assignment['id']}",
        css_styles="""
        {
            background: white;
            border-radius: 10px;
            padding: 1rem;
            margin: 0.5rem 0;
            border: 1px solid #e0e0e0;
        }
        """
    ):
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"**{assignment.get('title', 'Untitled Assignment')}**")
            
            if assignment.get('dueDate'):
                due_date = datetime(
                    year=assignment['dueDate']['year'],
                    month=assignment['dueDate']['month'],
                    day=assignment['dueDate']['day'],
                    hour=assignment['dueDate'].get('hours', 23),
                    minute=assignment['dueDate'].get('minutes', 59)
                )
                status = "✅ Submitted" if submission.get('state') == 'TURNED_IN' else (
                    "⚠️ Late" if datetime.now() > due_date else "⏳ Pending"
                )
                st.caption(f"Due: {due_date.strftime('%B %d, %Y at %H:%M')} • {status}")
            
            if assignment.get('description'):
                st.markdown(f"<div style='color: #555; font-size: 0.9rem;'>{assignment['description']}</div>", 
                          unsafe_allow_html=True)
        
        with col2:
            if submission.get('state') == 'TURNED_IN':
                st.success("Submitted")
                if submission.get('assignedGrade'):
                    st.markdown(f"**Grade:** {submission['assignedGrade']}")
            else:
                st.warning("Not Submitted")

# ===== MAIN PAGE =====
def main():
    # Authentication check
    if not os.path.exists(TOKEN_FILE):
        st.error("Please login first")
        st.stop()
    
    try:
        with open(TOKEN_FILE, "rb") as token:
            creds = pickle.load(token)
        
        # Verify credentials are still valid
        if not creds or not creds.valid:
            st.error("Session expired, please login again")
            os.remove(TOKEN_FILE)
            st.stop()
            
    except Exception as e:
        st.error(f"Invalid session: {str(e)}")
        if os.path.exists(TOKEN_FILE):
            os.remove(TOKEN_FILE)
        st.stop()

    # Page config
    st.set_page_config(
        page_title="Student Dashboard",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Custom CSS
    st.markdown("""
    <style>
        .stApp {
            background: #f5f7fa;
        }
        .sidebar .sidebar-content {
            background: #2563eb;
            color: white;
        }
        .sidebar .sidebar-content .stButton button {
            background: white;
            color: #2563eb;
            border-radius: 8px;
            padding: 8px 16px;
            font-weight: 500;
            margin-bottom: 10px;
        }
        .stButton button {
            width: 100%;
        }
        .stMarkdown h3 {
            margin-top: 0;
        }
        [data-testid="stSidebarUserContent"] {
            padding: 1rem;
        }
    </style>
    """, unsafe_allow_html=True)

    # Get user info
    creds = get_credentials()
    if not creds:
        st.error("Failed to load credentials")
        st.stop()
        
    user_info = build("oauth2", "v2", credentials=creds).userinfo().get().execute()
    user_email = user_info["email"]

    # Initialize session state
    if 'current_course' not in st.session_state:
        st.session_state.current_course = None

    # Sidebar
    with st.sidebar:
        st.markdown(f"""
        <div style="margin-bottom: 2rem;">
            <h2 style="color: white; margin-bottom: 0.5rem;">EduFlow</h2>
            <p style="color: rgba(255,255,255,0.8); margin: 0;">{user_email}</p>
        </div>
        """, unsafe_allow_html=True)

        if st.session_state.current_course:
            if st.button("Back to All Courses"):
                st.session_state.current_course = None
                st.rerun()

        st.markdown("---")
        
        if st.button("Sign Out", key="sidebar_sign_out"):
            os.remove(TOKEN_FILE)
            st.session_state.clear()
            st.rerun()

    # Main content
    st.title("Student Dashboard")

    # Get Classroom service
    service = get_classroom_service()
    if not service:
        st.error("Failed to initialize Classroom service")
        st.stop()

    # Course detail view
    if st.session_state.current_course:
        course = st.session_state.current_course
        with st.container():
            st.markdown(f"## {course['name']}")
            st.caption(f"Section: {course.get('section', 'N/A')} • Room: {course.get('room', 'N/A')}")
            
            tab1, tab2, tab3 = st.tabs(["Announcements", "Assignments", "Course Materials"])

            with tab1:  # Announcements (keep existing implementation)
                st.subheader("Announcements")
                
                announcements = list_announcements(service, course['id'])
                if announcements:
                    for announcement in announcements:
                        update_time = datetime.strptime(
                            announcement['updateTime'], 
                            "%Y-%m-%dT%H:%M:%S.%fZ"
                        ).strftime("%B %d, %Y at %H:%M")
                        
                        with stylable_container(
                            key=f"announcement_{announcement['id']}",
                            css_styles="""
                            {
                                background: white;
                                border-radius: 10px;
                                padding: 1rem;
                                margin: 0.5rem 0;
                                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                            }
                            """
                        ):
                            st.markdown(announcement['text'])
                            st.caption(f"Posted on {update_time}")
                else:
                    st.info("No announcements yet")

            with tab2:  # Enhanced Assignments tab
                st.subheader("Your Assignments")
                
                assignments = list_assignments(service, course['id'])
                if assignments:
                    for assignment in assignments:
                        submission = get_assignment_submission(service, course['id'], assignment['id'])
                        
                        with stylable_container(
                            key=f"assignment_{assignment['id']}",
                            css_styles="""
                            {
                                background: white;
                                border-radius: 10px;
                                padding: 1.5rem;
                                margin: 1rem 0;
                                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                            }
                            """
                        ):
                            # Assignment header with status
                            col1, col2 = st.columns([3, 1])
                            with col1:
                                st.markdown(f"### {assignment.get('title', 'Untitled Assignment')}")
                            with col2:
                                if submission.get('state') == 'TURNED_IN':
                                    st.success("✅ Submitted")
                                elif datetime.now() > datetime(
                                    year=assignment['dueDate']['year'],
                                    month=assignment['dueDate']['month'],
                                    day=assignment['dueDate']['day'],
                                    hour=assignment['dueTime'].get('hours', 23),
                                    minute=assignment['dueTime'].get('minutes', 59)
                                ):
                                    st.error("⚠️ Late")
                                else:
                                    st.warning("⏳ Pending")
                            
                            # Due date and description
                            due_date = datetime(
                                year=assignment['dueDate']['year'],
                                month=assignment['dueDate']['month'],
                                day=assignment['dueDate']['day'],
                                hour=assignment['dueTime'].get('hours', 23),
                                minute=assignment['dueTime'].get('minutes', 59)
                            ).strftime("%B %d, %Y at %H:%M")
                            
                            st.caption(f"**Due:** {due_date}")
                            
                            if assignment.get('description'):
                                st.markdown("---")
                                st.markdown(assignment['description'])
                            
                            # Assignment materials
                            if assignment.get('materials'):
                                st.markdown("---")
                                st.markdown("**Attached Materials:**")
                                for material in assignment['materials']:
                                    material_type, content = get_material_details(material)
                                    if material_type and content:
                                        st.markdown(f"{material_type}: {content}")
                            
                            # Submission status details
                            st.markdown("---")
                            if submission.get('state') == 'TURNED_IN':
                                st.markdown("**Submission Status:** Turned In")
                                if submission.get('assignedGrade'):
                                    st.markdown(f"**Grade:** {submission['assignedGrade']}")
                                if submission.get('draftGrade'):
                                    st.markdown(f"**Draft Grade:** {submission['draftGrade']}")
                            else:
                                st.markdown("**Submission Status:** Not Submitted")
                            
                            # Add a submit button (would need additional implementation)
                            # if submission.get('state') != 'TURNED_IN':
                            #     if st.button("Submit Assignment", key=f"submit_{assignment['id']}"):
                            #         # Implement submission logic here
                            #         pass
                else:
                    st.info("No assignments yet")

            with tab3:  # New Course Materials tab
                st.subheader("Course Materials")
                
                materials = list_course_materials(service, course['id'])
                if materials:
                    for material in materials:
                        update_time = datetime.strptime(
                            material['updateTime'], 
                            "%Y-%m-%dT%H:%M:%SZ"
                        ).strftime("%B %d, %Y at %H:%M")
                        
                        with stylable_container(
                            key=f"material_{material['id']}",
                            css_styles="""
                            {
                                background: white;
                                border-radius: 10px;
                                padding: 1.5rem;
                                margin: 1rem 0;
                                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                            }
                            """
                        ):
                            st.markdown(f"### {material.get('title', 'Untitled Material')}")
                            st.caption(f"Posted on {update_time}")
                            
                            if material.get('description'):
                                st.markdown("---")
                                st.markdown(material['description'])
                            
                            if material.get('materials'):
                                st.markdown("---")
                                st.markdown("**Resources:**")
                                for item in material['materials']:
                                    material_type, content = get_material_details(item)
                                    if material_type and content:
                                        st.markdown(f"- {material_type}: {content}")
                else:
                    st.info("No course materials yet")


    else:
        # Course list view
        st.subheader("Your Courses")
        
        with st.spinner("Loading courses..."):
            courses = list_courses(service)
            
            if courses:
                for course in courses:
                    course_card(course)
            else:
                st.info("You are not enrolled in any courses yet")

if __name__ == "__main__":
    main()