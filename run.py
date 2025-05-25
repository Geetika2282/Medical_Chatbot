import os
import streamlit as st
from groq import Groq
from langchain_groq import ChatGroq
from langchain.chains import ConversationChain
from langchain.memory import ConversationSummaryMemory
from scipy import stats
import numpy as np
from googletrans import Translator
import json
from uuid import uuid4
import asyncio
import platform

# Load environment variables
from dotenv import load_dotenv
load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY", "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")
if not groq_api_key:
    st.error("GROQ_API_KEY not found. Please set it in a .env file or environment variables.")
    st.stop()

# Initialize Streamlit
st.set_page_config(page_title="HealthSync Assistant", layout="wide")
st.markdown("""
    <style>
        .main { background-color: #f0f4f8; }
        .stButton>button { background-color: #4CAF50; color: white; }
        .stTextInput>div>input { border-radius: 10px; }
        .sidebar .sidebar-content { background-color: #e8f5e9; }
        .health-tip { background-color: #e3f2fd; padding: 10px; border-radius: 5px; }
    </style>
""", unsafe_allow_html=True)

# System prompt with enhanced safety
system_prompt = """
You are HealthSync, an advanced health assistant providing accurate, evidence-based health information. Offer concise, safe answers to health-related questions. For serious symptoms (e.g., chest pain combined with difficulty breathing), urge immediate medical attention. Always include: 'I am not a doctor. Consult a healthcare professional for medical advice.' For non-health questions, redirect to health topics politely. Use a friendly, empathetic tone.
"""

# Initialize Groq client and LangChain
llm = ChatGroq(
    groq_api_key=groq_api_key,
    model_name="llama-3.1-8b-instant",
    temperature=0.7
)

# Initialize conversation memory with summarization
if 'memory' not in st.session_state:
    st.session_state.memory = ConversationSummaryMemory(llm=llm)

# Conversation chain
if 'conversation' not in st.session_state:
    st.session_state.conversation = ConversationChain(
        llm=llm,
        memory=st.session_state.memory,
        verbose=False
    )

# Initialize state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'health_challenges' not in st.session_state:
    st.session_state.health_challenges = {"water_intake": 0, "steps": 0}
if 'language' not in st.session_state:
    st.session_state.language = "en"

# Multilingual support
translator = Translator()

# BMI calculation with statistical context
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
            return f"Your BMI is {bmi:.1f} ({category}). Consult a doctor for personalized advice.", bmi
    return f"Your BMI is {bmi:.1f}. Consult a doctor for personalized advice.", bmi

# LLM-based symptom checker
def symptom_checker(symptoms):
    if not symptoms:
        return "No symptoms selected. Please choose symptoms to analyze."
    
    # Check for critical symptom combinations
    critical_combinations = [
        ("Chest pain", "Difficulty breathing"),
        ("Chest pain", "Loss of consciousness"),
        ("Difficulty breathing", "Loss of consciousness")
    ]
    for sym1, sym2 in critical_combinations:
        if sym1 in symptoms and sym2 in symptoms:
            return "🚨 Urgent: These symptoms may indicate a serious condition. Seek immediate medical attention."
    
    # Construct prompt for LLM
    symptom_list = ", ".join(symptoms)
    symptom_prompt = f"""
    {system_prompt}
    The user reports the following symptoms: {symptom_list}.
    Based on these symptoms, suggest up to three possible medical conditions with brief explanations. If symptoms are ambiguous, state so. Always emphasize consulting a healthcare professional and avoid definitive diagnoses. Format the response as:
    - Condition 1: [Explanation]
    - Condition 2: [Explanation]
    - Condition 3: [Explanation]
    I am not a doctor. Consult a healthcare professional for medical advice.
    """
    
    # Get LLM response
    response = llm.invoke(symptom_prompt).content
    return response

# Sidebar navigation
st.sidebar.title("HealthSync Tools")
tool = st.sidebar.selectbox("Choose a tool", ["Chat", "BMI Calculator", "Symptom Checker", "Health Challenges"])
st.sidebar.markdown("---")
st.sidebar.subheader("Language")
language = st.sidebar.selectbox("Select language", ["English", "Spanish", "French"], index=["en", "es", "fr"].index(st.session_state.language))
lang_map = {"English": "en", "Spanish": "es", "French": "fr"}
if language != st.session_state.language:
    st.session_state.language = lang_map[language]

# Main title and health tip
st.title("HealthSync Assistant")
st.markdown("Your AI-powered health companion. Always consult a doctor for medical advice.")
st.markdown("Created by Geetika Kanwar")
st.markdown('<div class="health-tip">💡 Daily Tip: Stay hydrated! Aim for 8 glasses of water daily.</div>', unsafe_allow_html=True)

