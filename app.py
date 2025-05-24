import streamlit as st
from gtts import gTTS
import os
import tempfile
import base64
import google.generativeai as genai
from streamlit_mic_recorder import speech_to_text

st.set_page_config(page_title="J.A.R.V.I.S Assistant",
                   page_icon="👽", layout="wide")

# Custom CSS for better styling
st.markdown("""
<style>
.main-header {
    text-align: center;
    padding: 1rem 0;
    background: linear-gradient(90deg, #ff6b6b, #4ecdc4);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-size: 2.5rem;
    font-weight: bold;
    margin-bottom: 2rem;
}
.chat-container {
    max-height: 400px;
    overflow-y: auto;
    border: 1px solid #e0e0e0;
    border-radius: 10px;
    padding: 1rem;
    margin: 1rem 0;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="main-header">🤖 J.A.R.V.I.S Assistant</h1>',
            unsafe_allow_html=True)

# Sidebar for settings
with st.sidebar:
    st.header("⚙️ Settings")

    # Accent selection
    selected_accent = st.selectbox(
        "Choose Voice Accent:",
        options=list({
            "US English": {"lang": "en", "tld": "com"},
            "UK English": {"lang": "en", "tld": "co.uk"},
            "Australian English": {"lang": "en", "tld": "com.au"},
            "Indian English": {"lang": "en", "tld": "co.in"},
            "Urdu": {"lang": "ur", "tld": "com"},
        }.keys()),
        index=1  # Default to UK English
    )

    ACCENTS = {
        "US English": {"lang": "en", "tld": "com"},
        "UK English": {"lang": "en", "tld": "co.uk"},
        "Australian English": {"lang": "en", "tld": "com.au"},
        "Indian English": {"lang": "en", "tld": "co.in"},
        "Urdu": {"lang": "ur", "tld": "com"},
    }

    # Voice speed
    voice_speed = st.checkbox("Slow Speech", value=False)

    st.divider()

    # Auto-stop settings
    st.subheader("🎤 Recording Settings")
    auto_stop = st.checkbox("Auto-stop when silence detected", value=True)

    if auto_stop:
        silence_threshold = st.slider(
            "Silence Detection (seconds)",
            min_value=1.0,
            max_value=5.0,
            value=2.0,
            step=0.5,
            help="Stop recording after this many seconds of silence"
        )

        silence_level = st.slider(
            "Silence Sensitivity",
            min_value=0.01,
            max_value=0.1,
            value=0.05,
            step=0.01,
            help="Lower = more sensitive to quiet sounds"
        )
    else:
        # Default values when auto-stop is disabled
        silence_threshold = None
        silence_level = None

    st.divider()

    # Clear chat button
    if st.button("🗑️ Clear Chat History"):
        if "messages" in st.session_state:
            st.session_state.messages = []
            st.rerun()

# Initialize Gemini AI
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    instruction = """You are JARVIS, a helpful and intelligent AI assistant. 
    Respond to user questions in a friendly, concise manner. 
    Keep responses under 150 words unless more detail is specifically requested.
    Be helpful, accurate, and engaging."""

    model = genai.GenerativeModel(
        'gemini-2.0-flash',
        generation_config={"temperature": 0.3, "max_output_tokens": 200},
        system_instruction=instruction
    )
except Exception as e:
    st.error(f"Failed to initialize AI model: {e}")
    st.stop()


def text_to_speech(text, accent_info, slow=False):
    """Convert text to speech with specified accent"""
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
            tts = gTTS(
                text=text,
                lang=accent_info["lang"],
                tld=accent_info["tld"],
                slow=slow
            )
            tts.save(fp.name)
            return fp.name
    except Exception as e:
        st.error(f"Text-to-speech error: {e}")
        return None


def clean_text_for_speech(text):
    """Remove markdown and special characters that interfere with TTS"""
    # Remove markdown formatting
    text = text.replace('**', '').replace('*', '').replace('_', '')
    text = text.replace('#', '').replace('`', '')
    # Remove extra whitespace
    text = ' '.join(text.split())
    return text


# Initialize session state
if "chat" not in st.session_state:
    st.session_state.chat = model.start_chat(history=[])
if "messages" not in st.session_state:
    st.session_state.messages = []

# Main interface
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("🎤 Voice Input")

    # Display current recording settings
    if auto_stop:
        st.info(f"🔇 Auto-stop enabled: {silence_threshold}s timeout")

        # Simple auto-stop with timer
        st.markdown(f"""
        <script>
        let recordingTimer;
        let recordingStartTime;
        
        // Function to auto-stop recording after specified time
        function startAutoStopTimer() {{
            recordingStartTime = Date.now();
            recordingTimer = setTimeout(function() {{
                // Find and click the stop button
                const stopButtons = document.querySelectorAll('button');
                for (let button of stopButtons) {{
                    if (button.textContent.includes('Stop Recording') || 
                        button.textContent.includes('⏹️')) {{
                        button.click();
                        break;
                    }}
                }}
            }}, {int(silence_threshold * 1000 * 3)}); // 3x silence threshold for safety
        }}
        
        // Monitor for start recording button clicks
        document.addEventListener('click', function(e) {{
            if (e.target.textContent && 
                (e.target.textContent.includes('Start Recording') || 
                 e.target.textContent.includes('🎤'))) {{
                setTimeout(startAutoStopTimer, 500); // Small delay to ensure recording starts
            }}
            
            if (e.target.textContent && 
                (e.target.textContent.includes('Stop Recording') || 
                 e.target.textContent.includes('⏹️'))) {{
                if (recordingTimer) {{
                    clearTimeout(recordingTimer);
                }}
            }}
        }});
        </script>
        """, unsafe_allow_html=True)
    else:
        st.info("⏱️ Manual recording mode - click stop when done")

    with st.spinner("🎧 Listening... Speak now!"):
        # Use different keys to reset component state
        text = speech_to_text(
            language="en",
            just_once=True,
            key=f"STT_{'auto' if auto_stop else 'manual'}_{int(silence_threshold) if auto_stop else 'manual'}",
            start_prompt=f"🎤 Start Recording ({'Auto-stop' if auto_stop else 'Manual'})",
            stop_prompt="⏹️ Stop Recording"
        )

with col2:
    st.subheader("📊 Status")
    if text:
        st.success("✅ Speech recognized!")
        st.info(f"Voice: {selected_accent}")
        if auto_stop:
            st.info(f"🔇 Auto-stopped with timer")
    else:
        st.info("🔴 Waiting for input...")
        if auto_stop:
            max_time = int(silence_threshold * 3)
            st.caption(f"Will auto-stop after ~{max_time}s")

# Process user input
if text:
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": text})

    # Display user message
    with st.chat_message("user", avatar="🧑"):
        st.write(text)

    # Generate assistant response
    response_text = None
    try:
        with st.spinner("🤔 J.A.R.V.I.S is thinking..."):
            response = st.session_state.chat.send_message(text)
            response_text = response.text

        # Display assistant response
        with st.chat_message("assistant", avatar="🤖"):
            st.write(response_text)

        # Add assistant message to history
        st.session_state.messages.append(
            {"role": "assistant", "content": response_text})

    except Exception as e:
        st.error(f"❌ Error generating response: {e}")
        st.info("Please try speaking again or check your internet connection.")

    # Generate and play audio OUTSIDE of chat message context
    if response_text:
        with st.spinner("🔊 Generating speech..."):
            try:
                clean_text = clean_text_for_speech(response_text)
                accent_info = ACCENTS[selected_accent]
                audio_file = text_to_speech(
                    clean_text, accent_info, voice_speed)

                if audio_file:
                    # Use Streamlit's native audio player for better reliability
                    with open(audio_file, "rb") as f:
                        audio_bytes = f.read()

                    st.subheader("🔊 J.A.R.V.I.S Voice Response:")
                    st.audio(audio_bytes, format="audio/mp3", autoplay=True)

                    # Clean up temp file
                    try:
                        os.remove(audio_file)
                    except Exception as e:
                        st.warning(f"Could not clean up audio file: {e}")

            except Exception as e:
                st.error(f"Audio generation error: {e}")

# Chat History Section
if st.session_state.messages:
    st.subheader("💬 Conversation History")

    with st.container():
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        # Show last 6 messages
        for i, message in enumerate(st.session_state.messages[-6:]):
            if message["role"] == "user":
                st.markdown(f"**🧑 You:** {message['content']}")
            else:
                st.markdown(f"**🤖 J.A.R.V.I.S:** {message['content']}")
            if i < len(st.session_state.messages[-6:]) - 1:
                st.markdown("---")
        st.markdown('</div>', unsafe_allow_html=True)

# Instructions
if not st.session_state.messages:
    st.markdown("""
    ### 🚀 How to Use J.A.R.V.I.S:
    
    1. **🎤 Click "Start Recording"** and speak your question
    2. **🔇 Auto-stop mode** will automatically stop after a set time
    3. **⏹️ Manual mode** requires clicking "Stop Recording" when done
    4. **🤖 J.A.R.V.I.S will respond** with both text and voice
    5. **⚙️ Customize settings** in the sidebar (accent, speech speed, auto-stop)
    6. **🗑️ Clear history** anytime using the sidebar button
    
    **💡 Tips:**
    - **Auto-stop mode**: Speak your question, it will stop automatically
    - **Manual mode**: Better for longer questions or detailed conversations
    - Adjust auto-stop timer based on your speaking pace
    - Try different accents to find your preference
    
    **🔧 Troubleshooting:**
    - If auto-stop cuts you off: Increase the silence threshold time
    - For long questions: Use manual mode or increase timer
    - Can always click stop manually even in auto mode
    """)
else:
    st.info("🎤 Ready for your next question! Click 'Start Recording' to continue the conversation.")
