import sqlite3
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import os # Garanta que 'os' está importado no topo do arquivo

class AgriculturalDatabase:
    def __init__(self, db_name: str = "data/agricultural_system.db"):
        """
        Inicializa o banco de dados agrícola
        """
        self.db_name = db_name
        self.connection = None
        self.cursor = None

        # --- INÍCIO DA MODIFICAÇÃO ---
        # Garante que o diretório do banco de dados exista antes de conectar.
        db_dir = os.path.dirname(self.db_name)
        if db_dir and not os.path.exists(db_dir):
            print(f"Diretório '{db_dir}' não encontrado. Criando...")
            os.makedirs(db_dir)
        # --- FIM DA MODIFICAÇÃO ---
        
        self.connect()
        # Apenas crie tabelas se a conexão for bem-sucedida
        if self.connection:
            self.create_tables()
    
    def connect(self):
        """Conecta ao banco de dados SQLite"""
        try:
            self.connection = sqlite3.connect(self.db_name)
            self.cursor = self.connection.cursor()
            print(f"Conectado ao banco de dados: {self.db_name}")
        except sqlite3.Error as e:
            print(f"Erro ao conectar ao banco de dados: {e}")
            # Importante: garantir que fiquem como None se a conexão falhar
            self.connection = None
            self.cursor = None
    
    def disconnect(self):
        """Desconecta do banco de dados"""
        if self.connection:
            self.connection.close()
            print("Desconectado do banco de dados")
    
    def create_tables(self):
        """Cria todas as tabelas do sistema"""
        try:
            # Tabela Sensores
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS TABELA_SENSORES (
                    id_sensor VARCHAR(10) PRIMARY KEY,
                    tipo_sensor VARCHAR(10),
                    id_setor VARCHAR(10)
                )
            ''')
            
            # Tabela Setores
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS TABELA_SETORES (
                    id_setor VARCHAR(10) PRIMARY KEY,
                    area_setor DECIMAL(9,2),
                    id_cultura VARCHAR(10)
                )
            ''')
            
            # Tabela Culturas
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS TABELA_CULTURAS (
                    id_cultura VARCHAR(10) PRIMARY KEY,
                    nome_cultura VARCHAR(50),
                    ph_minimo_ideal DECIMAL(10,5),
                    ph_maximo_ideal DECIMAL(10,5),
                    fosforo_minimo_ideal DECIMAL(10,5),
                    fosforo_maximo_ideal DECIMAL(10,5),
                    potassio_minimo_ideal DECIMAL(10,5),
                    potassio_maximo_ideal DECIMAL(10,5),
                    umidade_minima_ideal DECIMAL(10,5),
                    umidade_maxima_ideal DECIMAL(10,5)
                )
            ''')
            
            # Tabela Medicoes
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS TABELA_MEDICOES (
                    id_medicao VARCHAR(10) PRIMARY KEY,
                    valor_medicao DECIMAL(10,5),
                    data_medicao DATETIME,
                    id_sensor VARCHAR(10),
                    FOREIGN KEY (id_sensor) REFERENCES TABELA_SENSORES(id_sensor)
                )
            ''')
            
            # Tabela Aplicacoes Nutrientes
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS TABELA_APLICACOES_NUTRIENTES (
                    id_aplicacao_nutriente VARCHAR(10) PRIMARY KEY,
                    tipo_aplicacao VARCHAR(50),
                    volume_aplicacao DECIMAL(10,2),
                    data_aplicacao DATETIME,
                    id_setor VARCHAR(10),
                    FOREIGN KEY (id_setor) REFERENCES TABELA_SETORES(id_setor)
                )
            ''')
            
            # Tabela Correcoes PH
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS TABELA_CORRECOES_PH (
                    id_correcao_ph VARCHAR(10) PRIMARY KEY,
                    tipo_correcao VARCHAR(50),
                    volume_correcao DECIMAL(10,2),
                    data_correcao DATETIME,
                    id_setor VARCHAR(10),
                    FOREIGN KEY (id_setor) REFERENCES TABELA_SETORES(id_setor)
                )
            ''')
            
            # Tabela Irrigacoes
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS TABELA_IRRIGACOES (
                    id_irrigacao VARCHAR(10) PRIMARY KEY,
                    volume_irrigacao DECIMAL(10,2),
                    data_irrigacao DATETIME,
                    id_setor VARCHAR(10),
                    FOREIGN KEY (id_setor) REFERENCES TABELA_SETORES(id_setor)
                )
            ''')
            
            # Adicionar foreign keys que não foram criadas inicialmente
            try:
                self.cursor.execute('''
                    CREATE TABLE IF NOT EXISTS TABELA_SENSORES_NEW (
                        id_sensor VARCHAR(10) PRIMARY KEY,
                        tipo_sensor VARCHAR(10),
                        id_setor VARCHAR(10),
                        FOREIGN KEY (id_setor) REFERENCES TABELA_SETORES(id_setor)
                    )
                ''')
                
                self.cursor.execute('''
                    CREATE TABLE IF NOT EXISTS TABELA_SETORES_NEW (
                        id_setor VARCHAR(10) PRIMARY KEY,
                        area_setor DECIMAL(9,2),
                        id_cultura VARCHAR(10),
                        FOREIGN KEY (id_cultura) REFERENCES TABELA_CULTURAS(id_cultura)
                    )
                ''')
            except:
                pass
            
            self.connection.commit()
            print("Tabelas criadas com sucesso!")
            
        except sqlite3.Error as e:
            print(f"Erro ao criar tabelas: {e}")
    
    # ========== CRUD PARA CULTURAS ==========
    
    def inserir_cultura(self, id_cultura: str, nome_cultura: str, 
                       ph_min: float, ph_max: float, fosforo_min: float, 
                       fosforo_max: float, potassio_min: float, potassio_max: float,
                       umidade_min: float, umidade_max: float) -> bool:
        """Insere uma nova cultura"""
        try:
            self.cursor.execute('''
                INSERT INTO TABELA_CULTURAS 
                (id_cultura, nome_cultura, ph_minimo_ideal, ph_maximo_ideal,
                 fosforo_minimo_ideal, fosforo_maximo_ideal, potassio_minimo_ideal,
                 potassio_maximo_ideal, umidade_minima_ideal, umidade_maxima_ideal)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (id_cultura, nome_cultura, ph_min, ph_max, fosforo_min, 
                  fosforo_max, potassio_min, potassio_max, umidade_min, umidade_max))
            self.connection.commit()
            print(f"Cultura {nome_cultura} inserida com sucesso!")
            return True
        except sqlite3.Error as e:
            print(f"Erro ao inserir cultura: {e}")
            return False
    
    def consultar_culturas(self) -> List[Dict]:
        """Consulta todas as culturas"""
        try:
            self.cursor.execute("SELECT * FROM TABELA_CULTURAS")
            culturas = self.cursor.fetchall()
            colunas = [desc[0] for desc in self.cursor.description]
            return [dict(zip(colunas, cultura)) for cultura in culturas]
        except sqlite3.Error as e:
            print(f"Erro ao consultar culturas: {e}")
            return []
    
    def atualizar_cultura(self, id_cultura: str, **kwargs) -> bool:
        """Atualiza uma cultura existente"""
        try:
            campos = []
            valores = []
            for campo, valor in kwargs.items():
                campos.append(f"{campo} = ?")
                valores.append(valor)
            
            valores.append(id_cultura)
            query = f"UPDATE TABELA_CULTURAS SET {', '.join(campos)} WHERE id_cultura = ?"
            
            self.cursor.execute(query, valores)
            self.connection.commit()
            print(f"Cultura {id_cultura} atualizada com sucesso!")
            return True
        except sqlite3.Error as e:
            print(f"Erro ao atualizar cultura: {e}")
            return False
    
    def remover_cultura(self, id_cultura: str) -> bool:
        """Remove uma cultura"""
        try:
            self.cursor.execute("DELETE FROM TABELA_CULTURAS WHERE id_cultura = ?", (id_cultura,))
            self.connection.commit()
            print(f"Cultura {id_cultura} removida com sucesso!")
            return True
        except sqlite3.Error as e:
            print(f"Erro ao remover cultura: {e}")
            return False
    
    # ========== CRUD PARA SETORES ==========
    
    def inserir_setor(self, id_setor: str, area_setor: float, id_cultura: str) -> bool:
        """Insere um novo setor"""
        try:
            self.cursor.execute('''
                INSERT INTO TABELA_SETORES (id_setor, area_setor, id_cultura)
                VALUES (?, ?, ?)
            ''', (id_setor, area_setor, id_cultura))
            self.connection.commit()
            print(f"Setor {id_setor} inserido com sucesso!")
            return True
        except sqlite3.Error as e:
            print(f"Erro ao inserir setor: {e}")
            return False
    
    def consultar_setores(self) -> List[Dict]:
        """Consulta todos os setores"""
        try:
            self.cursor.execute('''
                SELECT s.*, c.nome_cultura 
                FROM TABELA_SETORES s 
                LEFT JOIN TABELA_CULTURAS c ON s.id_cultura = c.id_cultura
            ''')
            setores = self.cursor.fetchall()
            colunas = [desc[0] for desc in self.cursor.description]
            return [dict(zip(colunas, setor)) for setor in setores]
        except sqlite3.Error as e:
            print(f"Erro ao consultar setores: {e}")
            return []
    
    def atualizar_setor(self, id_setor: str, **kwargs) -> bool:
        """Atualiza um setor existente"""
        try:
            campos = []
            valores = []
            for campo, valor in kwargs.items():
                campos.append(f"{campo} = ?")
                valores.append(valor)
            
            valores.append(id_setor)
            query = f"UPDATE TABELA_SETORES SET {', '.join(campos)} WHERE id_setor = ?"
            
            self.cursor.execute(query, valores)
            self.connection.commit()
            print(f"Setor {id_setor} atualizado com sucesso!")
            return True
        except sqlite3.Error as e:
            print(f"Erro ao atualizar setor: {e}")
            return False
    
    def remover_setor(self, id_setor: str) -> bool:
        """Remove um setor"""
        try:
            self.cursor.execute("DELETE FROM TABELA_SETORES WHERE id_setor = ?", (id_setor,))
            self.connection.commit()
            print(f"Setor {id_setor} removido com sucesso!")
            return True
        except sqlite3.Error as e:
            print(f"Erro ao remover setor: {e}")
            return False
    
    # ========== CRUD PARA SENSORES ==========
    
    def inserir_sensor(self, id_sensor: str, tipo_sensor: str, id_setor: str) -> bool:
        """Insere um novo sensor"""
        try:
            self.cursor.execute('''
                INSERT INTO TABELA_SENSORES (id_sensor, tipo_sensor, id_setor)
                VALUES (?, ?, ?)
            ''', (id_sensor, tipo_sensor, id_setor))
            self.connection.commit()
            print(f"Sensor {id_sensor} inserido com sucesso!")
            return True
        except sqlite3.Error as e:
            print(f"Erro ao inserir sensor: {e}")
            return False
    
    def consultar_sensores(self) -> List[Dict]:
        """Consulta todos os sensores"""
        try:
            self.cursor.execute('''
                SELECT s.*, st.area_setor 
                FROM TABELA_SENSORES s 
                LEFT JOIN TABELA_SETORES st ON s.id_setor = st.id_setor
            ''')
            sensores = self.cursor.fetchall()
            colunas = [desc[0] for desc in self.cursor.description]
            return [dict(zip(colunas, sensor)) for sensor in sensores]
        except sqlite3.Error as e:
            print(f"Erro ao consultar sensores: {e}")
            return []
    
    def atualizar_sensor(self, id_sensor: str, **kwargs) -> bool:
        """Atualiza um sensor existente"""
        try:
            campos = []
            valores = []
            for campo, valor in kwargs.items():
                campos.append(f"{campo} = ?")
                valores.append(valor)
            
            valores.append(id_sensor)
            query = f"UPDATE TABELA_SENSORES SET {', '.join(campos)} WHERE id_sensor = ?"
            
            self.cursor.execute(query, valores)
            self.connection.commit()
            print(f"Sensor {id_sensor} atualizado com sucesso!")
            return True
        except sqlite3.Error as e:
            print(f"Erro ao atualizar sensor: {e}")
            return False
    
    def remover_sensor(self, id_sensor: str) -> bool:
        """Remove um sensor"""
        try:
            self.cursor.execute("DELETE FROM TABELA_SENSORES WHERE id_sensor = ?", (id_sensor,))
            self.connection.commit()
            print(f"Sensor {id_sensor} removido com sucesso!")
            return True
        except sqlite3.Error as e:
            print(f"Erro ao remover sensor: {e}")
            return False
    
    # ========== CRUD PARA MEDICOES ==========
    
    def inserir_medicao(self, id_medicao: str, valor_medicao: float, 
                       data_medicao: str, id_sensor: str) -> bool:
        """Insere uma nova medição"""
        try:
            self.cursor.execute('''
                INSERT INTO TABELA_MEDICOES (id_medicao, valor_medicao, data_medicao, id_sensor)
                VALUES (?, ?, ?, ?)
            ''', (id_medicao, valor_medicao, data_medicao, id_sensor))
            self.connection.commit()
            print(f"Medição {id_medicao} inserida com sucesso!")
            return True
        except sqlite3.Error as e:
            print(f"Erro ao inserir medição: {e}")
            return False
    
    def consultar_medicoes(self) -> List[Dict]:
        """Consulta todas as medições"""
        try:
            self.cursor.execute('''
                SELECT m.*, s.tipo_sensor, s.id_setor 
                FROM TABELA_MEDICOES m 
                LEFT JOIN TABELA_SENSORES s ON m.id_sensor = s.id_sensor
            ''')
            medicoes = self.cursor.fetchall()
            colunas = [desc[0] for desc in self.cursor.description]
            return [dict(zip(colunas, medicao)) for medicao in medicoes]
        except sqlite3.Error as e:
            print(f"Erro ao consultar medições: {e}")
            return []
    
    def atualizar_medicao(self, id_medicao: str, **kwargs) -> bool:
        """Atualiza uma medição existente"""
        try:
            campos = []
            valores = []
            for campo, valor in kwargs.items():
                campos.append(f"{campo} = ?")
                valores.append(valor)
            
            valores.append(id_medicao)
            query = f"UPDATE TABELA_MEDICOES SET {', '.join(campos)} WHERE id_medicao = ?"
            
            self.cursor.execute(query, valores)
            self.connection.commit()
            print(f"Medição {id_medicao} atualizada com sucesso!")
            return True
        except sqlite3.Error as e:
            print(f"Erro ao atualizar medição: {e}")
            return False
    
    def remover_medicao(self, id_medicao: str) -> bool:
        """Remove uma medição"""
        try:
            self.cursor.execute("DELETE FROM TABELA_MEDICOES WHERE id_medicao = ?", (id_medicao,))
            self.connection.commit()
            print(f"Medição {id_medicao} removida com sucesso!")
            return True
        except sqlite3.Error as e:
            print(f"Erro ao remover medição: {e}")
            return False
    
    # ========== CRUD PARA APLICACOES NUTRIENTES ==========
    
    def inserir_aplicacao_nutriente(self, id_aplicacao: str, tipo_aplicacao: str, 
                                   volume_aplicacao: float, data_aplicacao: str, 
                                   id_setor: str) -> bool:
        """Insere uma nova aplicação de nutriente"""
        try:
            self.cursor.execute('''
                INSERT INTO TABELA_APLICACOES_NUTRIENTES 
                (id_aplicacao_nutriente, tipo_aplicacao, volume_aplicacao, data_aplicacao, id_setor)
                VALUES (?, ?, ?, ?, ?)
            ''', (id_aplicacao, tipo_aplicacao, volume_aplicacao, data_aplicacao, id_setor))
            self.connection.commit()
            print(f"Aplicação de nutriente {id_aplicacao} inserida com sucesso!")
            return True
        except sqlite3.Error as e:
            print(f"Erro ao inserir aplicação de nutriente: {e}")
            return False
    
    def consultar_aplicacoes_nutrientes(self) -> List[Dict]:
        """Consulta todas as aplicações de nutrientes"""
        try:
            self.cursor.execute('''
                SELECT a.*, s.area_setor 
                FROM TABELA_APLICACOES_NUTRIENTES a 
                LEFT JOIN TABELA_SETORES s ON a.id_setor = s.id_setor
            ''')
            aplicacoes = self.cursor.fetchall()
            colunas = [desc[0] for desc in self.cursor.description]
            return [dict(zip(colunas, aplicacao)) for aplicacao in aplicacoes]
        except sqlite3.Error as e:
            print(f"Erro ao consultar aplicações de nutrientes: {e}")
            return []
    
    def atualizar_aplicacao_nutriente(self, id_aplicacao: str, **kwargs) -> bool:
        """Atualiza uma aplicação de nutriente existente"""
        try:
            campos = []
            valores = []
            for campo, valor in kwargs.items():
                campos.append(f"{campo} = ?")
                valores.append(valor)
            
            valores.append(id_aplicacao)
            query = f"UPDATE TABELA_APLICACOES_NUTRIENTES SET {', '.join(campos)} WHERE id_aplicacao_nutriente = ?"
            
            self.cursor.execute(query, valores)
            self.connection.commit()
            print(f"Aplicação de nutriente {id_aplicacao} atualizada com sucesso!")
            return True
        except sqlite3.Error as e:
            print(f"Erro ao atualizar aplicação de nutriente: {e}")
            return False
    
    def remover_aplicacao_nutriente(self, id_aplicacao: str) -> bool:
        """Remove uma aplicação de nutriente"""
        try:
            self.cursor.execute("DELETE FROM TABELA_APLICACOES_NUTRIENTES WHERE id_aplicacao_nutriente = ?", (id_aplicacao,))
            self.connection.commit()
            print(f"Aplicação de nutriente {id_aplicacao} removida com sucesso!")
            return True
        except sqlite3.Error as e:
            print(f"Erro ao remover aplicação de nutriente: {e}")
            return False
    
    # ========== CRUD PARA CORRECOES PH ==========
    
    def inserir_correcao_ph(self, id_correcao: str, tipo_correcao: str, 
                           volume_correcao: float, data_correcao: str, 
                           id_setor: str) -> bool:
        """Insere uma nova correção de pH"""
        try:
            self.cursor.execute('''
                INSERT INTO TABELA_CORRECOES_PH 
                (id_correcao_ph, tipo_correcao, volume_correcao, data_correcao, id_setor)
                VALUES (?, ?, ?, ?, ?)
            ''', (id_correcao, tipo_correcao, volume_correcao, data_correcao, id_setor))
            self.connection.commit()
            print(f"Correção de pH {id_correcao} inserida com sucesso!")
            return True
        except sqlite3.Error as e:
            print(f"Erro ao inserir correção de pH: {e}")
            return False
    
    def consultar_correcoes_ph(self) -> List[Dict]:
        """Consulta todas as correções de pH"""
        try:
            self.cursor.execute('''
                SELECT c.*, s.area_setor 
                FROM TABELA_CORRECOES_PH c 
                LEFT JOIN TABELA_SETORES s ON c.id_setor = s.id_setor
            ''')
            correcoes = self.cursor.fetchall()
            colunas = [desc[0] for desc in self.cursor.description]
            return [dict(zip(colunas, correcao)) for correcao in correcoes]
        except sqlite3.Error as e:
            print(f"Erro ao consultar correções de pH: {e}")
            return []
    
    def atualizar_correcao_ph(self, id_correcao: str, **kwargs) -> bool:
        """Atualiza uma correção de pH existente"""
        try:
            campos = []
            valores = []
            for campo, valor in kwargs.items():
                campos.append(f"{campo} = ?")
                valores.append(valor)
            
            valores.append(id_correcao)
            query = f"UPDATE TABELA_CORRECOES_PH SET {', '.join(campos)} WHERE id_correcao_ph = ?"
            
            self.cursor.execute(query, valores)
            self.connection.commit()
            print(f"Correção de pH {id_correcao} atualizada com sucesso!")
            return True
        except sqlite3.Error as e:
            print(f"Erro ao atualizar correção de pH: {e}")
            return False
    
    def remover_correcao_ph(self, id_correcao: str) -> bool:
        """Remove uma correção de pH"""
        try:
            self.cursor.execute("DELETE FROM TABELA_CORRECOES_PH WHERE id_correcao_ph = ?", (id_correcao,))
            self.connection.commit()
            print(f"Correção de pH {id_correcao} removida com sucesso!")
            return True
        except sqlite3.Error as e:
            print(f"Erro ao remover correção de pH: {e}")
            return False
    
    # ========== CRUD PARA IRRIGACOES ==========
    
    def inserir_irrigacao(self, id_irrigacao: str, volume_irrigacao: float, 
                         data_irrigacao: str, id_setor: str) -> bool:
        """Insere uma nova irrigação"""
        try:
            self.cursor.execute('''
                INSERT INTO TABELA_IRRIGACOES 
                (id_irrigacao, volume_irrigacao, data_irrigacao, id_setor)
                VALUES (?, ?, ?, ?)
            ''', (id_irrigacao, volume_irrigacao, data_irrigacao, id_setor))
            self.connection.commit()
            print(f"Irrigação {id_irrigacao} inserida com sucesso!")
            return True
        except sqlite3.Error as e:
            print(f"Erro ao inserir irrigação: {e}")
            return False
    
    def consultar_irrigacoes(self) -> List[Dict]:
        """Consulta todas as irrigações"""
        try:
            self.cursor.execute('''
                SELECT i.*, s.area_setor 
                FROM TABELA_IRRIGACOES i 
                LEFT JOIN TABELA_SETORES s ON i.id_setor = s.id_setor
            ''')
            irrigacoes = self.cursor.fetchall()
            colunas = [desc[0] for desc in self.cursor.description]
            return [dict(zip(colunas, irrigacao)) for irrigacao in irrigacoes]
        except sqlite3.Error as e:
            print(f"Erro ao consultar irrigações: {e}")
            return []
    
    def atualizar_irrigacao(self, id_irrigacao: str, **kwargs) -> bool:
        """Atualiza uma irrigação existente"""
        try:
            campos = []
            valores = []
            for campo, valor in kwargs.items():
                campos.append(f"{campo} = ?")
                valores.append(valor)
            
            valores.append(id_irrigacao)
            query = f"UPDATE TABELA_IRRIGACOES SET {', '.join(campos)} WHERE id_irrigacao = ?"
            
            self.cursor.execute(query, valores)
            self.connection.commit()
            print(f"Irrigação {id_irrigacao} atualizada com sucesso!")
            return True
        except sqlite3.Error as e:
            print(f"Erro ao atualizar irrigação: {e}")
            return False
    
    def remover_irrigacao(self, id_irrigacao: str) -> bool:
        """Remove uma irrigação"""
        try:
            self.cursor.execute("DELETE FROM TABELA_IRRIGACOES WHERE id_irrigacao = ?", (id_irrigacao,))
            self.connection.commit()
            print(f"Irrigação {id_irrigacao} removida com sucesso!")
            return True
        except sqlite3.Error as e:
            print(f"Erro ao remover irrigação: {e}")
            return False
    
    # ========== MÉTODOS AUXILIARES ==========
    
    def obter_relatorio_setor(self, id_setor: str) -> Dict:
        """Obtém um relatório completo de um setor"""
        try:
            # Informações do setor
            self.cursor.execute('''
                SELECT s.*, c.nome_cultura 
                FROM TABELA_SETORES s 
                LEFT JOIN TABELA_CULTURAS c ON s.id_cultura = c.id_cultura 
                WHERE s.id_setor = ?
            ''', (id_setor,))
            setor_info = self.cursor.fetchone()
            
            if not setor_info:
                return {}
            
            # Sensores do setor
            self.cursor.execute('''
                SELECT * FROM TABELA_SENSORES WHERE id_setor = ?
            ''', (id_setor,))
            sensores = self.cursor.fetchall()
            
            # Últimas medições
            self.cursor.execute('''
                SELECT m.*, s.tipo_sensor 
                FROM TABELA_MEDICOES m 
                JOIN TABELA_SENSORES s ON m.id_sensor = s.id_sensor 
                WHERE s.id_setor = ? 
                ORDER BY m.data_medicao DESC 
                LIMIT 10
            ''', (id_setor,))
            medicoes = self.cursor.fetchall()
            
            # Irrigações recentes
            self.cursor.execute('''
                SELECT * FROM TABELA_IRRIGACOES 
                WHERE id_setor = ? 
                ORDER BY data_irrigacao DESC 
                LIMIT 5
            ''', (id_setor,))
            irrigacoes = self.cursor.fetchall()
            
            return {
                'setor': setor_info,
                'sensores': sensores,
                'medicoes_recentes': medicoes,
                'irrigacoes_recentes': irrigacoes
            }
            
        except sqlite3.Error as e:
            print(f"Erro ao obter relatório do setor: {e}")
            return {}
    
    def listar_todas_tabelas(self):
        """Lista o conteúdo de todas as tabelas"""
        tabelas = [
            'TABELA_CULTURAS',
            'TABELA_SETORES', 
            'TABELA_SENSORES',
            'TABELA_MEDICOES',
            'TABELA_APLICACOES_NUTRIENTES',
            'TABELA_CORRECOES_PH',
            'TABELA_IRRIGACOES'
        ]
        
        for tabela in tabelas:
            print(f"\n=== {tabela} ===")
            try:
                self.cursor.execute(f"SELECT * FROM {tabela}")
                registros = self.cursor.fetchall()
                if registros:
                    colunas = [desc[0] for desc in self.cursor.description]
                    print(f"Colunas: {', '.join(colunas)}")
                    for registro in registros:
                        print(registro)
                else:
                    print("Nenhum registro encontrado")
            except sqlite3.Error as e:
                print(f"Erro ao consultar {tabela}: {e}")


