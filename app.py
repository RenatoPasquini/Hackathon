# app.py (Backend Flask)

import os
import json
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
import google.generativeai as genai

# Carregar variáveis de ambiente do ficheiro .env
load_dotenv()

app = Flask(__name__, template_folder='template', static_folder='static')

# Configurar a API Key do Gemini
# Certifique-se de que tem a variável GEMINI_API_KEY no seu ficheiro .env
try:
    gemini_api_key = os.environ["GEMINI_API_KEY"]
    if not gemini_api_key:
        raise ValueError("A GEMINI_API_KEY não foi definida no ficheiro .env")
    genai.configure(api_key=gemini_api_key)
    # Modelo Gemini a ser utilizado (pode ajustar conforme necessário)
    model = genai.GenerativeModel('gemini-2.0-flash')
    print("Modelo Gemini configurado com sucesso.")
except Exception as e:
    print(f"Erro crucial ao configurar o Gemini: {e}")
    print("Por favor, verifique se a GEMINI_API_KEY está corretamente definida no seu ficheiro .env.")
    model = None # Impede a execução se o modelo não estiver configurado

DB_FILE = 'event_data_poc.json'

def read_db():
    """Lê os dados do ficheiro JSON."""
    if not os.path.exists(DB_FILE):
        return {"eventos_registados": []}
    try:
        with open(DB_FILE, 'r', encoding='utf-8') as f:
            # Lidar com ficheiro vazio
            content = f.read()
            if not content:
                return {"eventos_registados": []}
            return json.loads(content)
    except (json.JSONDecodeError, FileNotFoundError):
        return {"eventos_registados": []} # Retorna uma estrutura válida em caso de erro

def write_db(data):
    """Escreve os dados no ficheiro JSON."""
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

@app.route('/')
def index():
    """Renderiza a página principal do wizard."""
    return render_template('index.html')

@app.route('/api/suggest_themes', methods=['POST'])
def suggest_themes_route():
    """
    Endpoint da API para receber detalhes do evento e devolver sugestões de temas do LLM.
    Atua como o "Orquestrador" que delega ao "Agente de Tematização" (simulado pelo LLM).
    """
    if not model:
        return jsonify({"erro": "O modelo Gemini não está configurado. Verifique a API Key."}), 500

    try:
        event_details = request.json
        if not event_details:
            return jsonify({"erro": "Nenhum detalhe do evento foi fornecido."}), 400

        print(f"Detalhes do evento recebidos para sugestão de temas: {event_details}")

        # --- Lógica do Orquestrador e Prompt para o Agente de Tematização ---
        prompt_parts = [
            "Você é um assistente especialista em criar temas criativos e adequados para eventos corporativos.",
            "Com base nos seguintes detalhes fornecidos pelo organizador, sugira 3 (três) temas distintos para o evento.",
            "Para cada tema, forneça um nome conciso e uma breve descrição (1-2 frases) que explique o conceito.",
            "\nDetalhes do Evento:",
            f"- Nome do Evento: {event_details.get('eventName', 'Não especificado')}",
            f"- Tipo de Evento: {event_details.get('eventType', 'Não especificado')}",
            f"- Número Estimado de Pessoas: {event_details.get('guestCount', 'Não especificado')}",
            f"- Orçamento Preliminar: {event_details.get('budget', 'Não especificado')}",
            f"- Data Desejada: {event_details.get('eventDate', 'Não especificado')}",
            f"- Principal Objetivo/Mensagem: {event_details.get('eventObjective', 'Não especificado')}",
        ]
        if event_details.get('themeIdea'):
            prompt_parts.append(f"- Ideia Inicial de Tema (do organizador): {event_details.get('themeIdea')}")

        prompt_parts.append("\nPor favor, formate a sua resposta claramente, listando cada tema e sua descrição.")
        prompt_parts.append("Exemplo de formato para cada tema:\nTema 1: [Nome do Tema 1]\nDescrição: [Descrição do Tema 1]\n")

        final_prompt = "\n".join(prompt_parts)

        print("\n--- Prompt Estruturado para o Gemini (Agente de Tematização) ---")
        print(final_prompt)
        print("--- Fim do Prompt ---\n")

        # Chamada ao LLM (Gemini)
        try:
            response = model.generate_content(final_prompt)
            # Aceder ao texto da resposta. A API pode variar ligeiramente.
            # Para gemini-1.5-flash, response.text é comum.
            # Verifique a documentação se response.parts[0].text for necessário.
            llm_suggestions_text = response.text
        except Exception as e_gemini:
            print(f"Erro ao comunicar com a API do Gemini: {e_gemini}")
            return jsonify({"erro": f"Não foi possível obter sugestões do LLM: {e_gemini}"}), 503 # Service Unavailable

        print(f"Sugestões recebidas do LLM: {llm_suggestions_text}")

        # Guardar no "banco de dados" JSON
        db_data = read_db()
        novo_evento_registado = {
            "id_evento": f"evt_{len(db_data['eventos_registados']) + 1}",
            "detalhes_fornecidos": event_details,
            "prompt_enviado_llm": final_prompt, # Para debugging e referência
            "sugestoes_temas_llm": llm_suggestions_text
        }
        db_data["eventos_registados"].append(novo_evento_registado)
        write_db(db_data)

        return jsonify({
            "mensagem": "Sugestões de temas geradas com sucesso!",
            "sugestoes_temas": llm_suggestions_text
        })

    except Exception as e:
        print(f"Erro inesperado no endpoint /api/suggest_themes: {e}")
        return jsonify({"erro": f"Ocorreu um erro interno no servidor: {e}"}), 500

if __name__ == '__main__':
    # Garante que as pastas 'templates' e 'static' existem no mesmo nível que app.py
    # ou ajuste os caminhos em Flask(..., template_folder=..., static_folder=...)
    app.run(debug=True, port=5001) 