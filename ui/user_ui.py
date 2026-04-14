import streamlit as st
import streamlit.components.v1 as components
import base64
import datetime
import json
import os
from config import UPLOAD_DIR
from services.parser_service import parser_service
from services.model_service import model_service
from services.recommendation import get_course_recommendations, get_random_support_videos
from services.db_service import insert_data

def section_card(title, icon, subtitle=""):
    st.markdown(f"""
    <div class='section-card'>
      <div class='section-heading'>{icon} {title}</div>
      <p class='section-description'>{subtitle}</p>
    </div>
    """, unsafe_allow_html=True)

def show_pdf(file_path):
    """Renders a PDF preview using base64 via st.components to avoid Chrome iframe blocking."""
    with open(file_path, "rb") as f:
        pdf_bytes = f.read()
        base64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')

    # st.components.v1.html renders in a sandboxed iframe Chrome doesn't block
    pdf_html = f"""
    <style>
        body {{ margin: 0; padding: 0; }}
        iframe {{ border: none; border-radius: 8px; }}
    </style>
    <iframe
        src="data:application/pdf;base64,{base64_pdf}"
        width="100%"
        height="600px"
        type="application/pdf"
    ></iframe>
    """
    components.html(pdf_html, height=620, scrolling=False)

    # Fallback download button in case browser blocks PDF preview
    st.download_button(
        label="📥 Download Resume (if preview is not visible)",
        data=pdf_bytes,
        file_name=os.path.basename(file_path),
        mime="application/pdf",
    )

def render_skill_badges(skills):
    if not skills:
        st.markdown("<span class='empty-state'>No skills extracted</span>", unsafe_allow_html=True)
        return
        
    badges = "".join(f"<span class='skill-badge'>{skill}</span>" for skill in skills)
    st.markdown(f"<div class='skill-badge-container'>{badges}</div>", unsafe_allow_html=True)

def render_score_block(score, category):
    color_class = category.lower()
    st.markdown(f"""
    <div class='score-block-container'>
        <span class='score-indicator {color_class}'></span>
        <span class='score-text {color_class}'>Resume Strength: {category}</span>
    </div>
    """, unsafe_allow_html=True)

def course_recommender(course_list):
    st.subheader("Courses 🎓")
    rec_course_names = []
    for i, (c_name, c_link) in enumerate(course_list, 1):
        st.markdown(f"{i}. [{c_name}]({c_link})")
        rec_course_names.append(c_name)
    return rec_course_names

