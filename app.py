import streamlit as st
import os
from dotenv import load_dotenv
from backend.database import init_db, seed_data
from backend.agent import build_agent, chat, analyze_photo

load_dotenv()

st.set_page_config(page_title="RoadWatch AI", page_icon="🛣️", layout="centered")

init_db()
seed_data()

st.title("🛣️ RoadWatch AI")
st.caption("Monitor road quality · Track public spending · Report issues to authorities")
st.divider()

# Build agent once
if "agent" not in st.session_state:
    try:
        st.session_state.agent = build_agent()
        st.session_state.messages = []
        st.session_state.photo_damage = ""
        st.session_state.photo_response = ""
    except ValueError as e:
        st.error(str(e))
        st.info("Get your free Groq API key at https://groq.com")
        st.stop()

# --- PHOTO UPLOAD SECTION ---
st.markdown("### 📷 Report a road issue with a photo")
st.markdown("Upload a photo of a damaged road — AI will assess the damage and draft a complaint.")

col1, col2 = st.columns(2)
with col1:
    uploaded_photo = st.file_uploader("Upload road damage photo", type=["jpg", "jpeg", "png"])
with col2:
    photo_location = st.text_input("Which road / area is this?", placeholder="e.g. Jubilee Hills Road No. 36")

if uploaded_photo and photo_location:
    if st.button("🔍 Analyze & Draft Complaint", type="primary", use_container_width=True):
        with st.spinner("Analyzing photo and finding responsible officer..."):
            image_bytes = uploaded_photo.read()
            damage_description = analyze_photo(image_bytes)
            complaint = chat(st.session_state.agent, f"File a complaint about {photo_location} for this issue: {damage_description[:200]}")
            response = complaint
            st.session_state.photo_damage = damage_description
            st.session_state.photo_response = response if response else ""

if st.session_state.get("photo_damage"):
    st.success("✅ Damage assessed and complaint drafted!")
    st.markdown("**AI Damage Assessment:**")
    st.info(st.session_state.photo_damage)
    st.markdown("**Complaint & Officer Details:**")
    st.markdown(st.session_state.photo_response)
    if st.button("🗑️ Clear photo result"):
        st.session_state.photo_damage = ""
        st.session_state.photo_response = ""
        st.rerun()

st.divider()

# --- ACCOUNTABILITY SCORE SECTION ---
st.markdown("### 📊 Road Accountability Score")
st.markdown("See how well a road is maintained relative to the money spent on it.")

score_cols = st.columns([2, 1])
with score_cols[0]:
    road_options = {
        "Jubilee Hills Road No. 36": 1,
        "Banjara Hills Road No. 12": 2,
        "NH-65 Hyderabad Bypass": 3,
        "Secunderabad MG Road": 4,
        "LB Nagar Main Road": 5,
        "Kukatpally Housing Board Road": 6,
        "Gachibowli Outer Ring Road": 7,
        "Ameerpet Metro Road": 8,
        "Dilsukhnagar Main Road": 9,
        "Madhapur Hi-Tech City Road": 10,
    }
    selected_road = st.selectbox("Select a road", list(road_options.keys()))

with score_cols[1]:
    st.markdown("<br>", unsafe_allow_html=True)
    check_btn = st.button("Check Score", type="primary", use_container_width=True)

if check_btn:
    from backend.tools import get_accountability_score, get_budget
    road_id = road_options[selected_road]
    score_data = get_accountability_score(road_id)
    budget_data = get_budget(road_id)

    if score_data["found"]:
        score = score_data["accountability_score"]
        if score >= 75:
            color = "🟢"
            label = "Good"
        elif score >= 45:
            color = "🟡"
            label = "Moderate"
        else:
            color = "🔴"
            label = "Poor"

        col1, col2, col3 = st.columns(3)
        col1.metric("Accountability Score", f"{color} {score}/100", label)
        col2.metric("Road Condition", score_data["condition"])
        col3.metric("Age Since Repair", f"{score_data['age_months']} months")

        if budget_data["found"]:
            col4, col5 = st.columns(2)
            col4.metric("Budget Sanctioned", budget_data["sanctioned"])
            col5.metric("Amount Spent", budget_data["spent"],
                       f"{budget_data['utilisation_percent']}% utilised")

        st.info(f"**Verdict:** {score_data['verdict']}")
        st.caption(f"Data source: {budget_data['source'] if budget_data['found'] else 'GHMC Records'}")

st.divider()

# --- CHAT SECTION ---
st.markdown("### 💬 Ask about any road")

if len(st.session_state.messages) == 0:
    st.markdown("**Try asking:**")
    cols = st.columns(2)
    suggestions = [
        "Show me road condition in Jubilee Hills",
        "Who is responsible for Banjara Hills Road?",
        "How much was spent on NH-65?",
        "File a complaint about Secunderabad MG Road",
    ]
    for i, s in enumerate(suggestions):
        if cols[i % 2].button(s, use_container_width=True):
            st.session_state.pending = s

if st.session_state.get("pending"):
    user_input = st.session_state.pending
    st.session_state.pending = None
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.spinner("Looking up road data..."):
        response = chat(st.session_state.agent, user_input)
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.rerun()

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Ask about any road in Hyderabad..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        with st.spinner("Looking up road data..."):
            response = chat(st.session_state.agent, prompt)
        st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})