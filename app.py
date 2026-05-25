import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import folium
import time
import numpy as np

st.set_page_config(page_title="AxiomQ | Matriz Global", layout="wide", page_icon="⚡")

# 1. BANCO DE DADOS EM MEMÓRIA APRIMORADO (COM PLANOS)
if 'usuarios' not in st.session_state:
    st.session_state['usuarios'] = {
        'ceo@axiomq.com.br': {'senha': '123', 'perfil': 'MASTER', 'nome': 'Cosme (CEO)'},
        'gerente@farmaciax.com.br': {'senha': '456', 'perfil': 'CLIENTE', 'empresa': 'Farmácia X', 'plano': 'POC (Teste) - Até 5 veículos', 'motos': 3, 'entregas': 45}
    }

if 'logado' not in st.session_state: st.session_state['logado'] = False
if 'user_atual' not in st.session_state: st.session_state['user_atual'] = None
if 'simulacao_farmacia' not in st.session_state: st.session_state['simulacao_farmacia'] = False

# ESTILIZAÇÃO VISUAL NEON
LOGO_HTML = """
<div style="text-align: center; margin-bottom: 20px;">
    <h1 style="font-size: 50px; font-weight: 800; color: white; margin: 0; text-shadow: 0 0 15px #2563eb, 0 0 30px #8b5cf6;">Axiom<span style="color: #2563eb;">Q</span></h1>
    <p style="color: #8b5cf6; font-size: 14px; letter-spacing: 4px; margin: 0;">NÚCLEO DE INTELIGÊNCIA LOGÍSTICA</p>
</div>
"""

# ==========================================
# TELA DE AUTENTICAÇÃO BLINDADA
# ==========================================
if not st.session_state['logado']:
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.write("<br><br>", unsafe_allow_html=True)
        st.markdown(LOGO_HTML, unsafe_allow_html=True)
        
        with st.form("login_central"):
            u_input = st.text_input("E-mail corporativo:")
            s_input = st.text_input("Senha tática:", type="password")
            # Texto do botão alterado conforme solicitado
            btn_entrar = st.form_submit_button("Acessar AxiomQ", use_container_width=True)
            
            if btn_entrar:
                # Tratamento de erro: remove espaços invisíveis e joga para minúsculo
                email_limpo = u_input.strip().lower()
                
                if email_limpo in st.session_state['usuarios'] and st.session_state['usuarios'][email_limpo]['senha'] == s_input:
                    st.session_state['logado'] = True
                    st.session_state['user_atual'] = email_limpo
                    st.rerun()
                else:
                    st.error("Credenciais inválidas. Verifique se não há espaços após o e-mail.")
    st.stop()

# LOGIN RECONHECIDO
user_info = st.session_state['usuarios'][st.session_state['user_atual']]

# BOTÃO DE LOGOUT NA BARRA LATERAL
st.sidebar.markdown("### Controle de Sessão")
if st.sidebar.button("🔒 Encerrar Sessão", use_container_width=True):
    st.session_state['logado'] = False
    st.session_state['user_atual'] = None
    st.rerun()

