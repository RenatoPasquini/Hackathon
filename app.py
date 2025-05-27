import streamlit as st
from data import EventData

# Configuração da página principal
descricao_app = "Seu copiloto para eventos corporativos inesquecíveis!"
st.set_page_config(page_title="Festa IA", layout="wide")
st.title(":tada: Planejador de Eventos IA")
st.markdown(descricao_app)

# Inicialização do estado do evento
if "event" not in st.session_state:
    st.session_state.event = EventData()

# Navegação pelas etapas
pages = ["1. Tipo e Objetivos", "2. Orçamento e Convidados", "3. Data e Local", "4. Resultado"]
st.sidebar.title("🎉 Menu")
selected_page = st.sidebar.radio("Etapas do Planejamento", pages)

# Renderiza a página conforme seleção
if selected_page == "1. Tipo e Objetivos":
    import pages.1_tipo_objetivos as p1
    p1.render()
elif selected_page == "2. Orçamento e Convidados":
    import pages.2_orcamento_pessoas as p2
    p2.render()
elif selected_page == "3. Data e Local":
    import pages.3_data_local as p3
    p3.render()
elif selected_page == "4. Resultado":
    import pages.4_resultado as p4
    p4.render()