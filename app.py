import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# 1. FORCED LIGHT MODE & ANIMATIONS (CSS)
st.set_page_config(page_title="Class Dinner Awards", page_icon="👑", layout="centered")

st.markdown("""
    <style>
    /* Force Light Mode Colors */
    :root { --primary-color: #FF4B4B; }
    .stApp { background-color: white; color: #31333F; }
    h1, h2, h3, p, span { color: #31333F !format !important; }
    
    /* Card Animation */
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .stImage, .stHeader { animation: fadeInUp 0.5s ease-out; }

    /* Emoji Button Styling */
    .stButton>button { 
        border-radius: 50%; 
        width: 60px !important; 
        height: 60px !important; 
        font-size: 25px !important; 
        padding: 0px !important;
        border: 1px solid #ddd !important;
        background: #f9f9f9 !important;
    }
    .stButton>button:hover { transform: scale(1.1); border: 1px solid gold !important; }
    
    /* Navigation Buttons */
    .nav-btn button { background-color: transparent !important; border: none !important; color: #888 !important; font-size: 0.9rem !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. Database Connection
url = "https://docs.google.com/spreadsheets/d/18YdQ6Od_jycVmhy-E8ZW-dWrKqzJJGF1YjeG6Z2x_qE/edit?gid=0#gid=0"
conn = st.connection("gsheets", type=GSheetsConnection)
df = conn.read(spreadsheet=url)

# Initialize Session States
if 'step' not in st.session_state: st.session_state.step = 'login'
if 'voter_name' not in st.session_state: st.session_state.voter_name = ""
if 'current_idx' not in st.session_state: st.session_state.current_idx = 0
if 'votes' not in st.session_state: st.session_state.votes = {}

# --- STEP 1: LOGIN (With Double-Vote Protection) ---
if st.session_state.step == 'login':
    st.title("🎓 Final Dinner Awards")
    st.write("Enter your ID to start ranking your classmates.")
    
    input_id = st.text_input("Student ID", placeholder="e.g. 123456")
    
    if st.button("Start Voting →"):
        # Check if they exist
        user_row = df[df['Student_ID'].astype(str) == input_id]
        
        if not user_row.empty:
            # Check for existing votes (This assumes you'll have a 'Voted' column eventually)
            # For now, we'll let them in, but we'll add the "Final Save" logic later
            st.session_state.voter_name = user_row.iloc[0]['Name']
            st.session_state.step = 'voting'
            st.rerun()
        else:
            st.error("ID not found! Please check your ID.")

# --- STEP 2: ANIMATED VOTING CARDS ---
elif st.session_state.step == 'voting':
    # Progress Bar
    total = len(df)
    st.progress(st.session_state.current_idx / total)
    
    # Header
    st.write(f"Voting as: **{st.session_state.voter_name}**")
    
    # Get current person
    person = df.iloc[st.session_state.current_idx]
    
    # Auto-skip self
    if person['Name'] == st.session_state.voter_name:
        st.session_state.current_idx = min(st.session_state.current_idx + 1, total - 1)
        st.rerun()

    # THE CARD (Animated via CSS class)
    st.markdown("---")
    placeholder_url = f"https://ui-avatars.com/api/?name={person['Name'].replace(' ', '+')}&size=400&background=random&color=fff"
    st.image(placeholder_url, width=250)
    st.header(person['Name'])
    
    # EMOJI ROW (Side-by-Side)
    st.write("Tap to Rank:")
    emoji_list = ["😶", "🙂", "😊", "😍", "👑"]
    cols = st.columns(5)
    
    for i, emoji in enumerate(emoji_list):
        if cols[i].button(emoji, key=f"e_{st.session_state.current_idx}_{i}"):
            st.session_state.votes[person['Student_ID']] = i + 1
            if st.session_state.current_idx < total - 1:
                st.session_state.current_idx += 1
            else:
                st.session_state.step = 'finish'
            st.rerun()

    # NAVIGATION ARROWS
    st.write("")
    nav_col1, nav_col2, nav_col3 = st.columns([1, 2, 1])
    with nav_col1:
        if st.session_state.current_idx > 0:
            if st.button("⬅️", key="prev"):
                st.session_state.current_idx -= 1
                st.rerun()
    with nav_col3:
        if st.session_state.current_idx < total - 1:
            if st.button("➡️", key="next"):
                st.session_state.current_idx += 1
                st.rerun()

# --- STEP 3: FINAL SUBMISSION ---
elif st.session_state.step == 'finish':
    st.balloons()
    st.title("Results Ready! 🥂")
    st.write(f"You have finished ranking all {len(st.session_state.votes)} classmates.")
    
    if st.button("🚀 SUBMIT ALL VOTES"):
        # Logic to write back to Google Sheets will go here
        st.success("Your votes are locked in. Enjoy the party!")
        st.session_state.step = 'locked'
        st.rerun()

elif st.session_state.step == 'locked':
    st.title("Submitted! ✅")
    st.info("You have already voted. You cannot vote twice!")
