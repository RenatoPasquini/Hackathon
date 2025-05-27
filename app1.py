import streamlit as st
import json
import os
import google.generativeai as genai
from dotenv import load_dotenv
import datetime # Importar datetime para o valor padrão de data_prevista_dt

# --- Configuração Inicial e Carregamento da API Key ---
try:
    load_dotenv()
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    if not GEMINI_API_KEY:
        if hasattr(st, 'secrets') and 'GEMINI_API_KEY' in st.secrets:
            GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
        else:
            st.error("Ops! A GEMINI_API_KEY não foi encontrada. Crie um ficheiro .env ou configure-a nos secrets do Streamlit Cloud.")
            st.stop()

    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-2.0-flash')
    print("Modelo Gemini configurado com sucesso.")
except Exception as e:
    st.error(f"Deu ruim na configuração do Gemini: {e}")
    st.stop()

# --- Simulação do Banco de Dados de Convidados (Arquivo JSON) ---
GUEST_LIST_FILE = "lista_convidados_poc.json"

def create_mock_guest_list():
    if not os.path.exists(GUEST_LIST_FILE):
        mock_data = [
            {"nome": "Carlos Alberto Nóbrega", "email": "carlos@empresa.com", "presenca_confirmada": True, "restricao_alimentar": "Vegetariano"},
            {"nome": "Maria Joaquina de Amaral Pereira Góes", "email": "maria.j@empresa.com", "presenca_confirmada": True, "restricao_alimentar": "Sem glúten"},
            {"nome": "João Kleber", "email": "joao.k@empresa.com", "presenca_confirmada": False, "restricao_alimentar": "Nenhuma"},
            {"nome": "Fausto Silva", "email": "fausto@empresa.com", "presenca_confirmada": True, "restricao_alimentar": "Nenhuma"},
            {"nome": "Silvio Santos", "email": "silvio@empresa.com", "presenca_confirmada": True, "restricao_alimentar": "Sem lactose"},
            {"nome": "Hebe Camargo", "email": "hebe@empresa.com", "presenca_confirmada": True, "restricao_alimentar": "Alérgico a camarão"}
        ]
        with open(GUEST_LIST_FILE, 'w', encoding='utf-8') as f:
            json.dump(mock_data, f, indent=2, ensure_ascii=False)
        print(f"Arquivo {GUEST_LIST_FILE} de exemplo criado.")

create_mock_guest_list()

# --- Funções dos Agentes (Simuladas e com Chamadas ao Gemini) ---

def agente_otimizador_festas(usar_feedback_passado):
    st.write("🧐 **Agente Otimizador de Festas consultando os universitários:** Relembrando os sucessos (e os micos) passados!")
    if usar_feedback_passado:
        try:
            prompt = """
            Você é um consultor de eventos experiente e bem-humorado.
            Com base em "pesquisas de satisfação de eventos corporativos anteriores" (use seu conhecimento geral sobre o que funciona e o que não funciona),
            forneça 3 dicas de ouro engraçadas e úteis para garantir que um evento corporativo seja um sucesso.
            Formate cada dica como um item de lista.
            """
            response = model.generate_content(prompt)
            return response.text.strip().split('\n')
        except Exception as e:
            st.error(f"O Agente Otimizador está com dor de cabeça: {e}")
            return ["Dica de emergência: Sirva bolo. Todo mundo gosta de bolo."]
    return ["Sem olhar para o passado desta vez? Ok, vida que segue, festa que surge! (Mas sério, um bom DJ faz milagres)."]

def agente_batizador_eventos(tipo_evento, objetivo_evento_str):
    st.write("🕵️‍♂️ **Agente Batizador entrando em cena:** Preparando nomes tão bons que vão virar meme!")
    try:
        prompt = f"""
        Você é um especialista em criar nomes para eventos corporativos, com um toque de humor e criatividade.
        Sugira 5 nomes engraçados e originais para um evento do tipo '{tipo_evento}'.
        Os objetivos principais do evento são: '{objetivo_evento_str if objetivo_evento_str else 'Não especificado, use a criatividade!'}'
        Liste os nomes, cada um em uma nova linha, sem numeração ou marcadores adicionais, apenas o nome.
        """
        response = model.generate_content(prompt)
        nomes_sugeridos = response.text.strip().split('\n')
        return [nome.replace("- ", "").strip() for nome in nomes_sugeridos if nome.strip()]
    except Exception as e:
        st.error(f"O Agente Batizador tropeçou feio: {e}")
        return ["Erro ao gerar nomes. Que tal 'Festa Surpresa do Chefe Que Não Sabe'?"]

def agente_sugestao_tema_com_restricoes(tipo_evento, ideia_tema_inicial, resumo_restricoes_str, sugestoes_comida_str=None):
    st.write("🎨 **Agente de Sugestão de Temas (com olhar clínico para dietas e cardápios) em ação!**")
    try:
        prompt_parts = [
            f"Você é um planejador de eventos criativo e consciente, especializado em sugerir temas para eventos corporativos do tipo '{tipo_evento}'.",
            "Sugira 3 temas originais e divertidos."
        ]
        if ideia_tema_inicial:
            prompt_parts.append(f"O organizador teve uma ideia inicial de tema: '{ideia_tema_inicial}'. Você pode se inspirar nela, melhorá-la ou sugerir alternativas.")
        
        if resumo_restricoes_str and "nenhuma" not in resumo_restricoes_str.lower() and "aparentemente" not in resumo_restricoes_str.lower() and "entrada manual" not in resumo_restricoes_str.lower():
            prompt_parts.append(f"Restrições alimentares predominantes no grupo: '{resumo_restricoes_str}'.")
        
        if sugestoes_comida_str and "nenhuma" not in sugestoes_comida_str.lower() and "flexível" not in sugestoes_comida_str.lower():
            prompt_parts.append(f"Com base nas restrições, foram sugeridos os seguintes conceitos de comida: '{sugestoes_comida_str}'. Tente alinhar os temas com essas sugestões gastronômicas, se possível, ou sugira temas que naturalmente acomodem essas opções.")
        else:
            prompt_parts.append("Não foram especificadas restrições alimentares significativas ou sugestões de comida específicas, então foque na criatividade geral do tema, mas mencione a versatilidade gastronômica se possível.")

        prompt_parts.extend([
            "Para cada tema sugerido, forneça:",
            "1. Nome do Tema (curto e chamativo)",
            "2. Descrição do Tema (1-2 frases explicando o conceito e o tom)",
            "3. Como o tema pode ser amigável às dietas e aos conceitos de comida sugeridos (se aplicável).",
            "Formate a resposta claramente para cada tema.",
            "Exemplo para um tema:",
            "Nome: Viagem Gastronômica Global",
            "Descrição: Uma celebração da culinária mundial, com estações representando diferentes países. Perfeito para paladares aventureiros!",
            "Amigável às Dietas/Comida: Extremamente versátil! Cada estação pode ter opções vegetarianas, veganas, sem glúten, etc., e se alinha bem com um conceito de 'comida internacional'."
        ])
        prompt = "\n".join(prompt_parts)
        # st.write(f"Debug - Prompt para Agente Sugestão de Temas:\n```\n{prompt}\n```")

        response = model.generate_content(prompt)
        sugestoes_formatadas = response.text.strip().split('\n\n') 
        if len(sugestoes_formatadas) < 2 and "\nNome:" in response.text: 
            sugestoes_formatadas = response.text.split("Nome:")[1:]
            sugestoes_formatadas = ["Nome: " + s.strip() for s in sugestoes_formatadas]

        return [s.strip() for s in sugestoes_formatadas if s.strip()]
    except Exception as e:
        st.error(f"O Agente de Sugestão de Temas está com bloqueio criativo (e técnico): {e}")
        return ["Tema Sugerido: 'A Festa do Improviso' (porque deu ruim aqui)."]


