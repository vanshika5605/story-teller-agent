import streamlit as st
from story_generator import (
    categorize_request,
    generate_story,
    length_instruction,
    arc_instruction,
    category_instruction
)
from story_improviser import judge_and_improve_story, revise_story

# Page configuration
st.set_page_config(
    page_title="Bedtime Story Generator",
    page_icon="🌙",
    layout="wide"
)

# Title and description
st.title("🌙 Bedtime Story Generator")
st.markdown("Create personalized bedtime stories for children aged 5-10")

# ---------- Session State Initialization ----------
if "story_generated" not in st.session_state:
    st.session_state.story_generated = False
if "final_story" not in st.session_state:
    st.session_state.final_story = ""
if "user_request" not in st.session_state:
    st.session_state.user_request = ""
if "category" not in st.session_state:
    st.session_state.category = ""
# Store the options used for the current story (for display)
if "length_display_saved" not in st.session_state:
    st.session_state.length_display_saved = None
if "arc_display_saved" not in st.session_state:
    st.session_state.arc_display_saved = None

# ---------- Sidebar: Story Settings ----------
with st.sidebar:
    st.header("Story Settings")
    
    length_options = {
        "Short (300-500 words)": "short",
        "Medium (600-900 words)": "medium",
        "Long (1000-1300 words)": "long"
    }
    length_display = st.selectbox(
        "Story Length",
        options=list(length_options.keys()),
        index=1
    )
    length_choice = length_options[length_display]
    
    arc_options = {
        "Confidence / Overcoming Fear": "confidence_overcoming_fear",
        "Kindness & Empathy": "kindness_empathy",
        "Friendship & Cooperation": "friendship_cooperation",
        "Curiosity & Love of Learning": "curiosity_learning",
        "Calm & Relaxation for Bedtime": "calming_bedtime",
        "Responsibility & Independence": "responsibility_independence",
        "Silly, Creative Fun": "silly_creative_fun"
    }
    arc_display = st.selectbox(
        "What should the story help your child feel or learn?",
        options=list(arc_options.keys()),
        index=4
    )
    arc_choice = arc_options[arc_display]

st.markdown("---")

# ---------- Story Request Input ----------
user_request = st.text_area(
    "Describe the kind of story you want",
    placeholder="e.g., 'A story about a shy dragon who learns to be brave'",
    height=100,
    help="Describe the characters, setting, or theme you'd like in the story"
)

# ---------- Generate Story ----------
if st.button("✨ Generate Story", type="primary", use_container_width=True):
    if not user_request.strip():
        st.error("Please enter a story request!")
    else:
        # Save request for future revisions
        st.session_state.user_request = user_request

        # Step 1: Categorize request
        with st.spinner("Detecting story category..."):
            category = categorize_request(user_request)
            st.session_state.category = category

        st.info(f"📚 Detected category: **{category.replace('_', ' ').title()}**")

        # Step 2: Generate draft story
        with st.spinner("Generating your bedtime story draft..."):
            draft_story = generate_story(user_request, length_choice, arc_choice, category)

        # Step 3: Improve story
        with st.spinner("Improving the story for clarity, age-appropriateness, and bedtime tone..."):
            final_story = judge_and_improve_story(user_request, draft_story)

        # Persist in session state
        st.session_state.final_story = final_story
        st.session_state.story_generated = True
        st.session_state.length_display_saved = length_display
        st.session_state.arc_display_saved = arc_display

        st.success("Story generated successfully! ✨")

# ---------- Display Generated Story + Revision ----------
if st.session_state.story_generated and st.session_state.final_story:
    st.markdown("---")
    st.header("📖 Your Bedtime Story")
    
    # Story display with nice formatting
    st.markdown(
        f'''
        <div style="background-color: #f8f9fa; padding: 20px; border-radius: 10px; border-left: 4px solid #4CAF50;">
            <div style="font-family: Georgia, serif; font-size: 18px; line-height: 1.8; color: #333;">
                {st.session_state.final_story.replace(chr(10), "<br>")}
            </div>
        </div>
        ''',
        unsafe_allow_html=True
    )
    
    # Story info
    with st.expander("📋 Story Details"):
        col1, col2, col3 = st.columns(3)
        with col1:
            length_label = (
                st.session_state.length_display_saved.split("(")[0].strip()
                if st.session_state.length_display_saved
                else "N/A"
            )
            st.metric("Length", length_label)
        with col2:
            st.metric("Theme", st.session_state.arc_display_saved or "N/A")
        with col3:
            st.metric(
                "Category",
                st.session_state.category.replace("_", " ").title() if st.session_state.category else "N/A"
            )
    
    st.markdown("---")
    st.subheader("💬 Want to make changes?")
    
    # ---------- Revision Form (simple, no extra state, no loops) ----------
    with st.form(key="revision_form", clear_on_submit=True):
        feedback = st.text_area(
            "Describe what you'd like to change",
            placeholder="e.g., 'shorter', 'add a dog', 'less silly', 'even calmer'",
            height=80
        )
        
        col1, col2 = st.columns([1, 4])
        with col1:
            submitted = st.form_submit_button("🔄 Revise Story", use_container_width=True)
        
        if submitted:
            if feedback and feedback.strip():
                with st.spinner("Applying your feedback and revising the story..."):
                    revised_story = revise_story(
                        st.session_state.user_request,
                        st.session_state.final_story,
                        feedback.strip()
                    )
                    st.session_state.final_story = revised_story

                st.success("Story revised successfully! ✨")
                # No rerun needed: the updated story is already in session_state
            else:
                st.warning("Please enter feedback to revise the story.")
    
    # ---------- New Story button ----------
    if st.button("🆕 Generate New Story", use_container_width=True, key="new_story_btn"):
        st.session_state.story_generated = False
        st.session_state.final_story = ""
        st.session_state.user_request = ""
        st.session_state.category = ""
        st.session_state.length_display_saved = None
        st.session_state.arc_display_saved = None
    
    # ---------- Download button ----------
    st.download_button(
        label="📥 Download Story",
        data=st.session_state.final_story,
        file_name="bedtime_story.txt",
        mime="text/plain",
        use_container_width=True
    )

# ---------- Footer ----------
st.markdown("---")
st.markdown(
    '<div style="text-align: center; color: #666; padding: 20px;">'
    'Made with ❤️ for bedtime stories'
    '</div>',
    unsafe_allow_html=True
)
