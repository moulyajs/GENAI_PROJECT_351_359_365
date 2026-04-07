import os
import sys
import tempfile
import warnings
from app.input.document_handler import extract_text_from_document
# Suppress transformers and torchvision warnings during Streamlit startup
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", module="transformers.*")
warnings.filterwarnings("ignore", message=".*torchvision.*")

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import streamlit as st # type: ignore
from app.input.image_handler import extract_text_from_image_path
from app.main import run_pipeline

@st.cache_resource
def initialize_pipeline():
    with st.spinner("Initializing security pipeline... (this may take a minute on first run)"):
        from app.main import _get_rag_agent
        _get_rag_agent()
    st.success("Pipeline ready!")
    return True

def display_output(final_decision, meta_reason, answer):
    st.subheader("Output")
    st.markdown("---")
    st.write("**Final Answer:**")
    st.write(answer or "N/A")
    st.write("**Block Status:**", final_decision)
    st.write("**Reason:**", meta_reason)

def handle_text_input():
    st.header("Text Input")
    prompt = st.text_area("Enter prompt", height=180)
    submit = st.button("Submit", key="text_submit")

    if not submit:
        return

    if not prompt.strip():
        st.warning("Please enter a prompt before submitting.")
        return

    with st.spinner("Processing input and agents..."):
        try:
            final_decision, meta_reason, agent_results, answer = run_pipeline(prompt)
        except Exception as exc:
            st.error(f"Pipeline error: {exc}")
            return

    if final_decision:
        st.error("Blocked")
        display_output(final_decision, meta_reason, answer)
        return

    with st.spinner("Generating response..."):
        pass

    display_output(final_decision, meta_reason, answer)

def handle_image_input():
    st.header("Image Input")
    uploaded_file = st.file_uploader(
        "Upload an image",
        type=["png", "jpg", "jpeg"],
        accept_multiple_files=False,
    )
    submit = st.button("Submit", key="image_submit")

    if not submit:
        return

    if uploaded_file is None:
        st.warning("Please upload an image file before submitting.")
        return

    suffix = os.path.splitext(uploaded_file.name)[1].lower()
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
        tmp_file.write(uploaded_file.read())
        temp_path = tmp_file.name

    try:
        with st.spinner("Processing input and agents..."):
            image_data = extract_text_from_image_path(temp_path)

        if not image_data or not image_data.get("prompt_found"):
            st.info("No text found in image")
            return

        extracted_text = image_data["prompt_found"]
        st.subheader("Extracted Text")
        st.write(extracted_text)

        with st.spinner("Processing input and agents..."):
            try:
                final_decision, meta_reason, agent_results, answer = run_pipeline(extracted_text)
            except Exception as exc:
                st.error(f"Pipeline error: {exc}")
                return

        if final_decision:
            st.error("Blocked")
            display_output(final_decision, meta_reason, answer)
            return

        with st.spinner("Generating response..."):
            pass

        display_output(final_decision, meta_reason, answer)

    finally:
        try:
            os.unlink(temp_path)
        except Exception:
            pass
def handle_document_input():
    st.header("Document Input")

    uploaded_file = st.file_uploader(
        "Upload a document",
        type=["pdf", "docx", "txt"],
        accept_multiple_files=False,
        key="doc_uploader"
    )

    submit = st.button("Submit", key="doc_submit")

    if not submit:
        return

    if uploaded_file is None:
        st.warning("Please upload a document before submitting.")
        return

    suffix = os.path.splitext(uploaded_file.name)[1].lower()

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
        tmp_file.write(uploaded_file.read())
        temp_path = tmp_file.name

    try:
        with st.spinner("Extracting and analyzing document..."):
            doc_data = extract_text_from_document(temp_path)

        if not doc_data or not doc_data.get("has_text"):
            st.info("No readable text found in document.")
            return

        extracted_text = doc_data["prompt_found"]

        st.subheader("Extracted Text")
        st.write(extracted_text[:1000])  # limit preview

        # 🔐 Show injection detection
        if doc_data.get("injection_detected"):
            st.error("⚠️ Potential Prompt Injection Detected!")
            st.write("Detected Patterns:", doc_data["injection_detected"])

        with st.spinner("Running security pipeline..."):
            try:
                final_decision, meta_reason, agent_results, answer = run_pipeline(extracted_text)
            except Exception as exc:
                st.error(f"Pipeline error: {exc}")
                return

        if final_decision:
            st.error("Blocked")
            display_output(final_decision, meta_reason, answer)
            return

        display_output(final_decision, meta_reason, answer)

    finally:
        try:
            os.unlink(temp_path)
        except Exception:
            pass

def main():
    st.set_page_config(page_title="LLM Security Pipeline", layout="centered")
    st.title("LLM Security Pipeline")
    st.write("A minimal UI for text and image security evaluation.")

    initialize_pipeline()

    tabs = st.tabs(["Text Input", "Image Input", "Document Input"])

    with tabs[0]:
        handle_text_input()

    with tabs[1]:
        handle_image_input()

    with tabs[2]:
        handle_document_input()

if __name__ == "__main__":
    main()
