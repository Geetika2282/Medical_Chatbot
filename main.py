import os
import streamlit as st
from groq import Groq
from langchain_groq import ChatGroq
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferWindowMemory
from scipy import stats
import numpy as np
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
groq_api_key = ("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")
if not groq_api_key:
    st.error("GROQ_API_KEY not found. Please set it in a .env file or environment variables.")
    st.stop()

# Initialize Streamlit
st.set_page_config(page_title="Health Assistant", layout="wide")
st.title("Health Assistant Chatbot")
st.write("Ask health-related questions or type 'BMI' to calculate your BMI. Always consult a doctor for medical advice.")

# System prompt for health-domain specificity
system_prompt = """
You are a health assistant specializing in general health information. Provide accurate, safe, and concise answers to health-related questions. Always include a disclaimer that you are not a doctor and that users should consult a healthcare professional for medical advice. For non-health questions, politely redirect to health topics.
"""

# Initialize Groq client and LangChain
llm = ChatGroq(
    groq_api_key=groq_api_key,
    model_name="llama-3.1-8b-instant",
    temperature=0.7
)

# Initialize conversation memory (stores last 10 exchanges)
if 'memory' not in st.session_state:
    st.session_state.memory = ConversationBufferWindowMemory(k=10)

# Conversation chain
if 'conversation' not in st.session_state:
    st.session_state.conversation = ConversationChain(
        llm=llm,
        memory=st.session_state.memory,
        verbose=False
    )

# BMI calculation function using SciPy for statistical context
def calculate_bmi(weight_kg, height_m):
    bmi = weight_kg / (height_m ** 2)
    categories = {
        (0, 18.5): "Underweight",
        (18.5, 25): "Normal",
        (25, 30): "Overweight",
        (30, np.inf): "Obese"
    }
    for (lower, upper), category in categories.items():
        if lower <= bmi < upper:
            return f"Your BMI is {bmi:.1f} ({category}). Consult a doctor for personalized advice."
    return f"Your BMI is {bmi:.1f}. Consult a doctor for personalized advice."

# Initialize chat history in session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Chat container for displaying messages
chat_container = st.container()

# Input form to prevent page refresh from clearing input
with st.form(key="chat_form", clear_on_submit=True):
    user_input = st.text_input("Your question:", key="user_input")
    submit_button = st.form_submit_button("Send")

# Handle user input
if submit_button and user_input:
    if user_input.lower() == "bmi":
        # BMI input form
        with st.form(key="bmi_form"):
            weight = st.number_input("Enter weight (kg):", min_value=0.0, step=0.1)
            height = st.number_input("Enter height (m):", min_value=0.0, step=0.01)
            bmi_submit = st.form_submit_button("Calculate BMI")
            if bmi_submit and weight > 0 and height > 0:
                result = calculate_bmi(weight, height)
                st.session_state.chat_history.append({"role": "user", "content": "BMI calculation"})
                st.session_state.chat_history.append({"role": "assistant", "content": result})
    else:
        # Process health question
        prompt = f"{system_prompt}\nUser: {user_input}"
        response = st.session_state.conversation.run(input=prompt)
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        st.session_state.chat_history.append({"role": "assistant", "content": response})

# Display chat history in the container
with chat_container:
    for message in st.session_state.chat_history:
        if message["role"] == "user":
            st.markdown(f"*You*: {message['content']}")
        else:
            st.markdown(f"*Health Assistant*: {message['content']}")

# Auto-scroll to the latest message
st.markdown(
    """
    <script>
        var container = document.getElementsByClassName('st-emotion-cache-1wbhy5x')[0];
        container.scrollTop = container.scrollHeight;
    </script>
    """,
    unsafe_allow_html=True
)