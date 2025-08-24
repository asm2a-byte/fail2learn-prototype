import sys
import os
import re

# Ajoute le dossier parent au path pour pouvoir importer `src`
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
import pandas as pd
from src.rl_agent import propose_strategy
from src.ai_chat import ask_mistral

# ========= Extraction par REGEX =========
def extract_conditions(text):
    text = text.lower()
    temp = None
    ph = None
    solvent = None

    # Température (ex: 25°C, 100 c, 50 degrees)
    match = re.search(r"(\d+)\s?(°|c|degrees)", text)
    if match:
        temp = float(match.group(1))

    # pH (ex: pH 7, pH=3)
    match = re.search(r"ph\s*=?\s*(\d+(\.\d+)?)", text)
    if match:
        ph = float(match.group(1))

    # Solvants connus
    known_solvents = ["water", "ethanol", "acetone", "methanol", "dichloromethane"]
    for s in known_solvents:
        if s in text:
            solvent = s
            break

    return temp, solvent, ph


# ========= Configuration Streamlit =========
st.set_page_config(page_title="Fail2LearnLab", layout="centered")
st.title(" Fail2LearnLab")
st.write("Transform failed chemical experiments into smarter strategies.")

# ========= Charger les données =========
df = pd.read_csv("data/failures_data.csv")
solvents = df["solvent"].unique().tolist()

# ========= Formulaire d'expérience =========
st.header(" Submit an Experimental Condition")

with st.form("experiment_form"):
    temperature = st.slider("Temperature (°C)", 20, 120, 70)
    solvent = st.selectbox("Solvent", solvents)
    pH = st.slider("pH", 1.0, 14.0, 7.0)
    time = st.slider("Reaction Time (min)", 5, 180, 60)
    submitted = st.form_submit_button("Check Experiment")

if submitted:
    match = df[
        (df["solvent"] == solvent) &
        (df["temperature_C"].round() == temperature) &
        (df["pH"].round() == round(pH)) &
        (df["reaction_time_min"].round() == time)
    ]
    if not match.empty:
        result = match["result"].values[0]
        if result == 0:
            st.error("❌ This experiment previously failed.")
        else:
            st.success("✅ This experiment previously succeeded.")
    else:
        st.info("ℹ️ This experiment has not been tested before.")

# ========= Suggestion d'IA =========
st.header(" AI-Suggested Strategy")
if st.button("Propose a New Strategy"):
    suggestion = propose_strategy()
    st.write("Here is a safer strategy to try:")
    st.json(suggestion)

# ========= Table des échecs =========
st.header(" Known Failed Experiments")
st.dataframe(df[df["result"] == 0].head(10))

# ========= Chatbot =========
st.header(" Ask Fail2LearnLab AI")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

user_input = st.text_input("Ask a question about experiments or failures")

if user_input:
    temp, solvent, ph = extract_conditions(user_input)
    context = ""

    # Ajouter contexte si paramètres détectés
    if temp or solvent or ph:
        matches = df.copy()
        if temp:
            matches = matches[(df["temperature_C"].round() == round(temp))]
        if solvent:
            matches = matches[(df["solvent"] == solvent)]
        if ph:
            matches = matches[(df["pH"].round() == round(ph))]

        if not matches.empty:
            failures = matches[matches["result"] == 0]
            successes = matches[matches["result"] == 1]
            if not failures.empty:
                context += f"⚠️ This combination (temp={temp}, solvent={solvent}, pH={ph}) has failed in {len(failures)} past experiments.\n"
            elif not successes.empty:
                context += f"✅ This combination (temp={temp}, solvent={solvent}, pH={ph}) has succeeded in previous experiments.\n"
        else:
            context += "ℹ️ This combination has not been tested in our database.\n"

    # Appel IA avec le contexte réel
    response = ask_mistral(user_input, context)

    st.session_state.chat_history.append(("🧪 You", user_input))
    st.session_state.chat_history.append(("🤖 Fail2LearnBot", response))

# Afficher l’historique
for sender, message in st.session_state.chat_history:
    st.markdown(f"**{sender}:** {message}")

# ========= Footer =========
st.markdown("---")
st.markdown("© 2025 [fail2learnlab.com](http://fail2learnlab.com) | Built with ❤️ + AI")
