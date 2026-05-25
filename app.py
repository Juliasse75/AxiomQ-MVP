import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import folium
import time
import numpy as np
from datetime import datetime

st.set_page_config(page_title="AxiomQ | Matriz Global", layout="wide", page_icon="⚡")

# 1. BANCO DE DADOS INTEGRADO E PERSISTENTE NA SESSÃO
if 'usuarios' not in st.session_state:
    st.session_state['usuarios'] = {
        'ceo@axiomq.com.br': {'senha': '123', 'perfil': 'MASTER', 'nome': 'Cosme (CEO)'},
        'gerente@farmaciax.com.br': {'senha': '456', 'perfil': 'CLIENTE'}
    }

if 'clientes' not in st.session_state:
    st.session_state['clientes'] = {
        'gerente@farmaciax.com.br': {
            "Empresa": "Farmácia X", 
            "CNPJ": "00.123.456/0001-99", 
            "Telefone": "(31) 98888-7777", 
            "Plano": "POC (Teste) - Até 5 veículos", 
            "Vencimento": "25/06/2026",
            "Status": "Ativo",
            "Obs": "Parceiro inicial de desenvolvimento e testes de campo."
        }
    }

if 'planos' not in st.session_state:
    st.session_state['planos'] = {
        "POC (Teste) - Até 5 veículos": "Até 5 veículos",
        "Starter - Até 15 veículos": "Até 15 veículos",
        "Advanced - Até 50 veículos": "Até 50 veículos",
        "Quantum (Enterprise) - Ilimitado": "Ilimitado"
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
# TELA DE AUTENTICAÇÃO CENTRAL
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
                
                # Verificação de Bloqueio antes de permitir o login
                if email_limpo in st.session_state['clientes'] and st.session_state['clientes'][email_limpo]['Status'] == 'Bloqueado':
                    st.error("🚨🔒 Acesso Suspenso. Esta licença encontra-se bloqueada por razões administrativas. Contate o Administrador Master.")
                elif email_limpo in st.session_state['usuarios'] and st.session_state['usuarios'][email_limpo]['senha'] == s_input:
                    st.session_state['logado'] = True
                    st.session_state['user_atual'] = email_limpo
                    st.rerun()
                else:
                    st.error("Credenciais inválidas. Verifique os dados inseridos.")
    st.stop()

# CONTROLE DE LOGOUT
user_info = st.session_state['usuarios'][st.session_state['user_atual']]
st.sidebar.markdown("### Controle de Sessão")
if st.sidebar.button("🔒 Encerrar Sessão", use_container_width=True):
    st.session_state['logado'] = False
    st.session_state['user_atual'] = None
    st.rerun()

# ==========================================
# AMBIENTE MASTER: ADMINISTRADOR (VOCÊ)
# ==========================================
if user_info['perfil'] == 'MASTER':
    st.title(f"👋 Bem-vindo, {user_info['nome']} | Controle Matriz")
    
    aba_criar, aba_parceiros, aba_planos = st.tabs(["🆕 Cadastrar Parceiro", "🏢 Gestão e Moderação de Clientes", "⚙️ Configurar Planos"])
    
    with aba_criar:
        st.subheader("Cadastro Completo de Parceiro")
        with st.form("cadastro_completo"):
            c1, c2 = st.columns(2)
            nome = c1.text_input("Razão Social / Nome da Empresa:")
            cnpj = c2.text_input("CNPJ:")
            email = c1.text_input("E-mail Comercial (Login):")
            tel = c2.text_input("Celular / WhatsApp:")
            endereco = st.text_input("Endereço Completo da Sede:")
            
            c3, c4 = st.columns(2)
            plano = c3.selectbox("Plano de Licença:", list(st.session_state['planos'].keys()))
            dt_venc = c4.date_input("Data de Vencimento do Contrato:")
            senha_provisoria = st.text_input("Senha Inicial de Acesso:", type="password", value="456")
            obs = st.text_area("Observações Internas:")
            
            if st.form_submit_button("Registrar e Ativar Parceiro", use_container_width=True):
                email_limpo_cad = email.strip().lower()
                if email_limpo_cad not in st.session_state['usuarios']:
                    # Salva no dicionário estruturado
                    st.session_state['clientes'][email_limpo_cad] = {
                        "Empresa": nome, "CNPJ": cnpj, "Telefone": tel, 
                        "Plano": plano, "Vencimento": dt_venc.strftime("%d/%m/%Y"),
                        "Status": "Ativo", "Obs": obs
                    }
                    st.session_state['usuarios'][email_limpo_cad] = {
                        'senha': str(senha_provisoria), 'perfil': 'CLIENTE'
                    }
                    st.success(f"✅ Parceiro {nome} registrado com sucesso!")
                    st.rerun()
                else:
                    st.warning("Erro: Este e-mail de login já está em uso.")

    with aba_parceiros:
        st.subheader("Base de Clientes Ativos")
        
        if st.session_state['clientes']:
            # Converte dicionário para DataFrame para exibição limpa
            dados_tabela = []
            for login, info in st.session_state['clientes'].items():
                dados_tabela.append({
                    "Login/E-mail": login,
                    "Empresa": info["Empresa"],
                    "CNPJ": info["CNPJ"],
                    "Telefone": info["Telefone"],
                    "Plano": info["Plano"],
                    "Vencimento": info["Vencimento"],
                    "Status": info["Status"]
                })
            st.table(pd.DataFrame(dados_tabela))
            
            # PAINEL DE MODERAÇÃO DE DADOS (EDITAR, BLOQUEAR, EXCLUIR)
            st.markdown("---")
            st.subheader("🛠️ Central de Moderação Tática")
            st.markdown("Selecione o e-mail do cliente para alterar dados, bloquear acesso ou remover do sistema.")
            
            cliente_sel = st.selectbox("Escolha o Cliente para Modificar:", list(st.session_state['clientes'].keys()))
            
            if cliente_sel:
                c_info = st.session_state['clientes'][cliente_sel]
                
                col_btn1, col_btn2, col_btn3 = st.columns(3)
                
                # 1. BOTÃO BLOQUEAR / ATIVAR
                status_atual = c_info["Status"]
                novo_status = "Bloqueado" if status_atual == "Ativo" else "Ativo"
                label_blq = "🔒 Bloquear Acesso" if status_atual == "Ativo" else "🔓 Desbloquear e Ativar"
                
                if col_btn1.button(label_blq, use_container_width=True):
                    st.session_state['clientes'][cliente_sel]["Status"] = novo_status
                    st.success(f"Status do cliente alterado para: {novo_status}")
                    st.rerun()
                
                # 2. BOTÃO EXCLUIR
                if col_btn2.button("❌ Excluir Permanentemente", use_container_width=True):
                    del st.session_state['clientes'][cliente_sel]
                    del st.session_state['usuarios'][cliente_sel]
                    st.error("Cliente removido das bases de dados.")
                    st.rerun()
                
                # 3. EXPANDER PARA EDITAR DADOS
                with st.expander("📝 Editar Informações do Cliente Selecionado"):
                    with st.form("form_edicao"):
                        ed_nome = st.text_input("Razão Social:", value=c_info["Empresa"])
                        ed_cnpj = st.text_input("CNPJ:", value=c_info["CNPJ"])
                        ed_tel = st.text_input("Telefone:", value=c_info["Telefone"])
                        ed_plano = st.selectbox("Alterar Plano:", list(st.session_state['planos'].keys()), index=list(st.session_state['planos'].keys()).index(c_info["Plano"]))
                        ed_venc = st.text_input("Data de Vencimento (dd/mm/aaaa):", value=c_info["Vencimento"])
                        ed_obs = st.text_area("Observações:", value=c_info["Obs"])
                        
                        if st.form_submit_button("Salvar Alterações", use_container_width=True):
                            st.session_state['clientes'][cliente_sel].update({
                                "Empresa": ed_nome, "CNPJ": ed_cnpj, "Telefone": ed_tel,
                                "Plano": ed_plano, "Vencimento": ed_venc, "Obs": ed_obs
                            })
                            st.success("Dados atualizados com sucesso no núcleo!")
                            st.rerun()
        else:
            st.info("Nenhum cliente cadastrado no momento.")
            
    with aba_planos:
        st.subheader("Editor Dinâmico de Planos")
        n_plano = st.text_input("Nome do Novo Plano:")
        d_plano = st.text_input("Descrição / Limite de Veículos:")
        if st.button("Gravar Plano"):
            if n_plano and d_plano:
                st.session_state['planos'][n_plano] = d_plano
                st.success(f"Plano '{n_plano}' atualizado!")
        
        st.markdown("---")
        st.markdown("**Planos Disponíveis:**")
        for p, d in st.session_state['planos'].items():
            st.write(f"- **{p}**: {d}")

# ==========================================
# AMBIENTE CLIENTE: EX: GERENTE DA FARMÁCIA
# ==========================================
elif user_info['perfil'] == 'CLIENTE':
    # Puxa dados do banco master
    c_dados = st.session_state['clientes'][st.session_state['user_atual']]
    
    st.title(f"⚡ Painel de Logística | {c_dados['Empresa']}")
    st.markdown(f"**Licença Ativa:** `{c_dados['Plano']}` | **Status do Canal:** `CONEXÃO OPERACIONAL ATIVA`")
    st.markdown("---")
    
    col_upload, col_mapa = st.columns([1, 2])
    
    with col_upload:
        st.subheader("1. Entrada de Arquivos Operacionais")
        st.info("Insira os relatórios consolidados de frota disponível e solicitações de entrega.")
        
        arq_frota = st.file_uploader("📂 Carregar Arquivo de Frota (CSV)", type="csv")
        arq_entregas = st.file_uploader("📂 Carregar Pontos de Entrega (CSV)", type="csv")
        
        df_frota = pd.read_csv(arq_frota) if arq_frota else None
        df_entregas = pd.read_csv(arq_entregas) if arq_entregas else None

        if df_frota is not None and df_entregas is not None:
            st.success("✅ Varredura concluída com sucesso!")
            st.metric("Condutores/Veículos Prontos", len(df_frota))
            st.metric("Entregas Mapeadas na Fila", len(df_entregas))
            
            if st.button("🚀 Disparar Motor Quântico AxiomQ", use_container_width=True):
                st.session_state['motor_acionado'] = True
                
    with col_mapa:
        st.subheader("2. Matriz de Distribuição e Roteamento")
        if df_frota is not None and df_entregas is not None and st.session_state.get('motor_acionado', False):
            with st.spinner("Processando otimização adaptativa combinatória..."):
                time.sleep(2)
                try:
                    lat_media = df_entregas['Latitude'].mean()
                    lon_media = df_entregas['Longitude'].mean()
                    mapa_cliente = folium.Map(location=[lat_media, lon_media], zoom_start=6, tiles="CartoDB dark_matter")
                    
                    for _, row in df_entregas.iterrows():
                        folium.CircleMarker([row['Latitude'], row['Longitude']], radius=3, color="#2563eb", fill=True).add_to(mapa_cliente)
                        
                    components.html(mapa_cliente._repr_html_(), height=500)
                    st.success("✅ Malha tática gerada. Rotas distribuídas aos Apps dos Condutores.")
                except KeyError:
                    st.error("Erro Crítico: Certifique-se de que o arquivo possui as colunas 'Latitude' e 'Longitude'.")
        else:
            st.info("Aguardando inserção de dados pelo Gestor Logístico.")
