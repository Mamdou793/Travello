from langgraph.graph import StateGraph, END
from typing import TypedDict, Dict, Any, List
from agents.researcher import ResearcherAgent
from agents.accountant import AccountantAgent
import os
import json
from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv

class TripState(TypedDict):
    origin: str
    destination: str
    budget: float
    days: int
    flight_class: str
    hotel_stars: int
    activities_preference: str
    hotel_data: Dict[str, Any]
    flight_data: Dict[str, Any]
    itinerary: List[Dict[str, Any]]
    total_cost: float
    status: str

def research_node(state: TripState) -> TripState:
    researcher = ResearcherAgent()
    
    destination = state.get("destination", "Destination")
    origin = state.get("origin", "Origin")
    budget = state.get("budget", 5000.0)
    days = state.get("days", 5)
    flight_class = state.get("flight_class", "Economy")
    hotel_stars = state.get("hotel_stars", 3)
    
    state["hotel_data"] = researcher.find_accommodations(destination, hotel_stars, budget, days)
    state["flight_data"] = researcher.find_flights(origin, destination, flight_class)
    state["status"] = "Research Complete"
    return state

def constraint_check_node(state: TripState) -> TripState:
    accountant = AccountantAgent()
    days = state.get("days", 5)
    
    # Safely unpack hotel data in case the model returns a list
    hotel_data = state["hotel_data"]
    if isinstance(hotel_data, list):
        hotel_data = hotel_data[0] if hotel_data else {}
        
    # Safely unpack flight data in case the model returns a list
    flight_data = state["flight_data"]
    if isinstance(flight_data, list):
        flight_data = flight_data[0] if flight_data else {}

    # Extract costs safely and cast to float, defaulting to 0 if None
    raw_hotel_price = hotel_data.get("price_per_night")
    hotel_price = float(raw_hotel_price) if raw_hotel_price is not None else 0.0
    
    raw_flight_cost = flight_data.get("flight_cost")
    flight_cost = float(raw_flight_cost) if raw_flight_cost is not None else 0.0

    hotel_cost = hotel_price * days
    costs = {"hotel": hotel_cost, "flight": flight_cost}
    
    budget_limit = state.get("budget", 5000.0)
    
    verification = accountant.verify_budget(budget_limit, costs)
    state["total_cost"] = verification["total_cost"]
    
    if verification["within_budget"]:
        state["status"] = "Budget Approved"
    else:
        state["status"] = "Review Needed: Over Budget"
        
    return state

def generate_fallback_itinerary(destination, days, activities_pref):
    """Generates a distinct and tailored fallback itinerary if the LLM fails."""
    activities_list = [a.strip() for a in activities_pref.split(',')] if ',' in activities_pref else [activities_pref]
    itinerary = []
    
    for i in range(days):
        # Pick an activity, cycling through preferences if there are multiple, or using the destination
        activity = f"Explore {destination} and enjoy {activities_list[i % len(activities_list)].lower()}" if activities_list else f"Explore {destination}"
        itinerary.append({
            "day": i + 1,
            "activity": f"Day {i + 1} in {destination}: {activity}",
            "transport": "Private Chauffeur"
        })
    return itinerary

def itinerary_node(state: TripState) -> TripState:
    # Load environment variables
    load_dotenv()
    
    destination = state.get("destination", "Destination")
    days = state.get("days", 5)
    activities_pref = state.get("activities_preference", "Explore local culture and relax")

    try:
        # Initialize the Azure OpenAI LLM client
        llm = AzureChatOpenAI(
            azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o-mini"), # e.g., your deployment name
            api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            temperature=0.7
        )
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", 
             "You are an expert travel agent. Create a highly detailed, day-by-day itinerary for a trip to {destination}.\n"
             "User preferences: {activities_preference}\n"
             "Generate an itinerary for exactly {days} days. Ensure each day has a unique, engaging, and varied activity specific to {destination}.\n"
             "DO NOT use generic templates or duplicate activities for all days. Each day must be different and tailored to the destination.\n"
             "DO NOT include activities or locations that do not belong in {destination}.\n"
             "Output your response strictly as a JSON list of dictionaries with the keys: 'day', 'activity', and 'transport'."),
            ("human", "Generate the itinerary now.")
        ])

        chain = prompt | llm
        response = chain.invoke({
            "destination": destination,
            "days": days,
            "activities_preference": activities_pref
        })
        
        content = response.content.strip()
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
            
        state["itinerary"] = json.loads(content)
        
    except Exception as e:
        # Fallback generator in case the call fails
        state["itinerary"] = generate_fallback_itinerary(destination, days, activities_pref)

    state["status"] = "Itinerary Complete"
    return state

workflow = StateGraph(TripState)
workflow.add_node("research", research_node)
workflow.add_node("verify", constraint_check_node)
workflow.add_node("build_itinerary", itinerary_node)

workflow.set_entry_point("research")
workflow.add_edge("research", "verify")

workflow.add_conditional_edges(
    "verify",
    lambda state: "build_itinerary" if state["total_cost"] <= state["budget"] else END,
    {
        "build_itinerary": "build_itinerary",
        END: END
    }
)
workflow.add_edge("build_itinerary", END)

app_graph = workflow.compile()