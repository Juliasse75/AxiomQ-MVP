import streamlit as st
import pandas as pd
import folium
import time
import numpy as np

st.set_page_config(page_title="AxiomQ | Matriz Global", layout="wide", page_icon="⚡")

# 1. BANCO DE DADOS PERSISTENTE NA SESSÃO
if 'usuarios' not in st.session_state:
    st.session_state['usuarios'] = {
        'ceo@axiomq.com.br': {'senha': '123', 'perfil': 'MASTER', 'nome': 'Cosme (CEO)'}
    }
if 'clientes' not in st.session_state:
    st.session_state['clientes'] = []
if 'planos' not in st.session_state:
    st.session_state['planos'] = {
        "POC (Teste)": "Até 5 veículos",
        "Starter": "Até 15 veículos",
        "Advanced": "Até 50 veículos",
        "Quantum": "Ilimitado"
    }

# ==========================================
# PAINEL MASTER (VOCÊ)
# ==========================================
def render_master():
    st.title("🛡️ Painel de Controle Master | AxiomQ")
    aba1, aba2, aba3 = st.tabs(["🆕 Cadastrar Cliente", "🏢 Gestão de Clientes", "⚙️ Configurar Planos"])
    
    with aba1:
        with st.form("cadastro_completo"):
            st.subheader("Cadastro de Novo Parceiro")
            c1, c2 = st.columns(2)
            nome = c1.text_input("Razão Social:")
            cnpj = c2.text_input("CNPJ:")
            email = c1.text_input("E-mail Comercial (Login):")
            tel = c2.text_input("Celular/WhatsApp:")
            endereco = st.text_input("Endereço Completo:")
            plano = st.selectbox("Plano:", list(st.session_state['planos'].keys()))
            dt_venc = st.date_input("Data de Vencimento:")
            
            if st.form_submit_button("Registrar Parceiro"):
                st.session_state['clientes'].append({
                    "Empresa": nome, "CNPJ": cnpj, "Email": email, 
                    "Tel": tel, "End": endereco, "Plano": plano, "Venc": dt_venc
                })
                st.session_state['usuarios'][email.lower()] = {'senha': '123', 'perfil': 'CLIENTE'}
                st.success(f"Parceiro {nome} registrado com sucesso!")

    with aba2:
        st.subheader("Clientes Ativos")
        if st.session_state['clientes']:
            df = pd.DataFrame(st.session_state['clientes'])
            st.table(df)
            
    with aba3:
        st.subheader("Editor de Planos")
        novo_plano = st.text_input("Nome do Novo Plano:")
        desc_plano = st.text_input("Descrição (ex: Até X veículos):")
        if st.button("Adicionar/Editar Plano"):
            st.session_state['planos'][novo_plano] = desc_plano
            st.success("Plano atualizado!")

# ==========================================
# LÓGICA DE LOGIN SIMPLIFICADA
# ==========================================
if 'logado' not in st.session_state: st.session_state['logado'] = False

if not st.session_state['logado']:
    u = st.text_input("E-mail:")
    p = st.text_input("Senha:", type="password")
    if st.button("Acessar AxiomQ"):
        u = u.strip().lower()
        if u in st.session_state['usuarios'] and st.session_state['usuarios'][u]['senha'] == p:
            st.session_state['logado'] = True
            st.session_state['user'] = u
            st.rerun()
else:
    user = st.session_state['user']
    if st.session_state['usuarios'][user]['perfil'] == 'MASTER':
        render_master()
    else:
        st.title(f"Bem-vindo, {user}")
        st.info("Painel do Cliente em construção: Upload de arquivos de frota e entregas virá aqui.")
    
    if st.sidebar.button("Sair"):
        st.session_state['logado'] = False
        st.rerun()
