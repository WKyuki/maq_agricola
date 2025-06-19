# irrigation_system/ui.py

import random
from datetime import datetime, timedelta

# Importações relativas dentro do mesmo pacote
from .database import AgriculturalDatabase
from .intelligence import IrrigationIntelligence


def gerar_dados_historicos(db, id_setor, id_sensor_umidade, id_sensor_ph, id_sensor_fosforo, dias=30):
    """Gera dados históricos simulados para treinamento."""
    print(f"\nGerando dados históricos para o setor {id_setor}...")
    data_inicial = datetime.now() - timedelta(days=dias)
    
    for dia in range(dias):
        for hora in range(24):
            data_atual = data_inicial + timedelta(days=dia, hours=hora)
            str_data = data_atual.strftime("%Y-%m-%d %H:%M:%S")

            umidade = random.uniform(30, 90) - (hora / 2)
            ph = random.uniform(6.0, 7.5)
            fosforo = random.uniform(15, 45)
            
            db.inserir_medicao(f"MED_U_{dia}_{hora}", umidade, str_data, id_sensor_umidade)
            db.inserir_medicao(f"MED_P_{dia}_{hora}", ph, str_data, id_sensor_ph)
            db.inserir_medicao(f"MED_F_{dia}_{hora}", fosforo, str_data, id_sensor_fosforo)

            if umidade < 55 and 5 <= hora <= 8:
                db.inserir_irrigacao(f"IRR_{dia}_{hora}", random.uniform(450.0, 550.0), str_data, id_setor)
    print("Geração de dados históricos concluída!")


