import streamlit as st
from textblob import TextBlob
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk
from gtts import gTTS
import speech_recognition as sr
from deep_translator import GoogleTranslator  # Fixed Translation Issue

# Download required NLTK data
nltk.download('punkt')
nltk.download('vader_lexicon')

# Initialize Sentiment Analyzer
sid = SentimentIntensityAnalyzer()

# Function to analyze sentiment
def get_sentiment(text):
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity
    scores = sid.polarity_scores(text)
    compound_score = scores['compound']
    combined_score = (0.7 * compound_score) + (0.3 * polarity)
    
    if combined_score > 0.1:
        return "Positive", combined_score
    elif combined_score < -0.1:
        return "Negative", combined_score
    else:
        return "Neutral", combined_score

# Function to generate chatbot response
def get_response(user_input):
    sentiment, score = get_sentiment(user_input)
    if sentiment == "Positive":
        return "🌟 I'm glad you're feeling positive! What's making you happy today?"
    elif sentiment == "Negative":
        return "😟 I'm sorry to hear that you're feeling down. Want to talk about it?"
    else:
        return "🤔 Hmm, that's interesting. Tell me more about what's on your mind."

# Function for Text-to-Speech using gTTS
def speak(text, language="en"):
    try:
        tts = gTTS(text, lang=language)
        tts.save("response.mp3")
        st.audio("response.mp3", format="audio/mp3")
    except Exception as e:
        st.error(f"Error in Text-to-Speech: {e}")

# Streamlit App UI
st.title("🎤 Mood-Based Chatbot")
st.write("Hi! I'm here to chat with you. Use your voice or type to share how you're feeling.")

# Tabs for Text Input and Voice Input
tab1, tab2 = st.tabs(["Text Input", "Voice Input"])

with tab1:
    user_input = st.text_input("Type your message below 👇:")

    if st.button("Submit Text"):
        if user_input.lower() == "bye":
            response = "👋 Goodbye! Take care!"
            st.success(response)
            speak(response)
        else:
            response = get_response(user_input)
            sentiment, score = get_sentiment(user_input)
            st.write("🤖 Chatbot:", response)
            st.write(f"💡 Mood Detected: **{sentiment}**")
            st.progress((score + 1) / 2)
            
            if st.checkbox("Enable Voice Response"):
                speak(response)

with tab2:
    st.write("🎙️ Speak into your microphone and I'll process your input.")
    recognizer = sr.Recognizer()

    timeout = st.slider("Set Listening Timeout (seconds):", 5, 15, 5)
    noise_sensitivity = st.slider("Adjust Noise Sensitivity (lower is stricter):", 0, 3, 1)

    if st.button("Start Voice Recording"):
        with sr.Microphone() as source:
            recognizer.dynamic_energy_threshold = True
            recognizer.energy_threshold = 300 + (noise_sensitivity * 100)
            st.info("🎧 Listening... Speak now!")
            
            try:
                audio_data = recognizer.listen(source, timeout=timeout)
                st.write("Processing your input...")
                user_input = recognizer.recognize_google(audio_data)
                st.success(f"🗣️ You said: {user_input}")
            except sr.UnknownValueError:
                st.error("Sorry, I couldn't understand you. Please try speaking more clearly.")
            except sr.RequestError as e:
                st.error(f"Speech Recognition error: {e}")
            except Exception as e:
                st.error(f"Unexpected error: {e}")

# Processing text after input from both text and voice
if user_input:
    if user_input.lower() == "bye":
        response = "👋 Goodbye! Take care!"
        st.success(response)
        speak(response)
    else:
        response = get_response(user_input)
        sentiment, score = get_sentiment(user_input)
        st.write("🤖 Chatbot:", response)
        st.write(f"💡 Mood Detected: **{sentiment}**")
        st.progress((score + 1) / 2)

        if st.checkbox("Enable Voice Response", key="voice_response_checkbox"):
            speak(response)

# Language Selector for TTS Output
language = st.selectbox("🌐 Select Language for Voice Output:", ["en", "es", "fr", "hi"])

if language != "en" and user_input:
    try:
        translated_text = GoogleTranslator(source="en", target=language).translate(response)
        st.write(f"🌐 Translated Response: {translated_text}")
        
        if st.checkbox("Enable Translated Voice Response", key="translated_voice_response_checkbox"):
            speak(translated_text, language)
    except Exception as e:
        st.error(f"Translation Error: {e}")