def agente_localizacao(tipo_evento, tema_final_escolhido, tipo_local_desejado, resumo_restricoes_str=None, sugestoes_comida_str=None, local_interno_especifico=None):
    st.write("🗺️ **Agente de Localização com o mapa na mão:** Procurando o esconderijo perfeito, considerando tema, dietas e tipos de comida!")
    sugestoes = []
    contatos_simulados = {}

    if tipo_local_desejado == "Interno na Empresa":
        if local_interno_especifico:
            sugestoes.append(f"Local Interno: {local_interno_especifico} da empresa. Vantagens: Custo zero (esperamos!), já é de casa. Desvantagens: A galera pode não desligar do trabalho.")
        else:
            sugestoes.append("Local Interno: Algum espaço bacana aí na empresa. Confere o auditório ou aquela área de convivência!")
        return sugestoes, contatos_simulados

    elif tipo_local_desejado == "Externo":
        try:
            prompt_local_parts = [
                "Você é um assistente de planejamento de eventos especializado em encontrar locais externos.",
                f"Para um evento corporativo do tipo '{tipo_evento}'"
            ]
            if tema_final_escolhido and tema_final_escolhido != "(Nenhum tema específico / Estilo Livre)":
                prompt_local_parts.append(f"O tema escolhido para o evento é: '{tema_final_escolhido}'. As sugestões de local devem, se possível, complementar ou ser adequadas a este tema.")

            prompt_local_parts.append(f"Sugira 2 opções de tipos de locais externos adequados (ex: Restaurante Temático que combine com o tema, Salão de Festas versátil, Chácara com boa estrutura).")

            if resumo_restricoes_str and "nenhuma" not in resumo_restricoes_str.lower() and "aparentemente" not in resumo_restricoes_str.lower() and "entrada manual" not in resumo_restricoes_str.lower() and "erro na leitura" not in resumo_restricoes_str.lower():
                 prompt_local_parts.append(f"Restrições alimentares predominantes no grupo: '{resumo_restricoes_str}'.")
            
            if sugestoes_comida_str and "nenhuma" not in sugestoes_comida_str.lower() and "flexível" not in sugestoes_comida_str.lower():
                prompt_local_parts.append(f"Conceitos de comida sugeridos com base nas dietas: '{sugestoes_comida_str}'.")
            
            prompt_local_parts.append("Ao sugerir restaurantes ou locais com buffet, mencione brevemente como eles poderiam atender às restrições e aos conceitos de comida mencionados, ou se são conhecidos por ter boas opções para dietas variadas e os tipos de cozinha sugeridos.")
            
            prompt_local_parts.extend([
                "Para cada sugestão, adicione uma breve justificativa (1 frase) e um \"contato simulado\" engraçado (ex: \"Falar com Chef Estrela Cadente - (11) 91234-5678, mestre em cardápios inclusivos\").",
                "Use seu conhecimento geral para dar sugestões criativas.",
                "Formate a resposta como:",
                "Opção 1: [Nome/Tipo do Local 1] - Justificativa: [Justificativa 1] - Adequação às Dietas/Comida: [Comentário] - Contato Simulado: [Contato 1]",
                "Opção 2: [Nome/Tipo do Local 2] - Justificativa: [Justificativa 2] - Adequação às Dietas/Comida: [Comentário] - Contato Simulado: [Contato 2]"
            ])
            prompt_local = "\n".join(prompt_local_parts)
            
            # st.write(f"Debug - Prompt para Agente Localização:\n```\n{prompt_local}\n```")

            response = model.generate_content(prompt_local)
            raw_sugestoes_bruto = response.text.strip()
            raw_sugestoes = []
            if "Opção 1:" in raw_sugestoes_bruto:
                partes_opcoes = raw_sugestoes_bruto.split("Opção ")[1:] 
                for parte in partes_opcoes:
                    raw_sugestoes.append("Opção " + parte.strip())
            else: 
                raw_sugestoes = raw_sugestoes_bruto.split('\n')

            current_option_lines = []
            for line_raw in raw_sugestoes:
                line = line_raw.strip()
                if line.startswith("Opção") and current_option_lines:
                    sugestoes.append(" ".join(current_option_lines).strip())
                    current_option_lines = [line]
                elif line: 
                    current_option_lines.append(line)
            if current_option_lines:
                sugestoes.append(" ".join(current_option_lines).strip())

            for sug_completa in sugestoes:
                if "Opção" in sug_completa and ("- Contato Simulado:" in sug_completa or "- Contato:" in sug_completa):
                    try:
                        contato_marker = "- Contato Simulado:" if "- Contato Simulado:" in sug_completa else "- Contato:"
                        partes_principais = sug_completa.split(contato_marker)
                        contato_info = partes_principais[-1].strip() if len(partes_principais) > 1 else "Contato Misterioso"
                        info_local = partes_principais[0]
                        nome_local_match = info_local.split(": ", 1)
                        if len(nome_local_match) > 1:
                            nome_local_contato = nome_local_match[1].split(" - Justificativa:")[0].strip()
                        else:
                            nome_local_contato = "Local Desconhecido"
                        contatos_simulados[nome_local_contato] = contato_info
                    except Exception as e_parse:
                        print(f"Erro ao parsear sugestão de local para contato: {sug_completa} - Erro: {e_parse}")
            if not sugestoes:
                 sugestoes.append("O Agente de Localização está consultando o Google Maps da alma... por enquanto, que tal um piquenique no parque se o tempo ajudar (e se não tiver restrição a formigas)?")
        except Exception as e:
            st.error(f"O Agente de Localização se perdeu no caminho: {e}")
            sugestoes.append("Deu pane no GPS do Agente de Localização. Sugestão: festa no metaverso? Lá todo mundo come pixel!")
        return sugestoes, contatos_simulados
    return ["Tipo de local não especificado claramente."], contatos_simulados


