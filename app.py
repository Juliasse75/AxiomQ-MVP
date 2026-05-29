import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import folium
import time
import numpy as np

st.set_page_config(page_title="AxiomQ | Matriz Global", layout="wide", page_icon="⚡")

# ==========================================
# 1. BANCO DE DADOS PERSISTENTE NA SESSÃO
# ==========================================
if 'usuarios' not in st.session_state:
    st.session_state['usuarios'] = {
        'ceo@axiomq.com.br': {'senha': '123', 'perfil': 'MASTER', 'nome': 'Cosme (CEO)'},
        'gerente@farmaciax.com.br': {'senha': '456', 'perfil': 'CLIENTE'}
    }

if 'clientes' not in st.session_state:
    st.session_state['clientes'] = {
        'gerente@farmaciax.com.br': {
            "Empresa": "Farmácia X", "CNPJ": "00.123.456/0001-99", "Telefone": "(31) 98888-7777", 
            "Plano": "POC (Teste) - Até 5 veículos", "Vencimento": "25/06/2026", "Status": "Ativo", "Obs": "Parceiro inicial."
        }
    }

if 'planos' not in st.session_state:
    st.session_state['planos'] = {
        "POC (Teste) - Até 5 veículos": "Até 5 veículos",
        "Starter - Até 15 veículos": "Até 15 veículos",
        "Advanced - Até 50 veículos": "Até 50 veículos",
        "Quantum (Enterprise) - Ilimitado": "Ilimitado"
    }

# LISTA GLOBAL DE MODAIS ATUALIZADA (COM CARRO LEVE)
LISTA_MODAIS = ["Carro Leve", "Picape 4x4", "Van", "Caminhão Pesado", "Motocicleta"]

if 'frotas' not in st.session_state:
    st.session_state['frotas'] = {
        'gerente@farmaciax.com.br': [
            {"ID_Veiculo": "Moto-01", "Tipo": "Motocicleta", "Capacidade_KG": 100, "Status": "Disponível"},
            {"ID_Veiculo": "Moto-02", "Tipo": "Motocicleta", "Capacidade_KG": 100, "Status": "Disponível"},
            {"ID_Veiculo": "Moto-03", "Tipo": "Motocicleta", "Capacidade_KG": 100, "Status": "Disponível"}
        ]
    }

if 'logado' not in st.session_state: st.session_state['logado'] = False
if 'user_atual' not in st.session_state: st.session_state['user_atual'] = None

LOGO_HTML = """
<div style="text-align: center; margin-bottom: 20px;">
    <h1 style="font-size: 50px; font-weight: 800; color: white; margin: 0; text-shadow: 0 0 15px #2563eb, 0 0 30px #8b5cf6;">Axiom<span style="color: #2563eb;">Q</span></h1>
    <p style="color: #8b5cf6; font-size: 14px; letter-spacing: 4px; margin: 0;">NÚCLEO DE INTELIGÊNCIA LOGÍSTICA</p>
</div>
"""

# TELA DE LOGIN
if not st.session_state['logado']:
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.write("<br><br>", unsafe_allow_html=True)
        st.markdown(LOGO_HTML, unsafe_allow_html=True)
        with st.form("login_central"):
            u_input = st.text_input("E-mail corporativo:")
            s_input = st.text_input("Senha tática:", type="password")
            if st.form_submit_button("Acessar AxiomQ", use_container_width=True):
                email_limpo = u_input.strip().lower()
                if email_limpo in st.session_state['clientes'] and st.session_state['clientes'][email_limpo]['Status'] == 'Bloqueado':
                    st.error("🚨🔒 Acesso Suspenso. Contate o Administrador Master.")
                elif email_limpo in st.session_state['usuarios'] and st.session_state['usuarios'][email_limpo]['senha'] == s_input:
                    st.session_state['logado'] = True
                    st.session_state['user_atual'] = email_limpo
                    st.rerun()
                else:
                    st.error("Credenciais inválidas.")
    st.stop()

user_info = st.session_state['usuarios'][st.session_state['user_atual']]
st.sidebar.markdown("### Controle de Sessão")
if st.sidebar.button("🔒 Encerrar Sessão", use_container_width=True):
    st.session_state['logado'] = False
    st.session_state['user_atual'] = None
    st.rerun()

