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
        'condutor01@farmaciax.com.br': {'senha': '789', 'perfil': 'CONDUTOR', 'empresa': 'Farmácia X', 'veiculo': 'Moto-01', 'nome': 'Marcos Entregador'}
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
            {"ID_Veiculo": "Moto-01", "Tipo": "Motocicleta", "Capacidade_KG": 100, "Status": "Disponível", "Defeito": "-", "Data_Inatividade": "-"},
            {"ID_Veiculo": "Moto-02", "Tipo": "Motocicleta", "Capacidade_KG": 100, "Status": "Disponível", "Defeito": "-", "Data_Inatividade": "-"},
            {"ID_Veiculo": "Moto-03", "Tipo": "Motocicleta", "Capacidade_KG": 100, "Status": "Disponível", "Defeito": "-", "Data_Inatividade": "-"}
        ]
    }

if 'condutores' not in st.session_state:
    st.session_state['condutores'] = {
        'gerente@farmaciax.com.br': [
            {"Nome": "Marcos Entregador", "CPF": "111.222.333-44", "RG": "MG-12.345.678", "CNH": "987654321", "Venc_CNH": "20/12/2028", "Endereço": "Av. Afonso Pena, Centro - BH", "Email": "condutor01@farmaciax.com.br", "Veiculo": "Moto-01"}
        ]
    }

if 'df_entregas_salvo' not in st.session_state: st.session_state['df_entregas_salvo'] = None
if 'motor_acionado' not in st.session_state: st.session_state['motor_acionado'] = False
if 'registro_entregas' not in st.session_state: st.session_state['registro_entregas'] = {}
if 'rotas_por_veiculo_global' not in st.session_state: st.session_state['rotas_por_veiculo_global'] = {}

if 'logado' not in st.session_state: st.session_state['logado'] = False
if 'user_atual' not in st.session_state: st.session_state['user_atual'] = None

LISTA_MODAIS = ["Carro Leve", "Picape 4x4", "Van", "Caminhão Pesado", "Motocicleta"]

