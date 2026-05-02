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
    hotel_data: List[Dict[str, Any]]
    flight_data: List[Dict[str, Any]]
    itinerary: List[Dict[str, Any]]
    total_cost: float
    status: str

def _extract_first_dict(item):
    """Safely extracts the first dictionary from a nested list or returns an empty dictionary."""
    while isinstance(item, list):
        if len(item) > 0:
            item = item[0]
        else:
            return {}
    if isinstance(item, dict):
        return item
    return {}

def research_node(state: TripState) -> TripState:
    researcher = ResearcherAgent()
    
    destination = state.get("destination", "Destination")
    origin = state.get("origin", "Origin")
    budget = state.get("budget", 5000.0)
    days = state.get("days", 5)
    flight_class = state.get("flight_class", "Economy")
    hotel_stars = state.get("hotel_stars", 3)
    
    try:
        load_dotenv()
        llm = AzureChatOpenAI(
            azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o-mini"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            temperature=0.7
        )
        
        flight_prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an expert travel assistant. Provide exactly 3 flight options for traveling from {origin} to {destination} in {flight_class} class. Provide the airline name and the estimated cost. Return the response strictly as a JSON list of dictionaries with keys 'airline', 'class_selected', and 'flight_cost'."),
            ("human", "Generate flight options.")
        ])
        
        flight_chain = flight_prompt | llm
        flight_resp = flight_chain.invoke({
            "origin": origin, 
            "destination": destination, 
            "flight_class": flight_class
        })
        
        flight_content = flight_resp.content.strip()
        if "```json" in flight_content:
            flight_content = flight_content.split("```json")[1].split("```")[0].strip()
        elif "```" in flight_content:
            flight_content = flight_content.split("```")[1].split("```")[0].strip()
            
        state["flight_data"] = json.loads(flight_content)
        
        hotel_prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an expert travel assistant. Provide exactly 3 hotel options in {destination} that are around or within {budget} and have at least {hotel_stars} stars. Provide the hotel name and the estimated price per night. Return the response strictly as a JSON list of dictionaries with keys 'hotel' and 'price_per_night'."),
            ("human", "Generate hotel options.")
        ])
        
        hotel_chain = hotel_prompt | llm
        hotel_resp = hotel_chain.invoke({
            "destination": destination, 
            "budget": budget, 
            "hotel_stars": hotel_stars
        })
        
        hotel_content = hotel_resp.content.strip()
        if "```json" in hotel_content:
            hotel_content = hotel_content.split("```json")[1].split("```")[0].strip()
        elif "```" in hotel_content:
            hotel_content = hotel_content.split("```")[1].split("```")[0].strip()
            
        state["hotel_data"] = json.loads(hotel_content)
        
    except Exception as e:
        state["flight_data"] = [researcher.find_flights(origin, destination, flight_class)]
        state["hotel_data"] = [researcher.find_accommodations(destination, hotel_stars, budget, days)]
        
    state["status"] = "Research Complete"
    return state

def constraint_check_node(state: TripState) -> TripState:
    accountant = AccountantAgent()
    days = state.get("days", 5)
    
    # Safely extract dictionary objects no matter the level of nesting
    hotel_data = _extract_first_dict(state.get("hotel_data", []))
    flight_data = _extract_first_dict(state.get("flight_data", []))

    raw_hotel_price = hotel_data.get("price_per_night")
    hotel_price = float(raw_hotel_price) if raw_hotel_price is not None else 0.0
    
    raw_flight_cost = flight_data.get("flight_cost")
    flight_cost = float(raw_flight_cost) if raw_flight_cost is not None else 0.0

    hotel_cost = hotel_price * days
    
    itinerary = state.get("itinerary", [])
    activities_cost = sum(float(item.get("cost", 0.0)) for item in itinerary)
    
    costs = {"hotel": hotel_cost, "flight": flight_cost, "activities": activities_cost}
    budget_limit = state.get("budget", 5000.0)
    
    verification = accountant.verify_budget(budget_limit, costs)
    state["total_cost"] = verification["total_cost"]
    
    difference = budget_limit - state["total_cost"]
    
    if verification["within_budget"]:
        state["status"] = "Budget Approved"
    else:
        state["status"] = f"Review Needed: Over Budget by ${abs(difference):,.2f}"
        
    return state

def generate_fallback_itinerary(destination, days, activities_pref):
    activities_list = [a.strip() for a in activities_pref.split(',')] if ',' in activities_pref else [activities_pref]
    itinerary = []
    
    for i in range(days):
        activity = f"Explore {destination} and enjoy {activities_list[i % len(activities_list)].lower()}" if activities_list else f"Explore {destination}"
        itinerary.append({
            "day": i + 1,
            "activity": f"Day {i + 1} in {destination}: {activity}",
            "transport": "Private Chauffeur",
            "cost": 50.0
        })
    return itinerary

def itinerary_node(state: TripState) -> TripState:
    load_dotenv()
    
    destination = state.get("destination", "Destination")
    days = state.get("days", 5)
    activities_pref = state.get("activities_preference", "Explore local culture and relax")

    try:
        llm = AzureChatOpenAI(
            azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o-mini"),
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
             "Provide an estimated cost in USD for the activity on that day.\n"
             "Output your response strictly as a JSON list of dictionaries with the keys: 'day', 'activity', 'transport', and 'cost'."),
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
        state["itinerary"] = generate_fallback_itinerary(destination, days, activities_pref)

    state["status"] = "Itinerary Complete"
    return state

workflow = StateGraph(TripState)
workflow.add_node("research", research_node)
workflow.add_node("verify", constraint_check_node)
workflow.add_node("build_itinerary", itinerary_node)

workflow.set_entry_point("research")
workflow.add_edge("research", "verify")
workflow.add_edge("verify", "build_itinerary")
workflow.add_edge("build_itinerary", END)

app_graph = workflow.compile()