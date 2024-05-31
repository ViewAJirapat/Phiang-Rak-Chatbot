#streamlit run chat.py

import streamlit as st
from pypdf import PdfReader
from langchain_community.llms import Ollama


class Chatbot:
    def __init__(self) -> None:
        self.model_options = ["llava:13b", "aya:latest"]
        self.selected_model = st.sidebar.selectbox("Select a model", self.model_options)
        self.llm = Ollama(model=self.selected_model)
        st.title(f"Flexible Q&A with Phiang-Rak : {self.selected_model}")
        self.textpage = ""
        self.prompt = ""
        self.previous_answers = []

    def _uploaded_file(self):
        if self.uploaded_file:
            # file_details = {
            #     "filename": self.uploaded_file.name,
            #     "filetype": self.uploaded_file.type,
            #     "filesize": self.uploaded_file.size
            # }
            # st.write(file_details)
            if self.uploaded_file.type == "application/pdf":
                reader = PdfReader(self.uploaded_file)
                pagecount = len(reader.pages)
                for page in range(pagecount):
                    getpage = reader.pages[page]
                    self.textpage += getpage.extract_text()

    def _prompt(self):
        if self.text_prompt:
            if self.previous_answers:
                self.prompt = f"{self.text_prompt} {' '.join(self.previous_answers)} I would like you to help answer my question with the information mentioned above. The question is: {self.text_prompt}"
            elif self.uploaded_file:
                self.prompt = f"{self.textpage} I would like you to help answer my question with the information mentioned above. The question is: {self.text_prompt}"
            else:
                self.prompt = self.text_prompt
        else:
            self.prompt = f"{self.textpage} So I would like you to help summarize what I have said above."

    def generate(self):
        st.sidebar.header("Chat with llava:13b")
        self.uploaded_file = st.sidebar.file_uploader(label="Upload a PDF (optional):", type="pdf")
        self.text_prompt = st.text_input("Enter your text prompt or question:", key="input")

        if st.button("Send"):
            if not self.text_prompt and not self.uploaded_file:
                st.warning("Please enter a text prompt or upload a PDF.")
            else:
                self._uploaded_file()
                self._prompt()
                if self.prompt:
                    with st.spinner("Generating response..."):
                        response = self.llm.invoke(self.prompt, stop=['<|eot_id|>'])
                        self.previous_answers.append(response)
                        st.session_state.chat_history.append({"role": "user", "content": self.text_prompt})
                        st.session_state.chat_history.append({"role": "assistant", "content": response})
                    

        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        for chat in st.session_state.chat_history:
            if chat["role"] == "user":
                st.write(f"**You:** {chat['content']}")
            else:
                st.write(f"**Phiang-Rak:** {chat['content']}")


if __name__ == "__main__":
    cb = Chatbot()
    cb.generate()
