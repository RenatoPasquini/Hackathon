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

# Configurar as API Keys
try:
    gemini_api_key = os.environ.get("GEMINI_API_KEY")
    if not gemini_api_key:
        raise ValueError("A GEMINI_API_KEY não foi definida no ficheiro .env")

    food_api_key = os.environ.get("FOOD_API_KEY")
    if not food_api_key:
        raise ValueError("A FOOD_API_KEY não foi definida no ficheiro .env")

    activities_api_key = os.environ.get("ACTIVITIES_API_KEY")
    if not activities_api_key:
        raise ValueError("A ACTIVITIES_API_KEY não foi definida no ficheiro .env")

    spotify_api_key = os.environ.get("SPOTIFY_API_KEY")
    if not spotify_api_key:
        raise ValueError("A SPOTIFY_API_KEY não foi definida no ficheiro .env")

    party_place_api_key = os.environ.get("PARTY_PLACE_API_KEY")
    if not party_place_api_key:
        raise ValueError("A PARTY_PLACE_API_KEY não foi definida no ficheiro .env")

    # Modelo OpenAI a ser utilizado (pode ajustar conforme necessário)
    # Configuração das APIs
    api_configurations = {
        "gemini": {
            "model": "gemini-2.0-flash",  # Ou outro modelo da OpenAI de sua preferência
            "url": "https://generativelanguage.googleapis.com/v1beta/openai/",
            "api_key": gemini_api_key,
            "client": None  # Inicializado posteriormente
        },
        "food": {
            "model": "gemini-2.0-flash",
            "api_key": food_api_key,
            "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/",
            "client": None  # Inicializado posteriormente
        },
        "activity": {
            "model": "gemini-2.0-flash",
            "api_key": activities_api_key,
            "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/",
            "client": None  # Inicializado posteriormente
        },
        "spotify": {
            "model": "gemini-2.0-flash",
            "api_key": spotify_api_key,
            "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/",
            "client": None  # Inicializado posteriormente
        },
        "party_place": {
            "model": "gemini-2.0-flash",
            "api_key": party_place_api_key,
            "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/",
            "client": None  # Inicializado posteriormente
        }
    }

    # Inicializar o cliente Gemini
    try:
        gemini_api = OpenAI(
            base_url=api_configurations["gemini"]["url"],
            api_key=api_configurations["gemini"]["api_key"],
        )
        print("Modelo Gemini configurado com sucesso.")
    except Exception as e:
        print(f"Erro ao configurar o modelo Gemini: {e}")
        gemini = None  # Garante que gemini seja None em caso de falha

    # Inicializar outras APIs
    try:
        food_api = OpenAI(api_key=api_configurations["food"]["api_key"], base_url=api_configurations["food"]["base_url"])
        print("Modelo de food_api configurado com sucesso.")
        activities_api = OpenAI(api_key=api_configurations["activity"]["api_key"], base_url=api_configurations["activity"]["base_url"])
        print("Modelo de activities_api configurado com sucesso.")
        spotify_api = OpenAI(api_key=api_configurations["spotify"]["api_key"], base_url=api_configurations["spotify"]["base_url"])
        print("Modelo de spotify_api configurado com sucesso.")
        party_place_api = OpenAI(api_key=api_configurations["party_place"]["api_key"], base_url=api_configurations["party_place"]["base_url"])
        print("Modelo de party_place_api configurado com sucesso.")
        print("Todas as APIs foram configuradas com sucesso.")
    except Exception as e:
        print(f"Erro ao configurar as APIs: {e}")
        # Considerar definir as APIs como None em caso de falha, similar ao Gemini
        food_api = None
        activities_api = None
        spotify_api = None
        party_place_api = None
except Exception as e:
    print(f"Erro ao configurar as APIs: {e}")
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

def get_food_suggestions(event_details, prompt):
    """Obtém sugestões de comida."""
    try:
        print("Estou a começar a Food")
        completion = food_api.chat.completions.create(
            model=api_configurations["food"]["model"],
            messages=[{"role": "user", "content": f"{prompt}. Detalhes do Evento: {event_details}"}],
        )
        return completion.choices[0].message.content
    except Exception as e:
        print(f"Erro ao obter sugestões de comida: {e}")
        return "Não foi possível obter sugestões de comida."

def get_activities_suggestions(event_details, prompt):
    """Obtém sugestões de atividades."""
    try:
        print("Estou a começar as atividades")
        completion = activities_api.chat.completions.create(
            model=api_configurations["activity"]["model"],
            messages=[{"role": "user", "content": f"{prompt}. Detalhes do Evento: {event_details}"}],
        )
        return completion.choices[0].message.content
    except Exception as e:
        print(f"Erro ao obter sugestões de atividades: {e}")
        return "Não foi possível obter sugestões de atividades."