# ==========================================
# AMBIENTE 1: PAINEL ADMINISTRADOR MASTER (VOCÊ)
# ==========================================
if user_info['perfil'] == 'MASTER':
    st.title(f"👋 Bem-vindo, {user_info['nome']} | Controle Matriz")
    st.markdown("Gestão central de clientes, emissão de acessos e controle de planos da AxiomQ.")
    
    aba_criar, aba_parceiros = st.tabs(["🆕 Cadastrar Novo Cliente", "🏢 Clientes e Planos Ativos"])
    
    with aba_criar:
        st.subheader("Emissão de Novo Acesso Cliente")
        with st.form("cadastro_cliente"):
            nome_empresa = st.text_input("Nome da Empresa Parceira:", placeholder="Ex: Material de Construção Silva")
            email_empresa = st.text_input("E-mail do Gestor Logístico (Login):", placeholder="Ex: logistica@silva.com")
            senha_empresa = st.text_input("Senha Provisória:", type="password")
            
            # Nova função de Planos Integrada
            plano_escolhido = st.selectbox(
                "Nível de Licença (Plano):", 
                [
                    "POC (Teste) - Até 5 veículos", 
                    "Starter - Até 15 veículos", 
                    "Advanced - Até 50 veículos", 
                    "Quantum (Enterprise) - Ilimitado"
                ]
            )
            
            btn_cadastrar = st.form_submit_button("Gerar Credenciais", use_container_width=True)
            
            if btn_cadastrar:
                email_limpo_cad = email_empresa.strip().lower()
                if email_limpo_cad not in st.session_state['usuarios']:
                    st.session_state['usuarios'][email_limpo_cad] = {
                        'senha': str(senha_empresa),
                        'perfil': 'CLIENTE',
                        'empresa': nome_empresa,
                        'plano': plano_escolhido,
                        'motos': 0, # Cliente cadastra depois
                        'entregas': 0 # Cliente cadastra depois
                    }
                    st.success(f"✅ Licença {plano_escolhido.split(' -')[0]} ativada para **{nome_empresa}**. Acesso liberado!")
                else:
                    st.warning("Erro: Este e-mail já possui uma licença ativa.")
                    
    with aba_parceiros:
        st.subheader("Monitoramento da Base de Clientes")
        lista_clientes = []
        for k, v in st.session_state['usuarios'].items():
            if v['perfil'] == 'CLIENTE':
                lista_clientes.append({
                    'Empresa': v['empresa'], 
                    'Login de Acesso': k, 
                    'Plano Ativo': v['plano']
                })
        
        if lista_clientes:
            st.table(pd.DataFrame(lista_clientes))
        else:
            st.info("Nenhuma empresa cadastrada no momento.")

# ==========================================
# AMBIENTE 2: PAINEL DO CLIENTE (EX: FARMÁCIA X)
# ==========================================
elif user_info['perfil'] == 'CLIENTE':
    st.title(f"⚡ Painel de Logística | {user_info['empresa']}")
    st.markdown(f"**Sua Licença:** `{user_info['plano']}`")
    st.markdown("---")
    
    col_indicators, col_actions = st.columns([1, 2])
    
    with col_indicators:
        st.subheader("Resumo Operacional")
        st.metric("Veículos Ativos (Hoje)", f"{user_info['motos']} veículos")
        st.metric("Entregas na Fila", f"{user_info['entregas']} pedidos")
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🚀 Iniciar Motor de Roteamento", use_container_width=True):
            with st.spinner("Calculando tráfego e distribuindo cargas..."):
                time.sleep(2) # Efeito visual de carregamento
                st.session_state['simulacao_farmacia'] = True
            
    with col_actions:
        if st.session_state['simulacao_farmacia']:
            st.success("✅ Roteamento Concluído! Cargas distribuídas e enviadas para o App do Condutor.")
            
            mapa_local = folium.Map(location=[-19.9386, -43.9340], zoom_start=14, tiles="CartoDB dark_matter")
            folium.Marker([-19.9386, -43.9340], popup="<b>Sede</b>", icon=folium.Icon(color="red", icon="home")).add_to(mapa_local)
            
            cores_motos = ['blue', 'purple', 'orange', 'green', 'lightgray']
            np.random.seed(42)
            
            # Proteção para não quebrar se motos = 0
            qtd_motos = max(1, user_info['motos'])
            
            for i in range(user_info['entregas']):
                m_designada = i % qtd_motos
                lat_p = -19.9386 + np.random.normal(0, 0.015)
                lon_p = -43.9340 + np.random.normal(0, 0.015)
                
                folium.CircleMarker(
                    [lat_p, lon_p],
                    radius=5,
                    color=cores_motos[m_designada % len(cores_motos)],
                    fill=True,
                    popup=f"Entrega #{i+1} - Condutor {m_designada+1}"
                ).add_to(mapa_local)
                
            components.html(mapa_local._repr_html_(), height=400)
        else:
            st.info("Aguardando acionamento do algoritmo...")
