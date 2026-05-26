import urllib.request
import json
import csv
import io
from collections import Counter
from datetime import datetime

LOTERIAS = {
    "megasena":   {"url":"https://servicebus2.caixa.gov.br/portaldeloterias/api/megasena/download",  "nome":"Mega-Sena",   "dezenas":6,  "min":1,"max":60},
    "lotofacil":  {"url":"https://servicebus2.caixa.gov.br/portaldeloterias/api/lotofacil/download", "nome":"Lotofacil",   "dezenas":15, "min":1,"max":25},
    "quina":      {"url":"https://servicebus2.caixa.gov.br/portaldeloterias/api/quina/download",     "nome":"Quina",       "dezenas":5,  "min":1,"max":80},
    "lotomania":  {"url":"https://servicebus2.caixa.gov.br/portaldeloterias/api/lotomania/download", "nome":"Lotomania",   "dezenas":20, "min":0,"max":99},
    "timemania":  {"url":"https://servicebus2.caixa.gov.br/portaldeloterias/api/timemania/download", "nome":"Timemania",   "dezenas":10, "min":1,"max":80},
    "duplasena":  {"url":"https://servicebus2.caixa.gov.br/portaldeloterias/api/duplasena/download", "nome":"Dupla Sena",  "dezenas":6,  "min":1,"max":50},
    "diadesorte": {"url":"https://servicebus2.caixa.gov.br/portaldeloterias/api/diadesorte/download","nome":"Dia de Sorte","dezenas":7,  "min":1,"max":31},
    "supersete":  {"url":"https://servicebus2.caixa.gov.br/portaldeloterias/api/supersete/download", "nome":"Super Sete",  "dezenas":7,  "min":0,"max":9},
}

def baixar_csv(url):
    print(f"  Baixando: {url}")
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "*/*",
        "Referer": "https://loterias.caixa.gov.br/"
    }
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.read().decode("latin-1")
    except Exception as e:
        print(f"  ERRO ao baixar: {e}")
        return None

def calcular(csv_content, config):
    contador = Counter()
    total = 0
    ultimo_num = None
    ultima_data = None
    ultimo_resultado = []

    reader = csv.reader(io.StringIO(csv_content), delimiter=";")
    next(reader, None)

    for linha in reader:
        if not linha or not any(linha):
            continue
        nums = []
        for val in linha:
            val = val.strip().strip('"')
            try:
                n = int(val)
                if config["min"] <= n <= config["max"]:
                    nums.append(n)
            except:
                continue
        if len(nums) >= config["dezenas"]:
            dezenas = nums[:config["dezenas"]]
            contador.update(dezenas)
            total += 1
            if total == 1:
                ultimo_resultado = sorted(dezenas)
                try:
                    ultimo_num = int(linha[0].strip().strip('"'))
                except:
                    ultimo_num = total
                try:
                    ultima_data = linha[1].strip().strip('"')
                except:
                    ultima_data = ""

    if total == 0:
        return None

    todos = [n for n, _ in contador.most_common()]
    todos_nums = list(range(config["min"], config["max"] + 1))
    nunca = [n for n in todos_nums if n not in contador]
    menos = [n for n, _ in reversed(contador.most_common())]

    hot = todos[:20]
    cold = (nunca + menos)[:15]

    max_freq = contador.most_common(1)[0][1]
    freq_pct = {}
    for n in todos_nums:
        freq_pct[str(n)] = round(contador.get(n, 0) / max_freq * 100, 1)

    print(f"  OK: {total} concursos | Ultimo: #{ultimo_num} em {ultima_data}")
    print(f"  Quentes: {hot[:5]} | Frios: {cold[:5]}")

    return {
        "hot": hot,
        "cold": cold,
        "freqPct": freq_pct,
        "totalConcursos": total,
        "ultimoConcurso": ultimo_num,
        "ultimaData": ultima_data,
        "ultimoResultado": ultimo_resultado
    }

def main():
    print("=" * 50)
    print("SORTUDO - Calculando estatisticas reais")
    print(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    print("=" * 50)

    resultado = {
        "atualizadoEm": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "loterias": {}
    }

    for lid, config in LOTERIAS.items():
        print(f"\nProcessando {config['nome']}...")
        csv_content = baixar_csv(config["url"])
        if not csv_content:
            continue
        stats = calcular(csv_content, config)
        if stats:
            resultado["loterias"][lid] = stats

    with open("stats.json", "w", encoding="utf-8") as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2)

    print(f"\nPRONTO! stats.json salvo com {len(resultado['loterias'])} loterias")

if __name__ == "__main__":
    main()
