import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import folium
import time
import numpy as np
import io

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
                        st.rerun()
        
        with col_lista_frota:
            st.markdown("### 📋 Frota Registrada no Sistema")
            frota_atual = st.session_state['frotas'].get(client_email, [])
            if frota_atual:
                df_frota_visu = pd.DataFrame(frota_atual)
                st.dataframe(df_frota_visu, use_container_width=True)
                
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
            else:
                st.warning("Nenhum veículo cadastrado.")

    # --- ABA 2: ROTEIRIZAR ENTREGAS (VISÃO TÁTICA E NOMINAL) ---
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
                try:
                    lat_media = df_entregas['Latitude'].mean()
                    lon_media = df_entregas['Longitude'].mean()
                    
                    mapa_cliente = folium.Map(location=[lat_media, lon_media], zoom_start=13, tiles="CartoDB dark_matter")
                    folium.Marker([lat_media, lon_media], popup="<b>HUB Central de Distribuição</b>", icon=folium.Icon(color="red", icon="home")).add_to(mapa_cliente)
                    
                    cores_hex = ["#3b82f6", "#a855f7", "#eab308", "#22c55e", "#ec4899", "#f97316", "#14b8a6", "#ef4444"]
                    qtd_v = len(veiculos_disponiveis)
                    
                    lista_resumo_kpis = []
                    romaneio_por_veiculo = {}
                    
                    df_ordenado = df_entregas.sort_values(by=['Latitude', 'Longitude']).reset_index(drop=True)
                    
                    # Bancos de Dados Simulados para impressionar no MVP
                    nomes_simulados = ["João Carlos da Silva", "Clínica Saúde & Vida", "Maria F. Santos", "Pedro Almeida", "Farmácia Preço Certo", "Auto Peças Central", "Drogaria São Paulo", "Sra. Ana Beatriz", "Mercado do Bairro", "Carlos Eduardo (Portaria)"]
                    bairros_simulados = ["Centro", "Savassi", "Lourdes", "Barro Preto", "Funcionários", "Belvedere", "Pampulha", "Venda Nova", "Buritis"]
                    municipio_simulado = "Belo Horizonte / MG"
                    
                    for idx_v, v in enumerate(veiculos_disponiveis):
                        pontos_v = df_ordenado[df_ordenado.index % qtd_v == idx_v].reset_index(drop=True)
                        cor_v = cores_hex[idx_v % len(cores_hex)]
                        
                        romaneio_por_veiculo[v["ID_Veiculo"]] = pontos_v
                        coordenadas_linha = [[lat_media, lon_media]]
                        
                        for _idx, row in pontos_v.iterrows():
                            pos = [row['Latitude'], row['Longitude']]
                            coordenadas_linha.append(pos)
                            
                            folium.CircleMarker(
                                location=pos, radius=5, color=cor_v, fill=True, fill_color=cor_v, fill_opacity=0.8,
                                popup=f"Parada #{_idx+1} | {v['ID_Veiculo']}"
                            ).add_to(mapa_cliente)
                        
                        if len(pontos_v) > 0:
                            folium.PolyLine(coordenadas_linha, color=cor_v, weight=2.5, opacity=0.7).add_to(mapa_cliente)
                        
                        total_entregas = len(pontos_v)
                        realizadas = max(0, int(total_entregas * np.random.uniform(0.5, 0.7))) if total_entregas > 0 else 0
                        pct_realizado = round((realizadas / total_entregas) * 100, 1) if total_entregas > 0 else 0.0
                        
                        distancia_simulada = round(total_entregas * np.random.uniform(2.1, 4.5), 1)
                        ocupacao_simulada = min(100, round((total_entregas * 3.5 / v["Capacidade_KG"]) * 100, 1)) if v["Capacidade_KG"] > 0 else 75.0
                        
                        lista_resumo_kpis.append({
                            "ID do Veículo": v["ID_Veiculo"],
                            "Tipo Modal": v["Tipo"],
                            "Carga Total Alocada": f"{total_entregas} Pacotes",
                            "Progresso de Campo": f"🟢 {realizadas} de {total_entregas} Concluídas",
                            "Taxa de Sucesso (%)": f"{pct_realizado} %",
                            "Distância Total da Rota": f"{distancia_simulada} KM",
                            "Ocupação da Carga": f"{ocupacao_simulada} %"
                        })
                    
                    components.html(mapa_cliente._repr_html_(), height=450)
                    st.success("✅ Central de Comando Ativa! Malha logística sincronizada com a frota.")
                    
                    st.markdown("### 📊 Quadro de Eficiência Operacional (KPIs)")
                    st.table(pd.DataFrame(lista_resumo_kpis))
                    
                    # --- NOVO: ROMANEIO COM NOME DO CLIENTE, BAIRRO E CIDADE ---
                    st.markdown("---")
                    st.markdown("### 📋 Manifesto de Carga nominal (Visão do Condutor)")
                    
                    v_filtro_romaneio = st.selectbox("Selecione o Veículo para Auditar o Manifesto:", [v["ID_Veiculo"] for v in veiculos_disponiveis])
                    
                    if v_filtro_romaneio:
                        df_paradas = romaneio_por_veiculo[v_filtro_romaneio]
                        
                        lista_nomes_finais = []
                        lista_enderecos_finais = []
                        lista_status_finais = []
                        
                        for idx_p, row in df_paradas.iterrows():
                            # Extrai ou simula o Nome do Cliente
                            nome = row.get('Nome') or row.get('Cliente') or row.get('Recebedor')
                            if not nome or pd.isna(nome):
                                nome = nomes_simulados[idx_p % len(nomes_simulados)]
                            lista_nomes_finais.append(nome)
                            
                            # Extrai ou simula a Rua, Bairro e Cidade
                            rua = row.get('Endereço') or row.get('Endereco') or row.get('Rua')
                            bairro = row.get('Bairro')
                            cidade = row.get('Cidade') or row.get('Municipio')
                            
                            if not rua or pd.isna(rua): rua = f"Av. Principal, Nº {int(idx_p * 55 + 10)}"
                            if not bairro or pd.isna(bairro): bairro = bairros_simulados[idx_p % len(bairros_simulados)]
                            if not cidade or pd.isna(cidade): cidade = municipio_simulado
                            
                            endereco_completo = f"{rua} - {bairro}, {cidade}"
                            lista_enderecos_finais.append(endereco_completo)
                            
                            # Progresso da entrega
                            total_desse_v = len(df_paradas)
                            limiar_realizadas = max(0, int(total_desse_v * 0.6))
                            if idx_p < limiar_realizadas:
                                lista_status_finais.append("✅ Pacote Entregue")
                            else:
                                lista_status_finais.append("⏳ Em Rota")
                                
                        df_exibicao_paradas = pd.DataFrame({
                            "Ordem": [f"{i+1}º" for i in range(len(df_paradas))],
                            "Recebedor / Cliente": lista_nomes_finais,
                            "Endereço Completo": lista_enderecos_finais,
                            "Status Operacional": lista_status_finais
                        })
                        st.dataframe(df_exibicao_paradas, use_container_width=True)
                        
                except Exception as e:
                    st.error(f"Erro Crítico na Roteirização: {e}")
            else:
                st.info("Aguardando a injeção do arquivo diário e o acionamento do motor.")