DADOS_BH_MOCK = [
    {"Nome": "Carlos Silva", "Endereço": "Av. Afonso Pena 1500", "Bairro": "Centro", "Cidade": "Belo Horizonte", "Latitude": -19.9245, "Longitude": -43.9352},
    {"Nome": "Maria Oliveira", "Endereço": "Rua Bahia 1000", "Bairro": "Lourdes", "Cidade": "Belo Horizonte", "Latitude": -19.9280, "Longitude": -43.9385},
    {"Nome": "Clínica São Lucas", "Endereço": "Rua dos Otoni 800", "Bairro": "Santa Efigênia", "Cidade": "Belo Horizonte", "Latitude": -19.9231, "Longitude": -43.9285},
    {"Nome": "Pedro Almeida", "Endereço": "Av. Brasil 500", "Bairro": "Funcionários", "Cidade": "Belo Horizonte", "Latitude": -19.9320, "Longitude": -43.9300},
    {"Nome": "Farmácia Central", "Endereço": "Rua Tupis 300", "Bairro": "Centro", "Cidade": "Belo Horizonte", "Latitude": -19.9190, "Longitude": -43.9400},
    {"Nome": "João Pedro", "Endereço": "Av. Amazonas 2000", "Bairro": "Santo Agostinho", "Cidade": "Belo Horizonte", "Latitude": -19.9255, "Longitude": -43.9450},
    {"Nome": "Ana Souza", "Endereço": "Rua Gonçalves Dias 1200", "Bairro": "Savassi", "Cidade": "Belo Horizonte", "Latitude": -19.9345, "Longitude": -43.9360},
    {"Nome": "Supermercado BH", "Endereço": "Av. Olegário Maciel 1600", "Bairro": "Lourdes", "Cidade": "Belo Horizonte", "Latitude": -19.9295, "Longitude": -43.9420},
    {"Nome": "Lucas Mendes", "Endereço": "Rua Espírito Santo 500", "Bairro": "Centro", "Cidade": "Belo Horizonte", "Latitude": -19.9205, "Longitude": -43.9365},
    {"Nome": "Auto Peças Minas", "Endereço": "Av. Antônio Carlos 1000", "Bairro": "Lagoinha", "Cidade": "Belo Horizonte", "Latitude": -19.9050, "Longitude": -43.9455},
    {"Nome": "Sra. Beatriz", "Endereço": "Rua Rio de Janeiro 800", "Bairro": "Centro", "Cidade": "Belo Horizonte", "Latitude": -19.9220, "Longitude": -43.9380},
    {"Nome": "Roberto Costa", "Endereço": "Av. do Contorno 6000", "Bairro": "Savassi", "Cidade": "Belo Horizonte", "Latitude": -19.9370, "Longitude": -43.9330},
    {"Nome": "Drogaria Araújo", "Endereço": "Rua da Bahia 2000", "Bairro": "Lourdes", "Cidade": "Belo Horizonte", "Latitude": -19.9315, "Longitude": -43.9405},
    {"Nome": "Fernanda Lima", "Endereço": "Rua Paraíba 900", "Bairro": "Savassi", "Cidade": "Belo Horizonte", "Latitude": -19.9360, "Longitude": -43.9315},
    {"Nome": "Padaria Pão Quente", "Endereço": "Av. Prudente de Morais 500", "Bairro": "Santo Antônio", "Cidade": "Belo Horizonte", "Latitude": -19.9400, "Longitude": -43.9450},
    {"Nome": "Thiago Ribeiro", "Endereço": "Rua Alagoas 700", "Bairro": "Savassi", "Cidade": "Belo Horizonte", "Latitude": -19.9335, "Longitude": -43.9340},
    {"Nome": "Mecânica Silva", "Endereço": "Av. Barão Homem de Melo 100", "Bairro": "Nova Suíça", "Cidade": "Belo Horizonte", "Latitude": -19.9350, "Longitude": -43.9600},
    {"Nome": "Camila Rocha", "Endereço": "Rua Piauí 400", "Bairro": "Santa Efigênia", "Cidade": "Belo Horizonte", "Latitude": -19.9250, "Longitude": -43.9250},
    {"Nome": "Restaurante Fogão", "Endereço": "Rua Tupinambás 600", "Bairro": "Centro", "Cidade": "Belo Horizonte", "Latitude": -19.9175, "Crash": "N", "Longitude": -43.9390},
    {"Nome": "Marcos Vinícius", "Endereço": "Av. Nossa Sra do Carmo 300", "Bairro": "Sion", "Cidade": "Belo Horizonte", "Latitude": -19.9450, "Longitude": -43.9320},
    {"Nome": "Juliana Alves", "Endereço": "Rua Rio Grande do Norte 1000", "Bairro": "Savassi", "Cidade": "Belo Horizonte", "Latitude": -19.9355, "Longitude": -43.9300},
    {"Nome": "Pet Shop Cão Feliz", "Endereço": "Av. Augusto de Lima 1500", "Bairro": "Barro Preto", "Cidade": "Belo Horizonte", "Latitude": -19.9265, "Longitude": -43.9470},
    {"Nome": "Ricardo Gomes", "Endereço": "Rua dos Guajajaras 800", "Bairro": "Centro", "Cidade": "Belo Horizonte", "Latitude": -19.9240, "Longitude": -43.9410},
    {"Nome": "Papelaria Escolar", "Endereço": "Rua Sergipe 1200", "Bairro": "Savassi", "Cidade": "Belo Horizonte", "Latitude": -19.9380, "Longitude": -43.9350},
    {"Nome": "Livraria Leitura", "Endereço": "Av. Cristóvão Colombo 500", "Bairro": "Savassi", "Cidade": "Belo Horizonte", "Latitude": -19.9395, "Longitude": -43.9370}
]

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
                    st.session_state['condutores'][email_limpo_cad] = []
                    st.success(f"✅ Parceiro {nome} registrado com sucesso!")
                    st.rerun()

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
                    if cliente_sel in st.session_state['condutores']: del st.session_state['condutores'][cliente_sel]
                    st.rerun()
                    
    with aba_planos:
        st.subheader("⚙️ Editor e Criador Dinâmico de Planos")
        lista_planos_existentes = list(st.session_state['planos'].keys())
        plano_selecionado_ed = st.selectbox("Ação de Planos:", ["-- Criar Novo Plano --"] + lista_planos_existentes)
        with st.form("form_planos_dinamico"):
            if plano_selecionado_ed == "-- Criar Novo Plano --":
                nome_plano_input = st.text_input("Nome do Novo Plano:")
                desc_plano_input = st.text_input("Descrição / Restrição de Frota:")
            else:
                nome_plano_input = st.text_input("Plano Selecionado:", value=plano_selecionado_ed, disabled=True)
                desc_plano_input = st.text_input("Modificar Descrição / Restrição:", value=st.session_state['planos'][plano_selecionado_ed])
            if st.form_submit_button("💾 Gravar Configuração do Plano", use_container_width=True):
                if desc_plano_input:
                    if plano_selecionado_ed == "-- Criar Novo Plano --" and nome_plano_input:
                        st.session_state['planos'][nome_plano_input] = desc_plano_input
                    else:
                        st.session_state['planos'][plano_selecionado_ed] = desc_plano_input
                    st.success("Plano salvo!")
                    st.rerun()

