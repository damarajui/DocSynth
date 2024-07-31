import asyncio
import base64

import httpx
import streamlit as st
from tenacity import retry, stop_after_attempt, wait_exponential

st.title("DocSynth: Concise Setup Guide Generator")

urls = st.text_area("Enter documentation URLs (one per line):")
uploaded_files = st.file_uploader("Upload documentation files:", accept_multiple_files=True)
project_type = st.selectbox("Select project type:", ["Web", "Mobile", "Desktop", "API", "Other"])

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
async def generate_and_display_guide():
    try:
        urls_list = [url.strip() for url in urls.split("\n") if url.strip()]
        files_list = []

        for file in uploaded_files:
            file_content = await file.read()
            # Use base64 encoding to avoid encoding issues
            encoded_content = base64.b64encode(file_content).decode('ascii')
            files_list.append({
                "filename": file.name,
                "content": encoded_content,
                "content_type": file.type
            })

        payload = {
            "urls": urls_list,
            "files": files_list,
            "project_type": project_type
        }

        async with httpx.AsyncClient() as client:
            response = await client.post("http://localhost:8000/generate_guide", 
                                         json=payload,
                                         timeout=60.0)
            
            response.raise_for_status()
            guide = response.json()
            
            st.subheader("Setup Guide")
            st.write(guide["content"])
            st.subheader("Sources")
            for source in guide["sources"]:
                st.write(f"- {source}")
            
            # Feedback section
            st.subheader("Feedback")
            rating = st.slider("Rate this guide:", 1, 5, 3)
            comments = st.text_area("Additional comments:")
            if st.button("Submit Feedback"):
                feedback_response = await client.post("http://localhost:8000/feedback",
                                                      json={"guide_id": guide["id"], "rating": rating, "comments": comments})
                feedback_response.raise_for_status()
                st.success("Thank you for your feedback!")
    except httpx.HTTPStatusError as e:
        st.error(f"HTTP error occurred: {e.response.text}")
    except httpx.RequestError as e:
        st.error(f"An error occurred while requesting: {e}")
    except Exception as e:
        st.error(f"An unexpected error occurred: {str(e)}")

if st.button("Generate Setup Guide"):
    urls_list = [url.strip() for url in urls.split("\n") if url.strip()]
    files_list = [{"filename": file.name, "content": file.read().decode()} for file in uploaded_files]
    with st.spinner("Generating guide..."):
        asyncio.run(generate_and_display_guide())