def get_spotify_playlist(event_details, prompt):
    """Obtém sugestões de playlist do Spotify."""
    try:
        print("Estou a começar as musicas")
        completion = spotify_api.chat.completions.create(
            model=api_configurations["spotify"]["model"],
            messages=[{"role": "user", "content": f"{prompt}. Detalhes do Evento: {event_details}"}],
        )
        return completion.choices[0].message.content
    except Exception as e:
        print(f"Erro ao obter sugestões de playlist: {e}")
        return "Não foi possível obter sugestões de playlist."

def get_party_place(event_details, prompt):
    """Obtém sugestões de local para a festa."""
    try:
        print("Estou a começar o local")
        completion = party_place_api.chat.completions.create(
            model=api_configurations["party_place"]["model"],
            messages=[{"role": "user", "content": f"{prompt}. Detalhes do Evento: {event_details}"}],
        )
        return completion.choices[0].message.content
    except Exception as e:
        print(f"Erro ao obter sugestões de local: {e}")
        return "Não foi possível obter sugestões de local."


@app.route("/")
def index():
    """Renderiza a página principal do wizard."""
    return render_template("index.html")


@app.route("/", methods=["POST"])
def compile_responses_route():
    """
    Endpoint da API para receber detalhes do evento e devolver respostas compiladas de várias APIs.
    Atua como o "Orquestrador" que delega a várias APIs especializadas.
    """
    if not gemini_api:
        return (
            jsonify({"erro": "O modelo OpenAI não está configurado. Verifique a API Key."}),
            500,
        )
    try:
        event_details = request.json
        if not event_details:
            return jsonify({"erro": "Nenhum detalhe do evento foi fornecido."}), 400
        print(f"Detalhes do evento recebidos para sugestão de temas: {event_details}")
        # --- Prompts para cada API ---
        food_prompt = f"Sugira opções de comida e bebida para um evento.E recomenda quantidades em função do numero de participantes, budget e o tema. Detalhes do Evento: {event_details}"
        activities_prompt = f"Sugira atividades para um evento. Tem em conta a altura do ano e o budget. Podes também considerar contratar alguam especie de entretenimento Detalhes do Evento: {event_details}"
        spotify_prompt = f"Sugira uma playlist do Spotify para um evento.Sugere apenas algumas músicas. Detalhes do Evento: {event_details}"
        party_place_prompt = f"Sugira um local para a festa.Tem em conta a altrua do ano com o tempo e o budget. O escritório da empresa que vai organizar o evento tem um terraço espaçoso para cerca de 35 pessoas e uma zona de almoço confortavél para cerca de 15 pessoas.Detalhes do Evento: {event_details}"
        # Obter respostas de várias APIs
        food_response = get_food_suggestions(event_details, food_prompt)
        activities_response = get_activities_suggestions(event_details, activities_prompt)
        spotify_response = get_spotify_playlist(event_details, spotify_prompt)
        party_place_response = get_party_place(event_details, party_place_prompt)

        print(f"Detalhes do evento recebidos para compilação de respostas: {event_details}")
        print(f"Resposta da API de comida: {food_response}")
        print(f"Resposta da API de atividades: {activities_response}")
        print(f"Resposta da API do Spotify: {spotify_response}")
        print(f"Resposta da API do local da festa: {party_place_response}")
        # --- Prompt para o Gemini compilar as respostas ---
        compilation_prompt = f"""
        Considere as seguintes sugestões para um evento que outros agentes decidiram e tu vais servir como compilador de todos para apresentar uma resposta unidficada e coerente:
        Comida: {food_response}
        Atividades: {activities_response}
        Playlist Spotify: {spotify_response}
        Local da Festa: {party_place_response}

        Com base nestas sugestões, crie uma resposta final em formato Markdown.
        """

        try:
            print("Estou a começar o final")
            completion = gemini_api.chat.completions.create(
                model=api_configurations["gemini"]["model"],
                messages=[{"role": "user", "content": compilation_prompt}],
            )
            compiled_response = completion.choices[0].message.content
        except Exception as e:
            print(f"Erro ao obter a resposta compilada do Gemini: {e}")
            compiled_response = "Não foi possível compilar as respostas."

        print(f"Resposta compilada pelo Gemini em Markdown: {compiled_response}")

        return jsonify({"compiled_response": compiled_response})

    except Exception as e:
        print(f"Erro inesperado no endpoint /api/compile_responses: {e}")
        return (
            jsonify({"erro": f"Ocorreu um erro interno no servidor: {e}"}),
            500,
        )


if __name__ == "__main__":
    # Garante que as pastas 'templates' e 'static' existem no mesmo nível que app.py
    # ou ajuste os caminhos em Flask(..., template_folder=..., static_folder=...)
    app.run(debug=True, port=5001)
