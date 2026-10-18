
import streamlit as st
import ollama
from datetime import datetime

# ==========================================
# 1. PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="FitMate AI | Personal Fitness Coach",
    page_icon="💚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# 2. CUSTOM CSS
# ==========================================

st.markdown(
    """
    <style>
    .stApp {
        background-color: #f5f8f6;
    }

    .main-title {
        font-size: 42px;
        font-weight: 800;
        color: #176b4d;
        text-align: center;
        margin-bottom: 5px;
    }

    .subtitle {
        text-align: center;
        font-size: 17px;
        color: #52665c;
        margin-bottom: 25px;
    }

    .section-title {
        color: #176b4d;
        font-size: 24px;
        font-weight: 700;
    }

    .footer {
        text-align: center;
        color: #65766c;
        font-size: 13px;
        padding: 20px;
    }

    div.stButton > button {
        background-color: #176b4d;
        color: white;
        border-radius: 9px;
        border: none;
        min-height: 45px;
        font-weight: 600;
    }

    div.stButton > button:hover {
        background-color: #23845f;
        color: white;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ==========================================
# 3. HEADER
# ==========================================

st.markdown(
    '<div class="main-title">💚 FitMate AI</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Your Personal AI Fitness Coach | Build Healthy Habits, '
    'One Day at a Time'
    '</div>',
    unsafe_allow_html=True
)

st.success("🤖 AI Engine: Ollama + Qwen 2.5 1.5B")

st.divider()

# ==========================================
# 4. SIDEBAR
# ==========================================

with st.sidebar:
    st.title("💚 FitMate AI")

    st.write("Your personal fitness companion.")

    st.divider()

    st.subheader("✨ What You Get")

    st.markdown(
        """
        - 🗓️ 7-day workout plan
        - 🥗 Healthy diet tips
        - 💪 Daily motivation
        - 😴 Recovery guidance
        - 📥 Downloadable plan
        """
    )

    st.divider()

    st.caption("Powered by Python, Streamlit and Ollama")

# ==========================================
# 5. USER DETAILS
# ==========================================

st.markdown(
    '<div class="section-title">👤 Your Fitness Profile</div>',
    unsafe_allow_html=True
)

st.write("Enter your details to generate a personalized fitness plan.")

col1, col2 = st.columns(2)

with col1:
    age = st.number_input(
        "Age",
        min_value=18,
        max_value=100,
        value=22,
        step=1
    )

    weight = st.number_input(
        "Weight (kg)",
        min_value=20.0,
        max_value=300.0,
        value=60.0,
        step=0.5
    )

    goal = st.selectbox(
        "🎯 Fitness Goal",
        [
            "Weight Loss",
            "Muscle Gain",
            "General Fitness",
            "Improve Stamina",
            "Maintain Weight"
        ]
    )

with col2:
    time_available = st.selectbox(
        "⏰ Daily Workout Time",
        [
            "15 minutes",
            "30 minutes",
            "45 minutes",
            "60 minutes"
        ],
        index=1
    )

    fitness_level = st.selectbox(
        "💪 Fitness Level",
        [
            "Beginner",
            "Intermediate",
            "Advanced"
        ]
    )

    equipment = st.selectbox(
        "🏋️ Available Equipment",
        [
            "No equipment",
            "Dumbbells",
            "Gym equipment"
        ]
    )

st.divider()

# ==========================================
# 6. GENERATE FITNESS PLAN
# ==========================================

if st.button(
    "✨ Generate My Fitness Plan",
    use_container_width=True
):

    prompt = f"""
You are FitMate AI, a responsible personal fitness coach.

USER DETAILS:
Age: {age}
Weight: {weight} kg
Fitness goal: {goal}
Daily available time: {time_available}
Fitness level: {fitness_level}
Equipment: {equipment}

Create a personalized 7-day fitness plan.

Use these headings:

## 1. My Fitness Goal
Explain the goal briefly.

## 2. My 7-Day Workout Plan
Create a Monday-to-Sunday table with:
Day | Exercises | Duration

Respect the user's daily time limit.
Include suitable exercises, warm-ups, rest periods,
and at least one recovery day.

## 3. Healthy Diet Tips
Suggest breakfast, lunch, dinner, and snacks.
Include vegetables, fruits, balanced meals, protein sources,
and hydration.
Do not recommend extreme diets or invent calorie requirements
from age and weight alone.

## 4. Daily Motivation
Give one short motivational message for each day.

## 5. Recovery and Healthy Habits
Explain sleep, hydration, gradual progress, and recovery.

SAFETY:
Do not recommend extreme weight loss or unnecessary supplements.
Age and weight alone cannot determine nutritional requirements.
Recommend professional advice for medical conditions, injuries,
or special dietary needs.
Tell the user to stop exercising if they experience chest pain,
dizziness, or severe pain.

Use simple English and concise explanations.
"""

    st.divider()

    st.markdown(
        '<div class="section-title">'
        '📋 Your Personalized Fitness Plan'
        '</div>',
        unsafe_allow_html=True
    )

    plan_placeholder = st.empty()
    fitness_plan = ""

    try:
        with st.spinner("💚 FitMate AI is preparing your plan..."):

            response_stream = ollama.chat(
                model="qwen2.5:1.5b",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are FitMate AI, a responsible fitness "
                            "planning assistant. Follow the requested "
                            "headings, use readable Markdown tables, "
                            "and provide concise, safe recommendations."
                        )
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                stream=True,
                options={
                    "temperature": 0.3,
                    "num_predict": 1000
                }
            )

            for chunk in response_stream:
                fitness_plan += chunk["message"]["content"]

                plan_placeholder.markdown(
                    fitness_plan + " ▌"
                )

        if fitness_plan.strip():

            plan_placeholder.markdown(fitness_plan)

            st.success("🎉 Your fitness plan is ready!")

            st.download_button(
                label="📥 Download My Fitness Plan",
                data=fitness_plan,
                file_name="FitMate_AI_Fitness_Plan.txt",
                mime="text/plain",
                use_container_width=True
            )

            st.caption(
                "Generated on "
                + datetime.now().strftime("%d %B %Y, %I:%M %p")
            )

        else:
            st.warning(
                "The AI returned an empty response. Please try again."
            )

    except Exception as error:
        st.error("Unable to generate your fitness plan.")

        with st.expander("View technical error"):
            st.code(str(error))

        st.info(
            "Check that Ollama is running and Qwen 2.5 1.5B "
            "is installed. Run 'ollama list' in your terminal."
        )

# ==========================================
# 7. FOOTER
# ==========================================

st.divider()

st.markdown(
    """
    <div class="footer">
        💚 FitMate AI — Your Journey, Your Progress
        <br><br>
        Built with Python, Streamlit and Ollama
        <br>
        For general fitness education only; not a substitute
        for professional medical advice.
    </div>
    """,
    unsafe_allow_html=True
)
