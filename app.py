import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import folium
import time
import numpy as np
import io

st.set_page_config(page_title="AxiomQ | Matriz Global", layout="wide", page_icon="⚡")

# ==========================================
# 1. BANCO DE DADOS INTEGRADO DA SESSÃO
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

if 'frotas' not in st.session_state:
    st.session_state['frotas'] = {
        'gerente@farmaciax.com.br': [
            {"ID_Veiculo": "Moto-01", "Tipo": "Motocicleta", "Capacidade_KG": 100, "Status": "Disponível"},
            {"ID_Veiculo": "Moto-02", "Tipo": "Motocicleta", "Capacidade_KG": 100, "Status": "Disponível"},
            {"ID_Veiculo": "Moto-03", "Tipo": "Motocicleta", "Capacidade_KG": 100, "Status": "Disponível"}
        ]
    }

if 'df_entregas_salvo' not in st.session_state: st.session_state['df_entregas_salvo'] = None
if 'motor_acionado' not in st.session_state: st.session_state['motor_acionado'] = False
if 'registro_entregas' not in st.session_state: st.session_state['registro_entregas'] = {}
if 'rotas_por_veiculo_global' not in st.session_state: st.session_state['rotas_por_veiculo_global'] = {}

if 'logado' not in st.session_state: st.session_state['logado'] = False
if 'user_atual' not in st.session_state: st.session_state['user_atual'] = None

LISTA_MODAIS = ["Carro Leve", "Picape 4x4", "Van", "Caminhão Pesado", "Motocicleta"]

LOGO_HTML = """
<div style="text-align: center; margin-bottom: 20px;">
    <h1 style="font-size: 50px; font-weight: 800; color: white; margin: 0; text-shadow: 0 0 15px #2563eb, 0 0 30px #8b5cf6;">Axiom<span style="color: #2563eb;">Q</span></h1>
    <p style="color: #8b5cf6; font-size: 14px; letter-spacing: 4px; margin: 0;">NÚCLEO DE INTELIGÊNCIA LOGÍSTICA</p>
</div>
"""