# ==========================================
# AMBIENTE MASTER: ADMINISTRADOR
# ==========================================
if user_info['perfil'] == 'MASTER':
    st.title(f"👋 Bem-vindo, {user_info['nome']} | Controle Matriz")
    aba_criar, aba_parceiros, aba_planos = st.tabs(["🆕 Cadastrar Parceiro", "🏢 Gestão de Clientes", "⚙️ Configurar Planos"])
    
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
                    st.session_state['clientes'][email_limpo_cad] = {
                        "Empresa": nome, "CNPJ": cnpj, "Telefone": tel, "Plano": plano, "Vencimento": dt_venc.strftime("%d/%m/%Y"), "Status": "Ativo", "Obs": obs
                    }
                    st.session_state['usuarios'][email_limpo_cad] = {'senha': str(senha_provisoria), 'perfil': 'CLIENTE'}
                    st.session_state['frotas'][email_limpo_cad] = []
                    st.success(f"✅ Parceiro {nome} registrado com sucesso!")
                    st.rerun()

    with aba_parceiros:
        if st.session_state['clientes']:
            dados_tabela = [{"Login/E-mail": k, "Empresa": v["Empresa"], "CNPJ": v["CNPJ"], "Telefone": v["Telefone"], "Plano": v["Plano"], "Vencimento": v["Vencimento"], "Status": v["Status"]} for k, v in st.session_state['clientes'].items()]
            st.table(pd.DataFrame(dados_tabela))
            st.markdown("---")
            st.subheader("🛠️ Central de Moderação Tática")
            cliente_sel = st.selectbox("Selecione o Cliente para Modificar:", list(st.session_state['clientes'].keys()))
            if cliente_sel:
                c_info = st.session_state['clientes'][cliente_sel]
                col_btn1, col_btn2 = st.columns(2)
                status_atual = c_info["Status"]
                novo_status = "Bloqueado" if status_atual == "Ativo" else "Ativo"
                label_blq = "🔒 Bloquear Acesso" if status_atual == "Ativo" else "🔓 Desbloquear e Ativar"
                
                if col_btn1.button(label_blq, use_container_width=True):
                    st.session_state['clientes'][cliente_sel]["Status"] = novo_status
                    st.rerun()
                if col_btn2.button("❌ Excluir Permanentemente", use_container_width=True):
                    del st.session_state['clientes'][cliente_sel]
                    del st.session_state['usuarios'][cliente_sel]
                    if cliente_sel in st.session_state['frotas']: del st.session_state['frotas'][cliente_sel]
                    st.rerun()
    with aba_planos:
        for p, d in st.session_state['planos'].items(): st.write(f"- **{p}**: {d}")

