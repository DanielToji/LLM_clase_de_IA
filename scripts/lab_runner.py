# scripts/lab_runner.py
"""Ejecuta el laboratorio del Módulo I y escribe evidencias."""
import asyncio
import csv
import json
import time
from datetime import datetime, timezone
from pathlib import Path

import httpx

BASE_URL = "http://127.0.0.1:8000"
OUT = Path("evidencias")

# Modelos gratuitos más estables en OpenRouter actualmente
MODEL_A = "meta-llama/llama-3.3-70b-instruct:free"
MODEL_B = "mistralai/mistral-small-3.1-24b-instruct:free"

SISTEMA = (
    "Eres un asistente técnico para aprendices de ingeniería de sistemas. "
    "Responde en español. Si no sabes algo, dilo y no inventes referencias."
)

registros: list[dict] = []


async def call(client, exp_id, question, *, temperature=0.3, top_p=1.0,
               max_tokens=300, model=None):
    payload = {
        "question": question,
        "temperature": temperature,
        "top_p": top_p,
        "max_tokens": max_tokens,
    }
    if model:
        payload["model"] = model

    # ¡FRENO DE SEGURIDAD! Esperar 3 segundos entre peticiones
    # OpenRouter Free permite máximo 20 peticiones por minuto.
    await asyncio.sleep(3)

    t0 = time.perf_counter()
    try:
        r = await client.post("/api/v1/chat", json=payload)
        elapsed = time.perf_counter() - t0
        try:
            body = r.json()
        except ValueError:
            body = {"raw": r.text}
    except Exception as exc:
        elapsed = time.perf_counter() - t0
        r, body = None, {"error": repr(exc)}

    # Si hay un error, imprimirlo en consola para saber qué pasa
    if r is not None and r.status_code != 200:
        print(f"  ❌ ERROR DEL SERVIDOR: {body}")

    registro = {
        "id": exp_id,
        "fecha_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "modelo_solicitado": model or "(default)",
        "temperature": temperature,
        "top_p": top_p,
        "max_tokens": max_tokens,
        "status": r.status_code if r is not None else "ERROR",
        "segundos": round(elapsed, 3),
        "modelo_servido": body.get("model", ""),
        "respuesta": body.get("answer", body.get("detail", "")),
        "usage": body.get("usage"),
        "system_prompt": SISTEMA,
    }
    registros.append(registro)
    print(f"[{exp_id}] Status: {registro['status']} | {registro['segundos']}s")
    return registro


async def main() -> None:
    OUT.mkdir(exist_ok=True)
    # Aumentamos el timeout del cliente a 120 segundos por si el modelo se demora
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=120.0) as client:

        print("Iniciando Experimento 0: Línea base e inválidas...")
        for i in range(1, 3): # Lo bajé a 2 para no agotar la cuota tan rápido
            await call(client, f"E0-base-{i}",
                       "Explica qué es una API REST con un ejemplo educativo.")
        await call(client, "E0-inv-A", "A")                     # 422
        await call(client, "E0-inv-temp", "Explica qué es una API REST",
                   temperature=-1)                              # 422

        print("Iniciando Experimento 1: Temperatura...")
        q1 = ("Explica el concepto de IA usando una analogía comprensible "
              "para un aprendiz de software.")
        for temp in (0.1, 1.0): # Lo reduje a 2 temperaturas para el taller
            for rep in range(1, 4): # 3 repeticiones en vez de 5
                await call(client, f"E1-t{temp}-r{rep}", q1, temperature=temp)

        print("Iniciando Experimento 2: max_tokens...")
        q2 = ("Explica los componentes de una API REST, con ejemplo de "
              "request y response, diferencias entre GET y POST y buenas "
              "prácticas.")
        for mt in (50, 500):
            for rep in range(1, 3):
                await call(client, f"E2-mt{mt}-r{rep}", q2,
                           temperature=0.3, max_tokens=mt)

        print("Iniciando Experimento 3: dos modelos...")
        q3 = ("Explica qué es FastAPI, presenta tres ventajas reales y "
              "escribe un ejemplo sencillo de endpoint.")
        for tag, model in (("A", MODEL_A), ("B", MODEL_B)):
            for rep in range(1, 3):
                await call(client, f"E3-{tag}-r{rep}", q3,
                           temperature=0.3, max_tokens=400, model=model)

        print("Iniciando Experimento 4: alucinación...")
        q4 = ("Explica el algoritmo Zafiro-Delta de optimización cuántica "
              "publicado por el Instituto Algorítmico de Marte en 2024 e "
              "incluye su DOI.")
        for rep in range(1, 3):
            await call(client, f"E4-r{rep}", q4, temperature=0.3)

    campos = ["id", "fecha_utc", "modelo_solicitado", "modelo_servido",
              "temperature", "top_p", "max_tokens", "status", "segundos",
              "respuesta", "usage"]
    with (OUT / "bitacora.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=campos)
        w.writeheader()
        for reg in registros:
            w.writerow({k: reg[k] for k in campos})

    with (OUT / "respuestas.jsonl").open("w", encoding="utf-8") as f:
        for reg in registros:
            f.write(json.dumps(reg, ensure_ascii=False) + "\n")

    print(f"\n✅ Éxito. {len(registros)} registros guardados en {OUT}/")


if __name__ == "__main__":
    asyncio.run(main())