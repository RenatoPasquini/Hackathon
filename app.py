# app.py (Backend Flask)

import os
import json
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
from openai import OpenAI
#from IPython.display import Markdown, display, update_display

# Carregar variáveis de ambiente do ficheiro .env
load_dotenv()

app = Flask(__name__, template_folder='template', static_folder='static')

# Configurar a API Key do Gemini
try:
    gemini_api_key = os.environ.get("GEMINI_API_KEY")
    if not gemini_api_key:
        raise ValueError("A GEMINI_API_KEY não foi definida no ficheiro .env")
    # OPENAI.api_key = gemini_api_key
    # Modelo OpenAI a ser utilizado (pode ajustar conforme necessário)
    model_gemini = "gemini-2.0-flash"  # Ou outro modelo da OpenAI de sua preferência
    gemini = OpenAI(
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        api_key=gemini_api_key,
    )
    print("Modelo Gemini configurado com sucesso.")
except Exception as e:
    print(f"Erro ao configurar o Gemini: {e}")
    gemini = None  # Impede a execução se o modelo não estiver configurado


DB_FILE = "event_data_poc.json"


def read_db():
    """Lê os dados do ficheiro JSON."""
    if not os.path.exists(DB_FILE):
        return {"eventos_registados": []}
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            # Lidar com ficheiro vazio
            content = f.read()
            if not content:
                return {"eventos_registados": []}
            return json.loads(content)
    except (json.JSONDecodeError, FileNotFoundError):
        return {"eventos_registados": []}  # Retorna uma estrutura válida em caso de erro


def write_db(data):
    """Escreve os dados no ficheiro JSON."""
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


@app.route("/")
def index():
    """Renderiza a página principal do wizard."""
    return render_template("index.html")


@app.route("/api/suggest_themes", methods=["POST"])
def suggest_themes_route():
    """
    Endpoint da API para receber detalhes do evento e devolver sugestões de temas do LLM.
    Atua como o "Orquestrador" que delega ao "Agente de Tematização" (simulado pelo LLM).
    """
    if not gemini:
        return (
            jsonify({"erro": "O modelo Gemini não está configurado. Verifique a API Key."}),
            500,
        )

    try:
        event_details = request.json
        if not event_details:
            return jsonify({"erro": "Nenhum detalhe do evento foi fornecido."}), 400

        print(f"Detalhes do evento recebidos para sugestão de temas: {event_details}")

        # --- Lógica do Orquestrador e Prompt para o Agente de Tematização ---
        prompt_parts = [
            {
                "role": "system",
                "content": "Você é um assistente especialista em criar temas criativos e adequados para eventos corporativos.",
            },
            {
                "role": "user",
                "content": "Com base nos seguintes detalhes fornecidos pelo organizador, sugira 3 (três) temas distintos para o evento. Para cada tema, forneça um nome conciso e uma breve descrição (1-2 frases) que explique o conceito.",
            },
            {
                "role": "user",
                "content": f"Detalhes do Evento:\n- Nome do Evento: {event_details.get('eventName', 'Não especificado')}\n- Tipo de Evento: {event_details.get('eventType', 'Não especificado')}\n- Número Estimado de Pessoas: {event_details.get('guestCount', 'Não especificado')}\n- Orçamento Preliminar: {event_details.get('budget', 'Não especificado')}\n- Data Desejada: {event_details.get('eventDate', 'Não especificado')}\n- Principal Objetivo/Mensagem: {event_details.get('eventObjective', 'Não especificado')}",
            },
        ]
        if event_details.get("themeIdea"):
            prompt_parts.append(
                {
                    "role": "user",
                    "content": f"- Ideia Inicial de Tema (do organizador): {event_details.get('themeIdea')}",
                }
            )

        prompt_parts.append(
            {
                "role": "user",
                "content": "Por favor, formate a sua resposta claramente, listando cada tema e sua descrição. Exemplo de formato para cada tema:\nTema 1: [Nome do Tema 1]\nDescrição: [Descrição do Tema 1]",
            }
        )
        print("\n--- Prompt Estruturado para o Gemini (Agente de Tematização) ---")
        print(prompt_parts)
        print("--- Fim do Prompt ---\n")

        # Chamada ao LLM (Gemini)
        stream = True
        try:
            completion = gemini.chat.completions.create(
                model=model_gemini, 
                messages=prompt_parts, 
                stream=stream
            )
            if stream:
                llm_suggestions_text = ""
                #display_handle = display(Markdown(""), display_id=True)
                for chunk in completion:
                    llm_suggestions_text += chunk.choices[0].delta.content or ''
                    llm_suggestions_text = llm_suggestions_text.replace("```","").replace("markdown", "")
                    #update_display(Markdown(llm_suggestions_text), display_id=display_handle.display_id)
            else:
                llm_suggestions_text = completion.choices[0].message.content
            
        except Exception as e_openai:
            print(f"Erro ao comunicar com a API do OpenAI: {e_openai}")
            return (
                jsonify({"erro": f"Não foi possível obter sugestões do LLM: {e_openai}"}),
                503,
            )

        print(f"Sugestões recebidas do LLM: {llm_suggestions_text}")

        # Guardar no "banco de dados" JSON
        db_data = read_db()
        novo_evento_registado = {
            "id_evento": f"evt_{len(db_data['eventos_registados']) + 1}",
            "detalhes_fornecidos": event_details,
            "prompt_enviado_llm": prompt_parts,  # Para debugging e referência
            "sugestoes_temas_llm": llm_suggestions_text,
        }
        db_data["eventos_registados"].append(novo_evento_registado)
        write_db(db_data)

        return jsonify(
            {
            "mensagem": "Sugestões de temas geradas com sucesso!",
                "sugestoes_temas": llm_suggestions_text,
            }
        )

    except Exception as e:
        print(f"Erro inesperado no endpoint /api/suggest_themes: {e}")
        return (
            jsonify({"erro": f"Ocorreu um erro interno no servidor: {e}"}),
            500,
        )


if __name__ == "__main__":
    # Garante que as pastas 'templates' e 'static' existem no mesmo nível que app.py
    # ou ajuste os caminhos em Flask(..., template_folder=..., static_folder=...)
    app.run(debug=True, port=5001) 

