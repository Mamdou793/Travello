import streamlit as st
import os
from workflow.graph import app_graph
from utils.pdf_generator import generate_itinerary_pdf
from utils.notifier import Notifier

st.set_page_config(page_title="Travello - AI Travel Concierge", layout="wide")

# Split the header area for the logo and title
col1, col2 = st.columns([1, 10])

with col1:
    try:
        st.image("logo.png", width=75)
    except FileNotFoundError:
        pass  # Gracefully skip if logo.png isn't found

with col2:
    st.title("Travello - Automated Travel Concierge")
    st.write("Plan and book custom itineraries with multi-agent orchestration.")

# Split form into responsive columns
col_1, col_2 = st.columns(2)

with col_1:
    st.subheader("Journey Parameters")
    # Empty fields requiring the user to specify locations
    origin = st.text_input("Origin (e.g., Riyadh, Saudi Arabia):", "")
    destination = st.text_input("Destination (e.g., Rome, Italy):", "")
    budget = st.number_input("Total Budget Package ($):", value=14000.00, step=500.00)
    days = st.number_input("Trip Duration (Days):", value=6, step=1, min_value=1)

with col_2:
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
                "hotel_data": [],
                "flight_data": [],
                "itinerary": [],
                "total_cost": 0.0,
                "status": "Initialized"
            }

            # Run state graph
            result = app_graph.invoke(user_input)
            st.session_state['result'] = result
            st.success("Research and Plan Complete!")
            st.rerun()

if 'result' in st.session_state:
    res = st.session_state['result']
    
    st.write("---")
    st.header("Results Summary")
    st.metric(label="Status", value=res.get('status', 'N/A'))
    
    flight_options = res.get("flight_data", [])
    hotel_options = res.get("hotel_data", [])
    
    c1, c2 = st.columns(2)
    
    with c1:
        st.subheader("Select Flight Option")
        if flight_options:
            flight_choices = []
            for f in flight_options:
                if isinstance(f, list) and len(f) > 0:
                    f_item = f[0]
                else:
                    f_item = f
                    
                if isinstance(f_item, dict):
                    airline = f_item.get('airline', 'N/A')
                    cost = float(f_item.get('flight_cost', 0.0))
                else:
                    airline, cost = 'N/A', 0.0
                    
                flight_choices.append(f"{airline} - ${cost:,.2f}")
                
            selected_flight_idx = st.selectbox("Choose flight:", range(len(flight_choices)), format_func=lambda i: flight_choices[i])
            selected_flight = flight_options[selected_flight_idx]
            
            # Normalize to dict object
            if isinstance(selected_flight, list) and len(selected_flight) > 0:
                selected_flight = selected_flight[0]
            elif not isinstance(selected_flight, dict):
                selected_flight = {"flight_cost": 0.0, "airline": "N/A"}
        else:
            selected_flight = {"flight_cost": 0.0, "airline": "N/A"}
            st.warning("No flight data found.")

    with c2:
        st.subheader("Select Hotel Option")
        if hotel_options:
            hotel_choices = []
            for h in hotel_options:
                if isinstance(h, list) and len(h) > 0:
                    h_item = h[0]
                else:
                    h_item = h
                    
                if isinstance(h_item, dict):
                    hotel_name = h_item.get('hotel', h_item.get('name', 'Hotel'))
                    price = float(h_item.get('price_per_night', 0.0))
                else:
                    hotel_name, price = 'Hotel', 0.0
                    
                hotel_choices.append(f"{hotel_name} - ${price:,.2f}/night")
                
            selected_hotel_idx = st.selectbox("Choose hotel:", range(len(hotel_choices)), format_func=lambda i: hotel_choices[i])
            selected_hotel = hotel_options[selected_hotel_idx]
            
            # Normalize to dict object
            if isinstance(selected_hotel, list) and len(selected_hotel) > 0:
                selected_hotel = selected_hotel[0]
            elif not isinstance(selected_hotel, dict):
                selected_hotel = {"price_per_night": 0.0, "hotel": "N/A"}
                
            nights = st.number_input("Number of Nights", min_value=1, value=res.get("days", 6), step=1)
        else:
            selected_hotel = {"price_per_night": 0.0, "hotel": "N/A"}
            nights = res.get("days", 6)
            st.warning("No hotel data found.")

    # Calculate costs safely based on the normalized dictionaries
    itinerary = res.get("itinerary", [])
    activity_cost = 0.0
    for item in itinerary:
        activity_cost += float(item.get('cost', 0.0))
        
    flight_cost = float(selected_flight.get("flight_cost", 0.0))
    hotel_cost = float(selected_hotel.get("price_per_night", 0.0)) * nights
    total_calculated_cost = flight_cost + hotel_cost + activity_cost

    st.write("### Trip Cost Breakdown")
    st.write(f"- **Selected Flight Cost:** ${flight_cost:,.2f}")
    st.write(f"- **Selected Hotel Cost:** ${hotel_cost:,.2f} ({nights} nights)")
    st.write(f"- **Activities Cost:** ${activity_cost:,.2f}")
    st.write(f"### Total Calculated Cost: ${total_calculated_cost:,.2f}")

    budget_limit = float(res.get("budget", 0.0))
    difference = budget_limit - total_calculated_cost
    
    if difference >= 0:
        st.info(f"💰 Under Budget by: ${difference:,.2f}")
    else:
        st.error(f"🚨 Over Budget by: ${abs(difference):,.2f}")

    st.subheader("📅 Detailed Itinerary")
    if itinerary:
        for item in itinerary:
            st.write(f"**Day {item.get('day', 'N/A')}:** {item.get('activity', 'N/A')} | Transport: {item.get('transport', 'N/A')} | Cost: ${float(item.get('cost', 0.0)):,.2f}")
    else:
        st.warning("No itinerary details were generated.")
        
    # PDF & Actions
    st.subheader("Download & Notifications")
    if st.button("Generate PDF Itinerary"):
        res["total_cost"] = total_calculated_cost
        res["flight_data"] = [selected_flight]
        res["hotel_data"] = [selected_hotel]
        
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
            if notifier.send_itinerary_email(recipient_email, st.session_state['pdf_path']):
                st.success(f"Email successfully sent to {recipient_email}!")
            else:
                st.error("Error sending email. Please check your Logic App endpoint in the .env file.")