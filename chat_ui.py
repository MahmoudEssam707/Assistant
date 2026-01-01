"""
Simple Streamlit Chat UI for Mail Sender Agent
"""

import streamlit as st
import requests
from typing import Optional


# Basic page config
st.set_page_config(page_title="Assistant", page_icon="🤖")

# Hide the toolbar
st.markdown("""
<style>
.e1o8oa9v2.st-emotion-cache-14vh5up.stAppToolbar {
    display: none !important;
}
</style>
""", unsafe_allow_html=True)

class SimpleChat:
    def __init__(self):
        self.api_url = "http://localhost:2024"

    def send_message(self, message: str) -> Optional[str]:
        """Send message to agent and return response."""
        try:
            payload = {"message": message, "thread_id": "simple_chat"}
            response = requests.post(f"{self.api_url}/query", json=payload)
            if response.status_code == 200:
                return response.json()["response"]
            else:
                return f"Error: {response.status_code}"
        except requests.exceptions.RequestException as e:
            return f"Connection error: {str(e)}"
    
    def run(self):
    
        st.title("🤖 Assistant 🤖", text_alignment="center")

        # Initialize chat history
        if "messages" not in st.session_state:
            st.session_state.messages = []

        # Display chat history
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])

        # Chat input only
        prompt = st.chat_input("Message")

        # Handle user input
        if prompt:
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.write(prompt)

            # Get and display assistant response
            with st.chat_message("assistant"):
                st.empty()
                with st.spinner("🤔 Thinking..."):
                    response = self.send_message(prompt)
                st.write(response)
                st.session_state.messages.append({"role": "assistant", "content": response})

if __name__ == "__main__":
    chat = SimpleChat()
    chat.run()