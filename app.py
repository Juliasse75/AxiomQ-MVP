import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import folium
import time
import numpy as np

st.set_page_config(page_title="AxiomQ | Matriz Global", layout="wide", page_icon="⚡")

# ==========================================
# 1. BANCO DE DADOS INTEGRADO E PERSISTENTE
# ==========================================
if 'usuarios' not in st.session_state:
    st.session_state['usuarios'] = {
        'ceo@axiomq.com.br': {'senha': '123', 'perfil': 'MASTER', 'nome': 'Cosme (CEO)'},
        'gerente@farmaciax.com.br': {'senha': '456', 'perfil': 'CLIENTE', 'empresa': 'Farmácia X'},
        'condutor01@farmaciax.com.br': {'senha': '789', 'perfil': 'CONDUTOR', 'empresa': 'Farmácia X', 'veiculo': 'Moto-01'}
    }

if 'clientes' not in st.session_state:
    st.session_state['clientes'] = {
        'gerente@farmaciax.com.br': {
            "Empresa": "Farmácia X", "CNPJ": "00.123.456/0001-99", "Telefone": "(31) 98888-7777", 
            "Plano": "POC (Teste) - Até 5 vehicles", "Vencimento": "25/06/2026", "Status": "Ativo", "Obs": "Parceiro inicial."
        }
    }

if 'frotas' not in st.session_state:
    st.session_state['frotas'] = {
        'gerente@farmaciax.com.br': [
            {"ID_Veiculo": "Moto-01", "Tipo": "Motocicleta", "Capacidade_KG": 100, "Status": "Disponível"},
            {"ID_Veiculo": "Moto-02", "Tipo": "Motocicleta", "Capacidade_KG": 100, "Status": "Disponível"},
            {"ID_Veiculo": "Moto-03", "Tipo": "Motocicleta", "Capacidade_KG": 100, "Status": "Disponível"}
        ]
    }

# Controle global de status das entregas para sincronização em tempo real
if 'registro_entregas' not in st.session_state:
    st.session_state['registro_entregas'] = {} # Chave: 'veiculo_indice_parada' -> Status string

if 'logado' not in st.session_state: st.session_state['logado'] = False
if 'user_atual' not in st.session_state: st.session_state['user_atual'] = None

LOGO_HTML = """
<div style="text-align: center; margin-bottom: 20px;">
    <h1 style="font-size: 50px; font-weight: 800; color: white; margin: 0; text-shadow: 0 0 15px #2563eb, 0 0 30px #8b5cf6;">Axiom<span style="color: #2563eb;">Q</span></h1>
    <p style="color: #8b5cf6; font-size: 14px; letter-spacing: 4px; margin: 0;">NÚCLEO DE INTELIGÊNCIA LOGÍSTICA</p>
</div>
"""

# TELA DE LOGIN CENTRAL
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
    aba_criar, aba_parceiros = st.tabs(["🆕 Cadastrar Parceiro", "🏢 Gestão de Clientes"])
    with aba_criar:
        st.info("Painel operacional ativo. Utilize o formulário padrão para novos registros.")
    with aba_parceiros:
        dados_tabela = [{"Login/E-mail": k, "Empresa": v["Empresa"], "CNPJ": v["CNPJ"], "Status": v["Status"]} for k, v in st.session_state['clientes'].items()]
        st.table(pd.DataFrame(dados_tabela))

