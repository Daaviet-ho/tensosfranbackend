from flask import Flask, request, jsonify, send_from_directory
from groq import Groq
from flask_cors import CORS
import os
import socket

def get_local_ip():
    try:
        # Obtener el nombre del host
        hostname = socket.gethostname()
        # Obtener la dirección IP local
        local_ip = socket.gethostbyname(hostname)
        return local_ip
    except:
        return "localhost"

app = Flask(__name__, static_folder='.')
CORS(app, resources={r"/*": {"origins": "*"}})

# Configurar la API key de Groq
os.environ["GROQ_API_KEY"] = "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"
client = Groq()

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('.', path)

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message', '')
    
    try:
        completion = client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=[
                {
                    "role": "system",
                    "content": "Eres Fran, el dueño de la página en la que estás incorporado. Tu objetivo es ayudarle al cliente a ubicarse dentro de la página y resolver sus dudas sobre esta misma. Eres el dueño de un negocio ubicado en Ibiza especializado en tensos de pérgola. Debes ser amable, profesional y mostrar tu experiencia en el campo de los tensos de pérgola. Responde como si fueras el dueño real del negocio."
                },
                {
                    "role": "user",
                    "content": user_message
                }
            ],
            temperature=1,
            max_completion_tokens=1024,
            top_p=1,
            stream=False,
            stop=None,
        )
        
        response = completion.choices[0].message.content
        return jsonify({"response": response})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    local_ip = get_local_ip()
    print(f"\nAccede desde tu teléfono usando: http://{local_ip}:5000\n")
    app.run(debug=True, host='0.0.0.0', port=5000)
