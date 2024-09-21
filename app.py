import os 
import subprocess
from flask import Flask, request, session, render_template

app = Flask(__name__)

# Set a secret key for session handling (for memory/contextual replies)
app.secret_key = 'your_secret_key'

# Predefined FAQ responses
faq_responses = {
    "what is your return policy?": "You can return items within 30 days for a full refund.",
    "pricing": "Our prices vary depending on the product. Please visit our website for more detailed pricing information.",
    "what is the delivery time?": "We typically deliver within 3-5 business days.",
    "what are your hours?": "We are open from 9 AM to 5 PM, Monday to Friday.",
    "where are you located?": "Our office is located at 123 Main St, Anytown.",
}

@app.route("/")
def home():
    return render_template('index.html')

def get_ollama_response(user_input):
    # This will call the Qwen 2.5 model using subprocess and capture the output
    result = subprocess.run(
        ['ollama', 'run', 'qwen2.5', user_input],  # Call Qwen 2.5 model
        capture_output=True, 
        text=True
    )
    
    # Extract the response from the result
    return result.stdout.strip()

@app.route("/whatsapp", methods=["POST"])
def whatsapp_reply():
    incoming_message = request.values.get('Body', '').lower()

    # Step 1: Check for FAQ keywords
    for keyword, response in faq_responses.items():
        if keyword in incoming_message:
            return f'<Response><Message>{response}</Message></Response>'

    # Step 2: Handle context from previous messages using Flask session
    previous_message = session.get('previous_message', None)
    session['previous_message'] = incoming_message

    # Contextual response for delivery inquiries
    if previous_message and "delivery" in previous_message:
        if "tell me more about delivery" in incoming_message:
            return f'<Response><Message>We typically deliver within 3-5 business days. Would you like to know more about our shipping options?</Message></Response>'
    
    # Step 3: Get AI response from Ollama model
    ai_response = get_ollama_response(incoming_message)

    # Step 4: Error handling and fallback to offer human support if AI doesn't understand
    if not ai_response or "i don't understand" in ai_response.lower():
        return '<Response><Message>Sorry, I didn’t quite get that. Would you like to speak with a human agent?</Message></Response>'

    # Step 5: Check if user wants to rate the chatbot
    if "rate" in incoming_message:
        rating = incoming_message.split()[-1]  # Example: "rate 5"
        with open("ratings.txt", "a") as f:
            f.write(f'User Rating: {rating}\n')
        return '<Response><Message>Thank you for your feedback!</Message></Response>'

    # Default response with AI-generated answer
    return f'<Response><Message>{ai_response}</Message></Response>'

# New route for serving the chatbot's HTML interface
@app.route('/chat', methods=['GET'])
def chat():
    return render_template('index.html')

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))  # Get the PORT from the environment
    app.run(host='0.0.0.0', port=port, debug=True)
