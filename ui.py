import streamlit as st
import os
from workflow.graph import app_graph
from utils.pdf_generator import generate_itinerary_pdf
from utils.notifier import Notifier

st.set_page_config(page_title="Travello - AI Travel Concierge", layout="wide")

st.title("✈️ Travello - Automated Travel Concierge")
st.write("Plan and book custom itineraries with multi-agent orchestration.")

# Split form into responsive columns
col1, col2 = st.columns(2)

with col1:
    st.subheader("Journey Parameters")
    # Empty fields requiring the user to specify locations
    origin = st.text_input("Origin (e.g., Riyadh, Saudi Arabia):", "")
    destination = st.text_input("Destination (e.g., Rome, Italy):", "")
    budget = st.number_input("Total Budget Package ($):", value=14000.00, step=500.00)
    days = st.number_input("Trip Duration (Days):", value=6, step=1, min_value=1)

with col2:
    st.subheader("Logistics & Preferences")
    flight_class = st.selectbox("Flight Class:", ["Economy", "Business", "First"])
    hotel_stars = st.slider("Hotel Rating (Stars):", min_value=3, max_value=5, value=5)
    activities_preference = st.text_area("What do you like to do? (Activities Preference):", 
                                          "Historical walking tours, visiting the Colosseum, and authentic Italian cooking classes.")

if st.button("Generate Trip Plan"):
    if not origin or not destination:
        st.error("Both Origin and Destination must be specified.")
    else:
        with st.spinner("Processing your criteria through your AI agents..."):
            user_input = {
                "origin": origin,
                "destination": destination,
                "budget": float(budget),
                "days": int(days),
                "flight_class": flight_class,
                "hotel_stars": int(hotel_stars),
                "activities_preference": activities_preference,
                "hotel_data": {},
                "flight_data": {},
                "itinerary": [],
                "total_cost": 0.0,
                "status": "Initialized"
            }

            # Run state graph
            result = app_graph.invoke(user_input)
            st.session_state['result'] = result
            st.success("Research and Plan Complete!")

if 'result' in st.session_state:
    res = st.session_state['result']
    
    st.write("---")
    st.header("Results Summary")
    st.metric(label="Status", value=res.get('status', 'N/A'))
    
    total_cost = res.get('total_cost', 0.0)
    budget = res.get('budget', 0.0)
    st.metric(label="Total Projected Cost", value=f"${total_cost:,.2f}", delta=f"${budget - total_cost:,.2f} under budget")
    
    c1, c2 = st.columns(2)
    
    # Safely unpack hotel data
    hotel_data = res.get("hotel_data", {})
    if isinstance(hotel_data, list) and len(hotel_data) > 0:
        hotel_data = hotel_data[0]
    elif not isinstance(hotel_data, dict):
        hotel_data = {}

    with c1:
        st.subheader("🏨 Hotel Details")
        st.write(f"**Name:** {hotel_data.get('hotel', 'N/A')}")
        st.write(f"**Location:** {hotel_data.get('location', 'N/A')}")
        
        hotel_price = hotel_data.get('price_per_night')
        if hotel_price is not None:
            st.write(f"**Cost / Night:** ${hotel_price:,.2f}")
        else:
            st.write("**Cost / Night:** N/A")
            
        amenities = hotel_data.get('amenities', [])
        st.write(f"**Amenities:** {', '.join(amenities) if isinstance(amenities, list) else amenities}")
        
    # Safely unpack flight data
    flight_data = res.get("flight_data", {})
    if isinstance(flight_data, list) and len(flight_data) > 0:
        flight_data = flight_data[0]
    elif not isinstance(flight_data, dict):
        flight_data = {}

    with c2:
        st.subheader("✈️ Flights")
        st.write(f"**Airline:** {flight_data.get('airline', 'N/A')}")
        st.write(f"**Class Selected:** {flight_data.get('class', flight_class)}")
        
        flight_cost = flight_data.get('flight_cost')
        if flight_cost is not None:
            st.write(f"**Cost:** ${flight_cost:,.2f}")
        else:
            st.write("**Cost:** N/A")
        
    st.subheader("📅 Detailed Itinerary")
    for day in res.get('itinerary', []):
        st.markdown(f"**Day {day.get('day', 'N/A')}:** {day.get('activity', 'N/A')} <br><em>Logistics: {day.get('transport', 'N/A')}</em>", unsafe_allow_html=True)
        
    # PDF & Actions
    st.subheader("Download & Notifications")
    if st.button("Generate PDF Itinerary"):
        pdf_path = generate_itinerary_pdf(res)
        st.session_state['pdf_path'] = pdf_path
        st.success("PDF Itinerary generated successfully!")
        
    if 'pdf_path' in st.session_state:
        with open(st.session_state['pdf_path'], "rb") as file:
            st.download_button(
                label="📥 Download PDF",
                data=file,
                file_name="itinerary.pdf",
                mime="application/pdf"
            )
            
    recipient_email = st.text_input("Enter Email to Deliver Itinerary:")
    if st.button("Email Itinerary"):
        if 'pdf_path' in st.session_state and os.path.exists(st.session_state['pdf_path']):
            notifier = Notifier()
            # Updated to pass the user's email and provide endpoint error handling
            if notifier.send_itinerary_email(recipient_email, st.session_state['pdf_path']):
                st.success(f"Email successfully sent to {recipient_email}!")
            else:
                st.error("Error sending email. Please check your Logic App endpoint in the .env file.")