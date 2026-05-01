import os
from openai import AzureOpenAI
from tavily import TavilyClient
from config import config
from dotenv import load_dotenv
import json

load_dotenv()

class ResearcherAgent:
    def __init__(self):
        # Initialize Azure OpenAI Client
        self.client = AzureOpenAI(
            api_key=config.AZURE_OPENAI_API_KEY or os.getenv("AZURE_OPENAI_API_KEY"),
            api_version=config.AZURE_OPENAI_API_VERSION or os.getenv("AZURE_OPENAI_API_VERSION"),
            azure_endpoint=config.AZURE_OPENAI_ENDPOINT or os.getenv("AZURE_OPENAI_ENDPOINT")
        )
        
        # Initialize Tavily Client directly
        self.tavily_client = TavilyClient(
            api_key=os.getenv("TAVILY_API_KEY") or config.TAVILY_API_KEY
        )

    def find_accommodations(self, destination: str, hotel_stars: int, budget: float, days: int) -> dict:
        """
        Searches for real accommodations at the destination using the Tavily API and parses the response.
        """
        query = f"Top {hotel_stars}-star luxury hotels in {destination} price per night and amenities"
        
        try:
            # Query Tavily directly
            results = self.tavily_client.search(query=query, max_results=3)
            context_str = "\n".join([f"- {item['title']}: {item['content']}" for item in results['results']])
            
            prompt = f"""
            Analyze these real-time web search results for accommodations in {destination}:
            {context_str}

            Extract the hotel details. Provide *only* a valid JSON object containing exactly:
            - hotel (string: Name of the actual hotel found in the text)
            - location (string: {destination})
            - price_per_night (float)
            - amenities (list of strings)
            """
            
            response = self.client.chat.completions.create(
                model=config.AZURE_OPENAI_DEPLOYMENT_NAME,
                messages=[
                    {"role": "system", "content": "You are a data extraction assistant. Respond only with a JSON object."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1
            )
            
            res_text = response.choices[0].message.content
            # Clean up response
            if "```json" in res_text:
                res_text = res_text.split("```json")[1].split("```")[0].strip()
            elif "```" in res_text:
                res_text = res_text.split("```")[1].split("```")[0].strip()
            
            return json.loads(res_text)
            
        except Exception as e:
            print(f"Error finding accommodations: {e}")
            return {
                "hotel": f"Standard Hotel in {destination}",
                "location": destination,
                "price_per_night": 250.00,
                "amenities": ["Wi-Fi", "Breakfast"],
            }

    def find_flights(self, origin: str, destination: str, flight_class: str) -> dict:
        """
        Searches for real flights between the origin and destination using the Tavily API and parses the response.
        """
        query = f"Flights from {origin} to {destination} {flight_class} class price"
        
        try:
            results = self.tavily_client.search(query=query, max_results=3)
            context_str = "\n".join([f"- {item['title']}: {item['content']}" for item in results['results']])
            
            prompt = f"""
            Analyze these real-time web search results for flights from {origin} to {destination}:
            {context_str}

            Extract flight details. Provide *only* a valid JSON object containing exactly:
            - airline (string)
            - flight_cost (float)
            - class (string: {flight_class})
            """
            
            response = self.client.chat.completions.create(
                model=config.AZURE_OPENAI_DEPLOYMENT_NAME,
                messages=[
                    {"role": "system", "content": "You are a data extraction assistant. Respond only with a JSON object."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1
            )
            
            res_text = response.choices[0].message.content
            # Clean up response
            if "```json" in res_text:
                res_text = res_text.split("```json")[1].split("```")[0].strip()
            elif "```" in res_text:
                res_text = res_text.split("```")[1].split("```")[0].strip()
            
            return json.loads(res_text)
            
        except Exception as e:
            print(f"Error finding flights: {e}")
            return {
                "airline": "Standard Airways",
                "flight_cost": 650.00,
                "class": flight_class,
            }