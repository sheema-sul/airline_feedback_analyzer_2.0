import streamlit as st
from predict import analyze_text

# PAGE CONFIG
st.set_page_config(
    page_title="Airline Feedback Analyzer",
    page_icon="✈️",
    layout="centered"
)

# CUSTOM STYLING
st.markdown("""
<style>
[data-testid="stAppViewContainer"] {
    background-color: #0E1117;
}

h1, h2, h3, p, label {
    color: white !important;
}

textarea {
    background-color: #1e1e1e !important;
    color: white !important;
    border-radius: 10px !important;
    border: 1px solid #555 !important;
}
            
button {
    background-color: #4CAF50 !important;
    color: white !important;
    border-radius: 10px !important;
    padding: 8px 16px;
}
</style>
""", unsafe_allow_html=True)

# HEADER
st.title("✈️ Airline Feedback Analyzer")
st.markdown("Analyze airline-related feedback using NLP")
st.markdown("👉 Supports single or multiple inputs (one per line).")
st.markdown("---")

# INPUT
user_input = st.text_area("Enter your feedback:")

# BUTTON ACTION
if st.button("Analyze"):

    if user_input.strip():

        # MULTI-INPUT LOGIC
        inputs = user_input.split("\n")

        st.markdown("## 📊 Results")

        for text in inputs:
            if text.strip():

                result = analyze_text(text)

                st.markdown(f"### Input: {text}")

                # PRIORITY 
                priority = result['urgency']

                if priority == "High":
                    color = "#FF4B4B"   # Red
                elif priority == "Medium":
                    color = "#FFA500"   # Orange
                else:
                    color = "#4CAF50"   # Green

                st.markdown(
                    f"<p style='color:{color}; font-size:16px; margin-bottom:0px;'><b>Urgency:</b> {priority}</p>",
                    unsafe_allow_html=True
                )

                # DETAILS 
                st.markdown(f"""
**Sentiment:** {result['sentiment']}  
**Category:** {result['category']}  
**Severity:** {result['severity']}  
""")

                st.markdown("---")

                # INSIGHT 
                st.markdown(f"**Insight:** {result['insight']}")

                # RECOMMENDATION 
                st.markdown(f"**Recommendation:** {result['recommendation']}")

                st.markdown("-----")

    else:
        st.warning("Please enter some text before analyzing.")