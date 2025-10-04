import streamlit as st
import pickle
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
import os

# --- 1. CONFIGURATION AND CUSTOM CSS STYLING ---

# Custom CSS to mimic the original Django/HTML layout (centered card, colors, font)
CUSTOM_CSS = """
<style>
    /* Use Roboto font and set the background gradient */
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700&display=swap');
    
    body {
        font-family: 'Roboto', sans-serif !important;
    }
    
    /* Apply the custom background gradient to the whole page */
    .stApp {
        background: linear-gradient(to right top, #000000, #0a0a0a, #121212, #181818, #1d1d1e, #262632, #2e2f47, #37395d, #fc4b11);
    }
    
    /* Center the main content column and apply the card style */
    /* This class selector targets the main container where content sits */
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
        background-color: #6a11cb;
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

    /* Style for the result text (mimicking the bold center display) */
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
    layout="centered", # Ensure Streamlit content is centered
    initial_sidebar_state="collapsed",
)

# Inject the custom CSS
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
    """
    Transforms the input message and predicts.
    Returns the descriptive message and the CSS class string (spam/ham).
    """
    if not model or not vectorizer:
        # Failsafe if model loading failed
        return 'Server Error: Model Initialization Failed', 'spam'
        
    # Transform message using the loaded vectorizer
    message_vector = vectorizer.transform([message])
    prediction = model.predict(message_vector)[0]
    
    # FIX: Check if the prediction is the integer 1 (Spam) or 0 (Ham)
    if prediction == 1:
        return 'Likely Scam', 'spam'
    else:
        # Assuming 0 is the non-spam class
        return 'Likely Not Spam', 'ham'


# --- 4. STREAMLIT APP LAYOUT ---

# Header Section
st.markdown(f'<h1 style="color: #6a11cb; font-size: 2em; margin-bottom: 5px;"><i class="fas fa-shield-alt"></i> Spam Detection</h1>', unsafe_allow_html=True)
st.markdown('<p style="font-size: 1.1em; margin-bottom: 20px;">Enter your message below to check if it is spam or not.</p>', unsafe_allow_html=True)


# Input Area
st.markdown('<p style="font-size: 1em; text-align: left; margin-bottom: -15px;">Text:</p>', unsafe_allow_html=True)
user_input = st.text_area(
    "Text:",
    placeholder="Enter your message here...",
    height=150,
    label_visibility="collapsed"
)

# Check Button
if st.button("Check", key="check_btn"):
    if user_input:
        # Run prediction
        display_message, css_class = predict_message(user_input, model, vectorizer)
        
        # Determine icon
        icon = '🚨' if css_class == 'spam' else '✅'
            
        # Display the result using the custom CSS classes
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

# Add Font Awesome dependency for icons (used in H1)
st.markdown('<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css">', unsafe_allow_html=True)