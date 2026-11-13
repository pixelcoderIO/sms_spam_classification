import streamlit as st
import pickle
import nltk
import re
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer

st.set_page_config(
    page_title="CyberShield | SMS Security",
    layout="wide"
)


@st.cache_resource
def load_model():
    with open("model.pkl", "rb") as f:
        model = pickle.load(f)

    with open("vectorizer.pkl", "rb") as f:
        vectorizer = pickle.load(f)

    return model, vectorizer


model, tfidf = load_model()

nltk.download("punkt_tab", quiet=True)
nltk.download("stopwords", quiet=True)

ps = PorterStemmer()
stop_words = set(stopwords.words("english"))


def transform_text(text):
    text = text.lower()
    tokens = nltk.word_tokenize(text)

    words = []

    for word in tokens:
        if word.isalnum() and word not in stop_words:
            words.append(ps.stem(word))

    return " ".join(words)


st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #080d1c, #10152b, #11102a);
    color: #f1f5f9;
}

header[data-testid="stHeader"] {
    background: transparent;
}

.block-container {
    padding-top: 2rem;
    max-width: 1150px;
}

.hero {
    text-align: center;
    padding: 35px 15px;
}

.hero h1 {
    font-size: 43px;
    font-weight: 800;
    color: #ffffff;
}

.hero h1 span {
    color: #60a5fa;
}

.hero p {
    color: #a5b4fc;
    font-size: 16px;
}

.panel {
    background: rgba(25, 34, 62, 0.85);
    border: 1px solid #293b68;
    border-radius: 18px;
    padding: 25px;
    margin-bottom: 20px;
}

.result-safe {
    background: #063d35;
    border: 1px solid #10b981;
    border-radius: 15px;
    padding: 22px;
    text-align: center;
}

.result-spam {
    background: #481c2b;
    border: 1px solid #fb7185;
    border-radius: 15px;
    padding: 22px;
    text-align: center;
}

div.stButton > button {
    width: 100%;
    background: linear-gradient(90deg, #2563eb, #7c3aed);
    color: white;
    border: none;
    border-radius: 10px;
    height: 48px;
    font-size: 16px;
    font-weight: bold;
}

div.stButton > button:hover {
    border: 1px solid #93c5fd;
    color: white;
}

textarea {
    background: #111a33 !important;
    color: white !important;
}

footer {
    visibility: hidden;
}
</style>
""", unsafe_allow_html=True)


st.markdown("""
<div class="hero">
    <h1>Cyber<span>Shield</span></h1>
    <p>AI-Powered SMS Spam Detection</p>
</div>
""", unsafe_allow_html=True)


st.markdown('<div class="panel">', unsafe_allow_html=True)

st.subheader("SMS Security Scanner")
st.write("Enter a message below to analyze whether it is Spam or Ham.")

message = st.text_area(
    "Message input",
    placeholder="Paste your SMS message here...",
    height=150,
    label_visibility="collapsed"
)

scan = st.button("SCAN MESSAGE")

st.markdown('</div>', unsafe_allow_html=True)


if scan:

    if not message.strip():
        st.warning("Please enter a message before scanning.")

    else:
        with st.spinner("Analyzing message..."):

            processed = transform_text(message)
            vector_input = tfidf.transform([processed])

            prediction = model.predict(vector_input)[0]

            probabilities = model.predict_proba(vector_input)[0]
            confidence = max(probabilities) * 100

        st.markdown("---")
        st.subheader("Security Analysis")

        if prediction == 1:
            st.markdown("""
            <div class="result-spam">
                <h2>SPAM DETECTED</h2>
                <p>This message has been classified as Spam.</p>
            </div>
            """, unsafe_allow_html=True)

        else:
            st.markdown("""
            <div class="result-safe">
                <h2>SAFE MESSAGE (HAM)</h2>
                <p>This message has been classified as Ham.</p>
            </div>
            """, unsafe_allow_html=True)

        st.write("")

        st.markdown("### Model Prediction Probability")
        st.progress(int(confidence))
        st.write(f"Probability: **{confidence:.2f}%**")

        # Suspicious keyword analysis
        suspicious_words = [
            "free", "win", "winner", "prize", "claim",
            "urgent", "cash", "offer", "reward",
            "click", "congratulations", "call"
        ]

        found_words = [
            word for word in suspicious_words
            if re.search(
                r"\b" + re.escape(word) + r"\b",
                message.lower()
            )
        ]

        st.markdown("### Message Analysis")

        a, b = st.columns(2)

        with a:
            st.markdown("**Detected suspicious keywords**")

            if found_words:
                st.warning(", ".join(found_words))
            else:
                st.success("No listed suspicious keywords found.")

        with b:
            st.markdown("**Message information**")
            st.write(f"Characters: {len(message)}")
            st.write(f"Words: {len(message.split())}")

        # Scan history
        if "history" not in st.session_state:
            st.session_state.history = []

        st.session_state.history.insert(0, {
            "Message": message[:65],
            "Prediction": "Spam" if prediction == 1 else "Ham",
            "Confidence": f"{confidence:.2f}%"
        })


if "history" in st.session_state and st.session_state.history:

    st.markdown("---")
    st.subheader("Recent Scan History")

    st.dataframe(
        st.session_state.history,
        use_container_width=True,
        hide_index=True
    )


st.markdown("---")

st.markdown("""
<div style="text-align:center;color:#8492b5;padding:15px;">
    CyberShield | SMS Spam Detection System
</div>
""", unsafe_allow_html=True)