def demonstrar_sistema():
    """Função para demonstrar o uso do sistema"""
    print("=== DEMONSTRAÇÃO DO SISTEMA DE BANCO DE DADOS AGRÍCOLA ===\n")
    
    # Criar instância do banco
    db = AgriculturalDatabase()
    
    # Inserir dados de exemplo
    print("1. Inserindo dados de exemplo...\n")
    
    # Culturas
    db.inserir_cultura("CULT001", "Milho", 6.0, 7.0, 20.0, 40.0, 150.0, 300.0, 60.0, 80.0)
    db.inserir_cultura("CULT002", "Soja", 6.2, 7.2, 25.0, 45.0, 200.0, 350.0, 65.0, 85.0)
    
    # Setores
    db.inserir_setor("SET001", 100.50, "CULT001")
    db.inserir_setor("SET002", 75.25, "CULT002")
    
    # Sensores
    db.inserir_sensor("SENS001", "pH", "SET001")
    db.inserir_sensor("SENS002", "Umidade", "SET001")
    db.inserir_sensor("SENS003", "Fosforo", "SET002")
    
    # Medições
    db.inserir_medicao("MED001", 6.5, "2024-06-15 10:30:00", "SENS001")
    db.inserir_medicao("MED002", 72.5, "2024-06-15 10:35:00", "SENS002")
    db.inserir_medicao("MED003", 28.0, "2024-06-15 11:00:00", "SENS003")
    
    # Irrigações
    db.inserir_irrigacao("IRR001", 500.0, "2024-06-15 06:00:00", "SET001")
    db.inserir_irrigacao("IRR002", 350.0, "2024-06-15 06:30:00", "SET002")
    
    # Aplicações de nutrientes
    db.inserir_aplicacao_nutriente("APL001", "NPK", 25.5, "2024-06-14 08:00:00", "SET001")
    db.inserir_aplicacao_nutriente("APL002", "Fosfato", 15.0, "2024-06-14 09:00:00", "SET002")
    
    # Correções de pH
    db.inserir_correcao_ph("COR001", "Calcário", 100.0, "2024-06-13 14:00:00", "SET001")
    
    print("\n2. Consultando dados...\n")
    
    # Consultar culturas
    print("=== CULTURAS ===")
    culturas = db.consultar_culturas()
    for cultura in culturas:
        print(f"ID: {cultura['id_cultura']}, Nome: {cultura['nome_cultura']}, pH: {cultura['ph_minimo_ideal']}-{cultura['ph_maximo_ideal']}")
    
    # Consultar setores
    print("\n=== SETORES ===")
    setores = db.consultar_setores()
    for setor in setores:
        print(f"ID: {setor['id_setor']}, Área: {setor['area_setor']} ha, Cultura: {setor.get('nome_cultura', 'N/A')}")
    
    # Consultar sensores
    print("\n=== SENSORES ===")
    sensores = db.consultar_sensores()
    for sensor in sensores:
        print(f"ID: {sensor['id_sensor']}, Tipo: {sensor['tipo_sensor']}, Setor: {sensor['id_setor']}")
    
    # Consultar medições
    print("\n=== MEDIÇÕES RECENTES ===")
    medicoes = db.consultar_medicoes()
    for medicao in medicoes:
        print(f"ID: {medicao['id_medicao']}, Valor: {medicao['valor_medicao']}, Sensor: {medicao['tipo_sensor']}, Data: {medicao['data_medicao']}")
    
    print("\n3. Atualizando dados...\n")
    
    # Atualizar uma cultura
    db.atualizar_cultura("CULT001", ph_minimo_ideal=6.1, ph_maximo_ideal=7.1)
    
    # Atualizar um setor
    db.atualizar_setor("SET001", area_setor=102.0)
    
    print("\n4. Relatório detalhado do setor SET001...\n")
    relatorio = db.obter_relatorio_setor("SET001")
    if relatorio:
        print(f"Setor: {relatorio['setor'][0]} - Área: {relatorio['setor'][1]} ha")
        print(f"Cultura: {relatorio['setor'][3]}")
        print(f"Número de sensores: {len(relatorio['sensores'])}")
        print(f"Medições recentes: {len(relatorio['medicoes_recentes'])}")
        print(f"Irrigações recentes: {len(relatorio['irrigacoes_recentes'])}")
    
    print("\n5. Demonstração de remoção...\n")
    
    # Remover uma medição
    db.remover_medicao("MED003")
    
    print("\n=== RESUMO FINAL DE TODAS AS TABELAS ===")
    db.listar_todas_tabelas()
    
    # Fechar conexão
    db.disconnect()
    print("\n=== DEMONSTRAÇÃO CONCLUÍDA ===")


