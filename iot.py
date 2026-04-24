import requests
import random
import time
from datetime import datetime


FIREBASE_URL = "https://banco-5cf3c-default-rtdb.firebaseio.com"

EQUIPAMENTOS = [
    {"nome": "Forno_Eletrico", "consumo_base": 4.5, "temp_base": 180},
    {"nome": "Freezer_Industrial", "consumo_base": 1.8, "temp_base": -15},
    {"nome": "Geladeira", "consumo_base": 1.2, "temp_base": 4},
    {"nome": "Iluminacao", "consumo_base": 0.8, "temp_base": 25},
]

def simular_leitura(equipamento):
    """
    Simula consumo (kWh) e temperatura do equipamento.
    Também injeta anomalias aleatórias.
    """
    consumo = equipamento["consumo_base"] + random.uniform(-0.3, 0.3)
    temperatura = equipamento["temp_base"] + random.uniform(-2, 2)

    # Simula status ON/OFF (mais provável ON)
    status = random.choices(["ON", "OFF"], weights=[90, 10])[0]

    if status == "OFF":
        consumo = 0
        # Temperatura tende ao ambiente quando OFF
        if equipamento["nome"] in ["Freezer_Industrial", "Geladeira"]:
            temperatura += random.uniform(5, 15)

    # Injeção de anomalias (picos)
    if random.random() < 0.05:  # 5% chance de anomalia
        consumo *= random.uniform(1.5, 3.0)
        temperatura += random.uniform(5, 20)

    consumo = round(consumo, 2)
    temperatura = round(temperatura, 2)

    return consumo, temperatura, status


def enviar_para_firebase(dado):
    """
    Envia dados para Firebase usando POST.
    """
    endpoint = f"{FIREBASE_URL}/leituras.json"
    response = requests.post(endpoint, json=dado)

    if response.status_code == 200:
        print("✅ Enviado:", dado)
    else:
        print("❌ Erro ao enviar:", response.text)


def main():
    print("🚀 Simulador IoT iniciado. Enviando dados para Firebase...")

    while True:
        timestamp = datetime.now().isoformat()

        for eq in EQUIPAMENTOS:
            consumo, temp, status = simular_leitura(eq)

            dado = {
                "timestamp": timestamp,
                "equipamento": eq["nome"],
                "consumo_kwh": consumo,
                "temperatura": temp,
                "status": status
            }

            enviar_para_firebase(dado)

        time.sleep(5)  # envia dados a cada 5 segundos


if __name__ == "__main__":
    main()