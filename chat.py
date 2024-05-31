#streamlit run chat.py

import streamlit as st
from pypdf import PdfReader, PdfWriter
from langchain_community.llms import Ollama


class Chatbot():
    def __init__(self) -> None:
        # Load the Ollama model (replace "aya:latest" with your desired model)
        self.llm = Ollama(model="llava:13b")
        st.title("Flexible Q&A with llava:13b (Text or PDF)")
        self.textpage = ""
        self.prompt = ""
        


    def _uploaded_file(self):
        if self.uploaded_file:
            file_details = {"filename": self.uploaded_file.name, "filetype":self.uploaded_file.type,
            "filesize":self.uploaded_file.size}
            st.write(file_details)
            if self.uploaded_file.type == "application/pdf":
                reader = PdfReader(self.uploaded_file)
                pagecount = len(reader.pages)
                for page in range(pagecount):
                    getpage = reader.pages[page]
                    self.textpage = getpage.extract_text()
                    # st.write(textpage)

    def _prompt(self):
        if self.text_prompt:
            self.prompt = self.textpage + "I would like you to help answer my question with the information mentioned above. The question is : " + self.text_prompt
        else:
            self.prompt = f"{self.textpage}" + "So I would like to help you summarize what I have said above."

    def generate(self):
        self.text_prompt = st.text_area("Enter your text prompt or question : ", height=100)
        self.uploaded_file = st.file_uploader(label="Upload a PDF (optional):", type="PDF")
        if st.button("Generate"):
            self._uploaded_file()
            self._prompt()
            if self.prompt:  # Ensure prompt is not empty after processing
                with st.spinner("Generating response..."):
                    st.write(self.llm.invoke(self.prompt, stop=['<|eot_id|>']))
            else:
                st.warning("Please enter a text prompt or upload a PDF.")


cb = Chatbot()
cb.generate()