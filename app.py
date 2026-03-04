import gradio as gr
import os
import io
import time
from contextlib import redirect_stdout
import sys

# Importa as funções do seu script existente
import dublador

def processar_video(video_path, openrouter_key, usar_el, el_key, el_voice_id):
    if not video_path:
        return None, "Erro: Nenhum vídeo foi enviado."
    if not openrouter_key:
        return None, "Erro: A chave do OpenRouter é obrigatória."
        
    # Injeta as configs via env vars
    os.environ["OPENROUTER_API_KEY"] = openrouter_key
    os.environ["USAR_ELEVENLABS"] = "true" if usar_el else "false"
    os.environ["ELEVENLABS_API_KEY"] = el_key or ""
    os.environ["ELEVENLABS_VOICE_ID"] = el_voice_id or ""
    os.environ["ARQUIVO_VIDEO"] = video_path

    # Captura logs do terminal pra mostrar na UI
    log_buffer = io.StringIO()
    try:
        with redirect_stdout(log_buffer):
            # Substitui a saída de erro padrão também para capturar warnings/erros
            sys.stderr = log_buffer 
            dublador.main()
    except Exception as e:
        log_buffer.write(f"\n❌ Erro durante o processo: {str(e)}")
    finally:
        sys.stderr = sys.__stderr__

    nome_saida = video_path.replace(".mp4", "_DUBLADO.mp4")
    
    # Verifica se o arquivo de saída realmente foi criado
    if os.path.exists(nome_saida):
        return nome_saida, log_buffer.getvalue()
    else:
        return None, log_buffer.getvalue() + "\n\n❌ O arquivo dublado não foi encontrado. Verifique os erros acima."

with gr.Blocks(title="🎬 Seamless AI Dub", theme=gr.themes.Soft()) as app:
    gr.Markdown("# 🎬 Seamless AI Dub\nDuble seus vídeos de inglês para português com IA.")

    with gr.Row():
        with gr.Column():
            video_input = gr.File(label="📁 Envie o vídeo (.mp4)", file_types=[".mp4"])
            openrouter_key = gr.Textbox(label="🔑 OpenRouter API Key", type="password")

        with gr.Column():
            usar_el = gr.Checkbox(label="Usar ElevenLabs (voz premium)?")
            el_key = gr.Textbox(label="ElevenLabs API Key", type="password", visible=False)
            el_voice_id = gr.Textbox(label="Voice ID ElevenLabs", visible=False)

    # Mostra campos do ElevenLabs só quando marcado
    usar_el.change(lambda x: [gr.update(visible=x), gr.update(visible=x)], usar_el, [el_key, el_voice_id])

    btn = gr.Button("🚀 Iniciar Dublagem", variant="primary")

    with gr.Row():
        video_output = gr.File(label="🎉 Vídeo Dublado")
        logs = gr.Textbox(label="📋 Logs do Processo", lines=15, interactive=False)

    btn.click(
        fn=processar_video,
        inputs=[video_input, openrouter_key, usar_el, el_key, el_voice_id],
        outputs=[video_output, logs]
    )

if __name__ == "__main__":
    print("Iniciando interface Gradio em http://localhost:7860")
    app.launch(share=False)
