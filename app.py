import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# 1. FORCE LIGHT MODE & MOBILE UI FIXES
st.set_page_config(page_title="Class Dinner Awards", page_icon="👑", layout="centered")

st.markdown("""
    <style>
    /* Force Light Mode */
    .stApp { background-color: white; color: #31333F; }
    
    /* Animation: Subtle Slide-In */
    @keyframes slideIn {
        0% { opacity: 0; transform: translateX(10px); }
        100% { opacity: 1; transform: translateX(0); }
    }
    .main-card { animation: slideIn 0.4s ease-out; }

    /* FORCE HORIZONTAL BUTTONS ON MOBILE */
    [data-testid="column"] {
        display: flex !important;
        flex-direction: row !important;
        justify-content: center !important;
        width: auto !important;
        flex: 1 1 auto !important;
    }
    
    /* Emoji Circle Style */
    .stButton>button { 
        border-radius: 50% !important; 
        width: 55px !important; 
        height: 55px !important; 
        font-size: 24px !important; 
        border: 1px solid #eee !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }

    /* Small Nav Arrows Styling */
    .nav-row button {
        background: none !important;
        border: none !important;
        font-size: 20px !important;
        color: #888 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. Connection
url = "https://docs.google.com/spreadsheets/d/18YdQ6Od_jycVmhy-E8ZW-dWrKqzJJGF1YjeG6Z2x_qE/edit?gid=0#gid=0"
conn = st.connection("gsheets", type=GSheetsConnection)
df = conn.read(spreadsheet=url)

# Session State Initialization
if 'step' not in st.session_state: st.session_state.step = 'login'
if 'voter_name' not in st.session_state: st.session_state.voter_name = ""
if 'current_idx' not in st.session_state: st.session_state.current_idx = 0
if 'votes' not in st.session_state: st.session_state.votes = {}

# --- STEP 1: LOGIN ---
if st.session_state.step == 'login':
    st.title("🎓 Final Dinner Awards")
    input_id = st.text_input("Enter Student ID to begin", placeholder="ID Number")
    if st.button("Start Voting →"):
        user_row = df[df['Student_ID'].astype(str) == input_id]
        if not user_row.empty:
            st.session_state.voter_name = user_row.iloc[0]['Name']
            st.session_state.step = 'voting'
            st.rerun()
        else:
            st.error("ID not found!")

# --- STEP 2: VOTING ---
elif st.session_state.step == 'voting':
    # Progress Calculation
    total = len(df)
    percent = int((st.session_state.current_idx / total) * 100)
    
    st.progress(st.session_state.current_idx / total)
    st.write(f"**{percent}% Complete** | Voting as: {st.session_state.voter_name}")

    person = df.iloc[st.session_state.current_idx]

    # Auto-skip self
    if person['Name'] == st.session_state.voter_name:
        st.session_state.current_idx = min(st.session_state.current_idx + 1, total - 1)
        st.rerun()

    # THE CARD CONTAINER
    with st.container():
        st.markdown('<div class="main-card">', unsafe_allow_html=True)
        
        # Photo Placeholder
        placeholder_url = f"https://ui-avatars.com/api/?name={person['Name'].replace(' ', '+')}&size=400&background=random&color=fff"
        st.image(placeholder_url, width=200)
        st.header(person['Name'])
        
        # HORIZONTAL EMOJIS (Forced row)
        st.write("Rate your classmate:")
        emoji_list = ["😶", "🙂", "😊", "😍", "👑"]
        e_cols = st.columns(5)
        for i, emoji in enumerate(emoji_list):
            if e_cols[i].button(emoji, key=f"e_{st.session_state.current_idx}_{i}"):
                st.session_state.votes[person['Student_ID']] = i + 1
                if st.session_state.current_idx < total - 1:
                    st.session_state.current_idx += 1
                else:
                    st.session_state.step = 'finish'
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)

    # HORIZONTAL NAVIGATION (Forced row)
    st.divider()
    n_cols = st.columns([1, 1, 1])
    with n_cols[0]:
        if st.session_state.current_idx > 0:
            if st.button("⬅️", key="prev"):
                st.session_state.current_idx -= 1
                st.rerun()
    with n_cols[1]:
        st.write(f"{st.session_state.current_idx + 1}/{total}")
    with n_cols[2]:
        if st.session_state.current_idx < total - 1:
            if st.button("➡️", key="next"):
                st.session_state.current_idx += 1
                st.rerun()

# --- STEP 3: FINISH ---
elif st.session_state.step == 'finish':
    st.balloons()
    st.title("Well done! 🎉")
    st.write(f"You've ranked everyone. Click below to finalize.")
    if st.button("🚀 SUBMIT FINAL RESULTS"):
        st.success("Votes recorded! See you at dinner.")
        st.session_state.step = 'locked'
