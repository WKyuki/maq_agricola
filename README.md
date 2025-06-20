# FIAP - Faculdade de Informática e Administração Paulista
# Máquina Agrícola - Fase 4

## 👨‍🎓 Integrantes: 
- Yuki Watanabe Kuramoto
- Ricardo Batah Leone
- Cayo Henrique Gomes do Amaral
- Guilherme Martins Ventura Vieira Romeiro
- Rodrigo de Melo Reinaux Porto

## 👩‍🏫 Professores:
### Tutor(a) 
- Lucas Gomes Moreira
### Coordenador(a)
- André Godoi


## 📜 Descrição

**Gerenciamento de Dados:**  
Utiliza um banco de dados SQLite para armazenar de forma persistente informações sobre culturas, setores de plantio, sensores e medições.
Oferece uma interface de linha de comando (CLI) para realizar operações CRUD (Criar, Ler, Atualizar, Deletar) em todas as tabelas do banco de dados.  
  
**Inteligência Preditiva:**  
Implementa um modelo de Machine Learning (RandomForestClassifier do Scikit-learn) para prever a necessidade futura de irrigação.
O modelo é treinado com base no histórico de medições dos sensores (umidade, pH, etc.) e registros de irrigações passadas.
Permite o retreinamento do modelo através da CLI à medida que novos dados são coletados.  
  
**Monitoramento e Visualização:**  
Inclui um dashboard web construído com Streamlit para monitoramento dos dados em tempo real.
O dashboard exibe métricas-chave do sistema, como o número de setores e sensores ativos.
Apresenta gráficos de séries temporais para visualizar a variação da umidade do solo, agregando dados de múltiplos sensores.  
  
**Simulação e Controle:**  
Contém um código de exemplo para microcontroladores (Arduino/ESP32) que simula a lógica de leitura de sensores e acionamento de um relé de irrigação.
A CLI possui uma funcionalidade para gerar dados históricos simulados, permitindo o teste e treinamento do modelo de IA mesmo sem dados reais.


## 📁 Estrutura de pastas

Dentre os arquivos e pastas presentes na raiz do projeto, definem-se:

- main.py: Ponto de entrada para a aplicação de console (CLI). Use este script para gerenciar o banco de dados e treinar o modelo de IA.
- dashboard.py: Ponto de entrada para o dashboard web interativo. Use-o com o Streamlit para visualizar os dados.
- requirements.txt: Lista de todas as bibliotecas Python necessárias para o projeto.
- irrigation_system/: Pacote principal contendo toda a lógica da aplicação.
  - database.py: Gerencia a conexão e todas as operações com o banco de dados SQLite.
  - intelligence.py: Contém a classe IrrigationIntelligence, responsável pelo treinamento e previsão do modelo de Machine Learning.
  - ui.py: Define a interface do usuário para a aplicação de console (o MenuInterativo).
- data/: Diretório para armazenar arquivos gerados pela aplicação, como o banco de dados e o modelo treinado. Esta pasta é ignorada pelo Git (via .gitignore).
- arduino/: Contém o código (.ino) a ser embarcado no hardware de controle, como um Arduino ou ESP32.

## Como Executar o Código

Para executar este projeto, você precisará ter o **Python 3.10+** instalado. Siga os passos abaixo.

### 1. Configuração do Ambiente

Primeiro, clone o repositório e configure o ambiente virtual.

```bash
# 1. Navegue até a pasta raiz do projeto
cd smart_irrigation_system

# 2. Crie um ambiente virtual para isolar as dependências
python -m venv venv

# 3. Ative o ambiente virtual
# No Windows (PowerShell):
.\venv\Scripts\Activate.ps1

# No macOS/Linux:
source venv/bin/activate

# 4. Instale todas as bibliotecas necessárias a partir do arquivo requirements.txt
pip install -r requirements.txt
```

### 2. Executando a Aplicação de Console (CLI)

A aplicação de console é usada para gerenciar o banco de dados e treinar o modelo de IA.

```bash
python main.py
```

#### Uso Recomendado (Primeira Vez):

1. Use as opções **1, 2 e 3** para cadastrar Culturas, Setores e Sensores. **Anote os IDs!**
2. Navegue até o menu **9. Inteligência Preditiva**
3. Use a opção **3** para gerar dados históricos de exemplo
4. Use a opção **1** para treinar o modelo de IA com os dados gerados

### 3. Executando o Dashboard Web

O dashboard oferece uma visualização em tempo real dos dados do sistema.

Certifique-se de que seu ambiente virtual esteja ativo.

```bash
streamlit run dashboard.py
```

O comando acima iniciará um servidor web local e abrirá o dashboard no seu navegador padrão.

## 🗃 Histórico de lançamentos  
  
Fase 3: https://github.com/WKyuki/Cap1_MaqAgricola
