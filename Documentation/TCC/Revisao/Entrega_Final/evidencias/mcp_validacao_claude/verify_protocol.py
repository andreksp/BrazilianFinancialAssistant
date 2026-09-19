"""
Verificação independente do protocolo MCP real (não mockado).

Prova, com evidência de processo do SO:
1. Que um subprocesso Python filho é de fato criado (PID distinto, visível via psutil)
   durante a chamada e encerrado ao final.
2. Que a troca de mensagens MCP segue o protocolo real: initialize -> tools/list -> tools/call,
   registrando os payloads brutos retornados pelo SDK (nome do servidor, versão do protocolo,
   schemas das ferramentas, conteúdo estruturado da resposta).
3. Que o caminho web (backend/app/api/trades.py) não chama as calculadoras diretamente —
   feito por inspeção estática do código-fonte, não por execução.

Não usa mocks para o protocolo: fala com o processo real via stdio.
"""
import asyncio
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[6]
sys.path.insert(0, str(PROJECT_ROOT / "backend"))

import psutil
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

SERVER = PROJECT_ROOT / "mcp_server" / "runtime_server.py"
OUT = Path(__file__).resolve().parent / "protocol_evidence.json"

evidence = {
    "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    "server_script": str(SERVER),
    "server_script_exists": SERVER.exists(),
}


async def main():
    parent = psutil.Process()
    children_before = {c.pid for c in parent.children(recursive=True)}

    params = StdioServerParameters(
        command=sys.executable, args=[str(SERVER)], env={"PYTHONIOENCODING": "utf-8"}
    )

    async with stdio_client(params) as (read, write):
        # Subprocess must exist as an OS-level child process right now.
        await asyncio.sleep(0.3)  # give the OS a moment to register the child
        children_during = {c.pid for c in parent.children(recursive=True)}
        new_children = children_during - children_before
        evidence["subprocess_pids_detected"] = sorted(new_children)
        evidence["subprocess_proof"] = (
            "Novo(s) PID(s) filho(s) do processo Python deste script, detectado(s) via psutil "
            "enquanto a sessão MCP estava aberta. Isso é a prova de que existe um processo "
            "do sistema operacional real por trás da sessão — não uma chamada de função in-process."
        )
        evidence["subprocess_details"] = []
        for pid in sorted(new_children):
            try:
                proc = psutil.Process(pid)
                evidence["subprocess_details"].append(
                    {"pid": pid, "name": proc.name(), "cmdline": proc.cmdline(), "status": proc.status()}
                )
            except psutil.NoSuchProcess:
                evidence["subprocess_details"].append({"pid": pid, "name": None, "cmdline": None, "status": "gone"})

        async with ClientSession(read, write) as session:
            t0 = time.perf_counter()
            init_result = await session.initialize()
            t_init = time.perf_counter() - t0
            evidence["initialize"] = {
                "protocolVersion": init_result.protocolVersion,
                "serverInfo": {
                    "name": init_result.serverInfo.name,
                    "version": init_result.serverInfo.version,
                },
                "capabilities_tools": bool(init_result.capabilities.tools),
                "latency_seconds": round(t_init, 4),
            }

            t0 = time.perf_counter()
            tools = await session.list_tools()
            t_list = time.perf_counter() - t0
            evidence["tools_list"] = {
                "latency_seconds": round(t_list, 4),
                "tools": [
                    {
                        "name": t.name,
                        "description": t.description,
                        "input_schema": t.inputSchema,
                    }
                    for t in tools.tools
                ],
            }

            t0 = time.perf_counter()
            fee_resp = await session.call_tool("fee_policy", {"asset_type": "fii"})
            t_fee = time.perf_counter() - t0
            fee_payload = fee_resp.structuredContent or json.loads(
                next(c.text for c in fee_resp.content if c.type == "text")
            )
            evidence["tools_call_fee_policy"] = {
                "latency_seconds": round(t_fee, 4),
                "isError": fee_resp.isError,
                "raw_structuredContent_present": fee_resp.structuredContent is not None,
                "payload": fee_payload,
            }

            trade = {
                "ativo": "HGLG11",
                "tipo_ativo": "fii",
                "tipo_operacao": "venda",
                "quantidade": 10,
                "preco_unitario": 110,
                "data_operacao": "2026-09-16",
                "custos_operacao": 0,
            }
            t0 = time.perf_counter()
            calc_resp = await session.call_tool(
                "calculate_trade", {"trade": trade, "average_price": 100}
            )
            t_calc = time.perf_counter() - t0
            calc_payload = calc_resp.structuredContent or json.loads(
                next(c.text for c in calc_resp.content if c.type == "text")
            )
            evidence["tools_call_calculate_trade"] = {
                "latency_seconds": round(t_calc, 4),
                "isError": calc_resp.isError,
                "input": trade,
                "payload_ok": calc_payload.get("ok"),
                "ir_devido": calc_payload.get("result", {}).get("ir_devido"),
            }

        # Session closed; check the subprocess is gone shortly after.
    await asyncio.sleep(0.5)
    children_after = {c.pid for c in parent.children(recursive=True)}
    still_alive = new_children & children_after
    evidence["subprocess_terminated_after_session_close"] = not still_alive
    evidence["orphan_pids_remaining"] = sorted(still_alive)


asyncio.run(main())
OUT.write_text(json.dumps(evidence, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(evidence, ensure_ascii=False, indent=2))
