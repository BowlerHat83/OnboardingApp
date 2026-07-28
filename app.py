import streamlit as st
import os
import json
from engine.normalizer import run_full_client_audit

st.set_page_config(page_title="SEO & Digital Audit", layout="wide")

st.title("🚀 OnboardingApp Audit Engine")

domain = st.text_input("Enter Target Domain (e.g. bowlerhat.co.uk)", "bowlerhat.co.uk")

uploaded_files = st.file_uploader(
    "Upload Tool CSV Exports (Screaming Frog, SEMrush, SpyFu, BrightLocal, Waikay)",
    accept_multiple_files=True,
    type=["csv"]
)

if st.button("Run Audit"):
    if not domain:
        st.error("Please enter a domain name.")
    else:
        # Save uploaded files temporarily to input_csvs/
        os.makedirs("input_csvs", exist_ok=True)
        # Clear existing temporary files
        for f in os.listdir("input_csvs"):
            os.remove(os.path.join("input_csvs", f))
            
        for file in uploaded_files:
            with open(os.path.join("input_csvs", file.name), "wb") as f:
                f.write(file.getbuffer())

        with st.spinner("Processing audit & running pings..."):
            audit_result = run_full_client_audit(domain, csv_dir="input_csvs")

        st.success(f"Audit Complete! Overall Score: {audit_result.overall_score}/100")
        
        # Display high-level metrics
        col1, col2, col3 = st.columns(3)
        col1.metric("Overall Score", f"{audit_result.overall_score}/100")
        col2.metric("Technical SEO", f"{audit_result.technical_seo.score}/100")
        col3.metric("AI Readiness", f"{audit_result.ai_readiness.score}/100")

        st.json(audit_result.model_dump())
