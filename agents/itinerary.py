import os
from typing import Dict, Any, List

class ItineraryAgent:
    def __init__(self):
        pass

    def build_itinerary(self, destination: str, days: int, activities_preference: str) -> List[Dict[str, Any]]:
        itinerary = []
        for i in range(1, days + 1):
            if i == 1:
                itinerary.append({
                    "day": i,
                    "activity": f"Arrive at {destination}. Private transfer to the hotel, check-in, and welcome dinner.",
                    "transport": "Private Chauffeur"
                })
            elif i == days:
                itinerary.append({
                    "day": i,
                    "activity": f"Morning checkout and departure from {destination}.",
                    "transport": "Private Chauffeur"
                })
            else:
                itinerary.append({
                    "day": i,
                    "activity": f"Day {i}: Focused on your preferences: {activities_preference}",
                    "transport": "Premium Transport / Rental"
                })
        return itinerary