def agente_convidados_dietas(usar_json, arquivo_json_carregado):
    st.write("📋 **Agente de Convidados e Dietas na área:** De olho na lista VIP e nos 'não posso isso, não como aquilo'!")
    sugestoes_tipo_comida_str = "Cardápio flexível é uma boa pedida!" # Default
    
    if usar_json and arquivo_json_carregado:
        try:
            if hasattr(arquivo_json_carregado, 'getvalue'):
                 guest_data = json.loads(arquivo_json_carregado.getvalue().decode('utf-8'))
                 arquivo_json_carregado.seek(0)
            else:
                 with open(arquivo_json_carregado, 'r', encoding='utf-8') as f:
                    guest_data = json.load(f)

            confirmados = [p for p in guest_data if p.get("presenca_confirmada")]
            num_convidados = len(confirmados)
            restricoes = {}
            for convidado in confirmados:
                restricao = convidado.get("restricao_alimentar", "Nenhuma")
                if restricao and isinstance(restricao, str) and restricao.lower() != "nenhuma" and restricao.strip() != "":
                    restricoes[restricao] = restricoes.get(restricao, 0) + 1
            
            resumo_para_prompt = "Nenhuma específica"
            if not restricoes:
                resumo_detalhado_restricoes = "Aparentemente, todo mundo come de tudo! Ou esqueceram de avisar as frescurinhas... digo, restrições."
            else:
                lista_simples_restricoes = list(restricoes.keys())
                if len(lista_simples_restricoes) > 3:
                    resumo_para_prompt = ", ".join(lista_simples_restricoes[:3]) + " e outras."
                else:
                    resumo_para_prompt = ", ".join(lista_simples_restricoes)
                
                resumo_detalhado_restricoes = "Resumo das 'dietas especiais' da galera:\n" + \
                                   "\n".join([f"- {tipo}: {qtd} pessoa(s)" for tipo, qtd in restricoes.items()])
                
                # Nova chamada ao Gemini para sugerir tipos de comida
                try:
                    prompt_comida = f"""
                    Com base nas seguintes restrições alimentares de um grupo: {resumo_para_prompt}.
                    Sugira 2-3 tipos de culinária ou conceitos de buffet que seriam adequados e inclusivos para este grupo.
                    Por exemplo: 'Buffet com estações separadas para veganos e sem glúten', 'Cozinha Mediterrânea (rica em vegetais e opções leves)', 'Rodízio de Pizzas com opções sem glúten e veganas'.
                    Seja breve e direto nas sugestões.
                    """
                    response_comida = model.generate_content(prompt_comida)
                    sugestoes_tipo_comida_str = response_comida.text.strip()
                except Exception as e_comida:
                    st.warning(f"Agente de Dietas teve um soluço ao sugerir comidas: {e_comida}")
                    sugestoes_tipo_comida_str = "Foco em variedade para agradar a todos!"

            return num_convidados, resumo_detalhado_restricoes, resumo_para_prompt, sugestoes_tipo_comida_str
        except Exception as e:
            st.error(f"Ih, deu chabú ao ler o arquivo JSON dos convidados: {e}")
            return 0, "Não consegui ler a lista de convidados. Verifica o arquivo, por favor!", "Erro na leitura", sugestoes_tipo_comida_str
    elif usar_json:
        return 0, "Você disse que ia usar a lista, mas cadê o arquivo, meu consagrado?", "JSON não carregado", sugestoes_tipo_comida_str
    
    return None, "Número de pessoas a ser definido manualmente (restrições não analisadas).", "Entrada manual de público", sugestoes_tipo_comida_str

def agente_orcamentista(valor_disponivel, num_pessoas, tema_final_escolhido=None, sugestoes_locais_com_contatos=None):
    st.write("💰 **Agente Orçamentista fazendo as contas:** Money que é good nós não have, mas vamos ver o que dá pra fazer!")
    feedback_geral = ""
    if valor_disponivel is None or valor_disponivel == 0:
        feedback_geral = "Orçamento? Que orçamento? Estamos na base do 'fiado deluxe'?"
    elif num_pessoas is None or num_pessoas == 0:
        feedback_geral = "Sem saber quantas bocas pra alimentar (ou entreter), fica difícil pro Agente Orçamentista dar um pitaco preciso no custo por pessoa!"
    else:
        valor_por_pessoa = valor_disponivel / num_pessoas
        if valor_por_pessoa < 50:
            feedback_geral = f"Com R${valor_por_pessoa:.2f} por cabeça... vai ser um evento 'raiz', com coxinha e guaraná Dolly! Delícia!"
        elif valor_por_pessoa < 150:
            feedback_geral = f"R${valor_por_pessoa:.2f} por pessoa? Já dá pra pensar num churrasquinho honesto, talvez até com farofa gourmet!"
        else:
            feedback_geral = f"Uau! R${valor_por_pessoa:.2f} por pessoa? Prepara o caviar e o champagne, porque essa festa promete ser um luxo só!"

    if tema_final_escolhido and tema_final_escolhido != "(Nenhum tema específico / Estilo Livre)":
        feedback_geral += f"\nLembre-se que um tema como '{tema_final_escolhido}' pode adicionar uns trocados extras no orçamento para decoração e mimos temáticos, hein?! Planeje com carinho (e com a calculadora na mão)."

    feedback_locais = []
    if sugestoes_locais_com_contatos and (num_pessoas or 0) > 0:
        feedback_locais.append("\n**Análise de Custo para Locais Externos (Estimativa da POC):**")
        for nome_local, contato_str in sugestoes_locais_com_contatos.items(): 
            custo_simulado_por_pessoa = 0
            if isinstance(nome_local, str) and ("restaurante" in nome_local.lower() or "bistrô" in nome_local.lower() or "bar" in nome_local.lower()):
                custo_simulado_por_pessoa = float(os.getenv(f"CUSTO_POC_{nome_local.upper().replace(' ','_')}", default=75 + len(nome_local) % 50)) 
                custo_total_local = custo_simulado_por_pessoa * (num_pessoas or 1)
                feedback_locais.append(
                    f"- **{nome_local}:** Estimativa POC de R${custo_simulado_por_pessoa:.2f}/pessoa. "
                    f"Custo total estimado para {num_pessoas or 'X'} pessoas: R${custo_total_local:.2f}. Contato (simulado): {contato_str}"
                )
            else:
                 feedback_locais.append(f"- **{nome_local}:** Custo a verificar (não parece ser um restaurante para cálculo automático de POC). Contato (simulado): {contato_str}")
    
    final_feedback = feedback_geral
    if feedback_locais:
        final_feedback += "\n" + "\n".join(feedback_locais)
    return final_feedback


