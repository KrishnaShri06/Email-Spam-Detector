import streamlit as st
import pickle
import os
import json
import sys

def output_json_and_exit(data):
    print(json.dumps(data))
    sys.exit(0)

api_mode = None
try:
    api_mode = st.query_params.get("api")
except:
    pass


if api_mode == "true":

    MODEL_FILE = 'spam_model.pkl'
    VECTORIZER_FILE = 'vectorizer.pkl'

    @st.cache_resource
    def load_artifacts():
        try:
            with open(MODEL_FILE, 'rb') as file:
                model = pickle.load(file)

            with open(VECTORIZER_FILE, 'rb') as file:
                vectorizer = pickle.load(file)

            return model, vectorizer

        except FileNotFoundError:
            return None, None

    model, vectorizer = load_artifacts()

    message = st.query_params.get("message")

    def predict_message_api(message, model, vectorizer):
        if not model or not vectorizer:
            return 'Server Error: Model Initialization Failed', 'spam', 0.00

        message_vector = vectorizer.transform([message])
        probabilities = model.predict_proba(message_vector)[0]
        prediction_index = model.predict(message_vector)[0]

        confidence_float = probabilities[1] if prediction_index == 1 else probabilities[0]
        prediction_label = "spam" if prediction_index == 1 else "ham"

        return "OK", prediction_label, confidence_float

    if not model or not vectorizer:
        output_json_and_exit({"status": "error", "reason": "Server Error: Model files not found on disk."})

    if not message:
        output_json_and_exit({"status": "error", "reason": "Missing 'message' query parameter. Use: ?api=true&message=..."})


    display_message, prediction_label, confidence_float = predict_message_api(message, model, vectorizer)

    response_data = {
        "status": "success",
        "prediction": prediction_label,
        "confidence": confidence_float
    }

    output_json_and_exit(response_data)


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

    .stButton>button {
        background-color: rgb(203 70 17);
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
        font-size: 1.2em;
        font-weight: bold;
        text-align: center;
        line-height: 1.5;
    }

    .result-spam {
        background-color: #ffdddd;
        color: #d8000c;
        border: 1px solid #d8000c;
    }

    .result-ham {
        background-color: #e0ffe0;
        color: #008000;
        border: 1px solid #008000;
    }

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


MODEL_FILE = 'spam_model.pkl'
VECTORIZER_FILE = 'vectorizer.pkl'

@st.cache_resource
def load_artifacts():
    try:
        with open(MODEL_FILE, 'rb') as file:
            model = pickle.load(file)

        with open(VECTORIZER_FILE, 'rb') as file:
            vectorizer = pickle.load(file)

        return model, vectorizer

    except FileNotFoundError:
        st.error(f"Error: Required file not found. Ensure {MODEL_FILE} and {VECTORIZER_FILE} are deployed.")
        return None, None


def predict_message(message, model, vectorizer):

    if not model or not vectorizer:
        return 'Server Error: Model Initialization Failed', 'spam', 0.00, "0.00%"

    message_vector = vectorizer.transform([message])

    probabilities = model.predict_proba(message_vector)[0]

    prediction_index = model.predict(message_vector)[0]

    if prediction_index == 1:
        display_message = 'Likely Scam'
        css_class = 'spam'
        confidence_score = probabilities[1]
    else:
        display_message = 'Likely Not Spam'
        css_class = 'ham'
        confidence_score = probabilities[0]

    score_percent = f"{confidence_score * 100:.2f}%"

    return display_message, css_class, confidence_score, score_percent


model, vectorizer = load_artifacts()

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

        display_message, css_class, confidence_float, score_percent = predict_message(user_input, model, vectorizer)

        icon = '🚨' if css_class == 'spam' else '✅'

        st.markdown(
            f"""
            <div class="result-box result-{css_class}">
                {icon} The message is: <strong>{display_message}</strong>
                <br>
                Confidence Score: <strong>{score_percent}</strong>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.warning("Please enter a message to check.")

st.markdown('<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css">', unsafe_allow_html=True)
