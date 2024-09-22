import os 
import subprocess
from flask import Flask, request, session, render_template

app = Flask(__name__)

# Set a secret key for session handling (for memory/contextual replies)
app.secret_key = 'your_secret_key'

# Updated Predefined FAQ responses
faq_responses = {
    # General Information
    "what is af beauty castle?": "AF Beauty Castle is a premier beauty brand offering a wide range of beauty products and services, including skincare, haircare, and professional beauty treatments.",
    "where is af beauty castle located?": "We are located at 28, Herman Renlundin katu 67200, Kokkola. You can also contact us through WhatsApp Business.",
    "how can i contact af beauty castle for more information?": "You can reach us via email at arafatbisola111@gmail.com or through our customer support line at +1(415)523-8886.",
    
    # Product Information
    "what products do you offer?": "We offer a wide range of beauty products, including skincare (moisturizers, cleansers, serums), haircare (shampoos, conditioners, treatments), makeup (foundation, lipstick, eyeshadow), and beauty tools and accessories.",
    "can i get recommendations for products that suit my skin type?": "Absolutely! Please tell me your skin type (e.g., oily, dry, combination), and I can recommend products that are best suited to your needs.",
    
    # Service Information
    "what beauty services do you offer?": "We offer facials, hair styling and treatments, manicure and pedicure, and makeup application for special occasions. Contact us for more details.",
    "how do i book an appointment for a beauty service?": "You can book an appointment by contacting us via WhatsApp or phone at +1(415)523-8886. We recommend booking at least 48 hours in advance.",
    "what is your cancellation policy for appointments?": "We ask that you cancel or reschedule your appointment at least 24 hours in advance. Failure to do so may result in a cancellation fee.",
    
    # Pricing and Promotions
    "how much do your services cost?": "Service prices vary depending on the treatment. Please contact us for specific pricing information.",
    "do you offer discounts or promotions?": "Yes, we regularly offer promotions on our products and services. Follow us on social media for exclusive deals!",
    "do you offer membership or loyalty programs?": "Yes, we offer a loyalty program where you can earn points for every purchase, which can be redeemed for discounts on future services or products.",
    
    # Order Information
    "how do i place an order?": "You can place an order by contacting us directly. Add your desired products to the cart and proceed with payment.",
    "can i track my order?": "Yes, once you place your order, you'll receive a confirmation with a tracking number to monitor your delivery.",
    "how long does delivery take?": "Delivery typically takes 3-5 business days, depending on your location. We also offer express shipping.",
    "what are the shipping charges?": "Shipping charges vary depending on location and delivery speed. Free shipping is available for orders above 50 euros.",
    
    # Returns and Refunds
    "what is your return policy?": "We accept returns within 14 days of purchase, provided the product is unused and in its original packaging. Some exclusions apply.",
    "how do i return a product?": "To return a product, contact us with your order number and reason for return. We’ll guide you through the process.",
    "when will i receive my refund?": "Once we receive and inspect the returned product, your refund will be processed within 5-7 business days.",
    
    # Customer Support
    "what should i do if i have an issue with my order?": "If you experience any issues with your order, such as incorrect items or damaged products, please contact our support team at 0465494147 or arafatbisola111@gmail.com.",
    "how can i give feedback on my experience?": "We value your feedback! Feel free to leave a review or send your feedback directly to arafatbisola111@gmail.com.",
    
    # Chatbot Limitations and Escalation
    "what if the chatbot can’t answer my question?": "If the chatbot cannot assist, it will redirect you to a human agent. You can also type 'Talk to a human' at any time.",
    "how do i contact a live agent?": "If you need a live agent, type 'Talk to a human,' or contact us via WhatsApp or phone at 0465494147.",
    
    # Privacy and Security
    "is my personal information secure with af beauty castle?": "Yes, we take your privacy seriously. All personal information is protected and will not be shared with third parties.",
    "how is my payment information secured?": "All payment transactions are securely processed through our trusted payment gateway. We do not store your credit card information."
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
