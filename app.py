import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# 1. Page Setup
st.set_page_config(page_title="Class Dinner Awards", page_icon="👑", layout="centered")

# Custom CSS to make it look like a "Card" app
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 12px; height: 3.5em; font-size: 1.2rem; transition: 0.3s; }
    .stButton>button:hover { background-color: #FFD700; color: black; border: 1px solid gold; }
    .stProgress > div > div > div > div { background-color: #FF4B4B; }
    .main { background-color: #f8f9fa; }
    div[data-testid="stVerticalBlock"] > div:has(div.stImage) { 
        background: white; padding: 20px; border-radius: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    </style>
    """, unsafe_allow_html=True)

# 2. Connection (Change the URL to your sheet)
url = "https://docs.google.com/spreadsheets/d/18YdQ6Od_jycVmhy-E8ZW-dWrKqzJJGF1YjeG6Z2x_qE/edit?gid=0#gid=0"
conn = st.connection("gsheets", type=GSheetsConnection)
df = conn.read(spreadsheet=url)

# Initialize Session States
if 'step' not in st.session_state: st.session_state.step = 'login'
if 'voter_name' not in st.session_state: st.session_state.voter_name = ""
if 'current_idx' not in st.session_state: st.session_state.current_idx = 0
if 'votes' not in st.session_state: st.session_state.votes = {}

# --- STEP 1: LOGIN ---
if st.session_state.step == 'login':
    st.title("🎓 Final Dinner Awards")
    st.write("### Identify yourself to begin voting!")
    
    input_id = st.text_input("Enter your Student ID", placeholder="e.g. 123456")
    
    if st.button("Start Voting →"):
        user_row = df[df['Student_ID'].astype(str) == input_id]
        if not user_row.empty:
            st.session_state.voter_name = user_row.iloc[0]['Name']
            st.session_state.step = 'voting'
            st.rerun()
        else:
            st.error("Student ID not found in the list!")

# --- STEP 2: INDIVIDUAL VOTING CARDS ---
elif st.session_state.step == 'voting':
    # Progress Bar at the top
    total_people = len(df)
    progress_val = (st.session_state.current_idx) / total_people
    st.progress(progress_val)
    st.write(f"Classmate {st.session_state.current_idx + 1} of {total_people}")

    # Personalized Greeting
    st.markdown(f"### Hey **{st.session_state.voter_name}**! ✨")
    st.write("Rank your friend below:")
    
    # Get current person data
    person = df.iloc[st.session_state.current_idx]
    
    # Skip yourself automatically
    if person['Name'] == st.session_state.voter_name:
        if st.session_state.current_idx < total_people - 1:
            st.session_state.current_idx += 1
            st.rerun()
        else:
            st.session_state.step = 'finish'
            st.rerun()

    # THE CARD UI
    with st.container():
        col1, col2 = st.columns([1.2, 2])
        
        with col1:
            # Placeholder Image for Testing
            # This generates a 300x300 grey box with the person's name on it
            placeholder_url = f"https://ui-avatars.com/api/?name={person['Name'].replace(' ', '+')}&size=300&background=random"
            st.image(placeholder_url, use_container_width=True)
            
        with col2:
            st.header(person['Name'])
            st.caption(f"ID: {person['Student_ID']}")
            st.write("---")
            
            # Emoji Rating Logic
            emojis = ["😶", "🙂", "😊", "😍", "👑"]
            labels = ["Neutral", "Nice", "Great", "Awesome", "The GOAT"]
            
            for i, (emoji, label) in enumerate(zip(emojis, labels)):
                if st.button(f"{emoji} {label}", key=f"v_{st.session_state.current_idx}_{i}"):
                    # Save vote and move to next
                    st.session_state.votes[person['Student_ID']] = i + 1
                    if st.session_state.current_idx < total_people - 1:
                        st.session_state.current_idx += 1
                    else:
                        st.session_state.step = 'finish'
                    st.rerun()

    # Bottom Navigation
    st.write("")
    nav_prev, nav_next = st.columns(2)
    with nav_prev:
        if st.session_state.current_idx > 0:
            if st.button("← Previous"):
                st.session_state.current_idx -= 1
                st.rerun()

# --- STEP 3: SUMMARY & SUBMIT ---
elif st.session_state.step == 'finish':
    st.balloons()
    st.title("Checkmate! 🏁")
    st.write(f"Great job, **{st.session_state.voter_name}**. You've ranked everyone.")
    
    st.info(f"Total votes cast: {len(st.session_state.votes)}")
    
    if st.button("🚀 Submit Final Results"):
        # This is where we'll add the Google Sheet "Write" logic in the next step
        st.success("Results submitted! See you at the dinner!")