class MenuInterativo:
    """Interface de menu interativo para o sistema"""
    
    def __init__(self):
        # --- INÍCIO DA MODIFICAÇÃO ---
        # Define os caminhos padrão em um só lugar para consistência
        db_path = "data/agricultural_system.db"
        model_path = "data/irrigation_model.joblib"

        self.db = AgriculturalDatabase(db_name=db_path)
        self.intelligence = IrrigationIntelligence(db_manager=self.db, model_path=model_path)
    
    def mostrar_menu_principal(self):
        """Mostra o menu principal"""
        print("\n" + "="*50)
        print("SISTEMA DE GERENCIAMENTO AGRÍCOLA")
        print("="*50)
        print("1. Gerenciar Culturas")
        print("2. Gerenciar Setores")
        print("3. Gerenciar Sensores")
        print("4. Gerenciar Medições")
        print("5. Gerenciar Irrigações")
        print("6. Gerenciar Aplicações de Nutrientes")
        print("7. Gerenciar Correções de pH")
        print("8. Relatórios")
        print("9. Inteligência Preditiva")
        print("10. Listar todas as tabelas")
        print("0. Sair")
        print("="*50)

    # ========== MENU CULTURAS ==========
    def menu_culturas(self):
        while True:
            print("\n=== GERENCIAR CULTURAS ===")
            print("1. Inserir Cultura")
            print("2. Listar Culturas")
            print("4. Remover Cultura")
            print("0. Voltar")
            opcao = input("Escolha uma opção: ").strip()
            if opcao == "1": self.inserir_cultura_interativo()
            elif opcao == "2": self.listar_culturas()
            elif opcao == "4": self.remover_cultura_interativo()
            elif opcao == "0": break
            else: print("Opção inválida!")
    
    def inserir_cultura_interativo(self):
        print("\n--- Inserir Nova Cultura ---")
        try:
            id_cultura = input("ID da cultura: ").strip()
            nome_cultura = input("Nome da cultura: ").strip()
            ph_min = float(input("pH mínimo ideal: "))
            ph_max = float(input("pH máximo ideal: "))
            fosforo_min = float(input("Fósforo mínimo ideal: "))
            fosforo_max = float(input("Fósforo máximo ideal: "))
            potassio_min = float(input("Potássio mínimo ideal: "))
            potassio_max = float(input("Potássio máximo ideal: "))
            umidade_min = float(input("Umidade mínima ideal: "))
            umidade_max = float(input("Umidade máxima ideal: "))
            self.db.inserir_cultura(id_cultura, nome_cultura, ph_min, ph_max, fosforo_min, fosforo_max, potassio_min, potassio_max, umidade_min, umidade_max)
        except ValueError: print("Erro: Valores numéricos inválidos!")
    
    def listar_culturas(self):
        print("\n--- Lista de Culturas ---")
        culturas = self.db.consultar_culturas()
        if not culturas: print("Nenhuma cultura encontrada.")
        for c in culturas: print(f"ID: {c['id_cultura']}, Nome: {c['nome_cultura']}, Umidade Ideal: {c['umidade_minima_ideal']}-{c['umidade_maxima_ideal']}%")
    
    def remover_cultura_interativo(self):
        id_cultura = input("\nID da cultura a remover: ").strip()
        if input(f"Tem certeza que deseja remover a cultura {id_cultura}? (s/N): ").lower() == 's':
            self.db.remover_cultura(id_cultura)

    # ========== MENU SETORES ==========
    def menu_setores(self):
        while True:
            print("\n=== GERENCIAR SETORES ===")
            print("1. Inserir Setor")
            print("2. Listar Setores")
            print("3. Remover Setor")
            print("0. Voltar")
            opcao = input("Escolha uma opção: ").strip()
            if opcao == "1": self.inserir_setor_interativo()
            elif opcao == "2": self.listar_setores()
            elif opcao == "3": self.remover_setor_interativo()
            elif opcao == "0": break
            else: print("Opção inválida!")

    def inserir_setor_interativo(self):
        print("\n--- Inserir Novo Setor ---")
        try:
            id_setor = input("ID do setor: ").strip()
            area_setor = float(input("Área do setor (hectares): "))
            id_cultura = input("ID da cultura associada: ").strip()
            self.db.inserir_setor(id_setor, area_setor, id_cultura)
        except ValueError: print("Erro: Área deve ser um número!")

    def listar_setores(self):
        print("\n--- Lista de Setores ---")
        setores = self.db.consultar_setores()
        if not setores: print("Nenhum setor encontrado.")
        for s in setores: print(f"ID: {s['id_setor']}, Área: {s['area_setor']} ha, Cultura: {s.get('nome_cultura', 'N/A')} ({s['id_cultura']})")
    
    def remover_setor_interativo(self):
        id_setor = input("\nID do setor a remover: ").strip()
        if input(f"Tem certeza que deseja remover o setor {id_setor}? (s/N): ").lower() == 's':
            self.db.remover_setor(id_setor)

    # ========== MENU SENSORES ==========
    def menu_sensores(self):
        while True:
            print("\n=== GERENCIAR SENSORES ===")
            print("1. Inserir Sensor")
            print("2. Listar Sensores")
            print("3. Remover Sensor")
            print("0. Voltar")
            opcao = input("Escolha uma opção: ").strip()
            if opcao == "1": self.inserir_sensor_interativo()
            elif opcao == "2": self.listar_sensores()
            elif opcao == "3": self.remover_sensor_interativo()
            elif opcao == "0": break
            else: print("Opção inválida!")
    
    def inserir_sensor_interativo(self):
        print("\n--- Inserir Novo Sensor ---")
        id_sensor = input("ID do sensor: ").strip()
        # Padroniza o tipo de sensor para minúsculas para consistência com o modelo de IA
        tipo_sensor = input("Tipo do sensor (ex: umidade, ph, fosforo): ").strip().lower()
        id_setor = input("ID do setor onde está instalado: ").strip()
        self.db.inserir_sensor(id_sensor, tipo_sensor, id_setor)
    
    def listar_sensores(self):
        print("\n--- Lista de Sensores ---")
        sensores = self.db.consultar_sensores()
        if not sensores: print("Nenhum sensor encontrado.")
        for s in sensores: print(f"ID: {s['id_sensor']}, Tipo: {s['tipo_sensor']}, Setor: {s['id_setor']}")

    def remover_sensor_interativo(self):
        id_sensor = input("\nID do sensor a remover: ").strip()
        if input(f"Tem certeza que deseja remover o sensor {id_sensor}? (s/N): ").lower() == 's':
            self.db.remover_sensor(id_sensor)

    # ========== MENU MEDIÇÕES ==========
    def menu_medicoes(self):
        while True:
            print("\n=== GERENCIAR MEDIÇÕES ===")
            print("1. Inserir Medição")
            print("2. Listar Medições")
            print("3. Remover Medição")
            print("0. Voltar")
            opcao = input("Escolha uma opção: ").strip()
            if opcao == "1": self.inserir_medicao_interativo()
            elif opcao == "2": self.listar_medicoes()
            elif opcao == "3": self.remover_medicao_interativo()
            elif opcao == "0": break
            else: print("Opção inválida!")

    def inserir_medicao_interativo(self):
        print("\n--- Inserir Nova Medição ---")
        try:
            id_medicao = input("ID da medição: ").strip()
            valor_medicao = float(input("Valor medido: "))
            data_medicao = input(f"Data e hora (YYYY-MM-DD HH:MM:SS) [Enter para agora]: ").strip()
            if not data_medicao: data_medicao = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            id_sensor = input("ID do sensor que fez a medição: ").strip()
            self.db.inserir_medicao(id_medicao, valor_medicao, data_medicao, id_sensor)
        except ValueError: print("Erro: Valor da medição deve ser um número!")

    def listar_medicoes(self):
        print("\n--- Lista de Medições Recentes ---")
        medicoes = self.db.consultar_medicoes()
        if not medicoes: print("Nenhuma medição encontrada.")
        # Mostra as últimas 10 medições
        for m in sorted(medicoes, key=lambda i: i['data_medicao'], reverse=True)[:10]:
            print(f"ID: {m['id_medicao']}, Sensor: {m['id_sensor']} ({m['tipo_sensor']}), Valor: {m['valor_medicao']}, Data: {m['data_medicao']}")
            
    def remover_medicao_interativo(self):
        id_medicao = input("\nID da medição a remover: ").strip()
        if input(f"Tem certeza que deseja remover a medição {id_medicao}? (s/N): ").lower() == 's':
            self.db.remover_medicao(id_medicao)

    # ========== MENU IRRIGAÇÕES ==========
    def menu_irrigacoes(self):
        while True:
            print("\n=== GERENCIAR IRRIGAÇÕES ===")
            print("1. Registrar Irrigação")
            print("2. Listar Irrigações")
            print("0. Voltar")
            opcao = input("Escolha uma opção: ").strip()
            if opcao == "1": self.inserir_irrigacao_interativo()
            elif opcao == "2": self.listar_irrigacoes()
            elif opcao == "0": break
            else: print("Opção inválida!")

    def inserir_irrigacao_interativo(self):
        print("\n--- Registrar Nova Irrigação ---")
        try:
            id_irrigacao = input("ID da irrigação: ").strip()
            volume = float(input("Volume de água (litros): "))
            data = input(f"Data e hora (YYYY-MM-DD HH:MM:SS) [Enter para agora]: ").strip()
            if not data: data = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            id_setor = input("ID do setor irrigado: ").strip()
            self.db.inserir_irrigacao(id_irrigacao, volume, data, id_setor)
        except ValueError: print("Erro: Volume deve ser um número!")
    
    def listar_irrigacoes(self):
        print("\n--- Histórico de Irrigações ---")
        irrigacoes = self.db.consultar_irrigacoes()
        if not irrigacoes: print("Nenhuma irrigação registrada.")
        for i in sorted(irrigacoes, key=lambda item: item['data_irrigacao'], reverse=True):
            print(f"ID: {i['id_irrigacao']}, Setor: {i['id_setor']}, Volume: {i['volume_irrigacao']}L, Data: {i['data_irrigacao']}")

    # ========== MENU NUTRIENTES E PH ==========
    def menu_aplicacoes_nutrientes(self):
        print("Menu de Aplicações de Nutrientes - Implementação similar a Irrigações.")

    def menu_correcoes_ph(self):
        print("Menu de Correções de pH - Implementação similar a Irrigações.")
        
    # ========== MENU RELATÓRIOS ==========
    def menu_relatorios(self):
        while True:
            print("\n=== RELATÓRIOS ===")
            print("1. Relatório Detalhado de Setor")
            print("0. Voltar")
            opcao = input("Escolha uma opção: ").strip()
            if opcao == "1":
                id_setor = input("Digite o ID do setor: ").strip()
                relatorio = self.db.obter_relatorio_setor(id_setor)
                if not relatorio or not relatorio['setor']:
                    print("Setor não encontrado ou sem dados.")
                    continue
                
                print("\n" + "-"*20 + f" RELATÓRIO DO SETOR {id_setor} " + "-"*20)
                print(f"Informações do Setor: {relatorio['setor']}")
                print("\nSensores no Setor:")
                for s in relatorio['sensores']: print(f"  - ID: {s[0]}, Tipo: {s[1]}")
                print("\nMedições Recentes:")
                for m in relatorio['medicoes_recentes']: print(f"  - {m[2]}: Sensor {m[3]} ({m[4]}) - Valor {m[1]}")
                print("\nIrrigações Recentes:")
                for i in relatorio['irrigacoes_recentes']: print(f"  - {i[2]}: Volume {i[1]}L")
                print("-"*62)

            elif opcao == "0": break
            else: print("Opção inválida!")
            
    # ========== MENU INTELIGÊNCIA PREDITIVA ==========
    def menu_inteligencia(self):
        while True:
            print("\n=== INTELIGÊNCIA PREDITIVA ===")
            print("1. Treinar/Retreinar modelo de irrigação")
            print("2. Obter sugestão de irrigação")
            print("3. Gerar dados históricos de exemplo")
            print("0. Voltar")
            opcao = input("Escolha uma opção: ").strip()
            if opcao == "1":
                id_setor = input("Digite o ID do setor para treinar o modelo: ").strip()
                self.intelligence.train_model(id_setor)
            elif opcao == "2": self.obter_sugestao_irrigacao()
            elif opcao == "3":
                id_setor = input("Digite o ID do setor para gerar dados: ").strip()
                id_sensor_umidade = input("Digite o ID do sensor de 'umidade': ").strip()
                id_sensor_ph = input("Digite o ID do sensor de 'ph': ").strip()
                id_sensor_fosforo = input("Digite o ID do sensor de 'fosforo': ").strip()
                gerar_dados_historicos(self.db, id_setor, id_sensor_umidade, id_sensor_ph, id_sensor_fosforo)
            elif opcao == "0": break
            else: print("Opção inválida!")

    def obter_sugestao_irrigacao(self):
        print("\n--- Obter Sugestão de Irrigação ---")
        if not self.intelligence.model:
            print("ERRO: O modelo ainda não foi treinado. Use a opção 'Treinar modelo' primeiro.")
            return

        try:
            id_setor = input("Digite o ID do setor para a previsão: ").strip()
            print("Por favor, insira os valores atuais dos sensores:")
            
            current_data = {}
            for feature in self.intelligence.feature_names:
                if feature.lower() not in ['hora_do_dia', 'dia_da_semana']:
                    value = float(input(f"  - Valor para {feature}: "))
                    current_data[feature] = value
            
            prediction_time = datetime.now() + timedelta(hours=1)
            
            acao, prob = self.intelligence.predict_action(id_setor, current_data, prediction_time)
            
            print("\n--- Resultado da Previsão ---")
            print(acao)
            print(f"Probabilidade de necessidade de irrigação: {prob*100:.2f}%")
        except (ValueError, TypeError):
            print("Erro: Valor numérico inválido inserido ou dados de entrada incorretos.")
        except Exception as e:
            print(f"Ocorreu um erro: {e}")
    
    # ========== MÉTODO PRINCIPAL DE EXECUÇÃO ==========
    def executar(self):
        while True:
            self.mostrar_menu_principal()
            opcao = input("Escolha uma opção: ").strip()
            
            if opcao == "1": self.menu_culturas()
            elif opcao == "2": self.menu_setores()
            elif opcao == "3": self.menu_sensores()
            elif opcao == "4": self.menu_medicoes()
            elif opcao == "5": self.menu_irrigacoes()
            elif opcao == "6": self.menu_aplicacoes_nutrientes()
            elif opcao == "7": self.menu_correcoes_ph()
            elif opcao == "8": self.menu_relatorios()
            elif opcao == "9": self.menu_inteligencia()
            elif opcao == "10": self.db.listar_todas_tabelas()
            elif opcao == "0":
                print("Encerrando sistema...")
                self.db.disconnect()
                break
            else:
                print("Opção inválida!")