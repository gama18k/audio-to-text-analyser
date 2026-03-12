# Este modulo traduz a resposta textual do modelo para uma estrutura valida.
# Ele concentra o parsing do JSON, a normalizacao do Q&A e as validacoes
# necessarias antes da aplicacao persistir ou reutilizar o resultado.

import json


def extrair_json_resposta(resposta: str) -> dict:
    """Extrai o primeiro objeto JSON valido da resposta do modelo."""
    texto = resposta.strip()

    if texto.startswith("```"):
        linhas = texto.splitlines()
        if len(linhas) >= 3:
            texto = "\n".join(linhas[1:-1]).strip()

    inicio = texto.find("{")
    if inicio == -1:
        raise RuntimeError("❌ A resposta do modelo nao veio em JSON valido.")

    try:
        decoder = json.JSONDecoder()
        objeto, _ = decoder.raw_decode(texto[inicio:])
        return objeto
    except json.JSONDecodeError as e:
        raise RuntimeError(f"❌ Erro ao converter resposta do modelo para JSON: {e}") from e


def validar_analise_estruturada(dados: dict) -> dict:
    """Valida e normaliza a estrutura final retornada pelo LLM."""
    campos_obrigatorios = [
        "transcricao_limpa",
        "resumo",
        "motivo_contato",
        "proximos_passos",
        "categoria",
        "subcategoria",
        "sentimento_cliente",
        "ha_pendencias",
        "perguntas_respostas",
        "necessita_followup",
        "houve_confirmacao_dados",
    ]

    faltando = [campo for campo in campos_obrigatorios if campo not in dados]
    if faltando:
        raise RuntimeError(
            "❌ JSON da analise incompleto. Campos ausentes: "
            + ", ".join(faltando)
        )

    dados.setdefault("pendencias", [])
    if not isinstance(dados["pendencias"], list):
        dados["pendencias"] = [str(dados["pendencias"])]

    if not isinstance(dados["perguntas_respostas"], list):
        raise RuntimeError("❌ O campo perguntas_respostas deve ser uma lista.")

    qa_normalizado = []
    for item in dados["perguntas_respostas"]:
        if not isinstance(item, dict):
            continue
        pergunta = str(item.get("pergunta", "")).strip()
        resposta = str(item.get("resposta", "")).strip()
        if pergunta and resposta:
            qa_normalizado.append({
                "pergunta": pergunta,
                "resposta": resposta,
            })
    dados["perguntas_respostas"] = qa_normalizado

    dados["ha_pendencias"] = bool(dados["ha_pendencias"])
    dados["necessita_followup"] = bool(dados["necessita_followup"])
    dados["houve_confirmacao_dados"] = bool(dados["houve_confirmacao_dados"])

    return dados