# ==========================================
# AMBIENTE CLIENTE: PORTAL DO GESTOR DE LOGÍSTICA
# ==========================================
elif user_info['perfil'] == 'CLIENTE':
    client_email = st.session_state['user_atual']
    c_dados = st.session_state['clientes'][client_email]
    
    st.title(f"⚡ Painel de Logística | {c_dados['Empresa']}")
    st.markdown(f"**Licença Ativa:** `{c_dados['Plano']}` | **Status:** `CONEXÃO OPERACIONAL ATIVA`")
    st.markdown("---")
    
    aba_frota_cli, aba_roteiro_cli = st.tabs(["🚛 1. Gerenciar Frota Ativa", "📦 2. Roteirizar Entregas"])
    
    with aba_frota_cli:
        st.subheader("Controle de Ativos e Disponibilidade de Veículos")
        col_up_frota, col_lista_frota = st.columns([1, 2])
        
        with col_up_frota:
            st.markdown("### 📥 Carga Inicial de Frota")
            st.info("Suba sua planilha de veículos. Clique no botão de integração abaixo para salvar de forma permanente na sessão.")
            arq_f = st.file_uploader("Upload da Frota (CSV)", type="csv", key="frota_uploader")
            
            # FIX 3: Processamento explícito por botão para evitar o loop do Streamlit
            if arq_f:
                if st.button("🔄 Processar e Integrar Planilha", use_container_width=True):
                    try:
                        df_f_uploaded = pd.read_csv(arq_f)
                        nova_frota = []
                        for _, r in df_f_uploaded.iterrows():
                            # Mapeia tipos vindo da planilha ou joga padrão
                            tipo_planilha = str(r.get('Tipo', 'Carro Leve'))
                            if tipo_planilha not in LISTA_MODAIS:
                                tipo_planilha = "Carro Leve"
                                
                            nova_frota.append({
                                "ID_Veiculo": str(r.get('ID_Veiculo', f"VEIC-{_}")),
                                "Tipo": tipo_planilha,
                                "Capacidade_KG": int(r.get('Capacidade_KG', 500)),
                                "Status": "Disponível"
                            })
                        st.session_state['frotas'][client_email] = nova_frota
                        st.success(f"✅ Sucesso! {len(nova_frota)} veículos integrados à base ativa.")
                        time.sleep(1)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro ao ler planilha: {e}")
            
            st.markdown("---")
            st.markdown("### ➕ Incluir Veículo Avulso")
            with st.form("add_avulso"):
                id_v = st.text_input("Identificação do Veículo (Prefixo/Placa):")
                tipo_v = st.selectbox("Modal / Tipo:", LISTA_MODAIS) # FIX 1: Incluído Carro Leve
                cap_v = st.number_input("Capacidade de Carga (KG):", min_value=1, value=500)
                if st.form_submit_button("Adicionar à Frota Ativa", use_container_width=True):
                    if id_v:
                        st.session_state['frotas'][client_email].append({
                            "ID_Veiculo": id_v, "Tipo": tipo_v, "Capacidade_KG": int(cap_v), "Status": "Disponível"
                        })
                        st.success(f"Veículo {id_v} incluído com sucesso!")
                        time.sleep(0.5)
                        st.rerun()
        
        with col_lista_frota:
            st.markdown("### 📋 Frota Registrada no Sistema")
            frota_atual = st.session_state['frotas'].get(client_email, [])
            
            if frota_atual:
                df_frota_visu = pd.DataFrame(frota_atual)
                st.dataframe(df_frota_visu, use_container_width=True)
                
                # FIX 2: Exportação otimizada com separador nacional (;) e codificação UTF-8-SIG para Excel brasileiro
                csv_data = df_frota_visu.to_csv(index=False, sep=';', encoding='utf-8-sig')
                st.download_button(
                    label="📥 Exportar Frota Atual para Planilha (Padrão Excel BR)",
                    data=csv_data,
                    file_name="frota_atualizada_axiomq.csv",
                    mime="text/csv",
                    use_container_width=True
                )
                
                st.markdown("---")
                st.markdown("### 🛠️ Modificar Veículo Individual")
                v_selecionado = st.selectbox("Escolha o veículo para alterar:", [v["ID_Veiculo"] for v in frota_atual])
                
                if v_selecionado:
                    idx = next(i for i, v in enumerate(frota_atual) if v["ID_Veiculo"] == v_selecionado)
                    v_dados = frota_atual[idx]
                    col_edit1, col_edit2 = st.columns(2)
                    
                    lbl_status = "🔴 Deixar Indisponível" if v_dados["Status"] == "Disponível" else "🟢 Ativar Veículo"
                    n_stat = "Indisponível" if v_dados["Status"] == "Disponível" else "Disponível"
                    if col_edit1.button(lbl_status, use_container_width=True):
                        st.session_state['frotas'][client_email][idx]["Status"] = n_stat
                        st.rerun()
                        
                    if col_edit2.button("🗑️ Remover da Frota", use_container_width=True):
                        st.session_state['frotas'][client_email].pop(idx)
                        st.rerun()
                        
                    with st.expander("📝 Editar Detalhes Mecânicos"):
                        with st.form("edit_mec"):
                            novo_tipo = st.selectbox("Alterar Tipo:", LISTA_MODAIS, index=LISTA_MODAIS.index(v_dados["Tipo"]) if v_dados["Tipo"] in LISTA_MODAIS else 0)
                            nova_cap = st.number_input("Nova Capacidade (KG):", value=v_dados["Capacidade_KG"])
                            if st.form_submit_button("Salvar Alterações Mecânicas", use_container_width=True):
                                st.session_state['frotas'][client_email][idx]["Tipo"] = novo_tipo
                                st.session_state['frotas'][client_email][idx]["Capacidade_KG"] = int(nova_cap)
                                st.rerun()
            else:
                st.warning("Nenhum veículo cadastrado. Suba uma planilha ou insira um veículo avulso ao lado.")

    with aba_roteiro_cli:
        st.subheader("Injeção Diária de Pedidos e Roteamento Híbrido")
        col_pedidos, col_mapa_painel = st.columns([1, 2])
        
        with col_pedidos:
            st.markdown("### 📦 Entregas do Dia")
            arq_e = st.file_uploader("Carregar Pontos de Entrega (CSV)", type="csv", key="entregas_uploader")
            df_entregas = pd.read_csv(arq_e) if arq_e else None
            
            veiculos_disponiveis = [v for v in st.session_state['frotas'].get(client_email, []) if v["Status"] == "Disponível"]
            st.metric("Veículos Prontos para Rodar Hoje", len(veiculos_disponiveis))
            
            if df_entregas is not None:
                st.success(f"✅ {len(df_entregas)} pedidos mapeados com sucesso!")
                if len(veiculos_disponiveis) == 0:
                    st.error("🚨 Operação bloqueada: Você não possui nenhum veículo ativo hoje.")
                else:
                    if st.button("🚀 Disparar Motor Quântico AxiomQ", use_container_width=True):
                        st.session_state['motor_acionado'] = True
            else:
                st.info("Aguardando o upload do arquivo de entregas diárias.")
                
        with col_mapa_painel:
            st.markdown("### 🗺️ Visão de Terreno e Escalonamento")
            if df_entregas is not None and st.session_state.get('motor_acionado', False) and len(veiculos_disponiveis) > 0:
                with st.spinner("Processando otimização..."):
                    try:
                        lat_media = df_entregas['Latitude'].mean()
                        lon_media = df_entregas['Longitude'].mean()
                        mapa_cliente = folium.Map(location=[lat_media, lon_media], zoom_start=6, tiles="CartoDB dark_matter")
                        for _, row in df_entregas.iterrows():
                            folium.CircleMarker([row['Latitude'], row['Longitude']], radius=3, color="#2563eb", fill=True).add_to(mapa_cliente)
                        components.html(mapa_cliente._repr_html_(), height=500)
                        st.success("✅ Malha gerada com sucesso.")
                    except KeyError:
                        st.error("Erro Crítico: O arquivo precisa conter colunas 'Latitude' e 'Longitude'.")
            else:
                st.info("Aguardando acionamento do motor.")
