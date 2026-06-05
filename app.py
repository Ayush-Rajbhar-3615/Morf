from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

# DeepSeek API Configuration
DEEPSEEK_API_KEY = os.environ.get('DEEPSEEK_API_KEY', 'your-deepseek-api-key-here')
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

SYSTEM_PROMPT = """You are MORF AI, a next-generation intelligent AI assistant created by Ayush Rajbhar. 
You are helpful, creative, and knowledgeable. Your responses should be engaging, accurate, and well-structured.
You can help with coding, writing, analysis, creative tasks, and general questions.

About your creator:
- Founder: Ayush Rajbhar
- Vision: To make advanced AI accessible to everyone
- Mission: Empowering users through intelligent assistance

Respond in a warm, professional manner. Use markdown formatting for better readability when appropriate (bold, code blocks, lists).
Current date and time: {current_time}"""

def get_current_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        user_message = data.get('message', '')
        history = data.get('history', [])
        
        if not user_message:
            return jsonify({'error': 'No message provided'}), 400
        
        # Prepare messages for DeepSeek API
        messages = [
            {'role': 'system', 'content': SYSTEM_PROMPT.format(current_time=get_current_time())}
        ]
        
        # Add conversation history (last 10 exchanges)
        if history:
            messages.extend(history[-20:])  # Keep last 20 messages for context
        
        # Add current user message
        messages.append({'role': 'user', 'content': user_message})
        
        headers = {
            'Authorization': f'Bearer {DEEPSEEK_API_KEY}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'model': 'deepseek-chat',
            'messages': messages,
            'temperature': 0.7,
            'max_tokens': 2000,
            'stream': False
        }
        
        response = requests.post(DEEPSEEK_API_URL, headers=headers, json=payload, timeout=45)
        
        if response.status_code == 200:
            result = response.json()
            ai_response = result['choices'][0]['message']['content']
            return jsonify({'response': ai_response})
        else:
            error_msg = f"DeepSeek API error: {response.status_code}"
            print(error_msg)
            print(response.text)
            return jsonify({'response': 'I apologize, but I\'m having technical difficulties. Please try again in a moment.'}), 200
            
    except requests.exceptions.Timeout:
        return jsonify({'response': 'The request timed out. Please try again with a shorter message.'}), 200
    except requests.exceptions.ConnectionError:
        return jsonify({'response': 'Connection error. Please check your internet connection and try again.'}), 200
    except Exception as e:
        print(f"Error in chat endpoint: {str(e)}")
        return jsonify({'response': 'An unexpected error occurred. Our team has been notified. Please try again.'}), 200

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'service': 'MORF AI',
        'version': '2.0.0',
        'founder': 'Ayush Rajbhar',
        'timestamp': get_current_time()
    })

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        'name': 'MORF AI API',
        'version': '2.0.0',
        'founder': 'Ayush Rajbhar',
        'status': 'running',
        'endpoints': {
            '/api/chat': 'POST - Send messages to MORF AI',
            '/api/health': 'GET - Check API health'
        }
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