# ==========================================
# AMBIENTE CLIENTE: PORTAL DO GESTOR DA FARMÁCIA
# ==========================================
elif user_info['perfil'] == 'CLIENTE':
    client_email = st.session_state['user_atual']
    c_dados = st.session_state['clientes'][client_email]
    
    st.title(f"⚡ Painel de Logística | {c_dados['Empresa']}")
    st.markdown(f"**Licença Ativa:** `{c_dados['Plano']}`")
    st.markdown("---")
    
    aba_frota_cli, aba_roteiro_cli = st.tabs(["🚛 1. Gerenciar Frota Ativa", "📦 2. Roteirizar Entregas"])
    
    with aba_frota_cli:
        st.subheader("Controle de Ativos")
        frota_atual = st.session_state['frotas'].get(client_email, [])
        st.dataframe(pd.DataFrame(frota_atual), use_container_width=True)
        
    with aba_roteiro_cli:
        col_pedidos, col_mapa_painel = st.columns([1, 2])
        with col_pedidos:
            st.markdown("### 📦 Entregas do Dia")
            arq_e = st.file_uploader("Carregar Pontos de Entrega (CSV)", type="csv", key="entregas_uploader")
            df_entregas = pd.read_csv(arq_e) if arq_e else None
            veiculos_disponiveis = [v for v in st.session_state['frotas'].get(client_email, []) if v["Status"] == "Disponível"]
            st.metric("Veículos Ativos", len(veiculos_disponiveis))
            if df_entregas is not None and st.button("🚀 Disparar Motor Quântico AxiomQ", use_container_width=True):
                st.session_state['motor_acionado'] = True

        with col_mapa_painel:
            if df_entregas is not None and st.session_state.get('motor_acionado', False) and len(veiculos_disponiveis) > 0:
                lat_media, lon_media = df_entregas['Latitude'].mean(), df_entregas['Longitude'].mean()
                mapa_cliente = folium.Map(location=[lat_media, lon_media], zoom_start=13, tiles="CartoDB dark_matter")
                
                cores_hex = ["#3b82f6", "#a855f7", "#eab308", "#22c55e"]
                qtd_v = len(veiculos_disponiveis)
                df_ordenado = df_entregas.sort_values(by=['Latitude', 'Longitude']).reset_index(drop=True)
                
                nomes_simulados = ["João Carlos da Silva", "Clínica Saúde", "Maria F. Santos", "Pedro Almeida", "Farmácia Preço Certo"]
                bairros_simulados = ["Centro", "Savassi", "Lourdes", "Barro Preto", "Funcionários"]
                
                lista_resumo_kpis = []
                
                for idx_v, v in enumerate(veiculos_disponiveis):
                    pontos_v = df_ordenado[df_ordenado.index % qtd_v == idx_v].reset_index(drop=True)
                    cor_v = cores_hex[idx_v % len(cores_hex)]
                    
                    total_entregas = len(pontos_v)
                    realizadas = 0
                    
                    # Varre as paradas e computa o status vindo do App do Condutor
                    for idx_p, row in pontos_v.iterrows():
                        chave_status = f"{v['ID_Veiculo']}_{idx_p}"
                        
                        # Inicializa como Em Rota se não existir no registro global
                        if chave_status not in st.session_state['registro_entregas']:
                            st.session_state['registro_entregas'][chave_status] = "⏳ Em Rota"
                            
                        if st.session_state['registro_entregas'][chave_status] == "✅ Pacote Entregue":
                            realizadas += 1
                            
                        folium.CircleMarker(
                            location=[row['Latitude'], row['Longitude']], radius=5, color=cor_v, fill=True,
                            popup=f"Parada #{idx_p+1}"
                        ).add_to(mapa_cliente)
                        
                    pct_realizado = round((realizadas / total_entregas) * 100, 1) if total_entregas > 0 else 0.0
                    
                    lista_resumo_kpis.append({
                        "ID do Veículo": v["ID_Veiculo"],
                        "Tipo": v["Tipo"],
                        "Carga Alocada": f"{total_entregas} Pacotes",
                        "Progresso de Campo": f"🟢 {realizadas} de {total_entregas} Concluídas",
                        "Taxa de Sucesso": f"{pct_realizado} %"
                    })
                    
                components.html(mapa_cliente._repr_html_(), height=400)
                st.markdown("### 📊 Quadro de Eficiência Operacional (KPIs)")
                st.table(pd.DataFrame(lista_resumo_kpis))
                
                # Manifesto detalhado na visão do gerente
                st.markdown("---")
                st.markdown("### 📋 Auditoria de Manifesto Nominativo")
                v_sel = st.selectbox("Selecione o veículo para auditar:", [v["ID_Veiculo"] for v in veiculos_disponiveis])
                if v_sel:
                    v_idx = next(i for i, ve in enumerate(veiculos_disponiveis) if ve["ID_Veiculo"] == v_sel)
                    df_paradas = df_ordenado[df_ordenado.index % qtd_v == v_idx].reset_index(drop=True)
                    
                    tabela_gerente = []
                    for idx_p, row in df_paradas.iterrows():
                        chave = f"{v_sel}_{idx_p}"
                        tabela_gerente.append({
                            "Parada": f"{idx_p+1}º",
                            "Cliente/Recebedor": nomes_simulados[idx_p % len(nomes_simulados)],
                            "Endereço Completo": f"Av. Principal, {int(idx_p*30+10)} - {bairros_simulados[idx_p % len(bairros_simulados)]}, BH/MG",
                            "Status de Campo": st.session_state['registro_entregas'].get(chave, "⏳ Em Rota")
                        })
                    st.dataframe(pd.DataFrame(tabela_gerente), use_container_width=True)
            else:
                st.info("Aguardando ativação do motor para consolidar o relatório nominal de campo.")

