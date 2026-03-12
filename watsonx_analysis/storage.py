# Este modulo centraliza a persistencia e a montagem dos artefatos de saida.
# Ele grava texto, JSON e CSV, alem de construir o objeto estruturado que
# conecta metadados, transcricao e analise reutilizavel por outros setores.

import csv
import json
from datetime import datetime, timezone
from pathlib import Path


def salvar_texto(texto: str, caminho: Path):
    """Salva texto em arquivo, criando pastas se necessario."""
    try:
        caminho.parent.mkdir(parents=True, exist_ok=True)
        with open(caminho, "w", encoding="utf-8") as f:
            f.write(texto)
        print(f"✔ Arquivo salvo: {caminho}")
    except Exception as e:
        print(f"❌ Erro ao salvar arquivo {caminho}: {e}")


def salvar_json(dados: dict, caminho: Path):
    """Salva um dicionario em JSON legivel."""
    try:
        caminho.parent.mkdir(parents=True, exist_ok=True)
        with open(caminho, "w", encoding="utf-8") as f:
            json.dump(dados, f, ensure_ascii=False, indent=2)
        print(f"✔ Arquivo salvo: {caminho}")
    except Exception as e:
        print(f"❌ Erro ao salvar arquivo {caminho}: {e}")


def salvar_qa_csv(perguntas_respostas: list[dict], caminho: Path):
    """Salva um CSV com uma linha por pergunta e resposta."""
    try:
        caminho.parent.mkdir(parents=True, exist_ok=True)
        with open(caminho, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["pergunta", "resposta"])
            writer.writeheader()
            writer.writerows(perguntas_respostas)
        print(f"✔ Arquivo salvo: {caminho}")
    except Exception as e:
        print(f"❌ Erro ao salvar arquivo {caminho}: {e}")


def salvar_qa_consolidado_csv(dados: dict, caminho: Path):
    """Salva um CSV com metadados e uma linha por pergunta e resposta."""
    try:
        caminho.parent.mkdir(parents=True, exist_ok=True)
        metadados = dados["metadados"]
        analise = dados["analise"]
        perguntas_respostas = analise["perguntas_respostas"]

        fieldnames = [
            "arquivo_origem",
            "data_processamento",
            "content_type",
            "stt_model",
            "llm_model",
            "categoria",
            "subcategoria",
            "sentimento_cliente",
            "ha_pendencias",
            "necessita_followup",
            "houve_confirmacao_dados",
            "pergunta",
            "resposta",
        ]

        with open(caminho, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            for item in perguntas_respostas:
                writer.writerow({
                    "arquivo_origem": metadados["arquivo_origem"],
                    "data_processamento": metadados["data_processamento"],
                    "content_type": metadados["content_type"],
                    "stt_model": metadados["stt_model"],
                    "llm_model": metadados["llm_model"],
                    "categoria": analise["categoria"],
                    "subcategoria": analise["subcategoria"],
                    "sentimento_cliente": analise["sentimento_cliente"],
                    "ha_pendencias": analise["ha_pendencias"],
                    "necessita_followup": analise["necessita_followup"],
                    "houve_confirmacao_dados": analise["houve_confirmacao_dados"],
                    "pergunta": item["pergunta"],
                    "resposta": item["resposta"],
                })
        print(f"✔ Arquivo salvo: {caminho}")
    except Exception as e:
        print(f"❌ Erro ao salvar arquivo {caminho}: {e}")


def montar_saida_estruturada(
    caminho_audio: Path,
    caminho_prompt: Path,
    content_type: str,
    stt_model: str,
    llm_model: str,
    transcricao_bruta: str,
    analise: dict,
    tempo_transcricao_segundos: float,
    tempo_inferencia_segundos: float,
    tempo_total_segundos: float,
) -> dict:
    """Monta o dicionario final de saida estruturada."""
    return {
        "metadados": {
            "arquivo_origem": caminho_audio.name,
            "tamanho_arquivo_bytes": caminho_audio.stat().st_size,
            "content_type": content_type,
            "stt_model": stt_model,
            "llm_model": llm_model,
            "prompt_arquivo": str(caminho_prompt),
            "data_processamento": datetime.now(timezone.utc).isoformat(),
            "quantidade_perguntas_respostas": len(analise["perguntas_respostas"]),
            "tempo_transcricao_segundos": tempo_transcricao_segundos,
            "tempo_inferencia_segundos": tempo_inferencia_segundos,
            "tempo_total_segundos": tempo_total_segundos,
        },
        "transcricao": {
            "bruta": transcricao_bruta,
            "limpa": analise["transcricao_limpa"],
        },
        "analise": {
            "resumo": analise["resumo"],
            "motivo_contato": analise["motivo_contato"],
            "proximos_passos": analise["proximos_passos"],
            "categoria": analise["categoria"],
            "subcategoria": analise["subcategoria"],
            "sentimento_cliente": analise["sentimento_cliente"],
            "ha_pendencias": analise["ha_pendencias"],
            "pendencias": analise["pendencias"],
            "perguntas_respostas": analise["perguntas_respostas"],
            "necessita_followup": analise["necessita_followup"],
            "houve_confirmacao_dados": analise["houve_confirmacao_dados"],
        },
    }


def formatar_relatorio_analise(dados: dict) -> str:
    """Gera o relatorio textual apenas com perguntas e respostas."""
    analise = dados["analise"]
    perguntas_respostas = analise["perguntas_respostas"] or []
    if perguntas_respostas:
        return "\n\n".join(
            f"Pergunta:\n{item['pergunta']}\n\nResposta:\n{item['resposta']}"
            for item in perguntas_respostas
        )
    return "Nenhum Q&A identificado."
