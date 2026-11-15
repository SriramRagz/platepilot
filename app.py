
import os
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

# ---------------------------------------
# 1. PAGE CONFIGURATION
# ---------------------------------------

st.set_page_config(
    page_title="PlatePilot | AI Breakfast Companion",
    page_icon="🍽️",
    layout="wide"
)

# ---------------------------------------
# 2. LOAD ENVIRONMENT VARIABLES
# ---------------------------------------

project_root = Path(__file__).resolve().parents[2]
load_dotenv(project_root / ".env", override=True)

# ---------------------------------------
# 3. CUSTOM UI STYLING
# ---------------------------------------

st.markdown("""
<style>
.stApp {
    background-color: #101B18;
}

.block-container {
    max-width: 1050px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}

.hero {
    background: linear-gradient(120deg, #183C32, #285B43);
    padding: 35px;
    border-radius: 18px;
    margin-bottom: 28px;
    border: 1px solid #47765C;
}

.hero h1 {
    color: #F4F7E9;
    font-size: 42px;
}

.hero p {
    color: #D7E7D9;
    font-size: 17px;
}

.section-label {
    color: #D8E8D5;
    font-size: 23px;
    font-weight: 650;
    margin-bottom: 12px;
}

div[data-testid="stVerticalBlockBorderWrapper"] {
    background-color: #192923;
    border-radius: 14px;
    border-color: #385447;
}

div.stButton > button[kind="primary"] {
    background-color: #B7D99B;
    color: #17271D;
    border: none;
    border-radius: 9px;
    font-weight: 700;
    min-height: 48px;
}

div.stButton > button[kind="primary"]:hover {
    background-color: #D0E9B7;
    color: #17271D;
}

.footer {
    text-align: center;
    color: #A8B8AC;
    font-size: 13px;
    padding-top: 20px;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------
# 4. HERO SECTION
# ---------------------------------------

st.markdown("""
<div class="hero">
    <h1>PlatePilot</h1>
    <p><b>Your Smart AI Breakfast Companion</b></p>
    <p>
        Turn everyday ingredients into delicious breakfast ideas.
        Personalised recommendations, powered by AI.
    </p>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------
# 5. BREAKFAST PLANNER
# ---------------------------------------

st.markdown(
    '<div class="section-label">Create Your Breakfast Plan</div>',
    unsafe_allow_html=True
)

with st.container(border=True):

    col1, col2 = st.columns(2)

    with col1:
        breakfast_preference = st.selectbox(
            "What are you in the mood for?",
            [
                "Healthy and Nutritious",
                "Quick and Easy",
                "Traditional Indian",
                "Weight Management",
                "High Energy"
            ]
        )

    with col2:
        dietary_preference = st.selectbox(
            "Your dietary preference",
            [
                "Vegetarian",
                "Vegan",
                "High Protein",
                "Non-Vegetarian",
                "No Specific Preference"
            ]
        )

    ingredients = st.text_area(
        "What ingredients do you have?",
        placeholder="Example: Oats, banana, almonds, milk...",
        height=110
    )

    number_of_suggestions = st.slider(
        "How many ideas would you like?",
        min_value=1,
        max_value=10,
        value=3
    )

    generate = st.button(
        "Generate My Breakfast Plan",
        type="primary",
        use_container_width=True
    )

# ---------------------------------------
# 6. DIETARY RULES
# ---------------------------------------

dietary_rules = {
    "Vegetarian": (
        "Do not use meat, fish or seafood. "
        "Dairy is permitted. Do not use eggs."
    ),
    "Vegan": (
        "Do not use meat, fish, seafood, dairy, eggs or honey. "
        "Use only plant-based ingredients."
    ),
    "High Protein": (
        "Prioritise protein-rich ingredients such as lentils, "
        "beans, tofu, paneer, eggs or nuts. "
        "Avoid unsupported protein claims."
    ),
    "Non-Vegetarian": (
        "Eggs, meat and fish are permitted. "
        "Suggest balanced meals."
    ),
    "No Specific Preference": (
        "Suggest balanced breakfast options."
    )
}

# ---------------------------------------
# 7. AI RECOMMENDATION GENERATION
# ---------------------------------------

if generate:

    if not ingredients.strip():

        st.warning("Please enter your available ingredients.")

    elif not os.getenv("OPENAI_API_KEY"):

        st.error(
            "OpenAI API key was not found. "
            "Please check your environment configuration."
        )

    else:

        try:

            with st.spinner(
                "PlatePilot is preparing your personalised plan..."
            ):

                llm = ChatOpenAI(
                    model="gpt-4o-mini",
                    temperature=0.5
                )

                prompt = f"""
You are PlatePilot, an intelligent Indian breakfast planning assistant.

Generate exactly {number_of_suggestions} unique breakfast recommendations.

USER PREFERENCES:
Breakfast preference: {breakfast_preference}
Dietary preference: {dietary_preference}
Available ingredients: {ingredients}

STRICT DIETARY RULES:
{dietary_rules[dietary_preference]}

RECOMMENDATION RULES:
1. Strictly follow the selected dietary preference.
2. Prioritise ingredients supplied by the user.
3. Never claim an unavailable ingredient is available.
4. Clearly separate available and additional ingredients.
5. Prefer complete, satisfying breakfast meals.
6. Prioritise Indian breakfast options when Traditional Indian is selected.
7. Do not return only chutneys, sauces or beverages as complete meals.
8. Avoid repeating similar recipes.
9. Do not invent precise calorie, protein or nutritional values.
10. Avoid unsupported health claims.
11. Return exactly {number_of_suggestions} recommendations.

FOR EACH RECOMMENDATION USE THIS FORMAT:

### Recipe: [Breakfast Name]

**Available Ingredients Used:**
- List ingredients supplied by the user.

**Additional Ingredients Needed:**
- List additional ingredients, or None.

**Preparation Steps:**
1. Explain the first step.
2. Explain the next step.
3. Complete the preparation instructions.

**Nutritional Highlight:**
Provide a brief, realistic description of the ingredients' general nutritional benefits.

At the end of each recommendation, write:
---RECIPE---

Do not include an introduction or conclusion.
"""

                response = llm.invoke(prompt)

            # ---------------------------------------
            # 8. DISPLAY RECOMMENDATION CARDS
            # ---------------------------------------

            st.markdown("---")

            st.markdown(
                '<div class="section-label">'
                'Your Personalised Breakfast Recommendations'
                '</div>',
                unsafe_allow_html=True
            )

            recipes = response.content.split("---RECIPE---")

            valid_recipes = [
                recipe.strip()
                for recipe in recipes
                if recipe.strip()
            ]

            st.success(
                f"{len(valid_recipes)} breakfast recommendations generated!"
            )

            for index, recipe in enumerate(valid_recipes, start=1):

                with st.container(border=True):

                    st.markdown(
                        f"**BREAKFAST RECOMMENDATION {index}**"
                    )

                    st.markdown(recipe)

        except Exception:

            st.error(
                "We couldn't generate your recommendations. "
                "Please check your API configuration and try again."
            )

# ---------------------------------------
# 9. FOOTER
# ---------------------------------------

st.markdown("---")

st.markdown("""
<div class="footer">
    PlatePilot | Your Smart AI Breakfast Companion<br>
    Powered by Python, Streamlit, LangChain and GPT-4o-mini
</div>
""", unsafe_allow_html=True)
