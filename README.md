# Travello - AI Travel Concierge
Travello is a Python-based travel application that utilizes generative AI to create custom itineraries, estimate costs, and generate downloadable travel itineraries in PDF format.

## Features
- **AI-Powered Generation:** Automatically plans daily activities based on user preferences.
- **Multi-Agent Orchestration:** Uses specialized agents to search accommodations and flights, and verify budget constraints.
- **Dynamic Itinerary Generation:** Tailored, destination-specific daily activities generated using OpenAI or Azure OpenAI.
- **Cost Estimation:** Calculates total trip and activity costs.
- **PDF Generation:** Exports clear and professional itineraries containing trip summaries, flight details, hotel recommendations, and detailed day-by-day logs.

## Quick Start
Ensure you have the required packages installed and your API keys (e.g., Azure OpenAI) configured.

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