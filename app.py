
import os
import requests
import streamlit as st

# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------
st.set_page_config(
    page_title="FitMate AI | Personal Fitness Coach",
    page_icon="💪",
    layout="wide",
)

# --------------------------------------------------
# CUSTOM STYLING
# --------------------------------------------------
st.markdown(
    """
    <style>
    .stApp {
        background-color: #f5f8fc;
    }
    .main-title {
        text-align: center;
        color: #17365d;
        font-size: 42px;
        font-weight: 800;
        margin-bottom: 5px;
    }
    .subtitle {
        text-align: center;
        color: #526579;
        font-size: 17px;
        margin-bottom: 28px;
    }
    .section-title {
        color: #17365d;
        font-weight: 700;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --------------------------------------------------
# HEADER
# --------------------------------------------------
st.markdown(
    '<div class="main-title">💪 FitMate AI</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="subtitle">'
    'Your personal AI fitness and wellness coach'
    '</div>',
    unsafe_allow_html=True,
)

st.info(
    "Tell FitMate about your fitness goals to receive "
    "a personalized workout and healthy lifestyle plan."
)

# --------------------------------------------------
# GROQ API CONFIGURATION
# --------------------------------------------------
def get_api_key():
    """Read the API key from Streamlit Secrets or environment."""

    try:
        secret_key = st.secrets.get("GROQ_API_KEY", "")
    except Exception:
        secret_key = ""

    return secret_key or os.getenv("GROQ_API_KEY", "")


def generate_fitness_plan(user_details):
    """Generate a fitness plan using the Groq API."""

    api_key = get_api_key()

    if not api_key:
        raise ValueError(
            "GROQ_API_KEY is missing. Add your Groq API key "
            "in Streamlit Cloud → App settings → Secrets."
        )

    prompt = f"""
You are FitMate AI, a responsible personal fitness and
wellness assistant.

Create a practical, beginner-friendly fitness plan using
the user's details below.

USER DETAILS
{user_details}

Include these sections:

1. Fitness goal summary
2. Weekly workout schedule
3. Exercises, sets, repetitions, and rest periods
4. Warm-up and cool-down routines
5. General nutrition guidance
6. Hydration and sleep recommendations
7. Progress tracking tips
8. Safety precautions

IMPORTANT:
- Adapt the plan to the user's experience, equipment,
  available time, dietary preferences, and restrictions.
- Make the plan realistic and easy to follow.
- Do not recommend crash diets, starvation, or extreme exercise.
- Do not promise specific weight-loss results.
- Respect injuries, medical conditions, and stated restrictions.
- If medical details suggest a need for professional advice,
  recommend consulting a qualified healthcare professional.
- Use clear headings and bullet points.
- Do not diagnose medical conditions.
"""

    url = "https://api.groq.com/openai/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": "openai/gpt-oss-20b",
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a helpful, safe, and practical "
                    "fitness planning assistant."
                ),
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        "temperature": 0.5,
        "max_tokens": 2500,
    }

    response = requests.post(
        url,
        headers=headers,
        json=payload,
        timeout=120,
    )

    if response.status_code != 200:
        try:
            error_data = response.json()
            error_message = error_data.get("error", {}).get(
                "message", response.text
            )
        except ValueError:
            error_message = response.text

        raise RuntimeError(
            f"Groq API returned HTTP {response.status_code}: "
            f"{error_message}"
        )

    data = response.json()

    choices = data.get("choices", [])
    if not choices:
        raise RuntimeError(
            "The AI service returned an empty response. Please try again."
        )

    plan = choices[0].get("message", {}).get("content", "")

    if not plan.strip():
        raise RuntimeError(
            "The AI did not return a fitness plan. Please try again."
        )

    return plan.strip()


# --------------------------------------------------
# FITNESS INPUT FORM
# IMPORTANT: There is only ONE form in this app.
# --------------------------------------------------
st.markdown(
    '<h3 class="section-title">📋 Your Fitness Profile</h3>',
    unsafe_allow_html=True,
)

with st.form(key="fitness_plan_form", clear_on_submit=False):

    col1, col2 = st.columns(2)

    with col1:
        age = st.number_input(
            "Age",
            min_value=13,
            max_value=100,
            value=21,
            step=1,
            key="profile_age",
        )

        height = st.number_input(
            "Height (cm)",
            min_value=100.0,
            max_value=250.0,
            value=165.0,
            step=1.0,
            key="profile_height",
        )

        weight = st.number_input(
            "Weight (kg)",
            min_value=25.0,
            max_value=300.0,
            value=60.0,
            step=0.5,
            key="profile_weight",
        )

        goal = st.selectbox(
            "Primary fitness goal",
            [
                "General fitness",
                "Weight loss",
                "Muscle gain",
                "Strength improvement",
                "Improve stamina",
                "Flexibility and mobility",
                "Healthy lifestyle",
            ],
            key="profile_goal",
        )

    with col2:
        experience = st.selectbox(
            "Fitness experience",
            [
                "Beginner",
                "Intermediate",
                "Advanced",
            ],
            key="profile_experience",
        )

        activity_days = st.selectbox(
            "Available workout days per week",
            [2, 3, 4, 5, 6, 7],
            index=2,
            key="profile_days",
        )

        workout_minutes = st.selectbox(
            "Time available per workout",
            [15, 20, 30, 45, 60, 90],
            index=3,
            key="profile_minutes",
        )

        equipment = st.selectbox(
            "Available equipment",
            [
                "No equipment (home workout)",
                "Dumbbells",
                "Resistance bands",
                "Full gym",
                "Bodyweight and basic equipment",
            ],
            key="profile_equipment",
        )

    diet = st.selectbox(
        "Dietary preference",
        [
            "Vegetarian",
            "Non-vegetarian",
            "Vegan",
            "No specific preference",
        ],
        key="profile_diet",
    )

    restrictions = st.text_area(
        "Injuries, health considerations, food restrictions, "
        "or other preferences (optional)",
        placeholder=(
            "Example: knee discomfort, lactose intolerance, "
            "or exercises I prefer to avoid"
        ),
        key="profile_restrictions",
    )

    submitted = st.form_submit_button(
        "✨ Generate My Fitness Plan",
        use_container_width=True,
    )


# --------------------------------------------------
# GENERATE THE PLAN
# --------------------------------------------------
if submitted:

    if age < 18:
        st.warning(
            "Because you are under 18, your plan should focus on "
            "healthy habits, appropriate activity, and adequate "
            "nutrition rather than aggressive weight-loss goals. "
            "Consider guidance from a qualified professional."
        )

    user_details = f"""
Age: {age}
Height: {height} cm
Weight: {weight} kg
Fitness goal: {goal}
Experience: {experience}
Workout days per week: {activity_days}
Available time per workout: {workout_minutes} minutes
Equipment: {equipment}
Dietary preference: {diet}
Health considerations and preferences: {
    restrictions.strip() or "None provided"
}
"""

    try:
        with st.spinner(
            "🤖 FitMate AI is creating your personalized plan..."
        ):
            generated_plan = generate_fitness_plan(user_details)

        st.session_state["generated_fitness_plan"] = generated_plan
        st.success("Your fitness plan is ready!")

    except ValueError as error:
        st.error(str(error))

    except requests.exceptions.Timeout:
        st.error(
            "The AI service took too long to respond. "
            "Please try again in a moment."
        )

    except requests.exceptions.RequestException as error:
        st.error(
            "Could not connect to the AI service. "
            "Check your internet connection and try again."
        )
        st.caption(f"Technical details: {error}")

    except RuntimeError as error:
        st.error(str(error))

    except Exception as error:
        st.error("Something unexpected happened while creating your plan.")
        st.caption(f"Technical details: {error}")


# --------------------------------------------------
# DISPLAY THE GENERATED PLAN
# --------------------------------------------------
if st.session_state.get("generated_fitness_plan"):

    st.divider()

    st.markdown(
        '<h3 class="section-title">🎯 Your Personalized Plan</h3>',
        unsafe_allow_html=True,
    )

    plan = st.session_state["generated_fitness_plan"]

    st.markdown(plan)

    st.download_button(
        label="📥 Download My Fitness Plan",
        data=plan,
        file_name="my_fitness_plan.txt",
        mime="text/plain",
        key="download_fitness_plan",
        use_container_width=True,
    )

    st.caption(
        "Your plan is general wellness guidance, not a medical diagnosis "
        "or a substitute for professional medical advice."
    )

# --------------------------------------------------
# FOOTER
# --------------------------------------------------
st.divider()

st.markdown(
    "<div style='text-align:center; color:#526579;'>"
    "Built with Streamlit and Groq AI · FitMate AI 💙"
    "</div>",
    unsafe_allow_html=True,
)
