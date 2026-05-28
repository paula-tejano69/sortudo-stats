import urllib.request
import json
import time
from collections import Counter
from datetime import datetime

WORKER_BASE = "https://sortudo-api.gabriel-eca1908.workers.dev/api"
CONCURSOS_POR_LOTERIA = 200

LOTERIAS = [
    {"id": "megasena",   "apiId": "megasena",   "nome": "Mega-Sena",   "dezenas": 6,  "min": 1, "max": 60},
    {"id": "lotofacil",  "apiId": "lotofacil",  "nome": "Lotofacil",   "dezenas": 15, "min": 1, "max": 25},
    {"id": "quina",      "apiId": "quina",       "nome": "Quina",       "dezenas": 5,  "min": 1, "max": 80},
    {"id": "lotomania",  "apiId": "lotomania",   "nome": "Lotomania",   "dezenas": 20, "min": 0, "max": 99},
    {"id": "timemania",  "apiId": "timemania",   "nome": "Timemania",   "dezenas": 10, "min": 1, "max": 80},
    {"id": "duplasena",  "apiId": "duplasena",   "nome": "Dupla Sena",  "dezenas": 6,  "min": 1, "max": 50},
    {"id": "diadesorte", "apiId": "diadesorte",  "nome": "Dia de Sorte","dezenas": 7,  "min": 1, "max": 31},
    {"id": "supersete",  "apiId": "supersete",   "nome": "Super Sete",  "dezenas": 7,  "min": 0, "max": 9},
]

def fetch_json(url, tentativas=3):
    for tentativa in range(tentativas):
        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "Mozilla/5.0", "Accept": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception as e:
            print(f"    tentativa {tentativa+1} falhou: {e}")
            if tentativa < tentativas - 1:
                time.sleep(2)
    return None

def buscar_ultimo(api_id):
    data = fetch_json(f"{WORKER_BASE}/{api_id}/latest")
    if data and data.get("concurso"):
        return data["concurso"], data
    return None, None

def calcular(loteria):
    api_id = loteria["apiId"]
    nome = loteria["nome"]
    print(f"\nProcessando {nome}...")

    ultimo_num, ultimo_data = buscar_ultimo(api_id)
    if not ultimo_num:
        print(f"  ERRO: nao consegui buscar o ultimo concurso")
        return None

    print(f"  Ultimo concurso: #{ultimo_num}")

    contador = Counter()
    concursos_ok = 0
    ultimo_resultado = []
    ultima_data_str = ""

    if ultimo_data and ultimo_data.get("dezenas"):
        contador.update(ultimo_data["dezenas"])
        concursos_ok += 1
        ultimo_resultado = sorted(ultimo_data["dezenas"])
        ultima_data_str = ultimo_data.get("data", "")

    inicio = ultimo_num - 1
    fim = max(1, ultimo_num - CONCURSOS_POR_LOTERIA + 1)

    for num in range(inicio, fim - 1, -1):
        data = fetch_json(f"{WORKER_BASE}/{api_id}/{num}")
        if data and data.get("dezenas"):
            contador.update(data["dezenas"])
            concursos_ok += 1
        if concursos_ok % 25 == 0:
            print(f"  ... {concursos_ok}/{CONCURSOS_POR_LOTERIA} concursos")
        time.sleep(0.05)

    if concursos_ok == 0:
        print(f"  ERRO: nenhum concurso processado")
        return None

    print(f"  OK: {concursos_ok} concursos analisados")

    todos = list(range(loteria["min"], loteria["max"] + 1))
    ordenados = [n for n, _ in contador.most_common()]

    hot = ordenados[:20]
    nunca = [n for n in todos if n not in contador]
    menos = [n for n, _ in reversed(contador.most_common())]
    cold = (nunca + menos)[:15]

    # Contagem ABSOLUTA real de cada dezena
    contagem = {}
    for n in todos:
        contagem[str(n)] = contador.get(n, 0)

    # freqPct para compatibilidade
    max_freq = contador.most_common(1)[0][1] if contador else 1
    freq_pct = {}
    for n in todos:
        freq_pct[str(n)] = round(contador.get(n, 0) / max_freq * 100, 1)

    print(f"  Quentes: {hot[:5]}")
    print(f"  Frios:   {cold[:5]}")
    print(f"  Dezena {hot[0]} saiu {contador[hot[0]]}x em {concursos_ok} concursos")

    return {
        "hot": hot,
        "cold": cold,
        "contagem": contagem,
        "freqPct": freq_pct,
        "totalConcursos": concursos_ok,
        "ultimoConcurso": ultimo_num,
        "ultimaData": ultima_data_str,
        "ultimoResultado": ultimo_resultado
    }

def main():
    print("=" * 50)
    print("SORTUDO - Estatisticas REAIS v2")
    print(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    print("Salva contagem absoluta real de cada dezena")
    print("=" * 50)

    resultado = {
        "atualizadoEm": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "loterias": {}
    }

    for loteria in LOTERIAS:
        stats = calcular(loteria)
        if stats:
            resultado["loterias"][loteria["id"]] = stats
            print(f"  OK {loteria['nome']}")
        else:
            print(f"  FALHOU {loteria['nome']}")

    with open("stats.json", "w", encoding="utf-8") as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2)

    print(f"\nCONCLUIDO! {len(resultado['loterias'])}/8 loterias")

if __name__ == "__main__":
    main()
