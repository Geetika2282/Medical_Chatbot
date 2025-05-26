https://medicalchatbot-diseasesymptoms.streamlit.app/
# 🩺 Health Assistant Chatbot

A conversational AI chatbot built with **Streamlit**, **LangChain**, and **Groq's LLaMA 3.1 model** that specializes in general health information and BMI calculations. It provides helpful insights and answers to health-related queries with a clear disclaimer that it's not a substitute for professional medical advice.

---

## 🚀 Features

- ✅ Chat with an AI trained on health-related queries
- 🧠 Keeps track of the last 10 messages for better contextual replies
- 📊 BMI calculator included
- 🔐 Secure API usage with `.env` support
- 💬 Built with **LangChain**, **Groq API**, and **Streamlit**
- 🧪 Uses **SciPy** for BMI-related statistical processing

---

## 📦 Requirements

- Python 3.8+
- [Groq API Key](https://console.groq.com/)
- Streamlit
- LangChain
- langchain-groq
- groq
- numpy
- scipy
- python-dotenv

---

## 🔧 Installation

1. **Clone the repository**

```bash
git clone https://github.com/your-username/health-assistant-chatbot.git
cd health-assistant-chatbot
```

2. **Install dependencies**

```bash
pip install -r requirements.txt
```

3. **Add your GROQ API Key**

Create a `.env` file in the root directory and add:

```env
GROQ_API_KEY=your_actual_api_key_here
```

> Replace `your_actual_api_key_here` with your actual key.

4. **Run the app**

```bash
streamlit run app.py
```

---

## 🖥️ Usage

- Ask health-related questions like:
  - “What are the symptoms of flu?”
  - “How to stay hydrated during summer?”
- Type **`BMI`** to activate the BMI calculator.

---

## 📌 Disclaimer

This chatbot is designed for **educational and informational purposes only**. It is **not a replacement for professional medical advice**, diagnosis, or treatment. Always seek advice from a qualified healthcare provider for any medical concerns.

---

## 🧑‍💻 Author

**Geeetika Kanwar**  
Health Assistant project using LLaMA-3.1 and Groq API.

---

## 📜 License

This project is open-source and free to use under the [MIT License](LICENSE).
