# Este arquivo e o ponto de entrada da aplicacao.
# Ele faz a orquestracao do pipeline usando os modulos auxiliares:
# resolve argumentos, valida configuracao, chama STT, chama watsonx
# e dispara a gravacao dos outputs gerados pelos demais componentes.

import os
from pathlib import Path
import argparse
from time import perf_counter

from dotenv import load_dotenv
from watsonx_analysis.config import (
    PROMPT_PADRAO,
    detectar_content_type,
    listar_audios_disponiveis,
    resolver_llm_model,
    resolver_stt_model,
)
from watsonx_analysis.observability import log_etapa_fim, log_etapa_inicio
from watsonx_analysis.parsing import extrair_json_resposta, validar_analise_estruturada
from watsonx_analysis.prompt_utils import carregar_template_prompt, montar_prompt
from watsonx_analysis.services import analisar_ligacao, transcrever_audio_ibm
from watsonx_analysis.storage import (
    formatar_relatorio_analise,
    montar_saida_estruturada,
    salvar_json,
    salvar_qa_consolidado_csv,
    salvar_qa_csv,
    salvar_texto,
)

load_dotenv()


# MAIN

def main():
    parser = argparse.ArgumentParser(description="Transcrever e analisar ligação")
    parser.add_argument("audio", nargs="?", help="Caminho para o arquivo de audio a ser processado")
    parser.add_argument(
        "--prompt-file",
        default=str(PROMPT_PADRAO),
        help="Caminho para o arquivo de prompt usado na analise",
    )
    parser.add_argument(
        "--stt-model",
        help="Modelo do IBM Speech to Text para a transcricao",
    )
    parser.add_argument(
        "--llm-model",
        help="Modelo do watsonx usado na analise",
    )
    args = parser.parse_args()

    if not args.audio:
        audios_disponiveis = listar_audios_disponiveis(Path.cwd())
        print("❌ Nenhum arquivo de audio foi informado.")

        if audios_disponiveis:
            # Quando o usuario esquece o argumento, a CLI tenta orientar o proximo comando.
            print("\nArquivos de audio encontrados na pasta atual:")
            for audio in audios_disponiveis:
                print(f"- {audio.name}")
            print(f"\nExemplo de uso:\npython app.py {audios_disponiveis[0].name}")
        else:
            print("\nNenhum arquivo de audio foi encontrado na pasta atual.")
            print("Exemplo de uso:\npython app.py caminho/para/audio.mp3")
        return 1

    caminho_audio = Path(args.audio)
    caminho_prompt = Path(args.prompt_file)

    if not caminho_audio.exists():
        print(f"❌ Arquivo não encontrado: {caminho_audio}")
        return 1

    # CONFIGURAÇÕES (carregadas do .env)
    API_KEY_STT = os.getenv("API_KEY_STT")
    STT_URL = os.getenv("STT_URL")
    API_KEY_WX = os.getenv("API_KEY_WX")
    WATSONX_URL = os.getenv("WATSONX_URL")
    PROJECT_ID = os.getenv("PROJECT_ID")

    if not all([API_KEY_STT, STT_URL, API_KEY_WX, WATSONX_URL, PROJECT_ID]):
        print("❌ Configure as variáveis obrigatórias no arquivo .env")
        return 1

    try:
        inicio_total = perf_counter()
        log_etapa_inicio(
            "Processamento do audio",
            f"arquivo={caminho_audio.name}",
        )

        # 1) TRANSCRIÇÃO BRUTA
        content_type = detectar_content_type(caminho_audio)
        stt_model = resolver_stt_model(args.stt_model)
        llm_model = resolver_llm_model(args.llm_model)
        log_etapa_inicio(
            "Transcricao com IBM STT",
            f"content_type={content_type} | stt_model={stt_model}",
        )
        inicio_transcricao = perf_counter()
        transcricao_bruta = transcrever_audio_ibm(
            caminho_audio,
            API_KEY_STT,
            STT_URL,
            content_type,
            stt_model,
        )
        tempo_transcricao_segundos = round(perf_counter() - inicio_transcricao, 2)
        log_etapa_fim(
            "Transcricao com IBM STT",
            f"tempo={tempo_transcricao_segundos}s",
        )
        salvar_texto(transcricao_bruta, Path(f"output/{caminho_audio.stem}_01_transcricao.txt"))

        # 2) ANALISE ESTRUTURADA
        # O prompt eh carregado de arquivo para facilitar manutencao e testes de variacao.
        log_etapa_inicio(
            "Preparacao do prompt",
            f"prompt_file={caminho_prompt}",
        )
        template_prompt = carregar_template_prompt(caminho_prompt)
        prompt_final = montar_prompt(template_prompt, transcricao_bruta)
        log_etapa_fim("Preparacao do prompt")

        log_etapa_inicio(
            "Inferencia com watsonx",
            f"llm_model={llm_model}",
        )
        inicio_inferencia = perf_counter()
        resposta_modelo = analisar_ligacao(
            prompt_final,
            API_KEY_WX,
            WATSONX_URL,
            PROJECT_ID,
            llm_model,
        )
        tempo_inferencia_segundos = round(perf_counter() - inicio_inferencia, 2)
        log_etapa_fim(
            "Inferencia com watsonx",
            f"tempo={tempo_inferencia_segundos}s",
        )

        log_etapa_inicio("Validacao da resposta do modelo")
        try:
            analise_json = extrair_json_resposta(resposta_modelo)
        except RuntimeError:
            salvar_texto(
                resposta_modelo,
                Path(f"output/{caminho_audio.stem}_resposta_modelo_bruta.txt"),
            )
            raise
        analise_validada = validar_analise_estruturada(analise_json)
        log_etapa_fim("Validacao da resposta do modelo")

        tempo_total_segundos = round(perf_counter() - inicio_total, 2)
        saida_estruturada = montar_saida_estruturada(
            caminho_audio,
            caminho_prompt,
            content_type,
            stt_model,
            llm_model,
            transcricao_bruta,
            analise_validada,
            tempo_transcricao_segundos,
            tempo_inferencia_segundos,
            tempo_total_segundos,
        )

        log_etapa_inicio("Gravacao dos arquivos de saida")
        salvar_json(saida_estruturada, Path(f"output/{caminho_audio.stem}_02_analise.json"))

        relatorio = formatar_relatorio_analise(saida_estruturada)
        salvar_texto(relatorio, Path(f"output/{caminho_audio.stem}_03_relatorio.txt"))
        salvar_qa_csv(
            saida_estruturada["analise"]["perguntas_respostas"],
            Path(f"output/{caminho_audio.stem}_04_qa.csv"),
        )
        salvar_qa_consolidado_csv(
            saida_estruturada,
            Path(f"output/{caminho_audio.stem}_05_qa_consolidado.csv"),
        )
        log_etapa_fim("Gravacao dos arquivos de saida")

        print(
            "\n⏱️ Tempos de execucao:\n"
            f"- Transcricao: {tempo_transcricao_segundos}s\n"
            f"- Inferencia: {tempo_inferencia_segundos}s\n"
            f"- Total: {tempo_total_segundos}s"
        )

        log_etapa_fim(
            "Processamento do audio",
            f"tempo_total={tempo_total_segundos}s",
        )
        print("\n🎉 Processo concluído com sucesso!\n")

    except RuntimeError as e:
        print(str(e))
        return 1

    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
