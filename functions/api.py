from http.server import BaseHTTPRequestHandler
import json
import cohere
import re

# Replace with your Cohere API key
API_KEY = 'KTn7ndyWTyFbx9yGwzrS27JYOy0TRjttcObYzk5t'
co = cohere.Client(API_KEY)

def get_ai_response(prompt):
    try:
        response = co.generate(
            model='command-xlarge-nightly',
            prompt=prompt,
            max_tokens=250,
            temperature=0.7
        )
        return response.generations[0].text.strip()
    except Exception as e:
        return f"An error occurred: {e}"

def clean_input(user_input):
    user_input = re.sub(r'[^a-zA-Z, ]', '', user_input).lower().strip()
    return user_input

def remove_markdown(text):
    text = re.sub(r'\*\*', '', text)
    text = re.sub(r'[_]', '', text)
    text = re.sub(r'[`]', '', text)
    text = re.sub(r'~', '', text)
    return text

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data.decode('utf-8'))
        
        symptoms = data.get('symptoms', '')
        cleaned_input = clean_input(symptoms)
        
        if not cleaned_input:
            self.send_error(400, "Invalid input. Please describe your symptoms properly.")
            return

        user_symptoms = [symptom.strip() for symptom in cleaned_input.split(",")]
        
        ai_prompt = f"""
        The user has the following symptoms: {', '.join(user_symptoms)}.
        First, identify potential diseases or health conditions that may be associated with these symptoms.
        Then, as an herbal medicine assistant, suggest plant-based herbal medicines or mixtures of herbs traditionally used in herbal or Ayurvedic treatments for these conditions.
        Focus only on natural remedies using herbs and plants, and avoid recommending any pharmaceutical or synthetic treatments.
        """
        
        ai_response = get_ai_response(ai_prompt)
        ai_response = remove_markdown(ai_response)
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        response = {"response": ai_response}
        self.wfile.write(json.dumps(response).encode('utf-8'))

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        response = {"message": "Herbal Remedy Assistant API is running"}
        self.wfile.write(json.dumps(response).encode('utf-8'))