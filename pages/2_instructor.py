# pages/2_instructor.py

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
    """List all courses where user is instructor"""
    results = service.courses().list(teacherId="me").execute()
    return results.get("courses", [])

def create_course(service, course_title, course_section, description, room):
    """Create a new course"""
    course = {
        "name": course_title,
        "section": course_section,
        "descriptionHeading": "Welcome to " + course_title,
        "description": description,
        "room": room,
        "ownerId": "me",
        "courseState": "PROVISIONED"
    }
    return service.courses().create(body=course).execute()

def list_announcements(service, course_id):
    """List announcements for a course"""
    results = service.courses().announcements().list(
        courseId=course_id,
        orderBy="updateTime desc"
    ).execute()
    return results.get("announcements", [])

def create_announcement(service, course_id, text, materials=None):
    """Create a new announcement"""
    announcement = {
        "text": text,
        "state": "PUBLISHED"
    }
    if materials:
        announcement["materials"] = materials
    return service.courses().announcements().create(
        courseId=course_id,
        body=announcement
    ).execute()

def list_students(service, course_id):
    """List students in a course"""
    results = service.courses().students().list(courseId=course_id).execute()
    return results.get("students", [])

# ===== UI FUNCTIONS =====
def load_lottie(url):
    """Load Lottie animation from URL or local JSON"""
    if url.startswith('http'):
        import requests
        return requests.get(url).json()
    return json.loads(url)

