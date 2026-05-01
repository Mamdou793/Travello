from workflow.graph import app_graph

def run_travello():
    print(" === Welcome to Travello - Automated Travel Concierge === \n")
    
    print("Please enter your trip details below:\n")
    
    # Capture user inputs
    origin = input("Your current location / Origin (e.g., Riyadh, Saudi Arabia): ").strip()
    destination = input("Where would you like to travel? (e.g., Rome, Italy): ").strip()
    
    try:
        budget = float(input("Total budget in $ (e.g., 14000): ").strip())
    except ValueError:
        print("Invalid budget entered. Defaulting to $10,000.")
        budget = 10000.00
        
    try:
        days = int(input("How many days is the trip? (e.g., 6): ").strip())
    except ValueError:
        print("Invalid number of days. Defaulting to 5 days.")
        days = 5
        
    flight_class = input("Desired flight class (e.g., Economy, Business, First): ").strip()
    
    try:
        hotel_stars = int(input("Hotel star rating (e.g., 3, 4, 5): ").strip())
    except ValueError:
        hotel_stars = 5
        
    activities_preference = input("What type of activities do you enjoy? (e.g., Museums, beaches, or food tours): ").strip()
    
    # Initialize dynamic user state
    user_input = {
        "origin": origin,
        "destination": destination,
        "budget": budget,
        "days": days,
        "flight_class": flight_class,
        "hotel_stars": hotel_stars,
        "activities_preference": activities_preference,
        "total_cost": 0.0,
        "hotel_data": {},
        "flight_data": {},
        "itinerary": [],
        "status": "Initialized"
    }

    print("\nProcessing your preferences through Travello's AI orchestrator...")
    result = app_graph.invoke(user_input)
    
    # Output the result
    print("\n" + "="*50)
    print("        YOUR CUSTOM TRACE SUMMARY        ")
    print("="*50)
    print(f"Status: {result['status']}")
    print(f"Total Trip Package Cost: ${result['total_cost']:,.2f} / Budget: ${result['budget']:,.2f}\n")
    
    print("--- Hotel Recommendation ---")
    print(f"Hotel Name: {result['hotel_data']['hotel']}")
    print(f"Location: {result['hotel_data']['location']}")
    print(f"Cost Per Night: ${result['hotel_data']['price_per_night']:,.2f}")
    print(f"Amenities: {', '.join(result['hotel_data']['amenities'])}\n")
    
    print("--- Flight Recommendation ---")
    print(f"Airline: {result['flight_data']['airline']}")
    print(f"Class: {result['flight_data']['class']}")
    print(f"Flight Cost: ${result['flight_data']['flight_cost']:,.2f}\n")
    
    print("--- Custom Itinerary Plan ---")
    for day in result['itinerary']:
        print(f"Day {day['day']}: {day['activity']} | Logistics: {day['transport']}")
        
    print("\n--- Execution Complete ---")

if __name__ == "__main__":
    run_travello()