from flask import Flask, request, jsonify
from flask_cors import CORS
import re
from openai import OpenAI

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Replace with your Martian API key
API_KEY = 'sk-6f4945a475724fb49629eeac385e1fac'
client = OpenAI(
    api_key=API_KEY,
    base_url="https://withmartian.com/api/openai/v1"
)

# Function to generate AI response using the Martian model
def get_ai_response(prompt):
    try:
        chat_completion = client.chat.completions.create(
            model="router",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
        )
        return chat_completion["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"An error occurred: {e}"

# Function to clean and format the user's input
def clean_input(user_input):
    # Remove any extra spaces, special characters, and lowercase the input
    user_input = re.sub(r'[^a-zA-Z, ]', '', user_input).lower().strip()
    return user_input

# Function to remove markdown formatting
def remove_markdown(text):
    text = re.sub(r'\*\*', '', text)  # Remove bold markers
    text = re.sub(r'[_]', '', text)   # Remove italic markers if any
    text = re.sub(r'[`]', '', text)   # Remove inline code markers if any
    text = re.sub(r'~', '', text)     # Remove strikethrough markers if any
    return text

# API endpoint to receive symptoms and return herbal remedies
@app.route('/get_remedy', methods=['POST'])
def get_remedy():
    data = request.json
    symptoms = data.get('symptoms', '')

    # Clean the input
    cleaned_input = clean_input(symptoms)
    if not cleaned_input:
        return jsonify({"error": "Invalid input. Please describe your symptoms properly."}), 400

    # Process the symptoms
    user_symptoms = [symptom.strip() for symptom in cleaned_input.split(",")]

    # Generate a domain-specific prompt for the Martian API
    ai_prompt = f"""
    The user has the following symptoms: {', '.join(user_symptoms)}.
    First, identify potential diseases or health conditions that may be associated with these symptoms.
    Then, as an herbal medicine assistant, suggest plant-based herbal medicines or mixtures of herbs traditionally used in herbal or Ayurvedic treatments for these conditions.
    Focus only on natural remedies using herbs and plants, and avoid recommending any pharmaceutical or synthetic treatments.
    """

    # Get the AI response
    ai_response = get_ai_response(ai_prompt)
    ai_response = remove_markdown(ai_response)

    return jsonify({"response": ai_response})

if __name__ == '__main__':
    app.run(debug=True)
