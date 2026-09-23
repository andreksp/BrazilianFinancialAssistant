"""
Mede se a rota de chat (agora `def`, executada em threadpool pelo FastAPI)
ainda bloqueia o serviço completo durante a janela da requisição.

Método: dispara uma requisição de chat (lenta, ~3 chamadas ao "modelo" com
latência artificial + subprocesso MCP real) e, em paralelo, faz batimentos
em /health a cada 50 ms. Se o serviço bloqueia, os batimentos param.

Comparação de referência: mede também os batimentos com o serviço ocioso.
"""
import json
import threading
import time
from pathlib import Path
from urllib.request import urlopen, Request

BASE = "http://127.0.0.1:8030"
resultados = {}


def batimentos(duracao, parar):
    tempos = []
    inicio = time.perf_counter()
    while not parar.is_set() and time.perf_counter() - inicio < duracao:
        t0 = time.perf_counter()
        try:
            with urlopen(f"{BASE}/health", timeout=10) as r:
                r.read()
            tempos.append((time.perf_counter() - inicio, time.perf_counter() - t0))
        except Exception as e:
            tempos.append((time.perf_counter() - inicio, None))
        time.sleep(0.05)
    return tempos


def medir(nome, acao=None, duracao=12):
    parar = threading.Event()
    coletados = []

    def alvo():
        coletados.extend(batimentos(duracao, parar))

    t = threading.Thread(target=alvo)
    t.start()
    time.sleep(0.4)  # deixa acumular batimentos antes

    saida_acao = None
    t_acao = None
    if acao:
        t0 = time.perf_counter()
        saida_acao = acao()
        t_acao = time.perf_counter() - t0

    time.sleep(0.4)  # batimentos depois
    parar.set()
    t.join()

    marcas = [m for m, _ in coletados]
    intervalos = [b - a for a, b in zip(marcas, marcas[1:])]
    latencias = [l for _, l in coletados if l is not None]
    falhas = sum(1 for _, l in coletados if l is None)

    resultados[nome] = {
        "batimentos": len(coletados),
        "batimentos_falhos": falhas,
        "maior_intervalo_s": round(max(intervalos), 3) if intervalos else None,
        "intervalo_mediano_s": round(sorted(intervalos)[len(intervalos) // 2], 3) if intervalos else None,
        "maior_latencia_health_s": round(max(latencias), 3) if latencias else None,
        "duracao_acao_s": round(t_acao, 3) if t_acao else None,
        "resposta_acao": saida_acao,
    }
    print(f"[{nome}] batimentos={len(coletados)} falhos={falhas} "
          f"maior_intervalo={resultados[nome]['maior_intervalo_s']}s "
          f"maior_latencia_health={resultados[nome]['maior_latencia_health_s']}s "
          f"duracao_acao={resultados[nome]['duracao_acao_s']}s")


def chat(mensagem="Vendi as 10 cotas do HGLG11 a 110 reais hoje"):
    corpo = json.dumps({"message": mensagem}).encode()
    req = Request(f"{BASE}/api/chat/", data=corpo, headers={"Content-Type": "application/json"})
    with urlopen(req, timeout=120) as r:
        d = json.loads(r.read())
    return {"agent_name": d.get("agent_name"),
            "tem_calculo": d.get("calculation_result") is not None,
            "ir_devido": (d.get("calculation_result") or {}).get("ir_devido")}


def chats_concorrentes(n=3):
    saidas = []
    erros = []

    def um():
        try:
            saidas.append(chat())
        except Exception as e:
            erros.append(f"{type(e).__name__}: {e}")

    ts = [threading.Thread(target=um) for _ in range(n)]
    t0 = time.perf_counter()
    for t in ts:
        t.start()
    for t in ts:
        t.join()
    return {"n": n, "ok": len(saidas), "erros": erros,
            "tempo_total_s": round(time.perf_counter() - t0, 3), "amostra": saidas[:1]}


if __name__ == "__main__":
    medir("ocioso_referencia", None, duracao=3)
    medir("durante_um_chat", chat, duracao=25)
    medir("durante_tres_chats_concorrentes", lambda: chats_concorrentes(3), duracao=40)

    out = Path(__file__).resolve().parent / "resultados_concorrencia_servico.json"
    out.write_text(json.dumps(resultados, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nSalvo em {out}")