def agente_transporte(num_pessoas, local_evento_str, precisa_transporte_flag):
    st.write("🚌 **Agente de Transporte engatando a primeira:** Levando a galera pro rolê!")
    if not precisa_transporte_flag:
        return "Transporte por conta da galera? Menos uma preocupação (ou mais uma, dependendo do trânsito!)."
    
    local_evento_nome_curto = local_evento_str
    if isinstance(local_evento_str, str) and "-" in local_evento_str:
        try: 
            local_evento_nome_curto = local_evento_str.split(" - Justificativa:")[0].split(": ",1)[1].strip()
        except:
             pass

    if not local_evento_nome_curto or "Interno na Empresa" in local_evento_nome_curto: 
        return "Festa em casa (na empresa), então cada um com seu teletransporte (ou carro mesmo)."

    if num_pessoas is None or num_pessoas == 0:
        return "Sem saber quanta gente vai, fica difícil chamar o Uber ou o ônibus espacial."

    try:
        prompt = f"""
        Você é um especialista em logística de transporte para eventos corporativos.
        Para um evento externo com aproximadamente {num_pessoas} pessoas, que acontecerá em '{local_evento_nome_curto}',
        sugira 2-3 alternativas de transporte para os participantes, com um toque de humor.
        Considere opções como vans, ônibus fretado, ou incentivo a caronas/apps de transporte.
        """
        response = model.generate_content(prompt)
        sugestoes_transporte = response.text.strip().split('\n')
        return "\n".join([s.replace("- ","").strip() for s in sugestoes_transporte if s.strip()])
    except Exception as e:
        st.error(f"O Agente de Transporte furou o pneu: {e}")
        return "Deu ruim no transporte. Sugestão: todo mundo de patinete?"


# --- Controle do Wizard (Estado da Sessão) ---
if 'page' not in st.session_state:
    st.session_state.page = 1
if 'event_data' not in st.session_state:
    st.session_state.event_data = {
        'objetivos_selecionados': [],
        'objetivos_personalizados': [],
        'nome_evento_escolhido': None,
        'tema_final_escolhido': None 
    }
if 'objetivo_custom_temp_input' not in st.session_state:
    st.session_state.objetivo_custom_temp_input = ""
if 'sugestoes_nomes_cache' not in st.session_state:
    st.session_state.sugestoes_nomes_cache = None
if 'sugestoes_temas_cache' not in st.session_state:
    st.session_state.sugestoes_temas_cache = None


def next_page():
    st.session_state.page += 1
    st.rerun()

def prev_page():
    st.session_state.page -= 1
    st.rerun()

# --- Interface do Wizard ---
st.set_page_config(page_title="Planejador de Festas Malucas IA", layout="wide")
st.image("https://placehold.co/800x200/007bff/FFFFFF?text=Planejador+de+Festas+Corporativas+IA&font=sans-serif", use_container_width=True)
st.title("🎉 Planejador de Festas Corporativas IA 🎉")
st.subheader("Seu copiloto para eventos tão épicos que nem o chefe vai esquecer!")

# --- Página 1: Tipo de Evento, Nome e Objetivos ---
if st.session_state.page == 1:
    st.header("Página 1: O pontapé inicial da bagunça!")
    tipo_evento_opcoes = ["Confraternização", "Treinamento", "Team Building", "Workshop", "Lançamento de Produto", "Outro"]
    st.session_state.event_data['tipo_evento'] = st.selectbox(
        "Qual o tipo de evento que vamos aprontar?", tipo_evento_opcoes,
        index=tipo_evento_opcoes.index(st.session_state.event_data.get('tipo_evento', tipo_evento_opcoes[0])),
        key="tipo_evento_pg1"
    )
    st.session_state.event_data['nome_evento_input'] = st.text_input(
        "Qual o nome da criança... digo, do evento? (Opcional, viu?)",
        value=st.session_state.event_data.get('nome_evento_input', ''), key="nome_evento_input_pg1"
    )
    st.session_state.event_data['ajuda_nome'] = st.checkbox(
        "Preciso de uma luz divina (ou da IA) para batizar essa festança!",
        value=st.session_state.event_data.get('ajuda_nome', False), key="ajuda_nome_pg1"
    )
    if st.session_state.event_data['ajuda_nome'] and not st.session_state.event_data.get('nome_evento_input'):
        st.info("Maravilha! Na página de resultados, o Agente Batizador vai te dar umas ideias.")

    st.subheader("🎯 E qual é o grande objetivo por trás disso tudo?")
    opcoes_objetivos_comuns = [
        "Fazer a galera se enturmar (Integração)", "Celebrar as vitórias e conquistas do ano",
        "Apresentar novo produto/serviço com impacto", "Treinamento/Capacitação da equipe",
        "Fortalecer a cultura da empresa", "Networking e novas conexões",
        "Reconhecimento e premiação de colaboradores"
    ]
    st.session_state.event_data['objetivos_selecionados'] = st.multiselect(
        "Escolha os objetivos principais (pode marcar vários):", options=opcoes_objetivos_comuns,
        default=st.session_state.event_data.get('objetivos_selecionados', []), key="objetivos_sel_pg1"
    )
    st.markdown("##### Quer adicionar um objetivo super secreto ou específico?")
    st.session_state.objetivo_custom_temp_input = st.text_input(
        "Digite seu objetivo personalizado aqui:",
        value=st.session_state.get('objetivo_custom_temp_input', ""),
        placeholder="Ex: Dominar o mundo (começando pela festa!)", key="obj_custom_input_pg1"
    )
    if st.button("Adicionar Objetivo Personalizado", key="btn_add_obj_pg1"):
        if st.session_state.objetivo_custom_temp_input:
            if 'objetivos_personalizados' not in st.session_state.event_data:
                st.session_state.event_data['objetivos_personalizados'] = []
            st.session_state.event_data['objetivos_personalizados'].append(st.session_state.objetivo_custom_temp_input)
            st.session_state.objetivo_custom_temp_input = ""
            st.rerun()
        else:
            st.warning("Escreva alguma coisa aí, ué! Objetivo em branco não vale.")
    if st.session_state.event_data.get('objetivos_personalizados'):
        st.write("**Seus Objetivos Personalizados (até agora):**")
        objetivos_para_remover = []
        for i, obj_custom in enumerate(st.session_state.event_data['objetivos_personalizados']):
            col1_obj, col2_obj = st.columns([0.9, 0.1])
            with col1_obj: st.markdown(f"- {obj_custom}")
            with col2_obj:
                if st.button(f"🗑️", key=f"del_custom_obj_pg1_{i}", help="Remover este objetivo personalizado"):
                    objetivos_para_remover.append(i)
        if objetivos_para_remover:
            for index_to_remove in sorted(objetivos_para_remover, reverse=True):
                st.session_state.event_data['objetivos_personalizados'].pop(index_to_remove)
            st.rerun()
    if st.button("Próximo Passo: Orçamento e Convidados 👥", on_click=next_page, key="btn_prox_1_final_v2"): pass 


