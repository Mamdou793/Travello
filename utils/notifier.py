import requests
import os
import base64

class Notifier:
    def __init__(self):
        self.logic_app_url = os.getenv("LOGIC_APP_URL", "")

    def send_itinerary_email(self, recipient_email: str, pdf_path: str, subject: str = "Your Travello Itinerary") -> bool:
        try:
            if not os.path.exists(pdf_path):
                print(f"File not found: {pdf_path}")
                return False

            with open(pdf_path, "rb") as f:
                encoded_file = base64.b64encode(f.read()).decode('utf-8')

            payload = {
                "to": recipient_email,
                "subject": subject,
                "body": "Hello! Please find attached your customized Travello itinerary.",
                "attachment_name": "itinerary.pdf",
                "attachment_content": encoded_file
            }

            response = requests.post(self.logic_app_url, json=payload)
            
            # Azure Logic Apps typically return a 202 Accepted or 200 OK status
            return response.status_code in [200, 202]
            
        except Exception as e:
            print(f"Failed to send email via Logic App: {e}")
            return False