def user_page(cursor, connection, debug_mode):
    section_card("Resume Upload", "📄", "Upload a PDF resume to begin the analysis.")
    pdf_file = st.file_uploader("Upload Resume", type=["pdf"], label_visibility="collapsed")

    if pdf_file:
        path = os.path.join(UPLOAD_DIR, pdf_file.name)
        with open(path, "wb") as f:
            f.write(pdf_file.getbuffer())

        st.markdown("""
        <div class='dashboard-card'>
            <div class='resume-card-title'>📄 Resume preview</div>
        """, unsafe_allow_html=True)
        show_pdf(path)
        st.markdown("</div>", unsafe_allow_html=True)

        # Parsing Flow
        resume_text = parser_service.pdf_reader(path)
        resume_data = parser_service.parse_resume(resume_text)

        # Experience Level Estimation
        if resume_data['no_of_pages'] == 1:
            cand_level = "Fresher"
        elif resume_data['no_of_pages'] == 2:
            cand_level = "Intermediate"
        else:
            cand_level = "Experienced"

        # Model Inference
        predicted_role, confidence = model_service.predict_role(resume_text)
        confidence_pct = confidence * 100
        score, score_category = model_service.calculate_smart_score(resume_text, resume_data['skills'])

        left_col, right_col = st.columns([2, 1], gap="large")
        
        with left_col:
            section_card("Extracted Details", "🧠", "Core resume fields and candidate information.")
            st.markdown(f"""
            <div class='details-box'>
                <strong>Email:</strong> {resume_data['email'] or 'N/A'}<br>
                <strong>Phone:</strong> {resume_data['mobile_number'] or 'N/A'}<br>
                <strong>Pages:</strong> {resume_data['no_of_pages']}<br>
                <strong>Experience Level:</strong> {cand_level}
            </div>
            """, unsafe_allow_html=True)

            section_card("Suggestions", "🚀", "Actionable resume improvements based on your score.")
            feedback = model_service.generate_resume_feedback(resume_text, resume_data['skills'], score)
            if feedback:
                for suggestion in feedback:
                    st.markdown(f"- {suggestion}")
            else:
                st.markdown("<span class='empty-state'>No suggestions available at this time.</span>", unsafe_allow_html=True)

            missing = model_service.find_missing_skills(resume_data['skills'], predicted_role)
            section_card("Skill Gaps", "📊", "Core missing skills for the predicted role.")
            if missing:
                for skill in missing:
                    st.markdown(f"- {skill}")
            else:
                st.markdown("<span class='empty-state'>No core missing skills detected.</span>", unsafe_allow_html=True)

        with right_col:
            section_card("Extracted Skills", "📊", "Skills identified from the uploaded resume.")
            render_skill_badges(resume_data['skills'])
            st.markdown("<br>", unsafe_allow_html=True)

            section_card("Predictions", "🚀", "Resume prediction and confidence metrics.")
            st.markdown(f"""
            <div class='predictions-panel'>
                <div class='prediction-row'>
                    <span class='prediction-label'>Predicted Role</span>
                    <strong class='prediction-value-role'>{predicted_role}</strong>
                </div>
                <div class='prediction-row'>
                    <span class='prediction-label'>Confidence</span>
                    <strong class='prediction-value-confidence'>{confidence_pct:.0f}%</strong>
                </div>
            </div>
            """, unsafe_allow_html=True)
            st.progress(min(max(int(confidence_pct), 0), 100))
            st.markdown("<br>", unsafe_allow_html=True)

            section_card("Score", "📈", "Resume score and overall strength.")
            # st.markdown("<div class='dashboard-card'>", unsafe_allow_html=True)
            st.metric("Resume Score", f"{score:.0f}%")
            
            # Convert and render native streamit progress bar
            resume_score = float(score)
            st.write("Score value:", resume_score)
            
            # Use float mapped 0.0 to 1.0 per Streamlit requirement and constrain it
            st.progress(min(max(resume_score / 100.0, 0.0), 1.0))
            
            render_score_block(score, score_category)
            st.markdown("</div>", unsafe_allow_html=True)

            if debug_mode:
                st.markdown("<br>", unsafe_allow_html=True)
                with st.expander("Debug Info", expanded=True):
                    st.markdown("**Extracted raw text (first 500 chars):**")
                    st.code(resume_text[:500].strip() or "(no text extracted)")
                    st.markdown("**Detected skills:**")
                    st.write(resume_data['skills'] or [])
                    st.markdown("**Predicted role:**")
                    st.write(predicted_role)
                    st.markdown("**Similarity score:**")
                    st.write(f"{confidence:.4f}")

        # Courses & Videos
        recommended_skills, course_list = get_course_recommendations(predicted_role, resume_data['skills'])
        rec_course_names = course_recommender(course_list)

        # Database Save Sequence
        if connection and cursor:
            saved_ok = insert_data(cursor, connection, (
                "User",
                resume_data['email'],
                float(score),
                datetime.datetime.now(),
                int(resume_data['no_of_pages']),
                predicted_role,
                float(confidence),
                score_category,
                cand_level,
                json.dumps(resume_data['skills']),
                json.dumps(recommended_skills),
                json.dumps(rec_course_names)
            ))
            if not saved_ok and debug_mode:
                st.warning("Resume data could not be saved to PostgreSQL.")

        st.markdown("---")
        st.subheader("Learning & Interview Support")
        res_vid, int_vid = get_random_support_videos()
        if res_vid:
            st.video(res_vid)
        if int_vid:
            st.video(int_vid)
