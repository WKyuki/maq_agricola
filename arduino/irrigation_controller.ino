#include <Arduino.h>
#include "DHT.h"
#include <Wire.h>
#include <LiquidCrystal_I2C.h>

// Definições de pinos - usando const para economizar RAM
const uint8_t DHTPIN = 15;         // uint8_t ao invés de #define - economiza memória
const uint8_t DHTTYPE = DHT22;
const uint8_t SENSOR_P = 2;
const uint8_t SENSOR_K = 4;
const uint8_t SENSOR_PH = 34;
const uint8_t RELE_PIN = 5;
const uint8_t LED_STATUS = 26;

// Pinos I2C para ESP32 (padrão)
const uint8_t SDA_PIN = 21;
const uint8_t SCL_PIN = 22;

// Constantes de limites - usando const para armazenar na Flash ao invés da RAM
const float HUMIDITY_THRESHOLD = 40.0f;  // f indica float literal - mais eficiente
const uint8_t PH_MIN = 0;
const uint8_t PH_MAX = 14;
const uint16_t ADC_MAX = 4095;           // uint16_t suficiente para ADC de 12 bits

// Inicialização dos objetos
DHT dht(DHTPIN, DHTTYPE);
LiquidCrystal_I2C lcd(0x27, 20, 4);  // Endereço I2C 0x27, display 20x4

// Variáveis globais otimizadas
uint32_t lastUpdate = 0;              // uint32_t para millis() - 4 bytes ao invés de long
const uint16_t UPDATE_INTERVAL = 2000; // Intervalo de atualização em ms

void setup() {
  Serial.begin(115200);
  
  // Inicialização do DHT22
  dht.begin();
  
  // Inicialização do LCD I2C
  Wire.begin(SDA_PIN, SCL_PIN);  // Inicializa I2C nos pinos específicos
  lcd.init();
  lcd.backlight();
  
  // Configuração dos pinos - agrupada para eficiência
  pinMode(SENSOR_P, INPUT_PULLUP);
  pinMode(SENSOR_K, INPUT_PULLUP);
  pinMode(RELE_PIN, OUTPUT);
  pinMode(LED_STATUS, OUTPUT);

  // Estados iniciais
  digitalWrite(RELE_PIN, LOW);
  digitalWrite(LED_STATUS, LOW);
  
  // Mensagem inicial no LCD
  lcd.setCursor(0, 0);
  lcd.print(F("Sistema Irrigacao"));  // F() armazena string na Flash - economiza RAM
  lcd.setCursor(0, 1);
  lcd.print(F("Inteligente"));
  lcd.setCursor(0, 2);
  lcd.print(F("Iniciando..."));
  
  delay(2000);
  lcd.clear();
  
  // Mensagens no Serial
  Serial.println(F("Sistema de Irrigação Inteligente Iniciado"));
  Serial.println(F("Condições para irrigação:"));
  Serial.println(F("- Umidade < 40%"));
  Serial.println(F("- Presença de fósforo OU potássio"));
  Serial.println(F("----------------------------------------"));
}

