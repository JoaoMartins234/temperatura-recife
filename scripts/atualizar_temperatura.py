import os
import json
import requests
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo

# Coordenadas de Recife
LAT = -8.0476
LON = -34.8770
TIMEZONE = "America/Recife"

# Códigos WMO para condições (Open-Meteo)
WMO_CODES = {
    0: "Céu limpo",
    1: "Principalmente limpo",
    2: "Parcialmente nublado",
    3: "Nublado",
    45: "Neblina",
    48: "Neblina com geada",
    51: "Garoa leve",
    53: "Garoa moderada",
    55: "Garoa intensa",
    61: "Chuva leve",
    63: "Chuva moderada",
    65: "Chuva forte",
    80: "Pancadas de chuva leve",
    81: "Pancadas de chuva moderada",
    82: "Pancadas de chuva forte",
    95: "Tempestade",
}

def get_open_meteo():
    url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={LAT}&longitude={LON}"
        f"&current=temperature_2m,weather_code"
        f"&daily=temperature_2m_max,temperature_2m_min,weather_code"
        f"&forecast_days=5&timezone={TIMEZONE}"
    )
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    return resp.json()

def try_inmet(token, estacao="A301"):
    """Tenta obter temperatura atual do INMET. Endpoint pode precisar de ajuste."""
    if not token:
        return None
    # Tentativa com endpoint comum (pode estar desatualizado)
    # Formato aproximado baseado em documentações antigas
    today = datetime.now().strftime("%Y-%m-%d")
    url = f"https://apitempo.inmet.gov.br/token/estacao/{today}/{estacao}/{token}"
    try:
        resp = requests.get(url, timeout=20)
        if resp.status_code == 200:
            data = resp.json()
            # Estrutura varia; tenta extrair temp mais recente
            if isinstance(data, list) and data:
                # Assume último registro tem TEMP_INS ou similar
                latest = data[-1]
                temp = latest.get("TEMP_INS") or latest.get("TEM_INS") or latest.get("temperature")
                if temp is not None:
                    return float(temp)
    except Exception as e:
        print(f"INMET falhou: {e}")
    return None

def main():
    token = os.environ.get("INMET_TOKEN")
    estacao = os.environ.get("INMET_ESTACAO", "A301")

    fonte = "Open-Meteo"
    temp_atual = None

    # Tenta INMET primeiro para temperatura atual
    inmet_temp = try_inmet(token, estacao)
    if inmet_temp is not None:
        temp_atual = inmet_temp
        fonte = f"INMET (estação {estacao})"
    else:
        print("INMET não disponível ou sem token; usando Open-Meteo.")

    # Sempre pega previsão e condição do Open-Meteo
    om = get_open_meteo()
    current = om.get("current", {})
    if temp_atual is None:
        temp_atual = current.get("temperature_2m")
    weather_code = current.get("weather_code", 0)
    condicao = WMO_CODES.get(weather_code, "Desconhecido")

    # Previsão diária
    daily = om.get("daily", {})
    previsao = []
    times = daily.get("time", [])
    maxs = daily.get("temperature_2m_max", [])
    mins = daily.get("temperature_2m_min", [])
    codes = daily.get("weather_code", [])
    for i in range(min(5, len(times))):
        code = codes[i] if i < len(codes) else 0
        previsao.append({
            "data": times[i],
            "temp_max": maxs[i] if i < len(maxs) else None,
            "temp_min": mins[i] if i < len(mins) else None,
            "condicao": WMO_CODES.get(code, "Desconhecido"),
            "weather_code": code
        })

    # Timestamp local
    now = datetime.now(ZoneInfo(TIMEZONE))
    output = {
        "atualizado_em": now.isoformat(),
        "fonte": fonte,
        "temperatura_atual": round(temp_atual, 1) if temp_atual is not None else None,
        "condicao": condicao,
        "weather_code": weather_code,
        "previsao": previsao
    }

    with open("temperatura.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"Atualizado: {output['temperatura_atual']}°C via {fonte}")

if __name__ == "__main__":
    main()
