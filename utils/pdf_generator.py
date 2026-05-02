import os
from fpdf import FPDF

class PDF(FPDF):
    def header(self):
        # Draw background inside header so it doesn't cover up the image
        self.set_fill_color(248, 250, 252) # Soft, modern travel-app background
        self.rect(0, 0, 210, 297, 'F')
        
        # Logo - increased size, positioned at x=15, y=10, width=28
        try:
            self.image('logo.png', x=15, y=10, w=28)
        except:
            pass
            
        # Header title
        self.set_font('Arial', 'B', 18)
        self.set_text_color(15, 23, 42)  # Midnight/Dark slate
        self.set_xy(50, 11)
        self.cell(145, 8, 'Travello - Travel Itinerary', 0, 1, 'L')
        
        # Subtitle
        self.set_font('Arial', '', 9)
        self.set_text_color(100, 116, 139)  # Muted slate
        self.set_xy(50, 19)
        self.cell(145, 6, 'Your AI Travel Concierge | www.travello.ai', 0, 1, 'L')
        
        # Line separator (Travel-app blue)
        self.set_draw_color(14, 165, 233)
        self.set_line_width(1)
        self.line(15, 28, 195, 28)
        self.ln(6)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(148, 163, 184)
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
    pdf = PDF()
    pdf.add_page()
    
    # Starting below header
    pdf.set_y(32)
    
    # --- Trip Summary Card ---
    pdf.set_fill_color(255, 255, 255)
    pdf.set_draw_color(226, 232, 240)
    pdf.rect(15, 34, 180, 28, 'DF')
    
    # Accent bar on the side
    pdf.set_fill_color(14, 165, 233)
    pdf.rect(15, 34, 2, 28, 'F')
    
    pdf.set_xy(20, 37)
    pdf.set_font('Arial', 'B', 10)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(170, 5, "TRIP SUMMARY", 0, 1, 'L')
    pdf.ln(1)
    
    pdf.set_font('Arial', '', 9)
    pdf.set_text_color(71, 85, 105)
    
    pdf.set_x(20)
    pdf.cell(85, 5, f"Destination: {_sanitize_text(result_data.get('destination', ''))}", 0, 0, 'L')
    pdf.cell(85, 5, f"Total Trip Cost: ${result_data.get('total_cost', 0):,.2f}", 0, 1, 'L')
    
    pdf.set_x(20)
    pdf.cell(85, 5, f"Origin: {_sanitize_text(result_data.get('origin', ''))}", 0, 0, 'L')
    
    itinerary = result_data.get('itinerary', [])
    activity_cost = sum(float(item.get('cost', 0.0)) for item in itinerary)
    pdf.cell(85, 5, f"Total Activities Cost: ${activity_cost:,.2f}", 0, 1, 'L')
    
    # --- Flight Details ---
    pdf.ln(4)
    pdf.set_fill_color(255, 255, 255)
    pdf.rect(15, 68, 180, 20, 'DF')
    pdf.set_fill_color(14, 165, 233)
    pdf.rect(15, 68, 2, 20, 'F')
    
    pdf.set_xy(20, 71)
    pdf.set_font('Arial', 'B', 10)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(170, 5, "FLIGHT DETAILS", 0, 1, 'L')
    pdf.ln(1)
    
    flight_data = result_data.get('flight_data', {})
    if isinstance(flight_data, list):
        flight = flight_data[0] if flight_data else {}
    else:
        flight = flight_data
        
    airline = _sanitize_text(flight.get('airline') or "Not Specified")
    flight_class = _sanitize_text(flight.get('class_selected') or result_data.get('flight_class') or "Economy")
    flight_cost = float(flight.get('flight_cost') or flight.get('cost') or 0.0)
    
    pdf.set_font('Arial', '', 9)
    pdf.set_text_color(71, 85, 105)
    pdf.set_x(20)
    pdf.cell(60, 5, f"Airline: {airline}", 0, 0)
    pdf.cell(60, 5, f"Class: {flight_class}", 0, 0)
    pdf.cell(50, 5, f"Cost: ${flight_cost:,.2f}", 0, 1)
    
    # --- Hotel Recommendation ---
    pdf.ln(3)
    pdf.set_fill_color(255, 255, 255)
    pdf.rect(15, 93, 180, 20, 'DF')
    pdf.set_fill_color(14, 165, 233)
    pdf.rect(15, 93, 2, 20, 'F')
    
    pdf.set_xy(20, 96)
    pdf.set_font('Arial', 'B', 10)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(170, 5, "HOTEL RECOMMENDATION", 0, 1, 'L')
    pdf.ln(1)
    
    hotel_data = result_data.get('hotel_data', {})
    if isinstance(hotel_data, list):
        hotel = hotel_data[0] if hotel_data else {}
    else:
        hotel = hotel_data
        
    hotel_name = _sanitize_text(hotel.get('hotel') or hotel.get('name') or "Not Specified")
    hotel_price = float(hotel.get('price_per_night') or hotel.get('cost') or 0.0)
    
    pdf.set_font('Arial', '', 9)
    pdf.set_text_color(71, 85, 105)
    pdf.set_x(20)
    pdf.cell(120, 5, f"Hotel: {hotel_name}", 0, 0)
    pdf.cell(50, 5, f"Cost/night: ${hotel_price:,.2f}", 0, 1)
    
    # --- Detailed Itinerary Section ---
    pdf.ln(8) # Provides much more space
    pdf.set_font('Arial', 'B', 10)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(190, 6, "DETAILED ITINERARY", 0, 1, 'L')
    pdf.line(15, pdf.get_y(), 195, pdf.get_y())
    pdf.ln(3)
    
    for item in itinerary:
        day = item.get('day', 1)
        activity = _sanitize_text(item.get('activity', ''))
        transport = _sanitize_text(item.get('transport', ''))
        item_cost = float(item.get('cost', 0.0))
        
        text_block = f"Day {day}: {activity} | Logistics: {transport} | Cost: ${item_cost:,.2f}"
        
        # Check page bounds to prevent overflow
        if pdf.get_y() > 240:
            pdf.add_page()
            # Header draws background automatically
            pdf.set_y(25)
            
        # Draw side colored indicator bar for aesthetics
        pdf.set_fill_color(14, 165, 233)
        pdf.rect(15, pdf.get_y(), 2, 12, 'F')
        
        pdf.set_x(20)
        pdf.set_font('Arial', '', 8.5)
        pdf.set_text_color(71, 85, 105)
        
        # Use multi_cell to wrap full strings over multiple lines without cutting
        pdf.multi_cell(175, 4, text_block, 0, 'L')
        pdf.ln(4)
        
    pdf.output(filename)
    return filename