# --- Página 2: Orçamento e Público (Antiga Página 3) ---
elif st.session_state.page == 2:
    st.header("Página 2: Money, money, money... e a galera!") 
    st.session_state.event_data['valor_disponivel'] = st.number_input(
        "Quanto tem na carteira pra esse festerê? (Valor em R$)", min_value=0.0,
        value=st.session_state.event_data.get('valor_disponivel', 0.0), step=100.0, format="%.2f", key="valor_disp_pg2_new"
    )
    st.subheader("E o público, como vai ser?")
    fonte_convidados_escolha = st.radio(
        "Como vamos saber quem vem?",
        ("Informar quantidade manualmente", "Usar lista de presença (arquivo JSON)"),
        index=0 if st.session_state.event_data.get('fonte_convidados_raw', "manual") == "manual" else 1,
        key="radio_fonte_convidados_pg2_new"
    )
    st.session_state.event_data['fonte_convidados_raw'] = "manual" if fonte_convidados_escolha == "Informar quantidade manualmente" else "json"

    if st.session_state.event_data['fonte_convidados_raw'] == "manual":
        st.session_state.event_data['quantidade_pessoas_manual'] = st.number_input(
            "Quantas almas (estimadas) participarão?", min_value=1,
            value=st.session_state.event_data.get('quantidade_pessoas_manual', 10), step=1, key="qtd_manual_pg2_new"
        )
    else:
        st.markdown(f"Ok, vamos de JSON! Certifique-se que ele tem os campos: `nome`, `email`, `presenca_confirmada` (true/false), `restricao_alimentar`.\nUm arquivo de exemplo (`{GUEST_LIST_FILE}`) já está na área!")
        if 'uploader_key_count' not in st.session_state:
            st.session_state.uploader_key_count = 0
        
        arquivo_json_carregado = st.file_uploader(
            "Carregue o arquivo JSON da lista de presença:", 
            type=['json'], 
            key=f"uploader_convidados_pg2_new_{st.session_state.uploader_key_count}"
            )
        st.session_state.event_data['arquivo_json_obj'] = arquivo_json_carregado
        if arquivo_json_carregado: st.success("Arquivo JSON carregado!")
        else: st.warning("Esperando o arquivo JSON dos convidados...")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("⏪ Voltar (Tipo de Evento)", on_click=prev_page, key="btn_voltar_2_final_new"): pass 
    with col2:
        if st.button("Próximo Passo: Detalhes, Data e Local 🗓️📍", on_click=next_page, key="btn_prox_2_final_new"): pass 


