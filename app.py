
import os
import requests
import streamlit as st

# ---------------- PAGE CONFIGURATION ----------------
st.set_page_config(
    page_title="FitMate AI | Personal Fitness Coach",
    page_icon="💪",
    layout="wide"
)

# ---------------- CUSTOM STYLING ----------------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #101827, #172b3a, #123b40);
    color: white;
}
.main-title {
    font-size: 44px;
    font-weight: 800;
    text-align: center;
    color: #63f5c8;
}
.subtitle {
    text-align: center;
    color: #d0dce5;
    font-size: 17px;
    margin-bottom: 28px;
}
div[data-testid="stForm"] {
    background: rgba(255,255,255,0.06);
    padding: 22px;
    border-radius: 18px;
    border: 1px solid rgba(255,255,255,0.12);
}
.stButton > button {
    background: #63f5c8;
    color: #10202a;
    border-radius: 10px;
    border: none;
    font-weight: bold;
    min-height: 45px;
}
.stButton > button:hover {
    background: #40ddb0;
    color: #10202a;
}
</style>
""", unsafe_allow_html=True)

# ---------------- HEADER ----------------
st.markdown(
    '<div class="main-title">💪 FitMate AI</div>',
    unsafe_allow_html=True
)
st.markdown(
    '<div class="subtitle">Your personal AI fitness and wellness companion</div>',
    unsafe_allow_html=True
)

st.write(
    "Create a personalized weekly workout plan, practical nutrition tips, "
    "and motivational guidance based on your goals."
)

# ---------------- USER INPUTS ----------------
with st.form("fitness_form_main"):
    st.subheader("👤 Tell us about yourself")

    col1, col2 = st.columns(2)

    with col1:
        age = st.number_input(
            "Age",
            min_value=16,
            max_value=100,
            value=21
        )

        weight = st.number_input(
            "Weight (kg)",
            min_value=25.0,
            max_value=300.0,
            value=60.0,
            step=0.5
        )

        height = st.number_input(
            "Height (cm)",
            min_value=100,
            max_value=250,
            value=160
        )

    with col2:
        goal = st.selectbox(
            "Fitness Goal",
            [
                "Weight Loss",
                "Muscle Gain",
                "General Fitness",
                "Improve Stamina",
                "Flexibility"
            ]
        )

        experience = st.selectbox(
            "Fitness Experience",
            ["Beginner", "Intermediate", "Advanced"]
        )

        activity_time = st.selectbox(
            "Available Workout Time Per Day",
            ["15 minutes", "30 minutes", "45 minutes",
             "60 minutes", "90 minutes"]
        )

    equipment = st.selectbox(
        "Available Equipment",
        [
            "No equipment",
            "Dumbbells",
            "Gym equipment",
            "Resistance bands"
        ]
    )

    dietary_preference = st.selectbox(
        "Dietary Preference",
        [
            "Vegetarian",
            "Non-vegetarian",
            "Vegan",
            "No preference"
        ]
    )

    restrictions = st.text_input(
        "Injuries, health limitations, or food allergies (optional)",
        placeholder="Enter any relevant limitations"
    )

    submitted = st.form_submit_button(
        "✨ Generate My Fitness Plan",
        use_container_width=True
    )

# ---------------- AI GENERATION ----------------
if submitted:

    # Read the secret securely from Streamlit Cloud
    try:
        api_key = st.secrets["GROQ_API_KEY"]
    except (KeyError, FileNotFoundError):
        api_key = os.getenv("GROQ_API_KEY", "")

    if not api_key:
        st.error(
            "API key not found. Add GROQ_API_KEY in "
            "Streamlit Cloud → Manage app → Settings → Secrets."
        )
        st.stop()

    prompt = f"""
Create a practical, personalized 7-day fitness and wellness plan.

USER DETAILS
- Age: {age}
- Weight: {weight} kg
- Height: {height} cm
- Goal: {goal}
- Experience: {experience}
- Workout time per day: {activity_time}
- Equipment: {equipment}
- Dietary preference: {dietary_preference}
- Health limitations or allergies: {restrictions or "Not specified"}

RESPONSE FORMAT

## 1. Personal Fitness Overview
Briefly explain the user's goal and a realistic approach.

## 2. Seven-Day Workout Plan
Give a separate plan for Monday to Sunday.
For each day, include:
- Exercise names
- Sets and repetitions or duration
- Approximate workout duration
- Rest or recovery guidance

Adapt exercises to the available equipment, experience, and time.
Include recovery days where appropriate.

