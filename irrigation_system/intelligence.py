# intelligence.py

# Standard Library Imports
import os
import warnings
from datetime import datetime, timedelta

# Third-Party Library Imports
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split

# Suprimir avisos futuros do pandas para uma saída mais limpa
warnings.simplefilter(action='ignore', category=FutureWarning)

class IrrigationIntelligence:
    """
    Classe para gerenciar a inteligência preditiva do sistema de irrigação.
    """
    def __init__(self, db_manager, model_path="irrigation_model.joblib"):
        """
        Inicializa a classe de inteligência.

        Args:
            db_manager: Uma instância da classe AgriculturalDatabase.
            model_path (str): Caminho para salvar/carregar o modelo treinado.
        """
        self.db = db_manager
        self.model_path = model_path
        self.model = self.load_model()
        self.feature_names = None # Para garantir consistência nas colunas

    def _get_data_as_dataframe(self, id_setor: str) -> pd.DataFrame:
        """
        Busca e prepara os dados de um setor específico em um DataFrame do pandas.
        """
        print(f"\n[DEBUG] Iniciando busca de dados para o setor '{id_setor}'...")

        # 1. Consultar medições do setor especificado
        query_medicoes = f"""
            SELECT
                m.data_medicao,
                -- Padroniza o tipo de sensor para minúsculas para consistência
                LOWER(s.tipo_sensor) AS tipo_sensor,
                m.valor_medicao
            FROM TABELA_MEDICOES m
            JOIN TABELA_SENSORES s ON m.id_sensor = s.id_sensor
            WHERE s.id_setor = ?
        """
        try:
            # Usar parâmetros na query é mais seguro
            df_medicoes = pd.read_sql_query(query_medicoes, self.db.connection, params=(id_setor,))
            print(f"[DEBUG] Encontradas {len(df_medicoes)} medições no banco de dados.")
            if df_medicoes.empty:
                return pd.DataFrame()
        except Exception as e:
            print(f"[ERRO DEBUG] Falha ao consultar medições: {e}")
            return pd.DataFrame()

        # 2. Consultar irrigações do setor
        query_irrigacoes = f"""
            SELECT data_irrigacao, 1 AS irrigou
            FROM TABELA_IRRIGACOES
            WHERE id_setor = ?
        """
        df_irrigacoes = pd.read_sql_query(query_irrigacoes, self.db.connection, params=(id_setor,))
        print(f"[DEBUG] Encontradas {len(df_irrigacoes)} irrigações no banco de dados.")

        # 3. Processar medições
        df_medicoes['data_medicao'] = pd.to_datetime(df_medicoes['data_medicao'])
        
        # Pivotar a tabela de medições para ter sensores como colunas
        print("[DEBUG] Pivotando dados de medição (linhas -> colunas)...")
        df_pivot = df_medicoes.pivot_table(
            index='data_medicao',
            columns='tipo_sensor',
            values='valor_medicao'
        )
        print(f"[DEBUG] DataFrame após pivotar tem {df_pivot.shape[0]} linhas e {df_pivot.shape[1]} colunas.")
        print(f"[DEBUG] Colunas criadas: {list(df_pivot.columns)}")
        
        if df_pivot.empty:
            print("[ERRO DEBUG] Pivot falhou ou resultou em DataFrame vazio. Verifique os tipos de sensor no banco.")
            return pd.DataFrame()

        # 4. Reamostragem horária
        print("[DEBUG] Reamostrando dados para frequência horária...")
        # Renomeia colunas para serem mais amigáveis (capitalizadas)
        df_pivot.columns = [col.strip().capitalize() for col in df_pivot.columns]
        df_resampled = df_pivot.resample('H').mean()
        # Preenche valores ausentes para garantir continuidade
        df_resampled = df_resampled.ffill().bfill()
        print(f"[DEBUG] DataFrame após reamostragem tem {df_resampled.shape[0]} linhas.")


        # 5. Processar e juntar dados de irrigação
        if not df_irrigacoes.empty:
            df_irrigacoes['data_irrigacao'] = pd.to_datetime(df_irrigacoes['data_irrigacao'])
            df_irrigacoes.set_index('data_irrigacao', inplace=True)
            df_irrigacoes_resampled = df_irrigacoes.resample('H').sum().fillna(0)
            
            # Juntar dados de medição e irrigação
            df_final = df_resampled.join(df_irrigacoes_resampled, how='left')
            df_final['irrigou'] = df_final['irrigou'].fillna(0).astype(int)
        else:
            df_final = df_resampled
            df_final['irrigou'] = 0

        print(f"[DEBUG] DataFrame final pronto para feature engineering tem {len(df_final)} linhas.")
        return df_final.reset_index().rename(columns={'index': 'data_medicao'})

    def prepare_features_and_target(self, id_setor: str):
        """
        Prepara as features (X) e o alvo (y) para o treinamento do modelo.
        O objetivo é prever se a irrigação ocorrerá na *próxima* hora.
        """
        df = self._get_data_as_dataframe(id_setor)
        if df.empty or len(df) < 2:
            print(f"Dados insuficientes para o setor {id_setor}.")
            return None, None

        # Criar features baseadas no tempo
        df['hora_do_dia'] = df['data_medicao'].dt.hour
        df['dia_da_semana'] = df['data_medicao'].dt.dayofweek # Segunda=0, Domingo=6

        # Definir nosso alvo: prever se a irrigação aconteceu na próxima hora
        df['target'] = df['irrigou'].shift(-1).fillna(0)
        
        # Remover a última linha, pois não temos o alvo para ela
        df.dropna(inplace=True)

        # Definir features e target
        features = [col for col in df.columns if col not in ['data_medicao', 'irrigou', 'target']]
        self.feature_names = features # Salva os nomes das features
        
        X = df[features]
        y = df['target']
        
        return X, y

    def train_model(self, id_setor: str, test_size=0.2):
        """
        Treina o modelo de classificação para um setor específico.
        """
        print(f"\n--- Treinando modelo para o Setor: {id_setor} ---")
        X, y = self.prepare_features_and_target(id_setor)
        
        if X is None or y is None or X.empty:
            print("Treinamento cancelado por falta de dados.")
            return

        if len(y.unique()) < 2:
            print("Treinamento cancelado: são necessários dados de quando irrigou e quando não irrigou.")
            return

        # Dividir os dados em treino e teste
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42, stratify=y
        )
        
        print(f"Tamanho do conjunto de dados: {len(X)} amostras")
        print(f"Features utilizadas: {self.feature_names}")

        # Inicializar e treinar o modelo
        self.model = RandomForestClassifier(n_estimators=100, random_state=42, class_weight='balanced')
        self.model.fit(X_train, y_train)

        # Avaliar o modelo
        y_pred = self.model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        print("\n--- Avaliação do Modelo ---")
        print(f"Acurácia no conjunto de teste: {accuracy:.2f}")
        print("Relatório de Classificação:")
        print(classification_report(y_test, y_pred))
        
        # Salvar o modelo treinado
        self.save_model()
    
    def predict_action(self, id_setor: str, current_data: dict, prediction_time: datetime):
        """
        Prevê a necessidade de irrigação com base nos dados atuais.

        Args:
            id_setor (str): O setor para o qual a previsão é feita.
            current_data (dict): Um dicionário com as medições atuais.
                                 Ex: {'Umidade': 55.0, 'Ph': 6.8, 'Fosforo': 30.0}
            prediction_time (datetime): O horário para o qual a previsão está sendo feita.

        Returns:
            Tuple[str, float]: Uma tupla com a ação sugerida e a probabilidade.
        """
        if not self.model:
            return "Modelo não treinado. Por favor, treine o modelo primeiro.", 0.0

        # Criar features de tempo
        current_data['hora_do_dia'] = prediction_time.hour
        current_data['dia_da_semana'] = prediction_time.weekday()
        
        # Criar um DataFrame com os dados atuais na ordem correta das features
        try:
            input_df = pd.DataFrame([current_data], columns=self.feature_names)
        except Exception as e:
            return f"Erro ao criar DataFrame de entrada: {e}. Verifique as features.", 0.0

        # Fazer a predição
        prediction = self.model.predict(input_df)[0]
        probability = self.model.predict_proba(input_df)[0][1] # Probabilidade da classe "1" (irrigar)
        
        if prediction == 1:
            action = f"SUGESTÃO: Irrigar o setor {id_setor} na próxima hora."
        else:
            action = f"SUGESTÃO: Não irrigar o setor {id_setor} na próxima hora."
            
        return action, probability

    def save_model(self):
        """Salva o modelo treinado e os nomes das features em um arquivo."""
        if self.model and self.feature_names:
            # Garante que o diretório 'data/' exista
            os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
            
            # Cria um payload (pacote) com o modelo e as features
            payload = {'model': self.model, 'features': self.feature_names}
            joblib.dump(payload, self.model_path)
            print(f"Modelo e features salvos com sucesso em '{self.model_path}'")

    def load_model(self):
        """Carrega um modelo treinado e suas features do arquivo."""
        if os.path.exists(self.model_path):
            try:
                # Carrega o payload completo
                payload = joblib.load(self.model_path)
                self.model = payload['model']
                self.feature_names = payload['features']
                print(f"Modelo e features carregados de '{self.model_path}'")
            except (KeyError, EOFError) as e:
                print(f"Erro ao carregar o modelo de '{self.model_path}': {e}. O arquivo pode ser de uma versão antiga ou estar corrompido.")
                self.model = None
                self.feature_names = None
        else:
            print("Nenhum modelo pré-treinado encontrado. É necessário treinar um novo modelo.")