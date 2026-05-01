# Travello# ✈️ Travello - Automated Travel Concierge

Travello is an intelligent, multi-agent AI travel concierge designed to plan custom, budget-friendly, and destination-specific itineraries using the LangGraph framework and Streamlit.

## Features
- **Multi-Agent Orchestration:** Uses specialized agents to search accommodations and flights, and verify budget constraints.
- **Dynamic Itinerary Generation:** Tailored, destination-specific daily activities generated using OpenAI or Azure OpenAI.
- **Cost Analysis:** Calculates hotel and flight costs and compares them against the total budget.
- **PDF Generation & Email Notifications:** Generates a printable PDF of the itinerary and allows email delivery.

## Prerequisites
- Python 3.10+ 
- OpenAI API Key or Azure OpenAI Account

## Installation

1. Clone the repository:
```bash
git clone [https://github.com/Mamdou793/Travello.git](https://github.com/Mamdou793/Travello.git)
cd Travello

## Create and activate the environment
python -m venv venv
source venv/bin/activate

## Install the required Dependencies
pip install -r requirements.txt
pip install langchain-openai python-dotenv

## Configuration .env
AZURE_OPENAI_API_KEY=
AZURE_OPENAI_ENDPOINT=
AZURE_OPENAI_DEPLOYMENT_NAME=
AZURE_OPENAI_API_VERSION=
TAVILY_API_KEY=

## Usage
streamlit run ui.py