import streamlit as st
import os
st.set_page_config(page_title="AI Travel Planner", layout="wide")

# Other Streamlit code follows...
import openai
from tavily import TavilyClient

# ---- API Keys ----
import os
TAVILY_API_KEY = "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"
OPENROUTER_API_KEY = "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"

# Initialize Tavily Client
tavily_client = TavilyClient(api_key=TAVILY_API_KEY)

client = openai.OpenAI(
    api_key=OPENROUTER_API_KEY,  
    base_url="https://openrouter.ai/api/v1"
)
# Function to call OpenRouter (Mistral AI)
def chat_with_openrouter(prompt):
    response = client.chat.completions.create(
        model="mistralai/mistral-7b-instruct:free",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()

# ---- Streamlit UI Setup ----
st.set_page_config(page_title="AI Travel Planner", layout="wide")
st.title("🌍 AI Travel Planner")
st.write("Plan your trip with AI-powered recommendations!")

# ---- Step 1: Get Destination ----
destination = st.text_input("Enter your travel destination:", placeholder="E.g., Japan, Italy, Sri Lanka")

if destination:
    st.session_state.destination = destination
    st.write(f"📍 **Destination:** {destination}")

    # Step 2: Ask for Budget & Trip Duration
    budget = st.selectbox("Budget Preference:", ["Budget", "Moderate", "Luxury"])
    trip_duration = st.slider("Trip Duration (Days):", 1, 14, 3)

    # Step 3: Ask for Interests
    interests = st.multiselect("Select Your Interests:", ["Nightlife", "Adventure", "Relaxation", "History", "Food", "Culture", "Wildlife"])

    if st.button("Get Top 10 Places"):
        # Step 4: Fetch Places Using Tavily Search API
        query = f"Best places to visit in {destination}"
        search_results = tavily_client.search(query=query, search_depth="basic", max_results=5)

        # Extract titles from Tavily results
        titles = [result["title"] for result in search_results["results"]]
        title_text = "\n".join(titles)

        # Step 5: Extract Only Place Names Using OpenRouter
        prompt_places = f"""
        Extract **only the top 10 famous places** to visit in {destination} from the travel guides below.
        Return as a **numbered list** (strictly 10 places).
        Do **not** add explanations, just the names.

        **Travel Guides:**
        {title_text}
        """

        places_response = chat_with_openrouter(prompt_places)
        places = [place.split(". ", 1)[-1] for place in places_response.strip().split("\n") if place.strip()]
        st.session_state.places = places[:10]  # Store exactly 10 places

# ---- Step 6: Display Recommended Places ----
if "places" in st.session_state and st.session_state.places:
    st.write("✅ **Top 10 Recommended Places:**")
    for idx, place in enumerate(st.session_state.places, 1):
        st.markdown(f"**{idx}. {place}**")

    # ---- Step 7: Ask Additional Preferences ----
    dietary_pref = st.selectbox("Dietary Preferences:", ["No Preference", "Vegetarian", "Vegan", "Halal", "Gluten-Free"])
    mobility = st.selectbox("Mobility Needs:", ["No restrictions", "Limited walking", "Wheelchair accessible"])
    accommodation = st.selectbox("Accommodation Type:", ["Hostel", "Budget Hotel", "Luxury Resort", "Airbnb"])
    transport = st.selectbox("Preferred Transport:", ["Public Transport", "Rental Car", "Walking", "Taxi/Uber"])

    # ---- Step 8: Generate Itinerary ----
    if st.button("Generate Itinerary"):
        if not interests:
            st.warning("Please select at least one interest.")
        else:
            st.write("📝 Generating Itinerary...")

            # Construct Prompt for Itinerary Generation
            prompt_itinerary = f"""
            Create a exact {trip_duration}-day only travel itinerary for {destination}.

            **User Preferences:**
            - **Budget:** {budget}
            - **Interests:** {', '.join(interests)}
            - **Dietary Restrictions:** {dietary_pref}
            - **Mobility Needs:** {mobility}
            - **Accommodation:** {accommodation}
            - **Transport:** {transport}

            The user wants to visit these attractions: {', '.join(st.session_state.places)}.

            **Itinerary Requirements:**
            - Each day should have **morning, afternoon, and evening** activities.
            - Include **dining options** based on dietary preferences.
            - Mention if locations require **walking or transport**.
            - Recommend **cultural, nightlife, or adventure experiences** based on interests.
            """

            itinerary_response = chat_with_openrouter(prompt_itinerary)
            st.session_state.itinerary = itinerary_response.strip()

# ---- Step 9: Display Itinerary ----
if "itinerary" in st.session_state and st.session_state.itinerary:
    st.subheader("📜 Your AI-Powered Itinerary:")
    st.write(st.session_state.itinerary)

    # ---- Step 10: Download Itinerary ----
    if st.button("Download Itinerary (Markdown)"):
        itinerary_text = f"# AI-Generated Travel Itinerary for {destination}\n\n" + st.session_state.itinerary
        st.download_button("Download Markdown", itinerary_text, file_name="travel_itinerary.md")