## 3. Nutrition Tips
Provide practical, affordable meal ideas suitable for the dietary
preference. Include breakfast, lunch, dinner, and snack suggestions.
Avoid unsupported claims about supplements or guaranteed results.

## 4. Hydration and Sleep
Provide general, practical guidance.

## 5. Motivation and Consistency
Give three encouraging, realistic suggestions.

## 6. Weekly Progress Tracking
Suggest simple ways to track progress safely.

Keep the answer organized, understandable, and useful.
Do not diagnose medical conditions or prescribe treatment.
If health limitations are reported, recommend checking with a
qualified healthcare professional before starting relevant exercises.
"""

    with st.spinner("🤖 FitMate AI is preparing your personalized plan..."):
        try:
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "https://api.groq.com/openai/v1/models",
                    "messages": [
                        {
                            "role": "system",
                            "content": (
                                "You are FitMate AI, a responsible fitness "
                                "and wellness assistant. Give clear, practical "
                                "general guidance. Avoid medical diagnoses, "
                                "extreme diets, and unsafe exercise advice."
                            )
                        },
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.5,
                    "max_tokens": 2500
                },
                timeout=120
            )

            if response.ok:
                data = response.json()
                fitness_plan = data["choices"][0]["message"]["content"]

                st.success("Your fitness plan is ready! 🎉")
                st.markdown("---")
                st.markdown("## 🗓️ Your Personalized Fitness Plan")
                st.markdown(fitness_plan)

                st.download_button(
                    label="📥 Download My Fitness Plan",
                    data=fitness_plan,
                    file_name="my_fitness_plan.md",
                    mime="text/markdown",
                    use_container_width=True
                )

            else:
                try:
                    error_details = response.json().get(
                        "error", {}
                    ).get("message", "Unknown API error")
                except ValueError:
                    error_details = "The AI service returned an unexpected response."

                st.error(
                    f"AI service error ({response.status_code}): "
                    f"{error_details}"
                )

        except requests.exceptions.Timeout:
            st.error("The AI service took too long to respond. Please try again.")

        except requests.exceptions.RequestException:
            st.error(
                "Could not connect to the AI service. "
                "Check the connection and try again."
            )

st.markdown("---")
st.caption(
    "💚 FitMate AI | General wellness guidance, not a substitute "
    "for professional medical advice."
)

import os
import requests
import streamlit as st

# ---------------- PAGE CONFIGURATION ----------------
st.set_page_config(
    page_title="FitMate AI | Personal Fitness Coach",
    page_icon="💪",
    layout="wide"
)

# ---------------- CUSTOM STYLING ----------------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #101827, #172b3a, #123b40);
    color: white;
}
.main-title {
    font-size: 44px;
    font-weight: 800;
    text-align: center;
    color: #63f5c8;
}
.subtitle {
    text-align: center;
    color: #d0dce5;
    font-size: 17px;
    margin-bottom: 28px;
}
div[data-testid="stForm"] {
    background: rgba(255,255,255,0.06);
    padding: 22px;
    border-radius: 18px;
    border: 1px solid rgba(255,255,255,0.12);
}
.stButton > button {
    background: #63f5c8;
    color: #10202a;
    border-radius: 10px;
    border: none;
    font-weight: bold;
    min-height: 45px;
}
.stButton > button:hover {
    background: #40ddb0;
    color: #10202a;
}
</style>
""", unsafe_allow_html=True)

# ---------------- HEADER ----------------
st.markdown(
    '<div class="main-title">💪 FitMate AI</div>',
    unsafe_allow_html=True
)
st.markdown(
    '<div class="subtitle">Your personal AI fitness and wellness companion</div>',
    unsafe_allow_html=True
)

st.write(
    "Create a personalized weekly workout plan, practical nutrition tips, "
    "and motivational guidance based on your goals."
)