class MenuInterativo:
    """Interface de menu interativo para o sistema"""
    
    def __init__(self):
        self.db = AgriculturalDatabase()
    
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
        print("9. Listar todas as tabelas")
        print("0. Sair")
        print("="*50)
    
    def menu_culturas(self):
        """Menu para gerenciar culturas"""
        while True:
            print("\n=== GERENCIAR CULTURAS ===")
            print("1. Inserir Cultura")
            print("2. Listar Culturas")
            print("3. Atualizar Cultura")
            print("4. Remover Cultura")
            print("0. Voltar")
            
            opcao = input("Escolha uma opção: ").strip()
            
            if opcao == "1":
                self.inserir_cultura_interativo()
            elif opcao == "2":
                self.listar_culturas()
            elif opcao == "3":
                self.atualizar_cultura_interativo()
            elif opcao == "4":
                self.remover_cultura_interativo()
            elif opcao == "0":
                break
            else:
                print("Opção inválida!")
    
    def inserir_cultura_interativo(self):
        """Inserir cultura de forma interativa"""
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
            
            self.db.inserir_cultura(id_cultura, nome_cultura, ph_min, ph_max,
                                  fosforo_min, fosforo_max, potassio_min, 
                                  potassio_max, umidade_min, umidade_max)
        except ValueError:
            print("Erro: Valores numéricos inválidos!")
        except Exception as e:
            print(f"Erro: {e}")
    
    def listar_culturas(self):
        """Lista todas as culturas"""
        print("\n--- Lista de Culturas ---")
        culturas = self.db.consultar_culturas()
        if culturas:
            for cultura in culturas:
                print(f"\nID: {cultura['id_cultura']}")
                print(f"Nome: {cultura['nome_cultura']}")
                print(f"pH: {cultura['ph_minimo_ideal']} - {cultura['ph_maximo_ideal']}")
                print(f"Fósforo: {cultura['fosforo_minimo_ideal']} - {cultura['fosforo_maximo_ideal']}")
                print(f"Potássio: {cultura['potassio_minimo_ideal']} - {cultura['potassio_maximo_ideal']}")
                print(f"Umidade: {cultura['umidade_minima_ideal']} - {cultura['umidade_maxima_ideal']}")
                print("-" * 30)
        else:
            print("Nenhuma cultura encontrada!")
    
    def atualizar_cultura_interativo(self):
        """Atualizar cultura de forma interativa"""
        print("\n--- Atualizar Cultura ---")
        id_cultura = input("ID da cultura a atualizar: ").strip()
        
        print("Deixe em branco os campos que não deseja alterar:")
        nome = input("Novo nome (atual será mantido se vazio): ").strip()
        
        try:
            campos = {}
            if nome:
                campos['nome_cultura'] = nome
            
            ph_min = input("Novo pH mínimo: ").strip()
            if ph_min:
                campos['ph_minimo_ideal'] = float(ph_min)
            
            ph_max = input("Novo pH máximo: ").strip()
            if ph_max:
                campos['ph_maximo_ideal'] = float(ph_max)
            
            if campos:
                self.db.atualizar_cultura(id_cultura, **campos)
            else:
                print("Nenhum campo foi alterado!")
                
        except ValueError:
            print("Erro: Valores numéricos inválidos!")
    
    def remover_cultura_interativo(self):
        """Remover cultura de forma interativa"""
        print("\n--- Remover Cultura ---")
        id_cultura = input("ID da cultura a remover: ").strip()
        confirmacao = input(f"Tem certeza que deseja remover a cultura {id_cultura}? (s/N): ").strip().lower()
        
        if confirmacao == 's':
            self.db.remover_cultura(id_cultura)
        else:
            print("Remoção cancelada!")
    
    def menu_setores(self):
        """Menu para gerenciar setores"""
        while True:
            print("\n=== GERENCIAR SETORES ===")
            print("1. Inserir Setor")
            print("2. Listar Setores")
            print("3. Atualizar Setor")
            print("4. Remover Setor")
            print("0. Voltar")
            
            opcao = input("Escolha uma opção: ").strip()
            
            if opcao == "1":
                self.inserir_setor_interativo()
            elif opcao == "2":
                self.listar_setores()
            elif opcao == "3":
                self.atualizar_setor_interativo()
            elif opcao == "4":
                self.remover_setor_interativo()
            elif opcao == "0":
                break
            else:
                print("Opção inválida!")
    
    def inserir_setor_interativo(self):
        """Inserir setor de forma interativa"""
        print("\n--- Inserir Novo Setor ---")
        try:
            id_setor = input("ID do setor: ").strip()
            area_setor = float(input("Área do setor (hectares): "))
            id_cultura = input("ID da cultura: ").strip()
            
            self.db.inserir_setor(id_setor, area_setor, id_cultura)
        except ValueError:
            print("Erro: Área deve ser um número!")
        except Exception as e:
            print(f"Erro: {e}")
    
    def listar_setores(self):
        """Lista todos os setores"""
        print("\n--- Lista de Setores ---")
        setores = self.db.consultar_setores()
        if setores:
            for setor in setores:
                print(f"\nID: {setor['id_setor']}")
                print(f"Área: {setor['area_setor']} hectares")
                print(f"Cultura: {setor.get('nome_cultura', 'N/A')} (ID: {setor['id_cultura']})")
                print("-" * 30)
        else:
            print("Nenhum setor encontrado!")
    
    def atualizar_setor_interativo(self):
        """Atualizar setor de forma interativa"""
        print("\n--- Atualizar Setor ---")
        id_setor = input("ID do setor a atualizar: ").strip()
        
        try:
            campos = {}
            area = input("Nova área (deixe vazio para manter): ").strip()
            if area:
                campos['area_setor'] = float(area)
            
            cultura = input("Novo ID da cultura (deixe vazio para manter): ").strip()
            if cultura:
                campos['id_cultura'] = cultura
            
            if campos:
                self.db.atualizar_setor(id_setor, **campos)
            else:
                print("Nenhum campo foi alterado!")
                
        except ValueError:
            print("Erro: Área deve ser um número!")
    
    def remover_setor_interativo(self):
        """Remover setor de forma interativa"""
        print("\n--- Remover Setor ---")
        id_setor = input("ID do setor a remover: ").strip()
        confirmacao = input(f"Tem certeza que deseja remover o setor {id_setor}? (s/N): ").strip().lower()
        
        if confirmacao == 's':
            self.db.remover_setor(id_setor)
        else:
            print("Remoção cancelada!")
    
    def menu_relatorios(self):
        """Menu de relatórios"""
        while True:
            print("\n=== RELATÓRIOS ===")
            print("1. Relatório de Setor")
            print("2. Medições por Sensor")
            print("3. Histórico de Irrigações")
            print("0. Voltar")
            
            opcao = input("Escolha uma opção: ").strip()
            
            if opcao == "1":
                self.relatorio_setor()
            elif opcao == "2":
                self.relatorio_medicoes_sensor()
            elif opcao == "3":
                self.relatorio_irrigacoes()
            elif opcao == "0":
                break
            else:
                print("Opção inválida!")
    
    def relatorio_setor(self):
        """Gera relatório detalhado de um setor"""
        print("\n--- Relatório de Setor ---")
        id_setor = input("ID do setor: ").strip()
        
        relatorio = self.db.obter_relatorio_setor(id_setor)
        if relatorio and relatorio['setor']:
            setor = relatorio['setor']
            print(f"\n=== SETOR {setor[0]} ===")
            print(f"Área: {setor[1]} hectares")
            print(f"Cultura: {setor[3] if len(setor) > 3 else 'N/A'}")
            
            print(f"\nSensores ({len(relatorio['sensores'])}):")
            for sensor in relatorio['sensores']:
                print(f"  - {sensor[0]}: {sensor[1]}")
            
            print(f"\nMedições Recentes ({len(relatorio['medicoes_recentes'])}):")
            for medicao in relatorio['medicoes_recentes']:
                print(f"  - {medicao[3]}: {medicao[1]} ({medicao[2]})")
            
            print(f"\nIrrigações Recentes ({len(relatorio['irrigacoes_recentes'])}):")
            for irrigacao in relatorio['irrigacoes_recentes']:
                print(f"  - {irrigacao[2]}: {irrigacao[1]}L")
        else:
            print("Setor não encontrado!")
    
    def relatorio_medicoes_sensor(self):
        """Relatório de medições por sensor"""
        print("\n--- Medições por Sensor ---")
        medicoes = self.db.consultar_medicoes()
        
        if medicoes:
            sensores = {}
            for medicao in medicoes:
                sensor_id = medicao['id_sensor']
                if sensor_id not in sensores:
                    sensores[sensor_id] = []
                sensores[sensor_id].append(medicao)
            
            for sensor_id, lista_medicoes in sensores.items():
                print(f"\n=== SENSOR {sensor_id} ===")
                print(f"Tipo: {lista_medicoes[0]['tipo_sensor']}")
                print(f"Total de medições: {len(lista_medicoes)}")
                print("Últimas medições:")
                for medicao in lista_medicoes[-5:]:  # Últimas 5
                    print(f"  - {medicao['data_medicao']}: {medicao['valor_medicao']}")
        else:
            print("Nenhuma medição encontrada!")
    
    def relatorio_irrigacoes(self):
        """Relatório de irrigações"""
        print("\n--- Histórico de Irrigações ---")
        irrigacoes = self.db.consultar_irrigacoes()
        
        if irrigacoes:
            total_volume = 0
            for irrigacao in irrigacoes:
                print(f"Setor {irrigacao['id_setor']}: {irrigacao['volume_irrigacao']}L em {irrigacao['data_irrigacao']}")
                total_volume += irrigacao['volume_irrigacao']
            
            print(f"\nVolume total irrigado: {total_volume}L")
        else:
            print("Nenhuma irrigação encontrada!")
    
    def executar(self):
        """Executa o menu interativo"""
        while True:
            self.mostrar_menu_principal()
            opcao = input("Escolha uma opção: ").strip()
            
            if opcao == "1":
                self.menu_culturas()
            elif opcao == "2":
                self.menu_setores()
            elif opcao == "3":
                print("Menu de sensores - Implementação similar aos outros menus")
            elif opcao == "4":
                print("Menu de medições - Implementação similar aos outros menus")
            elif opcao == "5":
                print("Menu de irrigações - Implementação similar aos outros menus")
            elif opcao == "6":
                print("Menu de aplicações - Implementação similar aos outros menus")
            elif opcao == "7":
                print("Menu de correções pH - Implementação similar aos outros menus")
            elif opcao == "8":
                self.menu_relatorios()
            elif opcao == "9":
                self.db.listar_todas_tabelas()
            elif opcao == "0":
                print("Encerrando sistema...")
                self.db.disconnect()
                break
            else:
                print("Opção inválida!")


if __name__ == "__main__":
    print("Sistema de Gerenciamento de Banco de Dados Agrícola")
    print("1. Executar demonstração")
    print("2. Executar menu interativo")
    print("3. Sair")
    
    opcao = input("Escolha uma opção: ").strip()
    
    if opcao == "1":
        demonstrar_sistema()
    elif opcao == "2":
        menu = MenuInterativo()
        menu.executar()
    elif opcao == "3":
        print("Saindo...")
    else:
        print("Opção inválida!")