def course_card(course):
    """Display a course as a styled card (simplified version)"""
    with stylable_container(
        key=f"course_{course['id']}",
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
            st.markdown(f"### {course.get('name', 'Untitled Course')}")
            st.caption(f"Section: {course.get('section', 'N/A')} • Room: {course.get('room', 'N/A')}")
            if course.get('description'):
                st.markdown(f"<div style='color: #555; font-size: 0.9rem;'>{course['description']}</div>", 
                          unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"**ID:** `{course['id']}`")
            if st.button("Manage", key=f"manage_{course['id']}"):
                st.session_state.current_course = course


def enroll_student(service, course_id, student_email):
    """Enroll a student in a course"""
    student = {
        'userId': student_email
    }
    
    try:
        # Check if student is already enrolled
        existing = service.courses().students().list(
            courseId=course_id,
            userId=student_email
        ).execute()
        
        if existing.get('students'):
            return {'warning': 'Student already enrolled'}
            
        # If not enrolled, add them
        enrollment = service.courses().students().create(
            courseId=course_id,
            body=student
        ).execute()
        return {'success': f"Student {student_email} enrolled successfully"}
        
    except Exception as e:
        return {'error': str(e)}




def create_coursework(service, course_id, title, description, due_date, materials=None):
    """Create a new coursework/assignment"""
    coursework = {
        'title': title,
        'description': description,
        'workType': 'ASSIGNMENT',
        'state': 'PUBLISHED',
        'dueDate': {
            'year': due_date.year,
            'month': due_date.month,
            'day': due_date.day
        },
        'dueTime': {
            'hours': 23,
            'minutes': 59
        }
    }
    
    if materials:
        coursework['materials'] = materials
        
    return service.courses().courseWork().create(
        courseId=course_id,
        body=coursework
    ).execute()

def add_course_materials(service, course_id, title, description, materials):
    """Add materials to a course"""
    material = {
        'title': title,
        'description': description,
        'materials': materials
    }
    return service.courses().courseWorkMaterials().create(
        courseId=course_id,
        body=material
    ).execute()

def create_drive_file_material(drive_file_id):
    """Create material from Google Drive file"""
    return {
        'driveFile': {
            'driveFile': {
                'id': drive_file_id,
                'title': 'Drive File'
            },
            'shareMode': 'VIEW'  # or 'EDIT' if students should edit
        }
    }

def create_link_material(url, title):
    """Create material from external link"""
    return {
        'link': {
            'url': url,
            'title': title
        }
    }


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
    # Page config with more stable settings
    st.set_page_config(
        page_title="Instructor Dashboard",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Simplified CSS that won't cause disappearing elements
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

    # Check authentication
    if not os.path.exists(TOKEN_FILE):
        st.error("You need to login first")
        st.stop()

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
    if 'show_create_course' not in st.session_state:
        st.session_state.show_create_course = False

    # More stable sidebar implementation
    with st.sidebar:
        st.markdown(f"""
        <div style="margin-bottom: 2rem;">
            <h2 style="color: white; margin-bottom: 0.5rem;">EduFlow</h2>
            <p style="color: rgba(255,255,255,0.8); margin: 0;">{user_email}</p>
        </div>
        """, unsafe_allow_html=True)

        if st.button("Create New Course"):
            st.session_state.show_create_course = True
            st.session_state.current_course = None

        if st.session_state.current_course:
            if st.button("Back to All Courses"):
                st.session_state.current_course = None
                st.session_state.show_create_course = False

        st.markdown("---")
        
        if st.button("Sign Out", key="sidebar_sign_out"):
            os.remove(TOKEN_FILE)
            st.session_state.clear()
            st.rerun()

    # Main content with more stable rendering
    st.title("Instructor Dashboard")

    # Get Classroom service
    service = get_classroom_service()
    if not service:
        st.error("Failed to initialize Classroom service")
        st.stop()

    # Course management view - using columns for better layout stability
    if st.session_state.show_create_course:
        with st.container():
            st.subheader("Create New Course")
            with st.form("create_course_form"):
                col1, col2 = st.columns(2)
                with col1:
                    course_title = st.text_input("Course Title", placeholder="Introduction to Computer Science")
                with col2:
                    course_section = st.text_input("Section", placeholder="Fall 2023")
                
                description = st.text_area("Description", placeholder="Course objectives and overview...")
                room = st.text_input("Room", placeholder="Building A, Room 101")
                
                submitted = st.form_submit_button("Create Course")
                if submitted:
                    with st.spinner("Creating course..."):
                        try:
                            course = create_course(service, course_title, course_section, description, room)
                            st.success(f"Course created successfully! ID: {course['id']}")
                            st.session_state.show_create_course = False
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error creating course: {str(e)}")

    elif st.session_state.current_course:
        # Course detail view with more stable tabs implementation
        course = st.session_state.current_course
        with st.container():
            st.markdown(f"## {course['name']}")
            st.caption(f"Section: {course.get('section', 'N/A')} • Room: {course.get('room', 'N/A')}")
            
            tab1, tab2, tab3, tab4, tab5 = st.tabs(["Announcements", "Students", "Course Details", "Upload Materials", "Create Assignments"])
            
            with tab1:
                # Announcements section
                st.subheader("Announcements")
                
                with st.expander("Create New Announcement", expanded=False):
                    with st.form("announcement_form"):
                        announcement_text = st.text_area("Announcement Text")
                        submitted = st.form_submit_button("Post Announcement")
                        if submitted and announcement_text:
                            try:
                                create_announcement(service, course['id'], announcement_text)
                                st.success("Announcement posted!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error posting announcement: {str(e)}")
                
                announcements = list_announcements(service, course['id'])
                if announcements:
                    for announcement in announcements:
                        update_time = datetime.strptime(
                            announcement['updateTime'], 
                            "%Y-%m-%dT%H:%M:%S.%fZ"
                        ).strftime("%B %d, %Y at %H:%M")
                        
                        with st.container():
                            st.markdown(announcement['text'])
                            st.caption(f"Posted on {update_time}")
                            st.divider()
                else:
                    st.info("No announcements yet")
            
            with tab2:  # Students tab
                st.subheader("Enrolled Students")

                # 🧑‍🎓 Show list of enrolled students
                try:
                    students = list_students(service, course['id'])
                    if students:
                        for student in students:
                            profile = student.get("profile", {})
                            name = profile.get("name", {}).get("fullName", "Unknown Name")
                            email = profile.get("emailAddress", "Unknown Email")

                            st.markdown(f"- **{name}** ({email})")
                    else:
                        st.info("No students enrolled yet.")
                except Exception as e:
                    st.error(f"Failed to load students: {e}")

                # ➕ Add new student form
                with st.expander("Enroll New Student", expanded=False):
                    with st.form("enroll_student_form"):
                        student_email = st.text_input(
                            "Student Email",
                            placeholder="student@school.edu",
                            help="The email address the student uses for Classroom"
                        )   

                        if st.form_submit_button("Enroll Student"):
                            if student_email:
                                result = enroll_student(service, course['id'], student_email)
                                if 'success' in result:
                                    st.success(result['success'])
                                    st.rerun()
                                elif 'warning' in result:
                                    st.warning(result['warning'])
                                else:
                                    st.error(result['error'])

        
            with tab3:
                # Course details section
                st.subheader("Course Information")
            
                with stylable_container(
                    key="course_details",
                    css_styles="""
                    {
                    background: white;
                    border-radius: 10px;
                    padding: 1.5rem;
                    margin: 0.5rem 0;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                }
                """
                ):
                    st.markdown(f"**Course ID:** `{course['id']}`")
                    st.markdown(f"**Status:** {course.get('courseState', 'N/A')}")
                    st.markdown(f"**Created:** {datetime.strptime(course['creationTime'], '%Y-%m-%dT%H:%M:%S.%fZ').strftime('%B %d, %Y')}")
                
                    if course.get('descriptionHeading'):
                        st.markdown("---")
                        st.markdown(f"### {course['descriptionHeading']}")
                
                    if course.get('description'):
                        st.markdown(course['description'])

            with tab4:  # Upload Materials
                st.subheader("Upload Course Materials")
                
                with st.expander("Add New Materials", expanded=True):
                    with st.form("material_form"):
                        material_title = st.text_input("Material Title", placeholder="Lecture Slides Week 1")
                        material_description = st.text_area("Description", placeholder="Description of these materials")
                        
                        material_type = st.radio("Material Type", ["Google Drive File", "External Link"])
                        
                        if material_type == "Google Drive File":
                            drive_file_id = st.text_input("Google Drive File ID", 
                                                        help="The ID of the file in Google Drive (found in the file URL)")
                            materials = [create_drive_file_material(drive_file_id)] if drive_file_id else None
                        else:
                            link_url = st.text_input("URL", placeholder="https://example.com/resource")
                            link_title = st.text_input("Link Title", placeholder="Resource Title")
                            materials = [create_link_material(link_url, link_title)] if link_url and link_title else None
                        
                        submitted = st.form_submit_button("Upload Materials")
                        if submitted and materials:
                            try:
                                result = add_course_materials(service, course['id'], material_title, material_description, materials)
                                st.success("Materials uploaded successfully!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error uploading materials: {str(e)}")

            with tab5:  # Create Assignments
                st.subheader("Create Assignments")
                
                with st.expander("Create New Assignment", expanded=True):
                    with st.form("assignment_form"):
                        assignment_title = st.text_input("Assignment Title", placeholder="Homework 1")
                        assignment_description = st.text_area("Description", placeholder="Assignment instructions...")
                        due_date = st.date_input("Due Date", min_value=datetime.now().date())
                        
                        # Optional materials for assignment
                        st.markdown("**Add Materials (Optional)**")
                        drive_file_id = st.text_input("Google Drive File ID (optional)", 
                                                    help="Attach a file from Google Drive")
                        link_url = st.text_input("External URL (optional)", placeholder="https://example.com/resource")
                        link_title = st.text_input("Link Title (optional)", placeholder="Resource Title")
                        
                        materials = []
                        if drive_file_id:
                            materials.append(create_drive_file_material(drive_file_id))
                        if link_url and link_title:
                            materials.append(create_link_material(link_url, link_title))
                        
                        submitted = st.form_submit_button("Create Assignment")
                        if submitted and assignment_title:
                            try:
                                result = create_coursework(
                                    service, 
                                    course['id'], 
                                    assignment_title, 
                                    assignment_description, 
                                    due_date,
                                    materials if materials else None
                                )
                                st.success("Assignment created successfully!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error creating assignment: {str(e)}")

    else:
        # Course list view with more stable rendering
        st.subheader("Your Courses")
        
        with st.spinner("Loading courses..."):
            courses = list_courses(service)
            
            if courses:
                for course in courses:
                    with st.container():
                        course_card(course)
            else:
                st.info("You don't have any courses yet")
                if st.button("Create Your First Course"):
                    st.session_state.show_create_course = True
                    st.rerun()

if __name__ == "__main__":
    main()