# ---------------- USER INPUTS ----------------
with st.form("fitness_form_main"):
    st.subheader("👤 Tell us about yourself")

    col1, col2 = st.columns(2)

    with col1:
        age = st.number_input(
            "Age",
            min_value=16,
            max_value=100,
            value=21
        )

        weight = st.number_input(
            "Weight (kg)",
            min_value=25.0,
            max_value=300.0,
            value=60.0,
            step=0.5
        )

        height = st.number_input(
            "Height (cm)",
            min_value=100,
            max_value=250,
            value=160
        )

    with col2:
        goal = st.selectbox(
            "Fitness Goal",
            [
                "Weight Loss",
                "Muscle Gain",
                "General Fitness",
                "Improve Stamina",
                "Flexibility"
            ]
        )

        experience = st.selectbox(
            "Fitness Experience",
            ["Beginner", "Intermediate", "Advanced"]
        )

        activity_time = st.selectbox(
            "Available Workout Time Per Day",
            ["15 minutes", "30 minutes", "45 minutes",
             "60 minutes", "90 minutes"]
        )

    equipment = st.selectbox(
        "Available Equipment",
        [
            "No equipment",
            "Dumbbells",
            "Gym equipment",
            "Resistance bands"
        ]
    )

    dietary_preference = st.selectbox(
        "Dietary Preference",
        [
            "Vegetarian",
            "Non-vegetarian",
            "Vegan",
            "No preference"
        ]
    )

    restrictions = st.text_input(
        "Injuries, health limitations, or food allergies (optional)",
        placeholder="Enter any relevant limitations"
    )

    submitted = st.form_submit_button(
        "✨ Generate My Fitness Plan",
        use_container_width=True
    )

# ---------------- AI GENERATION ----------------
if submitted:

    # Read the secret securely from Streamlit Cloud
    try:
        api_key = st.secrets["GROQ_API_KEY"]
    except (KeyError, FileNotFoundError):
        api_key = os.getenv("GROQ_API_KEY", "")

    if not api_key:
        st.error(
            "API key not found. Add GROQ_API_KEY in "
            "Streamlit Cloud → Manage app → Settings → Secrets."
        )
        st.stop()

    prompt = f"""
Create a practical, personalized 7-day fitness and wellness plan.

USER DETAILS
- Age: {age}
- Weight: {weight} kg
- Height: {height} cm
- Goal: {goal}
- Experience: {experience}
- Workout time per day: {activity_time}
- Equipment: {equipment}
- Dietary preference: {dietary_preference}
- Health limitations or allergies: {restrictions or "Not specified"}

RESPONSE FORMAT

## 1. Personal Fitness Overview
Briefly explain the user's goal and a realistic approach.

## 2. Seven-Day Workout Plan
Give a separate plan for Monday to Sunday.
For each day, include:
- Exercise names
- Sets and repetitions or duration
- Approximate workout duration
- Rest or recovery guidance

Adapt exercises to the available equipment, experience, and time.
Include recovery days where appropriate.

## 3. Nutrition Tips
Provide practical, affordable meal ideas suitable for the dietary
preference. Include breakfast, lunch, dinner, and snack suggestions.
Avoid unsupported claims about supplements or guaranteed results.

## 4. Hydration and Sleep
Provide general, practical guidance.

## 5. Motivation and Consistency
Give three encouraging, realistic suggestions.

## 6. Weekly Progress Tracking
Suggest simple ways to track progress safely.

Keep the answer organized, understandable, and useful.
Do not diagnose medical conditions or prescribe treatment.
If health limitations are reported, recommend checking with a
qualified healthcare professional before starting relevant exercises.
"""

    with st.spinner("🤖 FitMate AI is preparing your personalized plan..."):
        try:
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "llama-3.3-70b-versatile",
                    "messages": [
                        {
                            "role": "system",
                            "content": (
                                "You are FitMate AI, a responsible fitness "
                                "and wellness assistant. Give clear, practical "
                                "general guidance. Avoid medical diagnoses, "
                                "extreme diets, and unsafe exercise advice."
                            )
                        },
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.5,
                    "max_tokens": 2500
                },
                timeout=120
            )

            if response.ok:
                data = response.json()
                fitness_plan = data["choices"][0]["message"]["content"]

                st.success("Your fitness plan is ready! 🎉")
                st.markdown("---")
                st.markdown("## 🗓️ Your Personalized Fitness Plan")
                st.markdown(fitness_plan)

                st.download_button(
                    label="📥 Download My Fitness Plan",
                    data=fitness_plan,
                    file_name="my_fitness_plan.md",
                    mime="text/markdown",
                    use_container_width=True
                )

            else:
                try:
                    error_details = response.json().get(
                        "error", {}
                    ).get("message", "Unknown API error")
                except ValueError:
                    error_details = "The AI service returned an unexpected response."

                st.error(
                    f"AI service error ({response.status_code}): "
                    f"{error_details}"
                )

        except requests.exceptions.Timeout:
            st.error("The AI service took too long to respond. Please try again.")

        except requests.exceptions.RequestException:
            st.error(
                "Could not connect to the AI service. "
                "Check the connection and try again."
            )

st.markdown("---")
st.caption(
    "💚 FitMate AI | General wellness guidance, not a substitute "
    "for professional medical advice."
)