# --- Página 3: Detalhes da Confraternização, Data e Local (Antiga Página 2) ---
elif st.session_state.page == 3:
    st.header("Página 3: Temperando a festa, definindo data e onde será o agito!") 
    if st.session_state.event_data.get('tipo_evento') == "Confraternização":
        st.markdown("Para confras: Vai ter fantasia ou a galera vai de 'look do dia corporativo'?")
        festa_tematica_escolha = st.radio(
            "Essa balada vai ser temática ou é cada um no seu estilo?",
            ("Sim, vai ser temática!", "Não, estilo livre!"),
            index=0 if st.session_state.event_data.get('festa_tematica_raw', "Sim") == "Sim" else 1,
            key="radio_festa_tematica_pg3_new"
        )
        st.session_state.event_data['festa_tematica'] = festa_tematica_escolha
        st.session_state.event_data['festa_tematica_raw'] = "Sim" if festa_tematica_escolha == "Sim, vai ser temática!" else "Não"
        if st.session_state.event_data['festa_tematica_raw'] == "Sim":
            st.session_state.event_data['ideia_tema'] = st.text_input(
                "Qual o tema da bagunça? (Opcional, deixe em branco se quiser sugestões da IA)",
                value=st.session_state.event_data.get('ideia_tema', ''), key="ideia_tema_pg3_new",
                placeholder="Ex: Anos 80, Baile de Máscaras, Hollywood..."
            )
    else:
        st.info(f"Como é um evento de '{st.session_state.event_data.get('tipo_evento')}', pulamos a parte do tema. Mas se quiser dar um toque especial, anota aí!")
        st.session_state.event_data['festa_tematica_raw'] = "Não" 

    default_date = st.session_state.event_data.get('data_prevista_dt', datetime.date.today() + datetime.timedelta(days=30))
    st.session_state.event_data['data_prevista'] = st.date_input(
        "E quando vai rolar esse regabofe/aprendizado intensivo?", value=default_date, key="data_prevista_pg3_new"
    )
    st.session_state.event_data['data_prevista_dt'] = st.session_state.event_data['data_prevista']

    st.subheader("📍 Onde vai ser o ponto de encontro dessa galera animada?")
    tipo_local_opcoes = ["Interno na Empresa", "Externo"]
    st.session_state.event_data['tipo_local_desejado'] = st.radio(
        "O evento será dentro da empresa ou vamos explorar novos horizontes?", tipo_local_opcoes,
        index=0 if st.session_state.event_data.get('tipo_local_desejado', tipo_local_opcoes[0]) == tipo_local_opcoes[0] else 1,
        key="tipo_local_pg3_new"
    )
    if st.session_state.event_data['tipo_local_desejado'] == "Interno na Empresa":
        locais_internos_opcoes = ["Auditório Principal", "Área de Lazer/Descompressão", "Refeitório (adaptado)", "Pátio/Área Externa da Empresa", "Outro Espaço Interno"]
        st.session_state.event_data['local_interno_especifico'] = st.selectbox(
            "Qual cantinho da firma vamos usar?", locais_internos_opcoes,
            index=locais_internos_opcoes.index(st.session_state.event_data.get('local_interno_especifico', locais_internos_opcoes[0])),
            key="local_interno_sel_pg3_new"
        )
    else: 
        st.session_state.event_data['local_externo_tipo_pref'] = st.selectbox(
            "Que tipo de local externo te agrada mais?",
            ["Restaurante/Bar com área reservada", "Salão de Festas", "Chácara/Sítio", "Espaço de Eventos Corporativos", "Outro tipo externo"],
            index=0, key="local_externo_sel_pg3_new"
        )
        if "Restaurante" in st.session_state.event_data['local_externo_tipo_pref'] and st.session_state.event_data.get('festa_tematica_raw') == "Sim":
            st.info(f"Boa! O Agente de Localização vai tentar achar restaurantes que combinem com o tema '{st.session_state.event_data.get('ideia_tema', '(a ser sugerido)')}'!")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("⏪ Voltar (Orçamento e Público)", on_click=prev_page, key="btn_voltar_3_final_new"): pass 
    with col2:
        if st.button("Próximo Passo: Ajustes Finais ✨", on_click=next_page, key="btn_prox_3_final_new"): pass 

# --- Página 4: Melhorias, Transporte e Considerações Finais ---
elif st.session_state.page == 4:
    st.header("Página 4: Ajustes finos e a logística da galera!")
    st.session_state.event_data['usar_feedback_passado'] = st.checkbox(
        "Usar a sabedoria das pesquisas de satisfação passadas para turbinar este evento?",
        value=st.session_state.event_data.get('usar_feedback_passado', False), key="check_feedback_pg4"
    )
    if st.session_state.event_data.get('tipo_local_desejado') == "Externo":
        st.subheader("🚌 E a Caravana da Alegria? (Transporte)")
        precisa_transporte_escolha = st.radio(
            "Vamos precisar organizar um esquema de transporte para a galera chegar no local externo?",
            ("Sim, por favor!", "Não, cada um por si (e a sorte por todos!)"),
            index=1 if not st.session_state.event_data.get('precisa_transporte', False) else 0,
            key="radio_transporte_pg4"
        )
        st.session_state.event_data['precisa_transporte'] = (precisa_transporte_escolha == "Sim, por favor!")
    else:
        st.session_state.event_data['precisa_transporte'] = False

    st.markdown("---")
    st.subheader("Tudo pronto para o Orquestrador e seus Agentes entrarem em ação?")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("⏪ Voltar (Detalhes, Data e Local)", on_click=prev_page, key="btn_voltar_4_final_new"): pass 
    with col2:
        if st.button("🥁 Gerar Plano Mestre da Festa! 🥁", type="primary", key="btn_gerar_plano_final"):
            st.session_state.page = 5
            st.rerun()