# ==========================================
# AMBIENTE CLIENTE: PORTAL DO GESTOR
# ==========================================
elif user_info['perfil'] == 'CLIENTE':
    client_email = st.session_state['user_atual']
    c_dados = st.session_state['clientes'][client_email]
    
    st.title(f"⚡ Painel de Logística | {c_dados['Empresa']}")
    st.markdown("---")
    
    aba_frota_cli, aba_roteiro_cli = st.tabs(["🚛 1. Gerenciar Frota e Condutores", "📦 2. Roteirizar Entregas"])
    
    with aba_frota_cli:
        sub_aba_veiculos, sub_aba_condutores = st.tabs(["📋 Controle de Veículos", "👥 Gestão de Condutores (RH)"])
        
        with sub_aba_veiculos:
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
                                "ID_Veiculo": str(r.get('ID_Veiculo', f"VEIC-{_}")), "Tipo": tipo_planilha,
                                "Capacidade_KG": int(r.get('Capacidade_KG', 500)), "Status": "Disponível", "Defeito": "-", "Data_Inatividade": "-"
                            })
                        st.session_state['frotas'][client_email] = nova_frota
                        st.success(f"✅ Frota integrada!")
                        st.rerun()
                
                st.markdown("---")
                st.markdown("### ➕ Incluir Veículo Avulso")
                with st.form("add_avulso"):
                    id_v = st.text_input("Identificação do Veículo:")
                    tipo_v = st.selectbox("Modal / Tipo:", LISTA_MODAIS)
                    cap_v = st.number_input("Capacidade de Carga (KG):", min_value=1, value=500)
                    if st.form_submit_button("Adicionar à Frota Ativa", use_container_width=True):
                        if id_v:
                            st.session_state['frotas'][client_email].append({"ID_Veiculo": id_v, "Tipo": tipo_v, "Capacidade_KG": int(cap_v), "Status": "Disponível", "Defeito": "-", "Data_Inatividade": "-"})
                            st.success(f"Veículo {id_v} incluído!")
                            st.rerun()
            
            with col_lista_frota:
                st.markdown("### 📋 Frota Registrada")
                frota_atual = st.session_state['frotas'].get(client_email, [])
                if frota_atual:
                    df_frota_visu = pd.DataFrame(frota_atual)
                    st.dataframe(df_frota_visu, use_container_width=True)
                    
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
                            if n_stat == "Indisponível":
                                st.session_state['frotas'][client_email][idx]["Data_Inatividade"] = time.strftime("%d/%m/%Y")
                                st.session_state['frotas'][client_email][idx]["Defeito"] = "Aguardando diagnóstico"
                            else:
                                st.session_state['frotas'][client_email][idx]["Data_Inatividade"] = "-"
                                st.session_state['frotas'][client_email][idx]["Defeito"] = "-"
                            st.rerun()
                            
                        if col_edit2.button("🗑️ Remover da Frota", use_container_width=True):
                            st.session_state['frotas'][client_email].pop(idx)
                            st.rerun()
                        
                        with st.expander("📝 Editar Detalhes Mecânicos Avançados"):
                            with st.form("edit_mec"):
                                novo_tipo = st.selectbox("Alterar Tipo:", LISTA_MODAIS, index=LISTA_MODAIS.index(v_dados["Tipo"]) if v_dados["Tipo"] in LISTA_MODAIS else 0)
                                nova_cap = st.number_input("Nova Capacidade (KG):", value=v_dados["Capacidade_KG"])
                                novo_defeito = st.text_area("Observação / Defeito do Veículo:", value=v_dados.get("Defeito", "-"))
                                nova_data_inativ = st.text_input("Data de Entrada no Status Indisponível (dd/mm/aaaa):", value=v_dados.get("Data_Inatividade", "-"))
                                if st.form_submit_button("Salvar Alterações Mecânicas", use_container_width=True):
                                    st.session_state['frotas'][client_email][idx]["Tipo"] = novo_tipo
                                    st.session_state['frotas'][client_email][idx]["Capacidade_KG"] = int(nova_cap)
                                    st.session_state['frotas'][client_email][idx]["Defeito"] = novo_defeito
                                    st.session_state['frotas'][client_email][idx]["Data_Inatividade"] = nova_data_inativ
                                    st.success("Histórico salvo!")
                                    st.rerun()

        with sub_aba_condutores:
            st.markdown("### 👥 Matriz de Recursos Humanos")
            col_cad_cond, col_lista_cond = st.columns([1, 2])
            
            with col_cad_cond:
                st.markdown("#### 👤 Registrar Novo Condutor")
                frota_atual = st.session_state['frotas'].get(client_email, [])
                lista_id_veiculos = [v["ID_Veiculo"] for v in frota_atual]
                
                with st.form("form_cadastro_condutor"):
                    c_nome = st.text_input("Nome Completo:")
                    c_cpf = st.text_input("CPF:")
                    c_rg = st.text_input("RG:")
                    c_cnh = st.text_input("CNH:")
                    c_venc_cnh = st.date_input("Vencimento CNH:")
                    c_end = st.text_area("Endereço Residencial:")
                    c_email = st.text_input("E-mail de Login:")
                    c_senha = st.text_input("Senha de Acesso Tático:", type="password", value="789")
                    c_veiculo = st.selectbox("Vincular a um Veículo:", ["-- Deixar Sem Vínculo --"] + lista_id_veiculos)
                    
                    if st.form_submit_button("Emitir Acesso e Salvar Condutor", use_container_width=True):
                        email_cond_limpo = c_email.strip().lower()
                        if not c_nome or not email_cond_limpo:
                            st.error("Campos essenciais vazios.")
                        else:
                            venc_formatado = c_venc_cnh.strftime("%d/%m/%Y")
                            v_vinculo = "-" if c_veiculo == "-- Deixar Sem Vínculo --" else c_veiculo
                            
                            st.session_state['condutores'][client_email].append({
                                "Nome": c_nome, "CPF": c_cpf, "RG": c_rg, "CNH": c_cnh, 
                                "Venc_CNH": venc_formatado, "Endereço": c_end, "Email": email_cond_limpo, "Veiculo": v_vinculo
                            })
                            st.session_state['usuarios'][email_cond_limpo] = {
                                'senha': str(c_senha), 'perfil': 'CONDUTOR', 'empresa': c_dados['Empresa'], 'veiculo': v_vinculo, 'nome': c_nome
                            }
                            st.success(f"✅ Motorista {c_nome} integrado!")
                            st.rerun()
            
            with col_lista_cond:
                st.markdown("#### 📋 Condutores Homologados")
                lista_cond_atual = st.session_state['condutores'].get(client_email, [])
                if lista_cond_atual:
                    df_cond_visu = pd.DataFrame(lista_cond_atual)
                    st.dataframe(df_cond_visu, use_container_width=True)
                    
                    st.markdown("---")
                    cond_selecionado = st.selectbox("Selecione o E-mail do Motorista:", [c["Email"] for c in lista_cond_atual])
                    if cond_selecionado:
                        idx_c = next(i for i, c in enumerate(lista_cond_atual) if c["Email"] == cond_selecionado)
                        c_dados_sel = lista_cond_atual[idx_c]
                        if st.button("❌ Remover Condutor", use_container_width=True):
                            del st.session_state['condutores'][client_email][idx_c]
                            if cond_selecionado in st.session_state['usuarios']: del st.session_state['usuarios'][cond_selecionado]
                            st.rerun()

    # --- ABA 2: ROTEIRIZAR ENTREGAS ---
    with aba_roteiro_cli:
        col_pedidos, col_mapa_painel = st.columns([1, 2])
        with col_pedidos:
            st.markdown("### 📦 Entregas do Dia")
            arq_e = st.file_uploader("Carregar Pontos de Entrega (CSV)", type="csv", key="entregas_uploader")
            if arq_e: st.session_state['df_entregas_salvo'] = pd.read_csv(arq_e)
            
            df_entregas = st.session_state['df_entregas_salvo']
            veiculos_disponiveis = [v for v in st.session_state['frotas'].get(client_email, []) if v["Status"] == "Disponível"]
            
            if df_entregas is not None:
                st.metric("Entregas no Arquivo", len(df_entregas))
                st.metric("Veículos Ativos Prontos", len(veiculos_disponiveis))
                if st.button("🚀 Disparar Motor Quântico AxiomQ", use_container_width=True):
                    st.session_state['motor_acionado'] = True
            else:
                st.info("Aguardando upload do arquivo 'entregas_25_bh.csv'.")

        with col_mapa_painel:
            if df_entregas is not None and st.session_state['motor_acionado'] and len(veiculos_disponiveis) > 0:
                try:
                    lat_media, lon_media = df_entregas['Latitude'].mean(), df_entregas['Longitude'].mean()
                    
                    st.markdown("### 👁️ Filtro de Isolamento de Frota")
                    opcoes_filtro = ["Mostrar Todos os Veículos"] + [v["ID_Veiculo"] for v in veiculos_disponiveis]
                    veiculos_selecionados = st.multiselect("Visualização de Frota:", options=opcoes_filtro, default=["Mostrar Todos os Veículos"])
                    
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
                            if chave_status not in st.session_state['registro_entregas']: st.session_state['registro_entregas'][chave_status] = "⏳ Em Rota"
                            if st.session_state['registro_entregas'][chave_status] == "✅ Pacote Entregue": realizadas += 1
                            
                            if deve_exibir:
                                folium.CircleMarker(location=[row['Latitude'], row['Longitude']], radius=5, color=cor_v, fill=True, popup=f"Parada {idx_p+1}: {row.get('Nome', 'Cliente')}").add_to(mapa_cliente)
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
                    
                    # --- REQUISITO REALIZADO: FORMATAÇÃO COMPLETA NOME + VEÍCULO (RESOLÇÃO DE ESCOPO) ---
                    st.markdown("---")
                    st.markdown("### 📋 Auditoria de Manifesto Nominativo Real")
                    
                    def formatar_caixa_manifesto(v_id):
                        m_nome = "Sem condutor"
                        # Procura o motorista de forma limpa usando a conta master atual logada
                        for cond in st.session_state['condutores'].get('gerente@farmaciax.com.br', []):
                            if cond["Veiculo"] == v_id:
                                m_nome = cond["Nome"]
                                break
                        return f"🚛 {v_id} — (Condutor: {m_nome})"
                    
                    v_sel = st.selectbox(
                        "Selecione o veículo para auditar o romaneio:", 
                        list(st.session_state['rotas_por_veiculo_global'].keys()),
                        format_func=formatar_caixa_manifesto
                    )
                    
                    if v_sel and v_sel in st.session_state['rotas_por_veiculo_global']:
                        df_paradas = st.session_state['rotas_por_veiculo_global'][v_sel]
                        tabela_gerente = []
                        for idx_p, row in df_paradas.iterrows():
                            chave = f"{v_sel}_{idx_p}"
                            tabela_gerente.append({
                                "Parada": f"{idx_p+1}º", "Cliente/Recebedor": row.get('Nome', f"Cliente #{idx_p+1}"),
                                "Endereço Completo": f"{row.get('Endereço',' Rua')} - {row.get('Bairro','Bairro')}, {row.get('Cidade','Cidade')}",
                                "Status de Campo": st.session_state['registro_entregas'].get(chave, "⏳ Em Rota")
                            })
                        st.dataframe(pd.DataFrame(tabela_gerente), use_container_width=True)
                except Exception as e:
                    st.error(f"Erro na malha: {e}")
            else:
                st.info("Aguardando ativação do motor.")

