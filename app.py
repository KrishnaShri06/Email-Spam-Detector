import streamlit as st
import pickle
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
import os

CUSTOM_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700&display=swap');
    
    body {
        font-family: 'Roboto', sans-serif !important;
    }
    
    .stApp {
        background: linear-gradient(to right top, #000000, #0a0a0a, #121212, #181818, #1d1d1e, #262632, #2e2f47, #37395d, #fc4b11);
    }
    
    .main [data-testid="stVerticalBlock"] { 
        max-width: 500px;
        width: 90%;
        margin: 50px auto;
        padding: 30px;
        background: #fff;
        border-radius: 15px;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
        text-align: center;
    }

    /* Style for the button (mimicking the original purple) */
    .stButton>button {
        background-color: rgb(203 70 17);;
        color: white;
        padding: 15px 30px;
        border-radius: 8px;
        font-size: 1.1em;
        border: none;
        transition: background-color 0.3s;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        width: 100%;
        max-width: 200px;
        margin-top: 20px;
    }
    .stButton>button:hover {
        background-color: #2575fc;
    }

    .result-box {
        margin-top: 20px;
        padding: 20px;
        border-radius: 8px;
        font-size: 1.5em;
        font-weight: bold;
        text-align: center;
    }
    
    /* Colors for 'Likely Scam' (Spam) */
    .result-spam {
        background-color: #ffdddd; /* Light Red */
        color: #d8000c; /* Dark Red */
        border: 1px solid #d8000c;
    }

    /* Colors for 'Likely Not Spam' (Ham) - The requested Green */
    .result-ham {
        background-color: #e0ffe0; /* Light Green */
        color: #008000; /* Dark Green */
        border: 1px solid #008000;
    }
    
    /* Hide Streamlit's default header/footer/sidebar buttons for a cleaner look */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
"""

st.set_page_config(
    page_title="Spam Detection",
    layout="centered", 
    initial_sidebar_state="collapsed",
)

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# --- 2. MODEL LOADING AND CACHING ---
# File names for the saved artifacts (Must match the files you downloaded)
MODEL_FILE = 'spam_model.pkl'
VECTORIZER_FILE = 'vectorizer.pkl'

@st.cache_resource
def load_artifacts():
    """Loads the pre-trained model and vectorizer from PKL files."""
    try:
        # Load the trained model
        with open(MODEL_FILE, 'rb') as file:
            model = pickle.load(file)

        # Load the fitted vectorizer
        with open(VECTORIZER_FILE, 'rb') as file:
            vectorizer = pickle.load(file)
            
        return model, vectorizer

    except FileNotFoundError:
        st.error(f"Error: Required file not found. Ensure {MODEL_FILE} and {VECTORIZER_FILE} are in the root directory.")
        return None, None

model, vectorizer = load_artifacts()


# --- 3. CORE PREDICTION LOGIC ---

def predict_message(message, model, vectorizer):
   
    if not model or not vectorizer:
        return 'Server Error: Model Initialization Failed', 'spam'
        
    message_vector = vectorizer.transform([message])
    prediction = model.predict(message_vector)[0]
    
    if prediction == 1:
        return 'Likely Scam', 'spam'
    else:
        return 'Likely Not Spam', 'ham'

st.markdown(f'<h1 style="color: rgb(203 70 17); font-size: 2em; margin-bottom: 5px;"><i class="fas fa-shield-alt"></i> Email Spam Detection</h1>', unsafe_allow_html=True)
st.markdown('<p style="font-size: 1.1em; margin-bottom: 20px;">Enter your message below to check if it is spam or not.</p>', unsafe_allow_html=True)

st.markdown('<p style="font-size: 1em; text-align: left; margin-bottom: -15px;">Text:</p>', unsafe_allow_html=True)
user_input = st.text_area(
    "Text:",
    placeholder="Enter your message here...",
    height=150,
    label_visibility="collapsed"
)

if st.button("Check", key="check_btn"):
    if user_input:
  
        display_message, css_class = predict_message(user_input, model, vectorizer)
        
        icon = '🚨' if css_class == 'spam' else '✅'
        
        st.markdown(
            f"""
            <div class="result-box result-{css_class}">
                {icon} The message is: {display_message}
            </div>
            """, 
            unsafe_allow_html=True
        )
    else:
        st.warning("Please enter a message to check.")

st.markdown('<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css">', unsafe_allow_html=True)