void loop() {
  uint32_t currentTime = millis();
  
  // Controle de timing otimizado - evita delay() que bloqueia o sistema
  if (currentTime - lastUpdate >= UPDATE_INTERVAL) {
    lastUpdate = currentTime;
    
    // Leitura dos sensores - usando tipos otimizados
    bool fosforo = (digitalRead(SENSOR_P) == LOW);
    bool potassio = (digitalRead(SENSOR_K) == LOW);
    
    // Leitura analógica otimizada
    uint16_t phAnalog = analogRead(SENSOR_PH);  // uint16_t suficiente para ADC
    float ph = map(phAnalog, PH_MIN, ADC_MAX, PH_MIN, PH_MAX);
    
    // Leitura da umidade com verificação de erro
    float humidity = dht.readHumidity();
    if (isnan(humidity)) {  // Verificação de erro do sensor DHT
      humidity = 0.0f;      // Valor padrão em caso de erro
      Serial.println(F("Erro na leitura do sensor DHT22"));
    }

    // Verificação das condições - usando variáveis booleanas compactas
    bool umidadeOk = (humidity < HUMIDITY_THRESHOLD);
    bool nutrientesOk = (fosforo || potassio);  // OR lógico otimizado
    bool irrigacaoAtiva = (umidadeOk && nutrientesOk);  // AND lógico das condições

    // Atualização do display LCD
    updateLCD(fosforo, potassio, ph, humidity, umidadeOk, nutrientesOk, irrigacaoAtiva);
    
    // Exibição otimizada no Serial Monitor
    printSerialData(fosforo, potassio, ph, humidity, umidadeOk, nutrientesOk, irrigacaoAtiva);

    // Controle da irrigação
    digitalWrite(RELE_PIN, irrigacaoAtiva ? HIGH : LOW);
    digitalWrite(LED_STATUS, irrigacaoAtiva ? HIGH : LOW);
  }
}

// Função para atualizar o LCD - separada para melhor organização e economia de stack
void updateLCD(bool fosforo, bool potassio, float ph, float humidity, 
               bool umidadeOk, bool nutrientesOk, bool irrigacaoAtiva) {
  
  lcd.clear();
  
  // Linha 1: Status da irrigação
  lcd.setCursor(0, 0);
  if (irrigacaoAtiva) {
    lcd.print(F("IRRIGACAO: ATIVA"));
  } else {
    lcd.print(F("IRRIGACAO: INATIVA"));
  }
  
  // Linha 2: Umidade
  lcd.setCursor(0, 1);
  lcd.print(F("Umidade: "));
  lcd.print(humidity, 1);  // 1 casa decimal
  lcd.print(F("%"));
  lcd.print(umidadeOk ? F(" LOW") : F(" OK"));
  
  // Linha 3: Nutrientes
  lcd.setCursor(0, 2);
  lcd.print(F("P:"));
  lcd.print(fosforo ? F("OK") : F("NO"));
  lcd.print(F(" K:"));
  lcd.print(potassio ? F("OK") : F("NO"));
  lcd.print(F(" pH:"));
  lcd.print(ph, 1);
  
  // Linha 4: Status geral
  lcd.setCursor(0, 3);
  if (irrigacaoAtiva) {
    lcd.print(F("Status: IRRIGANDO"));
  } else {
    lcd.print(F("Status: AGUARDANDO"));
  }
}

// Função para impressão no Serial - otimizada com F() macro
void printSerialData(bool fosforo, bool potassio, float ph, float humidity,
                     bool umidadeOk, bool nutrientesOk, bool irrigacaoAtiva) {
  
  Serial.print(F("Fósforo: "));
  Serial.print(fosforo ? F("PRESENTE") : F("AUSENTE"));
  Serial.print(F(" | Potássio: "));
  Serial.print(potassio ? F("PRESENTE") : F("AUSENTE"));
  Serial.print(F(" | pH: "));
  Serial.print(ph, 1);
  Serial.print(F(" | Umidade: "));
  Serial.print(humidity, 1);
  Serial.print(F("%"));
  Serial.print(umidadeOk ? F(" (BAIXA)") : F(" (ADEQUADA)"));
  Serial.print(F(" | Nutrientes: "));
  Serial.print(nutrientesOk ? F("OK") : F("INSUFICIENTES"));

  if (irrigacaoAtiva) {
    Serial.println(F(" -> IRRIGAÇÃO ATIVADA ✓"));
  } else {
    Serial.print(F(" -> IRRIGAÇÃO DESATIVADA - "));
    
    // Diagnóstico otimizado das condições não atendidas
    if (!umidadeOk) Serial.print(F("umidade alta "));
    if (!nutrientesOk) Serial.print(F("nutrientes insuficientes "));
    Serial.println();
  }
  
  Serial.println(F("----------------------------------------"));
}