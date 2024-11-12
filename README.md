# 🗣️ Speech-to-Speech Assistant

It's a minimalistic and efficient streamlit chatbot for Urdu speakers to ask questions and get response in both text and audio formats. 
It's powered by **Google Gemini**.

---

## ✨ Features

- **Converts Speech to Text**: Simply speak, and the app captures your input in Urdu.
- **Responds with Speech**: Get a spoken response back in Urdu from the LLM, ensuring seamless communication.
- **Chat History Tracking**: The assistant keeps track of the conversation so it feels continuous.

🌟 _The best part? This entire app only took 50 lines of code!_

---

## 📚 Libraries Used

- **Streamlit**: For building the interactive web interface.
- **gTTS**: Google Text-to-Speech for generating spoken responses.
- **Google Generative AI**: To power the conversational response generation.
- **Streamlit Mic Recorder**: For capturing speech input.

---

## 🛠️ Installation & Setup

### Step 1: Clone the Repository
```bash
git clone https://github.com/aasherkamal216/STT_TTS.git
cd STT_TTS
```

### Step 2: Set Up a Virtual Environment (Optional but Recommended)
```bash
python -m venv venv
venv\Scripts\activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Set Up API Key
In the `.streamlit/secrets.toml` file, add your Google API key:
```plaintext
GOOGLE_API_KEY = "your_google_gemini_api_key"
```

---

## 🚀 Running the App
To start the app, simply run:
```bash
streamlit run app.py
```

---

This assistant app provides a fast, interactive experience with only minimal code!