# Tool-specific logic
if tool == "Chat":
    with st.form(key="chat_form", clear_on_submit=True):
        user_input = st.text_input("Ask a health question:", key="user_input")
        submit_button = st.form_submit_button("Send")
    
    if submit_button and user_input:
        # Translate input to English if needed
        input_translated = user_input if st.session_state.language == "en" else translator.translate(user_input, dest="en").text
        prompt = f"{system_prompt}\nUser: {input_translated}"
        response = st.session_state.conversation.run(input=prompt)
        # Translate response back to user language
        response_translated = response if st.session_state.language == "en" else translator.translate(response, dest=st.session_state.language).text
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        st.session_state.chat_history.append({"role": "assistant", "content": response_translated})

elif tool == "BMI Calculator":
    st.subheader("BMI Calculator")
    with st.form(key="bmi_form"):
        weight = st.number_input("Enter weight (kg):", min_value=0.0, step=0.1)
        height = st.number_input("Enter height (m):", min_value=0.0, step=0.01)
        bmi_submit = st.form_submit_button("Calculate BMI")
        if bmi_submit and weight > 0 and height > 0:
            result, bmi = calculate_bmi(weight, height)
            st.session_state.chat_history.append({"role": "user", "content": "BMI calculation"})
            st.session_state.chat_history.append({"role": "assistant", "content": result})
            # Store for visualization
            if 'bmi_history' not in st.session_state:
                st.session_state.bmi_history = []
            st.session_state.bmi_history.append(bmi)
            # Chart.js visualization
            if len(st.session_state.bmi_history) > 1:
                chart_data = {
                    "type": "line",
                    "data": {
                        "labels": [f"Entry {i+1}" for i in range(len(st.session_state.bmi_history))],
                        "datasets": [{
                            "label": "BMI Trend",
                            "data": st.session_state.bmi_history,
                            "borderColor": "#4CAF50",
                            "backgroundColor": "rgba(76, 175, 80, 0.2)",
                            "fill": True
                        }]
                    },
                    "options": {
                        "scales": {
                            "y": {"beginAtZero": False, "title": {"display": True, "text": "BMI"}}
                        }
                    }
                }
                st.markdown(f"""
                    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
                    <canvas id="bmiChart" width="400" height="200"></canvas>
                    <script>
                        var ctx = document.getElementById('bmiChart').getContext('2d');
                        new Chart(ctx, {json.dumps(chart_data)});
                    </script>
                """, unsafe_allow_html=True)

elif tool == "Symptom Checker":
    st.subheader("Symptom Checker")
    symptom_options = [
        "Fever", "Cough", "Fatigue", "Headache", "Chest pain", "Difficulty breathing",
        "Sore throat", "Nausea", "Vomiting", "Diarrhea", "Muscle pain", "Joint pain",
        "Rash", "Dizziness", "Loss of appetite", "Shortness of breath", "Abdominal pain",
        "Chills", "Sweating", "Loss of consciousness"
    ]
    symptoms = st.multiselect("Select symptoms", symptom_options)
    if st.button("Analyze Symptoms"):
        result = symptom_checker(symptoms)
        st.session_state.chat_history.append({"role": "user", "content": f"Symptoms: {', '.join(symptoms)}"})
        st.session_state.chat_history.append({"role": "assistant", "content": result})

elif tool == "Health Challenges":
    st.subheader("Health Challenges")
    st.write("Track your daily health goals!")
    water = st.number_input("Glasses of water today:", min_value=0, step=1, value=st.session_state.health_challenges["water_intake"])
    steps = st.number_input("Steps taken today:", min_value=0, step=100, value=st.session_state.health_challenges["steps"])
    if st.button("Update Progress"):
        st.session_state.health_challenges["water_intake"] = water
        st.session_state.health_challenges["steps"] = steps
        st.success("Progress updated!")
        if water >= 8:
            st.balloons()
            st.write("🎉 Great job! You've met your daily water goal!")
        if steps >= 10000:
            st.balloons()
            st.write("🏃 Awesome! You've hit 10,000 steps today!")

# Display chat history
with st.container():
    for message in st.session_state.chat_history:
        if message["role"] == "user":
            st.markdown(f"**You**: {message['content']}")
        else:
            st.markdown(f"**HealthSync**: {message['content']}")

# Feedback widget
with st.form(key="feedback_form"):
    feedback = st.slider("Rate this response:", 1, 5, 3)
    feedback_text = st.text_area("Optional feedback:")
    feedback_submit = st.form_submit_button("Submit Feedback")
    if feedback_submit:
        st.session_state.chat_history.append({"role": "user", "content": f"Feedback: {feedback}/5 - {feedback_text}"})
        st.success("Thank you for your feedback!")

# Auto-scroll
st.markdown(
    """
    <script>
        var container = document.getElementsByClassName('st-emotion-cache-1wbhy5x')[0];
        container.scrollTop = container.scrollHeight;
    </script>
    """,
    unsafe_allow_html=True
)

# Pyodide compatibility
if platform.system() == "Emscripten":
    async def main():
        while True:
            await asyncio.sleep(1.0 / 60)  # 60 FPS for UI updates
    asyncio.ensure_future(main())
else:
    async def main():
        while True:
            await asyncio.sleep(1.0 / 60)  # You can customize this

    if __name__ == "__main__":
        asyncio.run(main())
