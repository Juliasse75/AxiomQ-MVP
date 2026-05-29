import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import folium
import time
import numpy as np

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

if 'frotas' not in st.session_state:
    st.session_state['frotas'] = {
        'gerente@farmaciax.com.br': [
            {"ID_Veiculo": "Moto-01", "Tipo": "Motocicleta", "Capacidade_KG": 100, "Status": "Disponível"},
            {"ID_Veiculo": "Moto-02", "Tipo": "Motocicleta", "Capacidade_KG": 100, "Status": "Disponível"},
            {"ID_Veiculo": "Moto-03", "Tipo": "Motocicleta", "Capacidade_KG": 100, "Status": "Disponível"}
        ]
    }

# Memórias de persistência de arquivos para evitar perdas no reload do Streamlit
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

# TELA DE AUTENTICAÇÃO
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
                    st.error("🚨🔒 Acesso Suspenso. Contate o Master.")
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

# PAINEL MASTER DO ADMINISTRADOR
if user_info['perfil'] == 'MASTER':
    st.title(f"👋 Bem-vindo, {user_info['nome']} | Controle Matriz")
    dados_tabela = [{"Login/E-mail": k, "Empresa": v["Empresa"], "CNPJ": v["CNPJ"], "Status": v["Status"]} for k, v in st.session_state['clientes'].items()]
    st.table(pd.DataFrame(dados_tabela))

# PAINEL DO CLIENTE (GERENTE DA FARMÁCIA)
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
            
            if arq_e:
                st.session_state['df_entregas_salvo'] = pd.read_csv(arq_e)
                st.success("Planilha carregada com sucesso na memória de sessão!")
            
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
                    mapa_cliente = folium.Map(location=[lat_media, lon_media], zoom_start=13, tiles="CartoDB dark_matter")
                    
                    folium.Marker([lat_media, lon_media], popup="<b>HUB Central</b>", icon=folium.Icon(color="red", icon="home")).add_to(mapa_cliente)
                    cores_hex = ["#3b82f6", "#a855f7", "#eab308", "#22c55e"]
                    qtd_v = len(veiculos_disponiveis)
                    
                    df_ordenado = df_entregas.sort_values(by=['Latitude', 'Longitude']).reset_index(drop=True)
                    lista_resumo_kpis = []
                    
                    # Limpa as rotas globais antes de recalcular
                    st.session_state['rotas_por_veiculo_global'] = {}
                    
                    for idx_v, v in enumerate(veiculos_disponiveis):
                        pontos_v = df_ordenado[df_ordenado.index % qtd_v == idx_v].reset_index(drop=True)
                        cor_v = cores_hex[idx_v % len(cores_hex)]
                        
                        # Salva na memória global para o condutor ler depois
                        st.session_state['rotas_por_veiculo_global'][v["ID_Veiculo"]] = pontos_v
                        coordenadas_linha = [[lat_media, lon_media]]
                        
                        total_entregas = len(pontos_v)
                        realizadas = 0
                        
                        for idx_p, row in pontos_v.iterrows():
                            chave_status = f"{v['ID_Veiculo']}_{idx_p}"
                            if chave_status not in st.session_state['registro_entregas']:
                                st.session_state['registro_entregas'][chave_status] = "⏳ Em Rota"
                                
                            if st.session_state['registro_entregas'][chave_status] == "✅ Pacote Entregue":
                                realizadas += 1
                                
                            folium.CircleMarker(
                                location=[row['Latitude'], row['Longitude']], radius=5, color=cor_v, fill=True,
                                popup=f"Parada {idx_p+1}: {row.get('Nome', 'Cliente')}"
                            ).add_to(mapa_cliente)
                            coordenadas_linha.append([row['Latitude'], row['Longitude']])
                        
                        if len(pontos_v) > 0:
                            folium.PolyLine(coordenadas_linha, color=cor_v, weight=2.5, opacity=0.7).add_to(mapa_cliente)
                            
                        pct_realizado = round((realizadas / total_entregas) * 100, 1) if total_entregas > 0 else 0.0
                        lista_resumo_kpis.append({
                            "ID do Veículo": v["ID_Veiculo"], "Tipo": v["Tipo"], "Carga Alocada": f"{total_entregas} Pacotes",
                            "Progresso de Campo": f"🟢 {realizadas} de {total_entregas} Concluídas", "Taxa de Sucesso": f"{pct_realizado} %"
                        })
                        
                    components.html(mapa_cliente._repr_html_(), height=420)
                    st.markdown("### 📊 Quadro de Eficiência Operacional (KPIs)")
                    st.table(pd.DataFrame(lista_resumo_kpis))
                    
                    # Manifesto Nominal usando os dados reais da planilha carregada
                    st.markdown("---")
                    st.markdown("### 📋 Auditoria de Manifesto Nominativo Real")
                    v_sel = st.selectbox("Selecione o veículo para auditar:", list(st.session_state['rotas_por_veiculo_global'].keys()))
                    
                    if v_sel and v_sel in st.session_state['rotas_por_veiculo_global']:
                        df_paradas = st.session_state['rotas_por_veiculo_global'][v_sel]
                        tabela_gerente = []
                        for idx_p, row in df_paradas.iterrows():
                            chave = f"{v_sel}_{idx_p}"
                            
                            # Puxa os dados reais da sua planilha de 25 pontos
                            nome_c = row.get('Nome', f"Cliente #{idx_p+1}")
                            rua_c = row.get('Endereço', 'Rua')
                            bairro_c = row.get('Bairro', 'Bairro')
                            cidade_c = row.get('Cidade', 'Cidade')
                            
                            tabela_gerente.append({
                                "Parada": f"{idx_p+1}º",
                                "Cliente/Recebedor": nome_c,
                                "Endereço Completo": f"{rua_c} - {bairro_c}, {cidade_c}",
                                "Status de Campo": st.session_state['registro_entregas'].get(chave, "⏳ Em Rota")
                            })
                        st.dataframe(pd.DataFrame(tabela_gerente), use_container_width=True)
                except Exception as e:
                    st.error(f"Erro no processamento da planilha: {e}")
            else:
                st.info("Aguardando acionamento do motor tático.")

# INTERFACE MOBILE: APP DO CONDUTOR
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
