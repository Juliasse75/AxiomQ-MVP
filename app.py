import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import folium
import time
import numpy as np

st.set_page_config(page_title="AxiomQ | Matriz Global", layout="wide", page_icon="⚡")

# 1. ESTRUTURA DE BANCO DE DADOS EM MEMÓRIA (SISTEMA DE USUÁRIOS)
if 'usuarios' not in st.session_state:
    st.session_state['usuarios'] = {
        'ceo@axiomq.com.br': {'senha': '123', 'perfil': 'MASTER', 'nome': 'Cosme (CEO)'},
        'gerente@farmaciax.com.br': {'senha': '456', 'perfil': 'CLIENTE', 'empresa': 'Farmácia X', 'motos': 3, 'entregas': 45}
    }

if 'logado' not in st.session_state: st.session_state['logado'] = False
if 'user_atual' not in st.session_state: st.session_state['user_atual'] = None
if 'simulacao_farmacia' not in st.session_state: st.session_state['simulacao_farmacia'] = False

# ESTILIZAÇÃO VISUAL NEON
LOGO_HTML = """
<div style="text-align: center; margin-bottom: 20px;">
    <h1 style="font-size: 50px; font-weight: 800; color: white; margin: 0; text-shadow: 0 0 15px #2563eb, 0 0 30px #8b5cf6;">Axiom<span style="color: #2563eb;">Q</span></h1>
    <p style="color: #8b5cf6; font-size: 14px; letter-spacing: 4px; margin: 0;">SISTEMA MATRIZ DE CONTROLE</p>
</div>
"""

# ==========================================
# TELA DE AUTENTICAÇÃO UNIFICADA
# ==========================================
if not st.session_state['logado']:
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.write("<br><br>", unsafe_allow_html=True)
        st.markdown(LOGO_HTML, unsafe_allow_html=True)
        
        with st.form("login_central"):
            u_input = st.text_input("E-mail de Acesso:")
            s_input = st.text_input("Senha Tática:", type="password")
            btn_entrar = st.form_submit_button("Autenticar no Núcleo", use_container_width=True)
            
            if btn_entrar:
                if u_input in st.session_state['usuarios'] and st.session_state['usuarios'][u_input]['senha'] == s_input:
                    st.session_state['logado'] = True
                    st.session_state['user_atual'] = u_input
                    st.rerun()
                else:
                    st.error("Acesso negado. Credenciais incorretas.")
    st.stop()

# LOGIN RECONHECIDO
user_info = st.session_state['usuarios'][st.session_state['user_atual']]

# BOTO DE LOGOUT
if st.sidebar.button("🔒 Encerrar Sessão"):
    st.session_state['logado'] = False
    st.session_state['user_atual'] = None
    st.rerun()

# ==========================================
# AMBIENTE 1: PAINEL ADMINISTRADOR MASTER (VOCÊ)
# ==========================================
if user_info['perfil'] == 'MASTER':
    st.title(f"👋 Olá, {user_info['nome']} | Painel do Administrador")
    st.markdown("Aqui você gerencia suas contas parceiras e cria acessos para os testes em campo.")
    
    aba_criar, aba_parceiros = st.tabs(["🆕 Cadastrar Empresa Parceira", "🏢 Empresas Ativas"])
    
    with aba_criar:
        st.subheader("Configurar Novo Cliente no Sistema")
        with st.form("cadastro_cliente"):
            nome_empresa = st.text_input("Nome da Empresa:", placeholder="Ex: Farmácia X")
            email_empresa = st.text_input("E-mail do Gestor Logístico:", placeholder="Ex: gerente@farmacia.com")
            senha_empresa = st.text_input("Senha Provisória de Acesso:", type="password")
            c_motos = st.number_input("Quantidade de Veículos/Motos:", min_value=1, value=3)
            
            btn_cadastrar = st.form_submit_button("Gerar Credenciais e Ativar Plataforma", use_container_width=True)
            
            if btn_cadastrar:
                if email_empresa not in st.session_state['usuarios']:
                    st.session_state['usuarios'][email_empresa] = {
                        'senha': str(senha_empresa),
                        'perfil': 'CLIENTE',
                        'empresa': nome_empresa,
                        'motos': c_motos,
                        'entregas': 30
                    }
                    st.success(f"✅ Sucesso! Conta para **{nome_empresa}** gerada. Envie o e-mail e senha para o cliente.")
                else:
                    st.warning("Este e-mail já está cadastrado no sistema.")
                    
    with aba_parceiros:
        st.subheader("Monitoramento de Clientes na Fase de Testes")
        # Transforma o dicionário em tabela para visualização fácil
        lista_clientes = []
        for k, v in st.session_state['usuarios'].items():
            if v['perfil'] == 'CLIENTE':
                lista_clientes.append({'Empresa/Cliente': v['empresa'], 'E-mail do Gestor': k, 'Frota Alocada': f"{v['motos']} Veículos", 'Status da POC': 'Em Teste (1 Mês)'})
        
        if lista_clientes:
            st.table(pd.DataFrame(lista_clientes))
        else:
            st.info("Nenhum parceiro de campo ativo ainda.")

# ==========================================
# AMBIENTE 2: PAINEL DO CLIENTE (EX: FARMÁCIA X)
# ==========================================
elif user_info['perfil'] == 'CLIENTE':
    st.title(f"⚡ Painel de Controle | {user_info['empresa']}")
    st.subheader("Módulo de Otimização de Rotas de Alta Performance")
    
    col_indicators, col_actions = st.columns([1, 2])
    
    with col_indicators:
        st.metric("Sua Frota Ativa", f"{user_info['motos']} Motocicletas")
        st.metric("Entregas Agendadas (Hoje)", f"{user_info['entregas']} Pedidos")
        
        if st.button("🚀 Otimizar Entregas da Farmácia", use_container_width=True):
            st.session_state['simulacao_farmacia'] = True
            
    with col_actions:
        if st.session_state['simulacao_farmacia']:
            st.success("Algoritmo Concluído! Rotas distribuídas igualmente entre as 3 motocicletas.")
            
            # Geração de mapa local simulado (Simulando entregas de bairro próximas ao centro)
            mapa_local = folium.Map(location=[-19.9386, -43.9340], zoom_start=14, tiles="CartoDB positron")
            
            # Ponto da Farmácia (Sede)
            folium.Marker([-19.9386, -43.9340], popup="<b>Farmácia X - Sede</b>", icon=folium.Icon(color="red", icon="plus")).add_to(mapa_local)
            
            # 3 cores diferentes para representar as 3 motos
            cores_motos = ['blue', 'purple', 'orange']
            np.random.seed(10)
            
            for i in range(user_info['entregas']):
                m_designada = i % user_info['motos']
                lat_p = -19.9386 + np.random.normal(0, 0.01)
                lon_p = -43.9340 + np.random.normal(0, 0.01)
                
                folium.CircleMarker(
                    [lat_p, lon_p],
                    radius=5,
                    color=cores_motos[m_designada],
                    fill=True,
                    popup=f"Entrega #{i+1} - Moto {m_designada+1}"
                ).add_to(mapa_local)
                
            components.html(mapa_local._repr_html_(), height=450)
        else:
            st.info("Aguardando acionamento do motor para desenhar o mapa de entregas de medicamentos do dia.")
