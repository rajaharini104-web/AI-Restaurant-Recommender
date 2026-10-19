import os
import streamlit as st
from groq import Groq


# -----------------------------------------
# PAGE CONFIGURATION
# -----------------------------------------

st.set_page_config(
    page_title="AI Restaurant Recommender",
    page_icon="🍽️",
    layout="wide"
)


# -----------------------------------------
# GROQ CONFIGURATION
# -----------------------------------------

# If this model is unavailable to your account,
# select a currently available model from:
# https://console.groq.com/docs/models

MODEL_NAME = "openai/gpt-oss-120b"


def get_api_key():
    """Read the Groq API key from Streamlit Secrets or environment."""

    try:
        key = st.secrets.get("GROQ_API_KEY", "")
    except Exception:
        key = ""

    if not key:
        key = os.environ.get("GROQ_API_KEY", "")

    return key


# -----------------------------------------
# PAGE DESIGN
# -----------------------------------------

st.markdown(
    """
    <style>
    .main {
        background-color: #fffaf5;
    }

    .main-title {
        text-align: center;
        font-size: 38px;
        font-weight: 800;
        color: #8b3a24;
    }

    .subtitle {
        text-align: center;
        font-size: 17px;
        color: #785b50;
        margin-bottom: 25px;
    }

    .info-note {
        background-color: #fff0e5;
        padding: 16px;
        border-radius: 12px;
        border: 1px solid #f0d3c3;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# -----------------------------------------
# HEADER
# -----------------------------------------

st.markdown(
    '<div class="main-title">🍽️ AI Restaurant Recommender</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Discover delicious, budget-friendly meals that match '
    'your taste and health goals.'
    '</div>',
    unsafe_allow_html=True
)

st.divider()


# -----------------------------------------
# USER INPUTS
# -----------------------------------------

st.subheader("🥗 Tell Us Your Food Preferences")

with st.form("restaurant_form"):

    col1, col2 = st.columns(2)

    with col1:

        food_preference = st.selectbox(
            "Food Preference",
            [
                "Vegetarian",
                "Non-Vegetarian",
                "Vegan",
                "Eggetarian",
                "Any Preference"
            ]
        )

        budget = st.number_input(
            "Budget Per Meal (₹)",
            min_value=30,
            max_value=5000,
            value=150,
            step=10
        )

        cuisine = st.selectbox(
            "Preferred Cuisine",
            [
                "South Indian",
                "North Indian",
                "Chinese",
                "Italian",
                "Mexican",
                "Continental",
                "Japanese",
                "Any Cuisine"
            ]
        )

    with col2:

        health_goal = st.selectbox(
            "Health Goal",
            [
                "Balanced Nutrition",
                "Weight Management",
                "High Protein",
                "Low Sugar",
                "Heart-Healthy Eating",
                "Muscle Building",
                "Light and Low-Calorie Meals"
            ]
        )

        meal_type = st.selectbox(
            "Meal Type",
            [
                "Breakfast",
                "Lunch",
                "Dinner",
                "Snacks",
                "Any Meal"
            ]
        )

        location = st.text_input(
            "City or Location (Optional)",
            placeholder="Example: Madurai"
        )

    dietary_restrictions = st.text_input(
        "Allergies or Dietary Restrictions (Optional)",
        placeholder="Example: Peanuts, lactose, gluten"
    )

    additional_preferences = st.text_area(
        "Additional Preferences (Optional)",
        placeholder=(
            "Example: Simple homemade food, less oil, "
            "easy-to-find ingredients, quick preparation"
        )
    )

    submitted = st.form_submit_button(
        "✨ Recommend 5 Meals",
        use_container_width=True
    )


# -----------------------------------------
# GENERATE RECOMMENDATIONS
# -----------------------------------------

if submitted:

    if budget < 30:
        st.warning("Please enter a valid meal budget.")

    elif not get_api_key():
        st.error(
            "Groq API key not found. Add GROQ_API_KEY "
            "to your Streamlit Cloud Secrets."
        )

    else:

        client = Groq(api_key=get_api_key())

        prompt = f"""
You are a practical food recommendation assistant.

Recommend EXACTLY FIVE suitable meal options based on the
user's food preferences, budget, cuisine, and health goal.

USER PREFERENCES:
- Food preference: {food_preference}
- Maximum budget per meal: INR {budget}
- Preferred cuisine: {cuisine}
- Health goal: {health_goal}
- Meal type: {meal_type}
- City or location: {location or "Not specified"}
- Allergies and dietary restrictions: {dietary_restrictions or "None specified"}
- Additional preferences: {additional_preferences or "None specified"}

IMPORTANT RULES:

1. Recommend exactly five different meal options.
2. Respect the user's vegetarian, non-vegetarian, vegan,
   or eggetarian preference.
3. Do not include ingredients listed as allergies or restrictions.
4. Keep estimated meal costs within the user's budget.
5. Use Indian Rupees (INR).
6. If a location is provided, consider commonly available
   ingredients and regional food preferences.
7. Do not claim a restaurant is open or that a particular dish
   is available at a specific restaurant unless verified.
8. If the location is provided, you may suggest types of places
   where the meal could be found, but label this as a suggestion.
9. Provide approximate calories per serving, not falsely precise
   nutritional measurements.
10. Clearly state that calories and prices vary by portion,
    recipe, restaurant, and location.
11. Consider the selected health goal without making medical claims.
12. If allergies are specified, avoid the named ingredients and
    mention that users should confirm cross-contamination risks
    with food providers.
13. Do not describe a meal as guaranteed to cause weight loss
    or treat a health condition.

OUTPUT FORMAT:

# Your Personalized Meal Recommendations

For each of the five recommendations, use:

## Meal 1: [Meal Name]

**Description:** Explain the meal briefly.

**Estimated Cost:** ₹ amount per serving.

**Estimated Calories:** Approximate kcal per serving.

**Cuisine:** Name the cuisine.

**Main Ingredients:** List the main ingredients.

**Why It Matches Your Goal:** Explain its suitability for
the user's selected preferences and health goal.

**Where to Find or Prepare It:** Suggest a suitable type of
restaurant or a simple preparation approach.

Repeat for meals 2 through 5.

Finish with a comparison table containing:
- Meal name
- Estimated cost
- Estimated calories
- Main benefit

Then provide three practical tips for choosing meals within
the user's budget and preferences.

Use clear headings and a friendly, informative tone.
"""

        try:

            with st.spinner(
                "👨‍🍳 Finding meals that match your preferences..."
            ):

                response = client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "You are a helpful food recommendation "
                                "assistant. Prioritize affordability, "
                                "dietary preferences, and realistic "
                                "nutrition estimates."
                            )
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    temperature=0.4,
                    max_tokens=3500
                )

                recommendations = (
                    response.choices[0].message.content
                )

            if not recommendations:
                st.warning(
                    "The AI returned an empty response. Please try again."
                )

            else:

                st.success("Your five meal recommendations are ready!")

                st.subheader("🥘 Recommended Meals")

                st.markdown(recommendations)

                st.info(
                    "Prices and calorie counts are estimates, not "
                    "verified restaurant listings or laboratory "
                    "nutrition measurements. Actual values vary."
                )

                st.download_button(
                    label="📥 Download Meal Recommendations",
                    data=recommendations,
                    file_name="meal_recommendations.md",
                    mime="text/markdown",
                    use_container_width=True
                )

        except Exception as error:

            message = str(error)
            lower_message = message.lower()

            if (
                "model_not_found" in lower_message
                or "404" in message
            ):
                st.error(
                    "The selected Groq model is unavailable. "
                    "Check the current model list and update "
                    "MODEL_NAME in app.py."
                )

            elif (
                "authentication" in lower_message
                or "invalid_api_key" in lower_message
                or "401" in message
            ):
                st.error(
                    "API authentication failed. Check your "
                    "GROQ_API_KEY in Streamlit Cloud Secrets."
                )

            elif "429" in message:
                st.error(
                    "The API rate or usage limit was reached. "
                    "Check your Groq account limits and try again later."
                )

            else:
                st.error(
                    "Unable to generate recommendations. "
                    "Please check your API configuration and try again."
                )

                with st.expander("Technical details"):
                    st.code(message)


# -----------------------------------------
# FOOTER
# -----------------------------------------

st.divider()

st.markdown(
    """
    <p style="text-align:center; color:#785b50;">
        🍽️ AI Restaurant Recommender |
        Built with Python, Streamlit and Groq
    </p>
    """,
    unsafe_allow_html=True
)