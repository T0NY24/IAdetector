from flask import Blueprint, request, jsonify
from services.deepseek_client import DeepSeekClient

bp = Blueprint("semantic", __name__, url_prefix="/api/semantic")

# Inicializar cliente
deepseek = DeepSeekClient()

@bp.route("/deepseek", methods=["POST"])
def deepseek_route():
    print("DEBUG: Received request to /api/semantic/deepseek")
    try:
        data = request.get_json()
        print(f"DEBUG: Request payload: {data}")

        prompt = data.get("prompt")
        if not prompt:
            print("DEBUG: Missing prompt")
            return jsonify({"error": "Missing prompt"}), 400

        print("DEBUG: Calling DeepSeek client...")
        result = deepseek.ask(prompt)
        print(f"DEBUG: DeepSeek result: {result}")

        if not result["success"]:
            print(f"DEBUG: Returning error 500: {result}")
            return jsonify(result), 500

        return jsonify(result)
    except Exception as e:
        print(f"DEBUG: Exception in route: {str(e)}")

@bp.route('/chat_analysis', methods=['POST'])
def chat_analysis():
    try:
        data = request.get_json()
        message = data.get('message')
        context = data.get('context')
        
        if not message or not context:
            return jsonify({"error": "Missing message or context"}), 400

        # Construir prompt con contexto
        system_prompt = f"""
        Eres el Asistente Forense de la plataforma ForensicAI.
        Acabas de analizar una imagen y este es el resultado técnico (JSON):
        {context}
        
        Tu tarea es explicar estos resultados al usuario y responder sus dudas.
        NO inventes datos. Basa tus respuestas ÚNICAMENTE en la evidencia del JSON.
        Sé profesional, técnico pero accesible.
        """
        
        full_prompt = f"{system_prompt}\n\nUsuario: {message}"
        
        # Usar el cliente existente
        result = deepseek.ask(full_prompt)
        
        if not result["success"]:
            return jsonify({"error": result.get("error", "Error desconocido")}), 500
            
        answer = result["response"]
        
        # Limpiar tags de pensamiento si existen
        if "</think>" in answer:
            answer = answer.split("</think>")[-1].strip()
            
        return jsonify({"response": answer})

    except Exception as e:
        print(f"Error in chat_analysis: {e}")
        return jsonify({"error": str(e)}), 500
