import streamlit as st
import replicate
import os
import pandas as pd
import toml

# Load API key from secrets.toml
def load_api_key():
    with open("secrets.toml", "r") as f:
        config = toml.load(f)
    return config["replicate"]["api_key"]

api_key = "r8_7Ft76NWHOdMafxCaRusVzWn6Uu1I3Xx3Isn9c"  # Ensure this is correct
print(api_key)

# Initialize Replicate client
replicate_client = replicate.Client(api_token=api_key)

# Set page config for Streamlit app
st.set_page_config(page_title="🤱 Postpartum Support Chatbot", layout="wide")

# Add the title 'MamaMind' at the top of the screen

st.markdown("<h1 style='font-size: 50px; text-align: left;'>MamáMind</h1>", unsafe_allow_html=True)

# Add some blank space between the title and the next line
st.markdown("<br><br>", unsafe_allow_html=True)

# Subheader for description
st.subheader("🤱 Postpartum Support Chatbot")
st.markdown("<h3 style='font-size: 20px;'>Here to listen, support, and guide you. 💙</h3>", unsafe_allow_html=True)



# Initialize session state for messages and mood tracking
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hello! How are you feeling today?"}]
if "mood_log" not in st.session_state:
    st.session_state.mood_log = []

# Display chat messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User input
user_input = st.chat_input("Type your message here...")
print(user_input)

# Define FAQ section
faq_dict = {
    "What is postpartum depression?": "Postpartum depression is a type of mood disorder that affects women after childbirth. Symptoms may include feelings of sadness, anxiety, and exhaustion. It's important to seek help if you're struggling.",
    "How can I manage postpartum anxiety?": "Managing postpartum anxiety can include practicing deep breathing exercises, connecting with a support group, and speaking with a healthcare provider. Seeking professional help is crucial if the anxiety becomes overwhelming.",
    "What are some signs I need to seek help?": "Some signs include persistent sadness, feeling overwhelmed, inability to care for yourself or your baby, and having thoughts of harming yourself or others. Reach out to a healthcare provider if you experience any of these signs.",
    "How long does postpartum recovery take?": "Postpartum recovery varies for every woman. It can take several months for your body and emotions to return to pre-pregnancy levels. It's important to give yourself grace and time to heal.",
    "Can I exercise postpartum?": "Once your healthcare provider gives the okay, light exercise like walking or postnatal yoga can help you feel better physically and emotionally. Always follow your doctor's guidance before starting any exercise program."
}

# Show FAQs in the sidebar
with st.sidebar:
    st.header("📚 Frequently Asked Questions")
    faq_button = st.button("Show FAQs")

    if faq_button:
        st.write("### Postpartum FAQs")
        for question, answer in faq_dict.items():
            st.write(f"**Q: {question}**")
            st.write(f"A: {answer}")

# Handle user input and generate response
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)
        print(user_input)

    # Mood tracking logic (simple sentiment analysis)
    mood_keywords = {
        "happy": ["happy", "good", "great", "better", "okay", "relieved", "joyful", "cheerful", "elated", "enthusiatic", "active", "productive"],
        "neutral": ["fine", "okay", "so-so", "meh"],
        "sad": ["sad", "tired", "overwhelmed", "anxious","don't feel good", "don't feel", "stressed", "depressed", "cry", "crying", "gloomy", "heartbroken", "lonely", "hopeless", "miserable"]
    }

    user_mood = "neutral"   #Default mood
    for mood, keywords in mood_keywords.items():
        if any(word in user_input.lower() for word in keywords):
            user_mood = mood
            break

    st.session_state.mood_log.append({"mood": user_mood, "message": user_input})

    # Generate AI response with context from Replicate
    try:
        # Update the model identifier and ensure input formatting is correct
        response = replicate_client.run(
            "a16z-infra/llama7b-v2-chat:4f0a4744c7295c024a1de15e1a63c880d3da035fa1f49bfd344fe076074c8eea",  # Replace with your model
            input={
                "prompt": user_input  # Ensure we are passing a prompt in the right format
            }
        )

        # Collect the full response before displaying it
        full_response = ""
        for chunk in response:
            full_response += chunk

        # Display the full response at once
        with st.chat_message("assistant"):
            st.markdown(full_response)

        # Append the assistant's response to the session state
        st.session_state.messages.append({"role": "assistant", "content": full_response})

    except Exception as e:
        st.write(f"Error: {e}")

# Sidebar for mood tracking and resources
with st.sidebar:
    st.header("📊 Mood Tracker")
    if st.session_state.mood_log:
        mood_df = pd.DataFrame(st.session_state.mood_log)
        st.write(mood_df.tail(5))  # Show last 5 moods
    else:
        st.write("Your mood entries will appear here.")

    # Display overall mood based on mood log
    mood_count = pd.Series([entry["mood"] for entry in st.session_state.mood_log]).value_counts()
    if len(mood_count) > 0:
        if len(mood_count) == 1:
            overall_mood = mood_count.idxmax()
        else:
            if mood_count.get("happy", 0) == mood_count.get("sad", 0):
                overall_mood = "neutral"
            elif mood_count.get("happy", 0) == mood_count.get("neutral", 0):
                overall_mood = "neutral"
            elif mood_count.get("sad", 0) == mood_count.get("neutral", 0):
                overall_mood = "neutral"
            else:
                overall_mood = mood_count.idxmax()

        if overall_mood == "happy":
            st.write("Great! You feel happy today! 😊")
        elif overall_mood == "sad":
            st.write("It's okay to feel sad sometimes. You're not alone. 💙")
        else:
            st.write("You're doing okay. Take it one day at a time. 💪")

    st.header("📚 Resources")
    st.markdown(""" 
    - *[Postpartum Support International](https://www.postpartum.net/)*  
    - *[Women Mental Health Alliance India](https://www.bing.com/ck/a?!&&p=c47b4a0a38408a27e08abebb97fbdb7037ccc1859f33d0b3fe89754268a2dd90JmltdHM9MTczODM2ODAwMA&ptn=3&ver=2&hsh=4&fclid=1f1ab4ca-f9f7-633e-2a73-a057f8456275&psq=mental+health+sites+for+postpartum+women+india&u=a1aHR0cHM6Ly93b21lbm1lbnRhbGhlYWx0aGFsbGlhbmNlaW5kaWEub3JnLw&ntb=1)*  
    - *[National Suicide Prevention Lifeline](https://988lifeline.org/) - Dial 988*  
    - *[Find a Therapist](https://www.psychologytoday.com/us/therapists)*  
    """)

st.success("Your chat session is private. If you need immediate help, reach out to a professional.")
