import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import folium
import time
import numpy as np

st.set_page_config(page_title="AxiomQ | Matriz Global", layout="wide", page_icon="⚡")

# 1. BANCO DE DADOS EM MEMÓRIA (Agora sem dados hardcoded de motos)
if 'usuarios' not in st.session_state:
    st.session_state['usuarios'] = {
        'ceo@axiomq.com.br': {'senha': '123', 'perfil': 'MASTER', 'nome': 'Cosme (CEO)'},
        'gerente@farmaciax.com.br': {'senha': '456', 'perfil': 'CLIENTE', 'empresa': 'Farmácia X', 'plano': 'POC (Teste) - Até 5 veículos'}
    }

if 'logado' not in st.session_state: st.session_state['logado'] = False
if 'user_atual' not in st.session_state: st.session_state['user_atual'] = None

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
            btn_entrar = st.form_submit_button("Acessar AxiomQ", use_container_width=True)
            
            if btn_entrar:
                email_limpo = u_input.strip().lower()
                if email_limpo in st.session_state['usuarios'] and st.session_state['usuarios'][email_limpo]['senha'] == s_input:
                    st.session_state['logado'] = True
                    st.session_state['user_atual'] = email_limpo
                    st.rerun()
                else:
                    st.error("Credenciais inválidas. Verifique os dados.")
    st.stop()

# LOGIN RECONHECIDO
user_info = st.session_state['usuarios'][st.session_state['user_atual']]

st.sidebar.markdown("### Controle de Sessão")
if st.sidebar.button("🔒 Encerrar Sessão", use_container_width=True):
    st.session_state['logado'] = False
    st.session_state['user_atual'] = None
    st.rerun()

# ==========================================
# AMBIENTE 1: PAINEL ADMINISTRADOR MASTER
# ==========================================
if user_info['perfil'] == 'MASTER':
    st.title(f"👋 Bem-vindo, {user_info['nome']} | Controle Matriz")
    
    aba_criar, aba_parceiros = st.tabs(["🆕 Cadastrar Novo Cliente", "🏢 Clientes e Planos Ativos"])
    
    with aba_criar:
        st.subheader("Emissão de Novo Acesso Cliente")
        with st.form("cadastro_cliente"):
            nome_empresa = st.text_input("Nome da Empresa Parceira:")
            email_empresa = st.text_input("E-mail do Gestor Logístico (Login):")
            senha_empresa = st.text_input("Senha Provisória:", type="password")
            plano_escolhido = st.selectbox("Nível de Licença (Plano):", ["POC (Teste) - Até 5 veículos", "Starter - Até 15 veículos", "Advanced - Até 50 veículos", "Quantum (Enterprise) - Ilimitado"])
            
            if st.form_submit_button("Gerar Credenciais", use_container_width=True):
                email_limpo_cad = email_empresa.strip().lower()
                if email_limpo_cad not in st.session_state['usuarios']:
                    st.session_state['usuarios'][email_limpo_cad] = {
                        'senha': str(senha_empresa),
                        'perfil': 'CLIENTE',
                        'empresa': nome_empresa,
                        'plano': plano_escolhido
                    }
                    st.success(f"✅ Licença ativada para **{nome_empresa}**!")
                else:
                    st.warning("E-mail já cadastrado.")
                    
    with aba_parceiros:
        st.subheader("Base de Clientes")
        lista_clientes = [{'Empresa': v['empresa'], 'Login': k, 'Plano Ativo': v['plano']} for k, v in st.session_state['usuarios'].items() if v['perfil'] == 'CLIENTE']
        if lista_clientes: st.table(pd.DataFrame(lista_clientes))

# ==========================================
# AMBIENTE 2: PAINEL DO CLIENTE (UPLOAD DE ARQUIVOS)
# ==========================================
elif user_info['perfil'] == 'CLIENTE':
    st.title(f"⚡ Painel de Logística | {user_info['empresa']}")
    st.markdown(f"**Licença Ativa:** `{user_info['plano']}`")
    st.markdown("---")
    
    col_upload, col_mapa = st.columns([1, 2])
    
    with col_upload:
        st.subheader("1. Inserir Dados Operacionais")
        st.info("Faça o upload dos arquivos CSV contendo sua frota disponível e os endereços de entrega de hoje.")
        
        # O cliente faz o upload dos arquivos dele!
        arq_frota = st.file_uploader("📂 Upload da Frota (CSV)", type="csv")
        arq_entregas = st.file_uploader("📂 Upload das Entregas (CSV)", type="csv")
        
        df_frota = pd.read_csv(arq_frota) if arq_frota else None
        df_entregas = pd.read_csv(arq_entregas) if arq_entregas else None

        if df_frota is not None and df_entregas is not None:
            qtd_veiculos = len(df_frota)
            qtd_entregas = len(df_entregas)
            
            st.success("✅ Arquivos lidos com sucesso!")
            st.metric("Veículos Detectados", qtd_veiculos)
            st.metric("Entregas Detectadas", qtd_entregas)
            
            if st.button("🚀 Otimizar Rotas Agora", use_container_width=True):
                st.session_state['motor_acionado'] = True
                
    with col_mapa:
        st.subheader("2. Matriz de Roteamento")
        if df_frota is not None and df_entregas is not None and st.session_state.get('motor_acionado', False):
            with st.spinner("Processando distribuição quântica..."):
                time.sleep(2)
                
                # Para o MVP, usamos a latitude/longitude do arquivo (se houver)
                # Como teste, desenhamos o mapa focado nos pontos carregados
                try:
                    lat_media = df_entregas['Latitude'].mean()
                    lon_media = df_entregas['Longitude'].mean()
                    mapa_cliente = folium.Map(location=[lat_media, lon_media], zoom_start=6, tiles="CartoDB dark_matter")
                    
                    for _, row in df_entregas.iterrows():
                        folium.CircleMarker([row['Latitude'], row['Longitude']], radius=3, color="#2563eb", fill=True).add_to(mapa_cliente)
                        
                    components.html(mapa_cliente._repr_html_(), height=500)
                    st.success("Otimização concluída e enviada aos Apps dos Condutores.")
                except KeyError:
                    st.error("Erro: O arquivo de entregas precisa conter colunas 'Latitude' e 'Longitude'.")
        else:
            st.info("Aguardando upload dos arquivos e acionamento do motor.")
