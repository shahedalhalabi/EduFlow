import streamlit as st
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
import os
import pickle
import base64
from streamlit_lottie import st_lottie
import json
from streamlit_extras.stylable_container import stylable_container

# ===== BACKEND CODE =====
CLIENT_SECRETS_FILE = "credentials.json"
SCOPES = [
    'https://www.googleapis.com/auth/classroom.courses',
    'https://www.googleapis.com/auth/userinfo.email', 
    'openid',

    'https://www.googleapis.com/auth/classroom.coursework.me',
    'https://www.googleapis.com/auth/classroom.coursework.students',
    'https://www.googleapis.com/auth/classroom.announcements',
    'https://www.googleapis.com/auth/classroom.rosters',
    'https://www.googleapis.com/auth/classroom.profile.emails',

    'https://www.googleapis.com/auth/classroom.courseworkmaterials',
    'https://www.googleapis.com/auth/classroom.coursework.students',
    'https://www.googleapis.com/auth/drive.readonly'
]
TOKEN_FILE = "token.json"

def is_authenticated():
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "rb") as token:
            creds = pickle.load(token)
            return creds and creds.valid
    return False

def authenticate():
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, 
        scopes=SCOPES, 
        redirect_uri="urn:ietf:wg:oauth:2.0:oob"
    )
    auth_url, _ = flow.authorization_url(prompt="consent")
    return auth_url

def fetch_token(auth_code):
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, 
        scopes=SCOPES, 
        redirect_uri="urn:ietf:wg:oauth:2.0:oob"
    )
    flow.fetch_token(code=auth_code)
    return flow.credentials

def detect_user_role(creds):
    try:
        classroom = build("classroom", "v1", credentials=creds)
        results = classroom.courses().list(teacherId="me").execute()
        return "teacher" if results.get('courses') else "student"
    except Exception:
        return "student"

# ===== UI ENHANCEMENTS =====
def load_lottie(url):
    """Load Lottie animation from URL"""
    if url.startswith('http'):
        import requests
        return requests.get(url).json()
    return json.loads(url)

# Embedded Lottie animation (fallback if no internet)
ANIMATION = {
    "v": "5.9.0",
    "fr": 60,
    "ip": 0,
    "op": 60,
    "w": 400,
    "h": 400,
    "nm": "Education",
    "assets": [],
    "layers": [{
        "ddd": 0,
        "ind": 1,
        "ty": 4,
        "nm": "Layer 1",
        "sr": 1,
        "ks": {"o": {"a": 0, "k": 100}, "r": {"a": 0, "k": 0}, "p": {"a": 0, "k": [200,200,0]}, "a": {"a": 0, "k": [0,0,0]}, "s": {"a": 0, "k": [100,100,100]}},
        "shapes": [{
            "ty": "gr",
            "it": [{
                "ty": "rc",
                "d": 1,
                "s": {"a": 0, "k": [300,300]},
                "p": {"a": 0, "k": [0,0]},
                "r": {"a": 0, "k": 0},
                "nm": "Rectangle",
                "mn": "ADBE Vector Shape - Rect",
                "hd": False
            }, {
                "ty": "fl",
                "c": {"a": 0, "k": [0.482,0.843,0.929,1]},
                "o": {"a": 0, "k": 100},
                "r": 1,
                "nm": "Fill 1",
                "mn": "ADBE Vector Graphic - Fill",
                "hd": False
            }],
            "nm": "Background",
            "np": 2,
            "mn": "ADBE Vector Group",
            "hd": False
        }]
    }]
}