# --- Página 5: Resultados e Plano Mestre ---
elif st.session_state.page == 5:
    st.header("📜 O Plano Mestre da Sua Festa Maluca! 📜")
    st.balloons()
    data = st.session_state.event_data

    # --- ORQUESTRAÇÃO DOS AGENTES ---
    st.subheader("🗣️ Atenção! Os Agentes Especializados estão entrando em Ação:")

    # 1. Agente Otimizador de Festas
    with st.expander("🧐 Dicas do Agente Otimizador de Festas", expanded=True):
        dicas_otimizador = agente_otimizador_festas(data.get('usar_feedback_passado'))
        for dica in dicas_otimizador:
            st.markdown(f"- _{dica}_")
    st.markdown("---")

    # 2. Agente de Convidados e Dietas
    num_convidados_final = 0
    resumo_restricoes_detalhado_final = "Aguardando processamento..."
    resumo_restricoes_para_prompt_final = "" 
    sugestoes_comida_do_agente_dietas = "Nenhuma sugestão de comida específica por enquanto."

    with st.expander("📋 Análise do Agente de Convidados e Dietas (e sugestões de rango!)", expanded=True):
        num_convidados_calc, resumo_detalhado_calc, resumo_prompt_calc, sugestoes_comida_calc = 0, "N/A", "", ""
        if data.get('fonte_convidados_raw') == "json":
            num_convidados_calc, resumo_detalhado_calc, resumo_prompt_calc, sugestoes_comida_calc = agente_convidados_dietas(True, data.get('arquivo_json_obj'))
        elif data.get('fonte_convidados_raw') == "manual":
            num_convidados_calc = data.get('quantidade_pessoas_manual', 0)
            _, resumo_detalhado_calc, resumo_prompt_calc, sugestoes_comida_calc = agente_convidados_dietas(False, None)

        if num_convidados_calc is not None:
            num_convidados_final = num_convidados_calc
        resumo_restricoes_detalhado_final = resumo_detalhado_calc
        resumo_restricoes_para_prompt_final = resumo_prompt_calc
        sugestoes_comida_do_agente_dietas = sugestoes_comida_calc
        
        st.session_state.event_data['num_convidados_final_calculado'] = num_convidados_final
        st.session_state.event_data['resumo_restricoes_final_calculado'] = resumo_restricoes_detalhado_final
        st.session_state.event_data['resumo_restricoes_para_prompt_final'] = resumo_restricoes_para_prompt_final
        st.session_state.event_data['sugestoes_comida_final'] = sugestoes_comida_do_agente_dietas # Salva para outros agentes
        
        st.write(f"**Estimativa de Almas Presentes:** {num_convidados_final} pessoas.")
        st.markdown(f"**Relatório de Dietas Especiais:**\n{resumo_restricoes_detalhado_final}")
        st.markdown(f"**Sugestões de Tipo de Comida/Culinária (baseado nas dietas):**\n{sugestoes_comida_do_agente_dietas}")
    st.markdown("---")

    # 3. Agente Batizador
    nome_final_evento = data.get('nome_evento_input', "Evento Surpresa") 
    if data.get('ajuda_nome') and not data.get('nome_evento_input'):
        if st.session_state.sugestoes_nomes_cache is None: 
            with st.spinner("Agente Batizador quebrando a cabeça para os nomes..."):
                objetivos_finais_lista_temp = data.get('objetivos_selecionados', []) + data.get('objetivos_personalizados', [])
                objetivos_para_prompt_str_temp = "; ".join(objetivos_finais_lista_temp) if objetivos_finais_lista_temp else "Não especificado"
                st.session_state.sugestoes_nomes_cache = agente_batizador_eventos(data.get('tipo_evento'), objetivos_para_prompt_str_temp)

        if st.session_state.sugestoes_nomes_cache and st.session_state.sugestoes_nomes_cache[0] != "Erro ao gerar nomes. Que tal 'Festa Surpresa do Chefe Que Não Sabe'?":
            opcoes_nomes = ["(Digitar meu próprio nome)"] + st.session_state.sugestoes_nomes_cache
            default_nome_index = 0
            nome_ja_escolhido_ou_digitado = st.session_state.event_data.get('nome_evento_escolhido') or st.session_state.event_data.get('nome_evento_digitado_final')
            if nome_ja_escolhido_ou_digitado:
                if nome_ja_escolhido_ou_digitado in opcoes_nomes: default_nome_index = opcoes_nomes.index(nome_ja_escolhido_ou_digitado)
                elif st.session_state.event_data.get('nome_evento_escolhido_selectbox_raw') == "(Digitar meu próprio nome)": default_nome_index = 0

            nome_escolhido_select = st.selectbox(
                "O Agente Batizador sugere (escolha um ou digite o seu abaixo):",
                options=opcoes_nomes, index=default_nome_index, key="select_nome_evento_final"
            )
            st.session_state.event_data['nome_evento_escolhido_selectbox_raw'] = nome_escolhido_select
            if nome_escolhido_select == "(Digitar meu próprio nome)":
                nome_final_evento = st.text_input("Então, qual vai ser o nome?", 
                                                  value=st.session_state.event_data.get('nome_evento_digitado_final', nome_final_evento),
                                                  key="input_nome_final_evento")
                st.session_state.event_data['nome_evento_digitado_final'] = nome_final_evento
            else:
                nome_final_evento = nome_escolhido_select
                if 'nome_evento_digitado_final' in st.session_state.event_data:
                    del st.session_state.event_data['nome_evento_digitado_final']
        else:
            st.warning("O Agente Batizador falhou em sugerir nomes. Pode digitar um nome abaixo.")
            nome_final_evento = st.text_input("Qual o nome da festa, então?", value=nome_final_evento, key="input_nome_final_evento_falha")
            st.session_state.event_data['nome_evento_digitado_final'] = nome_final_evento
    elif data.get('nome_evento_input'):
        nome_final_evento = data.get('nome_evento_input')
    st.session_state.event_data['nome_evento_escolhido'] = nome_final_evento

    # 4. Agente de Sugestão de Temas
    tema_final_para_agentes = data.get('ideia_tema', "(Nenhum tema específico / Estilo Livre)") 
    if data.get('festa_tematica_raw') == "Sim":
        with st.expander("🎨 Sugestões de Tema do Agente Especializado (considerando dietas e sugestões de comida!)", expanded=True):
            if st.session_state.sugestoes_temas_cache is None:
                with st.spinner("Agente de Temas buscando inspiração..."):
                    st.session_state.sugestoes_temas_cache = agente_sugestao_tema_com_restricoes(
                        data.get('tipo_evento'),
                        data.get('ideia_tema'), 
                        st.session_state.event_data.get('resumo_restricoes_para_prompt_final'),
                        st.session_state.event_data.get('sugestoes_comida_final') # Passa sugestões de comida
                    )
            
            if st.session_state.sugestoes_temas_cache:
                opcoes_temas_nomes = []
                ideia_original_formatada = f"Minha Ideia Original: {data.get('ideia_tema')}"
                if data.get('ideia_tema'):
                    opcoes_temas_nomes.append(ideia_original_formatada)

                for sugestao_completa in st.session_state.sugestoes_temas_cache:
                    nome_tema_extraido = sugestao_completa.split('\n')[0] 
                    if "Nome:" in sugestao_completa:
                        try: nome_tema_extraido = sugestao_completa.split("Nome:")[1].split("\n")[0].strip()
                        except: pass 
                    if nome_tema_extraido not in opcoes_temas_nomes and (not data.get('ideia_tema') or nome_tema_extraido != data.get('ideia_tema')):
                         opcoes_temas_nomes.append(nome_tema_extraido)
                
                opcoes_temas_nomes.append("(Digitar outro tema / Estilo Livre)")
                opcoes_temas_finais_unicas = list(dict.fromkeys(opcoes_temas_nomes))

                default_tema_idx = 0
                if data.get('tema_final_escolhido') in opcoes_temas_finais_unicas: default_tema_idx = opcoes_temas_finais_unicas.index(data.get('tema_final_escolhido'))
                elif data.get('ideia_tema') and ideia_original_formatada in opcoes_temas_finais_unicas: default_tema_idx = opcoes_temas_finais_unicas.index(ideia_original_formatada)

                tema_selecionado_selectbox = st.selectbox(
                    "Escolha o tema final para a festa (ou digite o seu):",
                    options=opcoes_temas_finais_unicas, index=default_tema_idx, key="select_tema_final"
                )

                if tema_selecionado_selectbox == "(Digitar outro tema / Estilo Livre)":
                    tema_final_para_agentes = st.text_input(
                        "Qual será o tema então (ou deixe em branco para estilo livre)?",
                        value=st.session_state.event_data.get('tema_digitado_final', ''), key="input_tema_final_usuario"
                    )
                    st.session_state.event_data['tema_digitado_final'] = tema_final_para_agentes
                elif tema_selecionado_selectbox.startswith("Minha Ideia Original: "):
                    tema_final_para_agentes = data.get('ideia_tema')
                else:
                    tema_final_para_agentes = tema_selecionado_selectbox
                
                st.session_state.event_data['tema_final_escolhido'] = tema_final_para_agentes if tema_final_para_agentes else "(Nenhum tema específico / Estilo Livre)"

                st.markdown("**Detalhes das Sugestões do Agente (se houver):**")
                if st.session_state.sugestoes_temas_cache[0].startswith("Tema Sugerido:"): 
                    st.write(st.session_state.sugestoes_temas_cache[0])
                else:
                    for i, sugestao_completa in enumerate(st.session_state.sugestoes_temas_cache):
                        with st.container():
                            st.markdown(f"--- Sugestão IA {i+1} ---")
                            st.markdown(sugestao_completa)
            else:
                st.write("O Agente de Temas está tirando uma soneca criativa.")
                st.session_state.event_data['tema_final_escolhido'] = data.get('ideia_tema', "(Nenhum tema específico / Estilo Livre)")
        st.markdown("---")
    else:
        st.session_state.event_data['tema_final_escolhido'] = "(Nenhum tema específico / Estilo Livre)"


    # 5. Agente de Localização
    sugestoes_locais_texto = ["Nenhuma sugestão de local por enquanto."]
    contatos_locais_simulados = {}
    with st.expander("🗺️ Sugestões do Agente de Localização", expanded=True):
        sugestoes_locais_texto, contatos_locais_simulados = agente_localizacao(
            data.get('tipo_evento'),
            st.session_state.event_data.get('tema_final_escolhido'), 
            data.get('tipo_local_desejado'),
            st.session_state.event_data.get('resumo_restricoes_para_prompt_final'),
            st.session_state.event_data.get('sugestoes_comida_final'), # Passa sugestões de comida
            data.get('local_interno_especifico') if data.get('tipo_local_desejado') == "Interno na Empresa" else None
        )
        for sug in sugestoes_locais_texto:
            st.markdown(f"- {sug}") 
    st.session_state.event_data['sugestoes_locais_finais'] = sugestoes_locais_texto
    st.session_state.event_data['contatos_locais_finais'] = contatos_locais_simulados
    st.markdown("---")

    # 6. Agente Orçamentista
    with st.expander("💰 Considerações do Agente Orçamentista", expanded=True):
        feedback_orcamento = agente_orcamentista(
            data.get('valor_disponivel'),
            st.session_state.event_data.get('num_convidados_final_calculado'),
            st.session_state.event_data.get('tema_final_escolhido'),
            st.session_state.event_data.get('contatos_locais_finais')
        )
        st.markdown(feedback_orcamento)
    st.markdown("---")

    # 7. Agente de Transporte
    if data.get('tipo_local_desejado') == "Externo" and data.get('precisa_transporte'):
        with st.expander("🚌 Ideias do Agente de Transporte", expanded=True):
            local_str_para_transporte = "Local Externo Genérico"
            if st.session_state.event_data.get('sugestoes_locais_finais') and isinstance(st.session_state.event_data['sugestoes_locais_finais'], list) and len(st.session_state.event_data['sugestoes_locais_finais']) > 0:
                 local_str_para_transporte = st.session_state.event_data['sugestoes_locais_finais'][0]
            
            feedback_transporte = agente_transporte(
                st.session_state.event_data.get('num_convidados_final_calculado'),
                local_str_para_transporte,
                data.get('precisa_transporte')
            )
            st.markdown(feedback_transporte)
        st.markdown("---")


    st.subheader("\n\n✨ Seu Plano Mestre Detalhado ✨")
    st.write(f"**Nome Final do Evento:** {st.session_state.event_data.get('nome_evento_escolhido', 'A definir pelo organizador')}")
    st.write(f"**Tipo de Evento:** {data.get('tipo_evento', 'Não definido')}")
    objetivos_finais_lista = data.get('objetivos_selecionados', []) + data.get('objetivos_personalizados', [])
    if objetivos_finais_lista:
        st.write("**Objetivos:**")
        for obj_final in objetivos_finais_lista: st.markdown(f"  - {obj_final}")
    
    st.write(f"**Tema Escolhido:** {st.session_state.event_data.get('tema_final_escolhido', '(Nenhum tema específico / Estilo Livre)')}")

    st.write(f"**Data Prevista:** {data.get('data_prevista').strftime('%d/%m/%Y') if data.get('data_prevista') else 'A definir'}")
    
    local_final_str = "A definir"
    if data.get('tipo_local_desejado') == "Interno na Empresa":
        local_final_str = data.get('local_interno_especifico', "Espaço interno não especificado")
    elif st.session_state.event_data.get('sugestoes_locais_finais'):
        locais_formatados = []
        for item_local in st.session_state.event_data['sugestoes_locais_finais']:
            locais_formatados.append(f"  - {item_local}")
        local_final_str = "\n".join(locais_formatados)

    st.markdown(f"**Local Previsto/Sugerido:**\n{local_final_str}")

    st.write(f"**Orçamento Total Estimado:** R$ {data.get('valor_disponivel', 0.0):.2f}")
    st.write(f"**Público Estimado:** {st.session_state.event_data.get('num_convidados_final_calculado', 0)} pessoas")
    st.markdown(f"**Restrições Alimentares Notáveis:** \n{st.session_state.event_data.get('resumo_restricoes_final_calculado', 'Não processado')}")
    st.markdown(f"**Sugestões de Tipo de Comida (baseado nas dietas):** \n{st.session_state.event_data.get('sugestoes_comida_final', 'Nenhuma específica')}")


    st.success("Voilà! Este é o seu rascunho inicial turbinado. Agora é só alegria... e um pouquinho mais de trabalho!")

    if st.button("Planejar Outra Festa Épica? 🚀", key="btn_planejar_outra_final"):
        st.session_state.page = 1
        st.session_state.event_data = { 
            'objetivos_selecionados': [], 'objetivos_personalizados': [],
            'nome_evento_escolhido': None, 'tema_final_escolhido': None
        }
        st.session_state.objetivo_custom_temp_input = ""
        st.session_state.sugestoes_nomes_cache = None
        st.session_state.sugestoes_temas_cache = None 
        if 'arquivo_json_obj' in st.session_state: 
             del st.session_state['arquivo_json_obj']
        st.session_state.uploader_key_count = st.session_state.get('uploader_key_count', 0) + 1 
        st.rerun()