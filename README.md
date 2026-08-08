# seamless-ai-dub

Pipeline automatizado para tradução e dublagem de vídeos do inglês para o português com sincronização de tempo por segmento.

[Estudo de caso](https://luantaraschi.dev/projeto-dub.html)

![Seamless AI Dub Interface](docs/dub.webp)

## Como funciona

O aplicativo automatiza o processo de dublagem através de um pipeline em Python (`dublador.py`):

1. **Transcrição:** O OpenAI Whisper extrai o áudio e gera os trechos com carimbos de data e hora (`timestamps`).
2. **Tradução:** O OpenRouter (utilizando modelos como Gemini via API) traduz o texto mantendo o tom e o contexto do idioma de origem.
3. **Síntese de voz:** O áudio em português é gerado via `edge-tts` (gratuito) ou opcionalmente via ElevenLabs.
4. **Sincronia temporal:** O PyDub e o MoviePy ajustam a velocidade e a duração dos trechos de áudio para encaixar exatamente no intervalo da fala original antes de remontar o vídeo final.

A aplicação conta com uma interface gráfica desenvolvida em Gradio (`app.py`) para upload de vídeos e ajuste de parâmetros de dublagem.

## Rodar local

Pré-requisitos: Python 3.10+ e FFmpeg instalado no sistema operacional.

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Crie o arquivo `.env` a partir do modelo `.env.example` e insira sua chave da OpenRouter:

```bash
OPENROUTER_API_KEY=sua_chave_aqui
```

Execute a interface gráfica:

```bash
python app.py
```

## Estado

O pipeline de dublagem exige uma chave de API válida do OpenRouter e o executável do `ffmpeg` no PATH do sistema para renderizar os arquivos de vídeo. O projeto não declara suíte de testes automatizados.

## Licença

MIT
