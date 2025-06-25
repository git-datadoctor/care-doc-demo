import streamlit as st
import processing
import os
from datetime import date

st.set_page_config(page_title="AI Care Documentation", layout="wide")

# Initialize session state
if 'analysis' not in st.session_state:
    st.session_state.analysis = None

st.title("🏥 AI Care Documentation Assistant")

# Patient data section
with st.sidebar:
    st.header("Patient Profile")
    name = st.text_input("Full Name")
    dob = st.date_input("Date of Birth", value=date(1990, 1, 1))
    st.divider()
    
    st.header("AI Options")
    use_openai = st.checkbox("Enable Advanced AI", help="Uses Azure OpenAI for enhanced analysis")
    debug_mode = st.checkbox("Show Debug Info")
    
    st.divider()
    st.caption("Demo Prototype v0.1 | Not for clinical use")

# Document processing tabs
tab1, tab2 = st.tabs(["📄 Document Scanner", "✍️ Text Input"])

with tab1:
    st.subheader("Upload Medical Document")
    col1, col2 = st.columns([2, 3])
    
    with col1:
        uploaded_file = st.file_uploader(
            "Upload PDF or image", 
            type=["pdf", "png", "jpg", "jpeg"],
            accept_multiple_files=False,
            label_visibility="collapsed"
        )
        
        if uploaded_file:
            if st.button("Extract Text", type="primary"):
                with st.spinner("Processing document..."):
                    extracted_text = processing.extract_text(uploaded_file)
                    st.session_state.extracted_text = extracted_text
            
            if st.button("Analyze with AI", disabled=not uploaded_file):
                with st.spinner("Analyzing content..."):
                    if use_openai and os.getenv("OPENAI_API_KEY"):
                        st.session_state.analysis = processing.enhanced_analysis(
                            st.session_state.get('extracted_text', '')
                        )
                    else:
                        st.session_state.analysis = processing.analyze_text(
                            st.session_state.get('extracted_text', '')
                        )
    
    with col2:
        if uploaded_file and uploaded_file.type.startswith('image'):
            st.image(uploaded_file, caption="Uploaded Document", use_column_width=True)
        
        if 'extracted_text' in st.session_state:
            st.subheader("Extracted Text")
            st.text_area("", st.session_state.extracted_text, height=250, label_visibility="collapsed")

with tab2:
    notes = st.text_area("Enter care notes:", height=200, 
                         placeholder="Enter nursing notes, observations, or care documentation...")
    
    if st.button("Analyze Text", key="analyze_text", disabled=not notes):
        with st.spinner("Generating insights..."):
            if use_openai and os.getenv("OPENAI_API_KEY"):
                st.session_state.analysis = processing.enhanced_analysis(notes)
            else:
                st.session_state.analysis = processing.analyze_text(notes)

# Display analysis results
if st.session_state.analysis:
    st.divider()
    st.subheader("AI Analysis Results")
    
    if isinstance(st.session_state.analysis, dict):
        # Basic analysis results
        protocols = st.session_state.analysis.get('protocols', [])
        meds = st.session_state.analysis.get('medications', [])
        warnings = st.session_state.analysis.get('warnings', [])
        critical = st.session_state.analysis.get('critical_terms', [])
        
        col1, col2 = st.columns(2)
        
        with col1:
            if protocols:
                st.success("**Recommended Care Protocols**")
                for p in protocols:
                    st.markdown(f"- {p}")
            else:
                st.info("No specific care protocols identified")
                
            if meds:
                st.info("**Detected Medications**")
                st.write(", ".join(meds))
        
        with col2:
            if warnings:
                st.error("**Clinical Warnings**")
                for w in warnings:
                    st.markdown(f"- ⚠️ {w}")
                    
            if critical:
                st.warning("**Critical Terms Detected**")
                st.write(", ".join([c for c in critical if c]))
    else:
        # OpenAI enhanced analysis
        st.markdown(st.session_state.analysis)

# Debug info
if debug_mode:
    st.divider()
    st.subheader("Debug Information")
    st.json(st.session_state.get('analysis', {}))