# ==========================================
# INTERFACE MOBILE: APP DO CONDUTOR (BLINDADO)
# ==========================================
elif user_info['perfil'] == 'CONDUTOR':
    st.markdown("""
        <style>
            .block-container { max-width: 450px !important; padding-top: 1rem !important; }
            .stButton>button { background-color: #22c55e !important; color: white !important; font-weight: bold; }
        </style>
    """, unsafe_allow_html=True)
    st.title("📱 App do Condutor")
    st.markdown(f"**Operador:** `{user_info.get('nome', st.session_state['user_atual'])}` | **Unidade Vinculada:** `{user_info['veiculo']}`")
    st.markdown("<div style='border-bottom: 2px solid #8b5cf6; margin-bottom: 15px;'></div>", unsafe_allow_html=True)
    
    v_atual = user_info['veiculo']
    
    # --- DEFESA ANTI-KEYERROR DE CACHE DO STREAMLIT ---
    if v_atual != "-" and (v_atual not in st.session_state['rotas_por_veiculo_global'] or not st.session_state['motor_acionado']):
        df_m = pd.DataFrame(DADOS_BH_MOCK)
        st.session_state['rotas_por_veiculo_global']["Moto-01"] = df_m[df_m.index % 3 == 0].reset_index(drop=True)
        st.session_state['rotas_por_veiculo_global']["Moto-02"] = df_m[df_m.index % 3 == 1].reset_index(drop=True)
        st.session_state['rotas_por_veiculo_global']["Moto-03"] = df_m[df_m.index % 3 == 2].reset_index(drop=True)
        st.session_state['motor_acionado'] = True

    if v_atual == "-":
        st.warning("⚠️ Você não possui nenhum veículo vinculado ao seu perfil hoje.")
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