# ==========================================
# TELA DE AUTENTICAÇÃO
# ==========================================
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
# AMBIENTE MASTER: ADMINISTRADOR (RESTAURADO COMPLETO)
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
                else:
                    st.warning("E-mail já existe.")

    with aba_parceiros:
        st.subheader("Base de Clientes Ativos")
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
        st.subheader("Editor Dinâmico de Planos")
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
    
    # --- ABA 1: GESTÃO DE FROTA (RESTAURADA E COMPLETA) ---
    with aba_frota_cli:
        st.subheader("Controle de Ativos e Disponibilidade de Veículos")
        col_up_frota, col_lista_frota = st.columns([1, 2])
        
        with col_up_frota:
            st.markdown("### 📥 Carga Inicial de Frota")
            arq_f = st.file_uploader("Upload da Frota (CSV)", type="csv", key="frota_uploader")
            if arq_f:
                if st.button("🔄 Processar e Integrar Planilha", use_container_width=True):
                    df_f_uploaded = pd.read_csv(arq_f)
                    nova_frota = []
                    for _, r in df_f_uploaded.iterrows():
                        tipo_planilha = str(r.get('Tipo', 'Carro Leve'))
                        if tipo_planilha not in LISTA_MODAIS: tipo_planilha = "Carro Leve"
                        nova_frota.append({
                            "ID_Veiculo": str(r.get('ID_Veiculo', f"VEIC-{_}")),
                            "Tipo": tipo_planilha,
                            "Capacidade_KG": int(r.get('Capacidade_KG', 500)),
                            "Status": "Disponível"
                        })
                    st.session_state['frotas'][client_email] = nova_frota
                    st.success(f"✅ Frota integrada com sucesso!")
                    time.sleep(1)
                    st.rerun()
            
            st.markdown("---")
            st.markdown("### ➕ Incluir Veículo Avulso")
            with st.form("add_avulso"):
                id_v = st.text_input("Identificação do Veículo (Prefixo/Placa):")
                tipo_v = st.selectbox("Modal / Tipo:", LISTA_MODAIS)
                cap_v = st.number_input("Capacidade de Carga (KG):", min_value=1, value=500)
                if st.form_submit_button("Adicionar à Frota Ativa", use_container_width=True):
                    if id_v:
                        st.session_state['frotas'][client_email].append({"ID_Veiculo": id_v, "Tipo": tipo_v, "Capacidade_KG": int(cap_v), "Status": "Disponível"})
                        st.success(f"Veículo {id_v} incluído!")
                        time.sleep(0.5)
                        st.rerun()
        
        with col_lista_frota:
            st.markdown("### 📋 Frota Registrada no Sistema")
            frota_atual = st.session_state['frotas'].get(client_email, [])
            
            if frota_atual:
                df_frota_visu = pd.DataFrame(frota_atual)
                st.dataframe(df_frota_visu, use_container_width=True)
                
                # Exportação corrigida para formato brasileiro (; e utf-8)
                csv_data = df_frota_visu.to_csv(index=False, sep=';', encoding='utf-8-sig')
                st.download_button(
                    label="📥 Exportar Frota Atual (Padrão Excel BR)",
                    data=csv_data,
                    file_name="frota_axiomq.csv",
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
                                st.success("Atualizado!")
                                time.sleep(0.5)
                                st.rerun()
            else:
                st.warning("Nenhum veículo cadastrado. Suba uma planilha ou insira um veículo avulso ao lado.")

    # --- ABA 2: ROTEIRIZAR ENTREGAS (MANTENDO O FILTRO DO MAPA E MEMÓRIA DE ENDEREÇOS) ---
    with aba_roteiro_cli:
        st.subheader("Injeção Diária de Pedidos e Roteamento Híbrido")
        col_pedidos, col_mapa_painel = st.columns([1, 2])
        
        with col_pedidos:
            st.markdown("### 📦 Entregas do Dia")
            arq_e = st.file_uploader("Carregar Pontos de Entrega (CSV)", type="csv", key="entregas_uploader")
            
            if arq_e:
                st.session_state['df_entregas_salvo'] = pd.read_csv(arq_e)
                st.success("✅ Planilha real carregada na memória com sucesso!")
            
            df_entregas = st.session_state['df_entregas_salvo']
            veiculos_disponiveis = [v for v in st.session_state['frotas'].get(client_email, []) if v["Status"] == "Disponível"]
            
            if df_entregas is not None:
                st.metric("Entregas Encontradas no Arquivo", len(df_entregas))
                st.metric("Veículos Ativos Prontos", len(veiculos_disponiveis))
                
                if st.button("🚀 Disparar Motor Quântico AxiomQ", use_container_width=True):
                    st.session_state['motor_acionado'] = True
            else:
                st.info("Insira o arquivo 'entregas_25_bh.csv' para iniciar a simulação real.")

        with col_mapa_painel:
            if df_entregas is not None and st.session_state['motor_acionado'] and len(veiculos_disponiveis) > 0:
                try:
                    lat_media = df_entregas['Latitude'].mean()
                    lon_media = df_entregas['Longitude'].mean()
                    
                    st.markdown("### 👁️ Filtro de Isolamento de Frota")
                    opcoes_filtro = ["Mostrar Todos os Veículos"] + [v["ID_Veiculo"] for v in veiculos_disponiveis]
                    veiculos_selecionados = st.multiselect(
                        "Selecione quais veículos deseja visualizar no mapa simultaneamente:",
                        options=opcoes_filtro,
                        default=["Mostrar Todos os Veículos"]
                    )
                    
                    mapa_cliente = folium.Map(location=[lat_media, lon_media], zoom_start=13, tiles="CartoDB dark_matter")
                    folium.Marker([lat_media, lon_media], popup="<b>HUB Central</b>", icon=folium.Icon(color="red", icon="home")).add_to(mapa_cliente)
                    
                    cores_hex = ["#3b82f6", "#a855f7", "#eab308", "#22c55e", "#ec4899", "#f97316", "#14b8a6", "#ef4444"]
                    qtd_v = len(veiculos_disponiveis)
                    
                    df_ordenado = df_entregas.sort_values(by=['Latitude', 'Longitude']).reset_index(drop=True)
                    lista_resumo_kpis = []
                    
                    st.session_state['rotas_por_veiculo_global'] = {}
                    
                    for idx_v, v in enumerate(veiculos_disponiveis):
                        pontos_v = df_ordenado[df_ordenado.index % qtd_v == idx_v].reset_index(drop=True)
                        cor_v = cores_hex[idx_v % len(cores_hex)]
                        
                        st.session_state['rotas_por_veiculo_global'][v["ID_Veiculo"]] = pontos_v
                        
                        deve_exibir = "Mostrar Todos os Veículos" in veiculos_selecionados or v["ID_Veiculo"] in veiculos_selecionados
                        
                        coordenadas_linha = [[lat_media, lon_media]]
                        total_entregas = len(pontos_v)
                        realizadas = 0
                        
                        for idx_p, row in pontos_v.iterrows():
                            chave_status = f"{v['ID_Veiculo']}_{idx_p}"
                            if chave_status not in st.session_state['registro_entregas']:
                                st.session_state['registro_entregas'][chave_status] = "⏳ Em Rota"
                                
                            if st.session_state['registro_entregas'][chave_status] == "✅ Pacote Entregue":
                                realizadas += 1
                                
                            if deve_exibir:
                                folium.CircleMarker(
                                    location=[row['Latitude'], row['Longitude']], radius=5, color=cor_v, fill=True, fill_color=cor_v, fill_opacity=0.8,
                                    popup=f"Parada {idx_p+1}: {row.get('Nome', 'Cliente')}"
                                ).add_to(mapa_cliente)
                            coordenadas_linha.append([row['Latitude'], row['Longitude']])
                        
                        if len(pontos_v) > 0 and deve_exibir:
                            folium.PolyLine(coordenadas_linha, color=cor_v, weight=2.5, opacity=0.7).add_to(mapa_cliente)
                            
                        pct_realizado = round((realizadas / total_entregas) * 100, 1) if total_entregas > 0 else 0.0
                        lista_resumo_kpis.append({
                            "ID do Veículo": v["ID_Veiculo"], "Tipo": v["Tipo"], "Carga Alocada": f"{total_entregas} Pacotes",
                            "Progresso de Campo": f"🟢 {realizadas} de {total_entregas} Concluídas", "Taxa de Sucesso": f"{pct_realizado} %"
                        })
                        
                    components.html(mapa_cliente._repr_html_(), height=420)
                    
                    st.markdown("### 📊 Quadro de Eficiência Operacional (KPIs)")
                    st.table(pd.DataFrame(lista_resumo_kpis))
                    
                    st.markdown("---")
                    st.markdown("### 📋 Auditoria de Manifesto Nominativo Real")
                    v_sel = st.selectbox("Selecione o veículo para auditar o romaneio:", list(st.session_state['rotas_por_veiculo_global'].keys()))
                    
                    if v_sel and v_sel in st.session_state['rotas_por_veiculo_global']:
                        df_paradas = st.session_state['rotas_por_veiculo_global'][v_sel]
                        tabela_gerente = []
                        for idx_p, row in df_paradas.iterrows():
                            chave = f"{v_sel}_{idx_p}"
                            tabela_gerente.append({
                                "Parada": f"{idx_p+1}º",
                                "Cliente/Recebedor": row.get('Nome', f"Cliente #{idx_p+1}"),
                                "Endereço Completo": f"{row.get('Endereço',' Rua')} - {row.get('Bairro','Bairro')}, {row.get('Cidade','Cidade')}",
                                "Status de Campo": st.session_state['registro_entregas'].get(chave, "⏳ Em Rota")
                            })
                        st.dataframe(pd.DataFrame(tabela_gerente), use_container_width=True)
                except Exception as e:
                    st.error(f"Erro no mapa: {e}")
            else:
                st.info("Aguardando acionamento do motor tático.")

# ==========================================
# INTERFACE MOBILE: APP DO CONDUTOR
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
    st.markdown("<div style='border-bottom: 2px solid #8b5cf6; margin-bottom: 15px;'></div>", unsafe_allow_html=True)
    
    v_atual = user_info['veiculo']
    
    if not st.session_state['motor_acionado'] or v_atual not in st.session_state['rotas_por_veiculo_global']:
        st.warning("⏳ Nenhuma rota ativa para este veículo. Aguardando processamento do painel central pelo gestor.")
    else:
        df_rotas_motorista = st.session_state['rotas_por_veiculo_global'][v_atual]
        st.subheader(f"📋 Suas Entregas ({len(df_rotas_motorista)} Paradas)")
        
        for i, row in df_rotas_motorista.iterrows():
            chave_entrega = f"{v_atual}_{i}"
            status_atual = st.session_state['registro_entregas'].get(chave_entrega, "⏳ Em Rota")
            
            with st.container():
                st.markdown(f"### **{i+1}ª Parada**")
                st.markdown(f"👤 **Cliente:** {row.get('Nome', 'Não Informado')}")
                st.markdown(f"📍 {row.get('Endereço', '')} - {row.get('Bairro', '')}, {row.get('Cidade', '')}")
                st.markdown(f"Status Atual: `{status_atual}`")
                
                if status_atual == "⏳ Em Rota":
                    if st.button(f"✓ Confirmar Entrega #{i+1}", key=f"btn_{chave_entrega}", use_container_width=True):
                        st.session_state['registro_entregas'][chave_entrega] = "✅ Pacote Entregue"
                        st.success("Status sincronizado via satélite!")
                        time.sleep(0.4)
                        st.rerun()
                else:
                    st.markdown("<p style='color: #22c55e; font-weight: bold;'>★ Entrega Concluída com Sucesso</p>", unsafe_allow_html=True)
                st.markdown("---")
