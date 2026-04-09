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

        # Fix 1 & 2: initialise session state at the top so it is always
        # available before any button callback runs, and so that
        # previous_answers survives Streamlit reruns.
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []
        if "previous_answers" not in st.session_state:
            st.session_state.previous_answers = []

    def _uploaded_file(self):
        if self.uploaded_file:
            if self.uploaded_file.type == "application/pdf":
                reader = PdfReader(self.uploaded_file)
                pagecount = len(reader.pages)
                for page in range(pagecount):
                    getpage = reader.pages[page]
                    self.textpage += getpage.extract_text()

    def _prompt(self):
        if self.text_prompt:
            # Fix 3: combine PDF context *and* conversation history when both
            # are available, instead of ignoring the PDF when there are prior
            # answers.
            context_parts = []
            if self.textpage:
                context_parts.append(self.textpage)
            if st.session_state.previous_answers:
                context_parts.append(" ".join(st.session_state.previous_answers))

            if context_parts:
                context = " ".join(context_parts)
                self.prompt = (
                    f"{context} I would like you to help answer my question "
                    f"with the information mentioned above. The question is: {self.text_prompt}"
                )
            else:
                self.prompt = self.text_prompt
        else:
            # Fix 5: only attempt summarisation when a PDF was actually
            # uploaded; skip silently otherwise to avoid sending an empty
            # prompt to the LLM.
            if self.textpage:
                self.prompt = f"{self.textpage} So I would like you to help summarize what I have said above."

    def generate(self):
        # Fix 4: use the dynamically selected model name in the sidebar header.
        st.sidebar.header(f"Chat with {self.selected_model}")
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
                        st.session_state.previous_answers.append(response)
                        st.session_state.chat_history.append({"role": "user", "content": self.text_prompt})
                        st.session_state.chat_history.append({"role": "assistant", "content": response})

        for chat in st.session_state.chat_history:
            if chat["role"] == "user":
                st.write(f"**You:** {chat['content']}")
            else:
                st.write(f"**Phiang-Rak:** {chat['content']}")


if __name__ == "__main__":
    cb = Chatbot()
    cb.generate()
