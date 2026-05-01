import os
from fpdf import FPDF

class PDFGenerator(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Travello - Custom Travel Itinerary', 0, 1, 'C')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def _sanitize_text(text: str) -> str:
    """Replaces common non-Latin-1 characters with safe ASCII alternatives."""
    if not text:
        return ""
    replacements = {
        "’": "'",
        "‘": "'",
        "“": '"',
        "”": '"',
        "–": "-",
        "—": "-",
        "…": "...",
    }
    for old, new in replacements.items():
        text = str(text).replace(old, new)
    return text

def generate_itinerary_pdf(result_data: dict, filename="itinerary.pdf") -> str:
    pdf = PDFGenerator()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    pdf.cell(200, 10, txt="Trip Summary & Itinerary", ln=True, align='C')
    pdf.ln(5)
    
    pdf.cell(200, 10, txt=f"Destination: {_sanitize_text(result_data.get('destination', ''))}", ln=True)
    pdf.cell(200, 10, txt=f"Origin: {_sanitize_text(result_data.get('origin', ''))}", ln=True)
    pdf.cell(200, 10, txt=f"Total Cost: ${result_data.get('total_cost', 0):,.2f}", ln=True)
    pdf.ln(5)
    
    # Flight details section
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt="Flight Details:", ln=True)
    pdf.set_font("Arial", size=10)
    
    flight_data = result_data.get('flight_data', {})
    if isinstance(flight_data, list):
        flight = flight_data[0] if flight_data else {}
    else:
        flight = flight_data
        
    airline = _sanitize_text(flight.get('airline') or "Not Specified")
    flight_class = _sanitize_text(flight.get('class_selected') or result_data.get('flight_class') or "Economy")
    flight_cost = flight.get('flight_cost', 0)
    
    pdf.cell(200, 10, txt=f"Airline: {airline}", ln=True)
    pdf.cell(200, 10, txt=f"Class Selected: {flight_class}", ln=True)
    pdf.cell(200, 10, txt=f"Cost: ${flight_cost:,.2f}", ln=True)
    pdf.ln(5)
    
    # Hotel recommendation section
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt="Hotel Recommendation:", ln=True)
    pdf.set_font("Arial", size=10)
    
    hotel_data = result_data.get('hotel_data', {})
    if isinstance(hotel_data, list):
        hotel = hotel_data[0] if hotel_data else {}
    else:
        hotel = hotel_data
        
    hotel_name = _sanitize_text(hotel.get('hotel') or hotel.get('name') or "Not Specified")
    hotel_price = hotel.get('price_per_night', 0)
    
    pdf.cell(200, 10, txt=f"Hotel: {hotel_name}", ln=True)
    pdf.cell(200, 10, txt=f"Cost per night: ${hotel_price:,.2f}", ln=True)
    pdf.ln(5)
    
    # Itinerary section
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt="Itinerary:", ln=True)
    pdf.set_font("Arial", size=10)
    
    for item in result_data.get('itinerary', []):
        day = item.get('day', 1)
        activity = _sanitize_text(item.get('activity', ''))
        transport = _sanitize_text(item.get('transport', ''))
        
        pdf.multi_cell(0, 8, f"Day {day}: {activity} | Logistics: {transport}")
        pdf.ln(2)
        
    pdf.output(filename)
    return filename