# ===== STREAMLIT UI =====
def main():
    # Page config
    st.set_page_config(
        page_title="EduFlow Login",
        layout="centered"
    )

    # Custom CSS
    st.markdown("""
    <style>
        .stApp {
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        }
        .login-card {
            background: rgba(255,255,255,0.95);
            border-radius: 15px;
            padding: 2rem;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.2);
        }
        .google-btn {
            background: white !important;
            color: #5f6368 !important;
            border: 1px solid #dadce0 !important;
            border-radius: 8px !important;
            padding: 10px 24px !important;
            font-weight: 500 !important;
            transition: all 0.3s !important;
        }
        .google-btn:hover {
            box-shadow: 0 2px 6px rgba(0,0,0,0.2) !important;
        }
        .role-btn {
            width: 100%;
            padding: 1rem;
            margin: 0.5rem 0;
            font-size: 1.1rem;
        }
    </style>
    """, unsafe_allow_html=True)

    # Animation at top
    try:
        st_lottie(load_lottie("https://assets1.lottiefiles.com/packages/lf20_ktwnwv5m.json"), 
                 height=200, key="login-anim")
    except Exception:
        st_lottie(ANIMATION, height=200, key="login-fallback")

    # Login card
    with stylable_container(
        key="login_container",
        css_styles="""
        {
            padding: 2rem;
        }
        """
    ):
        # Header
        st.markdown("""
        <div style="text-align: center; margin-bottom: 1.5rem;">
            <h1 style="display: inline-block; vertical-align: middle; color: #2563eb;">
                EduFlow Login
            </h1>
        </div>
        """, unsafe_allow_html=True)

        if not is_authenticated():
            # Google auth section
            auth_url = authenticate()
            st.markdown(f"""
            <div style="text-align: center; margin: 2rem 0;">
                <a href="{auth_url}" target="_blank">
                    <button class="google-btn">
                        <img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAOEAAADhCAMAAAAJbSJIAAABU1BMVEX////qQzU0qFNChfT7vAUufPPg6P07gvSCqvc1f/SxyPr7uQD7uAD/vQDqQTMopUv61NLpMR7pOirpNiUlpEnpMyHqPS78wgDpLBYToUAnpUr629npODe73sNDg/zsW1D2trL946n93Znx+fMzqkT98O/3xcLznJf0qqXzo57+9fT74+HwhH33v7vH2Pvi8eYYp1Zft3Se0arH5M5PsWhsvH/ubGPudGzrTkHxjYftX1X/+Oj80nH//vn95bL8zmT8yU/+89r7xDf92Yr94J9jrEjGtiVZkvWAxJDW69tArFzz9/6b0KihvvnvfnboIAD4uHXsUTHwcCj0jx74qhHuYS3ygiL2nhfweEBunvaTtPj+7MO90fv7wSuPuVzhuReErz7YuByuszB6rkKVsDnU4fxmrEdMqk3NynU9kMg6mp83onQ/jNg8lbM4nog1pWRAieNPNOw1AAAKuElEQVR4nO2caXfbxhVAIYiSLEsEhIUQQJUhG0oiKVJmuEmkZCVxncakRKtJmzaJna2Lu2Rr//+nYuEGEjOYGWBmQB7cjz7HBK7fm3lvFlgQUlJSUlJSUlJi4qx+dF6q1ioetWrp8uikzvulYuGifl5rXG2ZpqLkNE2domm5nGKaavGxUjo64/2SxJyUGkXVzKmGIW0FI0mGqilK/6p2vnaaR5UrU9EMCeTmFzXUnCk1LtfGsl66VhXVQHHzaWpmf3DE++XDqdeKTuww9aaW9r9M45y3AoyzatFUCe3mklpiI3l+ndOi6c0k+9UL3jYrnNVUhTQ5AyQ18/GEt5KPekOLJXwLGOZNckbkybUZX/gWHJV+MhxPrkzcyoCKpBT5O9avFVp+nuMN34n1bEAtflMM85pjr1PVVMp+rqNS4eR31M9RmF8CkLQtHql60TDZ+LmOZoN5C3BusEjQOarBeFZ9ZBhAD8kcMPQ72mIbQA+tz2zfo8I8gB6SWWLid3GV4+LnKjYYCJ4YtGs8DK1IvfyXOGXoFEOlvKoaKHwFnU71kqYgvyG4oGjWqPldFHkUiVUUWpXxbIvnHLOA9Ac6Y7EuJUVQodOH1xktJEKRTEqCce80kUItgokRTCNIxtnWhgsK/aTMopRSVLhJiiCtCF5rvNU8qEWwkoBe1IFaBC9N3moe1CJY57wenEJNUIitTjj3LlTNQ1UR7zDM/zatFBWu41gvSYamKFr/elCplhyqlcFjUbX/SEU9lKMXwaoS2U7NKcVG0LWgi5PLyo2qoJz704tgPeIsI6mKNIBeBro4qhVNLaTe0oug0I8yCCVD6VdQlqpnpRtoJOlFUBhEKPXOXQP0F6tXJODyk6LgEXmOSppawzwsuuwHb+NRTFHyHJW0rRLB886LAY4UIyhUSHNUzVUJH1kyltehNCNIOo8akfb6Kv57DzQjSLhkknI30Xb66sWFRp+q4CVRrTcU0gSdU5t1wjRTlLAf1YpxnGGeTHaeqUZQqBFMM7GdQ19cadQjeEGwZorzUGhgUo6gMMBfUhhGnIcJVZNqBIU6/imhWoz3wssl3TtCn2GHUL2i+kJxc5s5/Pw3WILaegkKzw8yx3/EUdSueb8yHreHmUzm+E/oimuWooLw8iDjKH6BKmgUeb8xJncZj+ODPyOFUdpK3pcDcH57kJk6/gVBUcqt3Vd232ZmHH8Zbmjyv2uOyYvDzIJiaNnI8bqhTM7zg8wiIWXDWLdp1J5n/IIhZUPKrdssszjPzBQhZUNZu0EoCB8vCzqAyobxyPt18bk9DDIElA1JW78cFT5ZSVJI2ciVeL8uAb8LFAwuG9K6dWsOwUkKKBt0txko8WFwknqKS2VjDUuhzUcQQ6dsLDqayfqMFRGIn8tC2VjPEL4AD8NJGOdlg+5eGC3ehyWppzgtG8YN75clIrChWVKclI0c1W8CqBEaQtfRKRuSyvtdiQgdhhNFu2yoLD+Vi4/VdQVA8Ys1LRXLi18YX/F+VzJATekqBy+JH/KwS5kH8LPvws2mHL4gNny6Q5mvwc+GtN0rEAsKT/e3KQN+9ltkw4PnCTbcAT87vKOZGX6YZMNd4LPRp9LD2wQb7j8DPhuhZ5tCLsjA8Cnw2cfISfpRkg333gCfjT7RvJ9oQ2C5QC8Wh28TbfgK9GjEvjsTbaJhUA+BBRG9HGbuEm24B+rb3iIXi28jCDIw3AcZoq6dMpmPk20ILPnILU2kYsHT8CWyIfnSiY3hu8iGUcohi3EIats2x/CbyIafpIacDUGtd2o4N0z6OEwNww0TXg+BhoBLCgGGCe9pgIYb05cCq8XmrC2AhpuyPgR2bRuzxgd23puyTwPZEt6QvTaI4Ybsl4J3MTZlzxu8E7Up5xaQ47UNOXvaBu4Ib8r5IXhXf1POgCEnM4zO8TmerrG5i8HzhBR9Ms1mviM33NkjAtkQcsqNvH7Kfi9aTVLDZ0/IQDeEXKhB7L2zf/tAlMekhoQ87CArwn4GJYbZ7A8fiDas1CY8Qx2+kGIhIPVt2e//5QrqHVZuHm9QB+I+uFgIKF1N9lPXz6bFys0DOUeBK3yXsIGYzf5jKihaI1ZyDujDEDaVCmF39bOZ388ERbnHSM4Fo4rCfwj6vUX2r+Ii5AWDgFeowxA+0cC/mXGKxCIsg7iLnKT7r+G/BG6+s9m/+wWZjsTXyEm6A+nZXECt6bRI+OgysXNA9YN3NC6Arf15kfAFscBETxC+QU5S8IWoKYFpulgk/EORhZ6AMc+EDkMhsK3xFQm/4ZCBnt2xofekwN3gOavri6Ui4c9TJr0begi398J/beV7/OUiwT5Pn6KHcO8Jwu/5l8EBRcJvyKAookcwpCmd4OtNA4uEP0/btAWfYBiG1gqXhf/bJPspXM9VpFz336HnaGjLNmE21wCLxFKilqkaovshJul8UzGb+SeKIOXW5muMHIWcyfjxLmXAisRSECkuhl9j5CjaTOrg9jXwIuFHpzahYtT6baRyP+H5wXS7CVWRUm+DvmjyQP7h28PQIsFEcRdnDCL1pDP+LWP5iXQS9QFjo9sBrRh6NC1cQ1GPfbrZxRREnmdchthBFOX7ePdt3u3jCYZtsi1Rxg+iKOfjXGigL3qnIUTrZ2aM8YNoN3DxHWa8wRUM36BZ4o5A0BmM8XRwD6+wDxnDty+WKegkirIcx9bNsx3MIUgQQpsuURRFqxc1jOWW9Z/36IdQEEYEk40bRj3airGty+Lpj7iKBCEkqhgeukieqgXRHR2nP21jJSruRDqBUNBxvCdzLHSno18Wf8YJI14tnNEhzFNSx/b94ux2+gu6Il47s8AwT64o6vIYp8kZDfWl2fv0V+S2DXxXL4z7CIZ2plndNprkaHxvrY76/H//hxbGHcgdobAnR8hTF93qjkfwW+HNwlAO0HP/iU6RygZJpZgxJqr7/te05Na4EBjLZqfdu7d0yJyNVDYIp5kJLdKS4ZOUdcsSe8Nxu9BxKBTa42HLDrAuh/08QtnAWfgGUI5BcEF0ihyqNvtLYWUjUo46RB6KkQkpG9Fy1KHAX/FXSKZGmEdnDKPPNhGBlI190lrvoxfHbBMNUNnYQ99AhNJNgGJw2diPPAg9ymICFH8KOAkmWjMBFPkTUDZ2olVCH03us424WjbimWWSpegrG4SrXiCjJCgulo3IvcwKiYjivGzsvSJeE4IVkXtJmpz+6O72723HL5iMojEpG3QEbcUElH5nifLzexRSdEIrGYPxF2qCdhvOfaXhnI5E+Vo+FP6LKYv2hcgR5ymV/jUzocxzMMpsvtUZc8vUfMxH6UBGnCoj9SE4567HIYwys5vzLh3mE47epXsJcoUy29IY9eCViNE9u0nVarH8ympOO88mVaOcKkfETlX6jnKM93QIaPYoO8rWkPEMs8KoRdFRtnpMv1UFMKIVx4T4OTRXTuFjQNeHfCbQYMptGXaYi41siW3e42+FTi+2QOp6j/H3/oiU210ryg2ViZ7VTV745jRtyQjpKus66hUVjjQLPZkklLJuicNCgqPnYzRuWTixtO3yveA7KQlmVBh2ZUuH9q6ynNct/b437qxL7JYpNzvtYUu07IDa5GWPvHPvxP4zS2wNx4XRusr5KDdHnUK7PZ7QLhQ6o+ZGmKWkpKSkpKQkgv8Dfs6yxW4kgvwAAAAASUVORK5CYII=" 
                             width="20" style="vertical-align: middle; margin-right: 10px;">
                        Continue with Google
                    </button>
                </a>
            </div>
            """, unsafe_allow_html=True)

            # Auth code input
            with stylable_container(
                key="auth_code_box",
                css_styles="""
                {
                    background: rgba(37, 99, 235, 0.05);
                    border-radius: 10px;
                    padding: 1.5rem;
                }
                """
            ):
                auth_code = st.text_input(
                    "Paste authorization code:", 
                    placeholder="Paste code from Google here...",
                    help="You'll get this after clicking the Google button",
                    key="auth_code_input"
                )

                if auth_code:
                    with st.spinner("Authenticating..."):
                        try:
                            creds = fetch_token(auth_code)
                            with open(TOKEN_FILE, "wb") as token:
                                pickle.dump(creds, token)
                            st.success("✅ Login successful!")
                            st.balloons()
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Error: {str(e)}")

        else:  # Authenticated view
            with open(TOKEN_FILE, "rb") as token:
                creds = pickle.load(token)
            
            user_info = build("oauth2", "v2", credentials=creds).userinfo().get().execute()
            user_email = user_info["email"]
            
            # Check if user needs to select role
            if 'user_role' not in st.session_state:
                st.markdown(f"""
                <div style="text-align: center; margin: 2rem 0;">
                    <h2 style="color: #2563eb;">Welcome to EduFlow!</h2>
                    <p style="color: #555;">{user_email}</p>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("### Please select your role:")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button(
                        "🎓 I'm a Student", 
                        use_container_width=True,
                        key="student_role_select_btn",
                        help="Select if you're here to learn"
                    ):
                        st.session_state.user_role = "student"
                        st.rerun()
                
                with col2:
                    if st.button(
                        "👨‍🏫 I'm an Instructor", 
                        use_container_width=True,
                        key="instructor_role_select_btn",
                        help="Select if you're here to teach"
                    ):
                        st.session_state.user_role = "instructor"
                        st.rerun()
                
                # Animation for role selection
                try:
                    st_lottie(
                        load_lottie("https://assets10.lottiefiles.com/packages/lf20_yo4yzvar.json"), 
                        height=250, 
                        key="role-select-anim"
                    )
                except Exception:
                    pass
                
                st.stop()  # Don't proceed until role is selected
            
            # Show welcome message with role
            user_role = st.session_state.user_role
            st.markdown(f"""
            <div style="text-align: center; margin: 2rem 0;">
                <h2 style="color: #2563eb;">Welcome, {user_role.capitalize()}!</h2>
                <p style="color: #555;">{user_email}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Dashboard animation
            try:
                st_lottie(
                    load_lottie("https://assets1.lottiefiles.com/packages/lf20_2cwDXD.json"), 
                    height=200, 
                    key="dashboard-anim"
                )
            except Exception:
                pass
            
            # Action buttons - MODIFIED SECTION FOR VERTICAL ALIGNMENT
            st.markdown("""
            <style>
                .stButton>button {
                    height: 3rem;
                    min-width: 100%;
                }
                .button-container {
                    display: flex;
                    flex-direction: column;
                    gap: 1rem;
                    align-items: center;
                }
            </style>
            """, unsafe_allow_html=True)
            
            with stylable_container(
                key="button_container",
                css_styles="""
                {
                    display: flex;
                    flex-direction: column;
                    gap: 1rem;
                    align-items: center;
                    width: 100%;
                }
                """
            ):
                if st.button(
                    "Go to Dashboard", 
                    type="primary",
                    key="go_to_dashboard_btn",
                    use_container_width=True
                ):
                    if st.session_state.user_role == "instructor":
                        target_page = os.path.join(os.path.dirname(__file__), "2_instructor.py")
                    else:
                        target_page = os.path.join(os.path.dirname(__file__), "3_student.py")
        
                    st.switch_page(target_page)
                
                if st.button(
                    "Sign Out",
                    key="sign_out_btn",
                    use_container_width=True
                ):
                    os.remove(TOKEN_FILE)
                    st.session_state.clear()
                    st.rerun()
if __name__ == "__main__":
    main()