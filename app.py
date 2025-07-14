from flask import Flask, request, jsonify, send_from_directory
from groq import Groq
from flask_cors import CORS
import os
import socket
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

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

# Get the API key from environment variables
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise ValueError("GROQ_API_KEY environment variable is not set")
client = Groq()

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('.', path)

# Almacenamiento en memoria para las conversaciones
conversations = {}

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message', '')
    conversation_id = data.get('conversationId', 'default')
    
    # Inicializar o recuperar el historial de la conversación
    if conversation_id not in conversations:
        conversations[conversation_id] = [
            {
                "role": "system",
                "content": """Eres Fran, un artesano apasionado y dueño de un negocio de tensos de pérgola en Ibiza. 
                Tienes más de 15 años de experiencia en el sector y te enorgullece ofrecer productos artesanales de alta calidad.

                Personalidad y estilo de comunicación:
                - Cercano y amable, pero profesional
                - Usa un tono conversacional natural, como si estuvieras hablando cara a cara
                - Comparte ocasionalmente anécdotas sobre tu experiencia en el sector
                - Muestra entusiasmo por tu trabajo y los productos
                - Usa "tú" en vez de "usted" para ser más cercano
                
                Conocimientos específicos:
                - Experto en materiales y técnicas de tensado
                - Conocimiento profundo sobre medidas, instalación y mantenimiento
                - Familiarizado con las condiciones climáticas de Ibiza y cómo afectan a los tensos
                
                Aspectos clave del negocio:
                - Fabricación artesanal a medida
                - Servicio personalizado
                - Envíos a toda España
                - Especialización en pérgolas para espacios residenciales y comerciales

                Recuerda el contexto de las conversaciones anteriores y haz referencias a ellas cuando sea relevante.
                Evita repetir exactamente las mismas frases y adapta tus respuestas al flujo natural de la conversación."""
            }
        ]
    
    # Añadir el mensaje del usuario al historial
    conversations[conversation_id].append({
        "role": "user",
        "content": user_message
    })
    
    try:
        completion = client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=conversations[conversation_id],
            temperature=1,
            max_completion_tokens=1024,
            top_p=1,
            stream=False,
            stop=None,
        )
        
        response = completion.choices[0].message.content
        
        # Añadir la respuesta del asistente al historial
        conversations[conversation_id].append({
            "role": "assistant",
            "content": response
        })
        
        # Mantener solo los últimos 10 mensajes para evitar que el contexto sea demasiado largo
        if len(conversations[conversation_id]) > 12:  # 1 system + 10 mensajes + 1 nuevo
            conversations[conversation_id] = [
                conversations[conversation_id][0]  # Mantener el mensaje del sistema
            ] + conversations[conversation_id][-10:]  # Mantener los últimos 10 mensajes
        
        return jsonify({"response": response})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    local_ip = get_local_ip()
    print(f"\nAccede desde tu teléfono usando: http://{local_ip}:5000\n")
    app.run(debug=True, host='0.0.0.0', port=5000)
