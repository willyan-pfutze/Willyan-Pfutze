import streamlit as st
import google.generativeai as genai
import os
import time

# --- Configuração da API do Gemini ---
try:
    print("Configurando API do Gemini...")
    genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
    print("API do Gemini configurada com sucesso.")
except Exception as e:
    st.error(f"Erro ao configurar a API do Gemini. Verifique se a variável de ambiente GOOGLE_API_KEY está definida. Detalhes: {e}")
    print(f"Erro ao configurar API do Gemini: {e}")
    st.stop()

# --- Definição dos Agentes ---

def knowledge_master_response(user_input):
    """
    Agente responsável por fornecer explicações e responder a perguntas técnicas.
    Integra com o modelo Gemini.
    """
    print(f"KnowledgeMaster: Recebeu input: {user_input}")
    try:
        prompt = f"""Você é o KnowledgeMaster, um assistente de aprendizagem focado em fornecer explicações claras e precisas.
        Responda à seguinte pergunta ou solicitação do aluno: {user_input}
        """
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        print(f"KnowledgeMaster: Resposta da API: {response.text}")
        return response.text
    except Exception as e:
        print(f"KnowledgeMaster: Erro na chamada da API: {e}")
        return f"KnowledgeMaster: Desculpe, não consegui processar sua solicitação no momento. Erro: {e}"

def empathy_buddy_response(user_input):
    """
    Agente responsável por oferecer suporte emocional, motivação e reconhecer dificuldades.
    """
    print(f"EmpathyBuddy: Recebeu input: {user_input}")
    user_input_lower = user_input.lower()
    if any(word in user_input_lower for word in ["difícil", "não entendi", "frustrado", "desmotivado", "complicado"]):
        response = "EmpathyBuddy: Entendo perfeitamente como você se sente. É totalmente normal encontrar dificuldades enquanto aprende. Não desanime! Cada passo, por menor que seja, te aproxima do seu objetivo. Se quiser, podemos tentar abordar isso de um ângulo diferente ou você pode me dizer exatamente o que está te deixando frustrado para que eu possa te ajudar melhor."
    elif any(word in user_input_lower for word in ["cansaço", "cansado", "pausa"]):
         response = "EmpathyBuddy: Parece que você pode estar precisando de uma pausa. Cuidar de si mesmo é parte importante da aprendizagem. Que tal fazer uma pausa rápida para recarregar as energias?"
    else:
        response = "EmpathyBuddy: Estou aqui para te apoiar em sua jornada de aprendizagem!"
    print(f"EmpathyBuddy: Resposta gerada: {response}")
    return response

# --- Agente Orquestrador ---

def orchestrator(user_input):
    """
    Direciona a entrada do usuário para o agente apropriado.
    """
    print(f"Orquestrador: Recebeu input: {user_input}")
    user_input_lower = user_input.lower()

    if any(word in user_input_lower for word in ["difícil", "não entendi", "frustrado", "desmotivado", "complicado", "cansaço", "cansado", "pausa"]):
        print("Orquestrador: Direcionando para EmpathyBuddy.")
        return empathy_buddy_response(user_input)
    else:
        print("Orquestrador: Direcionando para KnowledgeMaster.")
        return knowledge_master_response(user_input)

# --- Interface Streamlit ---

st.set_page_config(page_title="Sensei AI", layout="wide")

col1, col2, col3 = st.columns([1, 6, 1])

with col2:
    st.title("Sensei AI")
    st.markdown("""
    Aprenda no seu ritmo, com quem entende você
    """)

    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []

    # Exibir histórico de chat
    for message in st.session_state.chat_history:
        if "user" in message:
            st.markdown(f"**Você:** {message['user']}")
        elif "ai" in message:
            st.markdown(f"**Sensei AI:** {message['ai']}")

    # --- Formulário para permitir envio com Enter e limpar campo ---
    # Usamos um formulário com key e clear_on_submit=True
    with st.form(key='chat_form', clear_on_submit=True):
        # Lógica para pré-preencher o campo de texto a partir de um prompt opcional
        # Verifica se há um valor para pré-preencher na session_state
        prefill_value = st.session_state.get('prefill_input', '') # Usa .get() para evitar KeyError
        if prefill_value:
            # Limpa a session_state após usar o valor para pré-preencher
            st.session_state.prefill_input = ''

        user_input = st.text_input("Todo caminho começa com um passo. Qual passo deseja dar agora?", value=prefill_value, key="user_input_field")
        submit_button = st.form_submit_button(label='Enviar')

    # --- Lógica de processamento ---
    # Esta lógica é acionada pela submissão do formulário (Enter ou botão Enviar).
    # A lógica para processar os botões de prompt agora confia que o st.rerun()
    # irá acionar um novo ciclo onde o valor preenchido será submetido pelo formulário
    # na próxima interação, ou seja, o clique no botão de prompt SETA o prefill_input
    # e o st.rerun() causa um reload onde o FORMULÁRIO SUBMETE o valor pré-preenchido.
    if submit_button and user_input:
        print(f"Lógica de Processamento: Input do formulário submetido: {user_input}")
        st.session_state.chat_history.append({"user": user_input})

        with st.spinner("Sensei AI pensando..."):
            time.sleep(1)

            ai_response = orchestrator(user_input)
            print(f"Lógica de Processamento: Resposta do orquestrador: {ai_response}")

        if ai_response:
             st.session_state.chat_history.append({"ai": ai_response})
             print("Lógica de Processamento: Resposta adicionada ao histórico.")
        else:
            print("Lógica de Processamento: Resposta do orquestrador vazia ou None.")
            st.session_state.chat_history.append({"ai": "Sensei AI: Desculpe, não consegui gerar uma resposta."})

        # Adiciona st.rerun() explícito aqui para garantir que a interface atualize
        # após a adição da resposta ao histórico.
        st.rerun()


    # --- Botões de Prompts Opcionais ---
    st.markdown("---")
    st.markdown("**Sugestões rápidas:**")



# Adicionar um rodapé
st.markdown("---")
st.markdown("Desenvolvido com Streamlit e Google Gemini.")