# ==========================================
# AMBIENTE CONDUTOR: APP DO CONDUTOR (MOBILE)
# ==========================================
elif user_info['perfil'] == 'CONDUTOR':
    st.markdown("""
        <style>
            .block-container { max-width: 450px !important; padding-top: 1rem !important; }
            .stButton>button { background-color: #22c55e !important; color: white !important; font-weight: bold; }
        </style>
    """, unsafe_allow_html=True)
    
    st.title("📱 App do Condutor")
    st.markdown(f"**Operador:** `{st.session_state['user_atual']}` | **Unidade:** `{user_info['veiculo']}`")
    st.markdown("<div style='border-bottom: 2px solid #8b5cf6;'></div>", unsafe_allow_html=True)
    
    # Verifica se o motor já gerou rotas
    if not st.session_state.get('motor_acionado', False):
        st.warning("⏳ Nenhuma rota disponível. Aguardando disparo do painel central pelo gestor.")
    else:
        st.subheader("📋 Suas Entregas de Hoje")
        st.write("Siga a sequência ordenada abaixo para realizar as paradas:")
        
        # Simula as paradas correspondentes ao veículo Moto-01 (índice 0 na divisão por 3 frotas)
        nomes_simulados = ["João Carlos da Silva", "Clínica Saúde", "Maria F. Santos", "Pedro Almeida", "Farmácia Preço Certo"]
        bairros_simulados = ["Centro", "Savassi", "Lourdes", "Barro Preto", "Funcionários"]
        
        # Simulamos 3 paradas fixas para a Moto-01 para demonstração móvel direta
        for i in range(3):
            chave_entrega = f"{user_info['veiculo']}_{i}"
            status_atual = st.session_state['registro_entregas'].get(chave_entrega, "⏳ Em Rota")
            
            with st.container():
                st.markdown(f"### **{i+1}ª Parada**")
                st.markdown(f"**Cliente:** {nomes_simulados[i % len(nomes_simulados)]}")
                st.markdown(f"📍 Av. Principal, {int(i*30+10)} - {bairros_simulados[i % len(bairros_simulados)]}, BH/MG")
                st.markdown(f"**Status:** `{status_atual}`")
                
                if status_atual == "⏳ Em Rota":
                    if st.button(f"✓ Confirmar Entrega #{i+1}", key=f"btn_{chave_entrega}", use_container_width=True):
                        st.session_state['registro_entregas'][chave_entrega] = "✅ Pacote Entregue"
                        st.success(f"Entrega #{i+1} confirmada no satélite!")
                        time.sleep(0.5)
                        st.rerun()
                else:
                    st.markdown("<p style='color: #22c55e;'>★ Concluído</p>", unsafe_allow_html=True)
                st.markdown("---")
