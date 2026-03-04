# Dublador de Vídeo (PT-BR)

Projeto de automação multimodal em Python que transforma vídeos em inglês em versões dubladas em português.

## Resumo
Pipeline completo para:
- extrair áudio do vídeo,
- transcrever com Whisper,
- traduzir com OpenRouter (Gemini Flash),
- gerar voz em português (Edge-TTS ou ElevenLabs),
- sincronizar segmentos e renderizar vídeo final dublado.

## Valor técnico (portfólio)
- Integração de múltiplas APIs (OpenRouter + ElevenLabs) com fallback resiliente.
- Processamento de mídia ponta a ponta (áudio/vídeo) com MoviePy e PyDub.
- Ajuste de sincronização por segmento com aceleração controlada de fala.
- Boas práticas de produção: segredos fora do código, `.env`, `.gitignore`, documentação e reprodutibilidade.

## Stack
- Linguagem: Python
- IA: Whisper, OpenRouter (Gemini Flash), Edge-TTS, ElevenLabs (opcional)
- Mídia: MoviePy, PyDub, FFmpeg
- Ambiente: virtualenv + `.env`

## Arquitetura (visão rápida)
1. `VideoFileClip` extrai áudio do vídeo de entrada.
2. Whisper transcreve em segmentos com timestamps.
3. Cada segmento é traduzido para PT-BR.
4. A voz é sintetizada (ElevenLabs quando configurado; fallback para Edge-TTS).
5. Quando necessário, o áudio gerado é acelerado sem distorção forte de pitch.
6. Os clipes de voz são posicionados por timestamp e mixados com áudio original baixo.
7. O vídeo final `_DUBLADO.mp4` é renderizado.

## Requisitos
- Python 3.10+
- `ffmpeg` instalado e no PATH (necessário para `moviepy` e `pydub`)

## Instalação
1. Crie e ative um ambiente virtual:
   - Windows (PowerShell):
     ```powershell
     python -m venv venv
     .\venv\Scripts\Activate.ps1
     ```
2. Instale dependências:
   ```powershell
   pip install -r requirements.txt
   ```

## Configuração
1. Copie o arquivo de exemplo:
   ```powershell
   Copy-Item .env.example .env
   ```
2. Preencha no `.env`:
   - `OPENROUTER_API_KEY` (obrigatória)
   - `ARQUIVO_VIDEO` (ex: `parte2.mp4`)
   - `USAR_ELEVENLABS=true` + `ELEVENLABS_API_KEY` + `ELEVENLABS_VOICE_ID` (opcional)

## Execução
No PowerShell (com ambiente ativado):
```powershell
# Carrega variáveis do .env para a sessão atual
Get-Content .env | ForEach-Object {
  if ($_ -match '^\s*#' -or $_ -notmatch '=') { return }
  $name, $value = $_ -split '=', 2
  [Environment]::SetEnvironmentVariable($name.Trim(), $value.Trim(), 'Process')
}

python dublador.py
```

Saída esperada:
- Arquivo final com sufixo `_DUBLADO.mp4` no mesmo diretório.

## Observações
- Se ElevenLabs não estiver configurado corretamente, o script faz fallback automático para Edge-TTS.
- O projeto ignora arquivos temporários e segredos via `.gitignore`.

## Resultado esperado
- Entrada: `parte2.mp4` (ou arquivo definido em `ARQUIVO_VIDEO`)
- Saída: `parte2_DUBLADO.mp4`
- Comportamento: preserva áudio original em baixo volume e sobrepõe dublagem sincronizada.

## Interface Web (Gradio)

A partir da versão atual, o projeto conta com uma interface web interativa via **Gradio**, disponível em `app.py`.

### Como usar a interface web

1. Instale as dependências (inclui `gradio`):
   ```powershell
   pip install -r requirements.txt
   ```

2. Inicie a interface:
   ```powershell
   python app.py
   ```

3. Acesse no navegador: [http://localhost:7860](http://localhost:7860)

### Funcionalidades da UI
- **Upload de vídeo** `.mp4` direto pelo navegador.
- **Campo de API Key** do OpenRouter (obrigatório).
- **Toggle ElevenLabs** — ativa campos de chave e Voice ID para voz premium; usa Edge-TTS como fallback automático.
- **Logs em tempo real** exibidos na tela durante o processamento.
- **Download do vídeo dublado** ao final do processo.

> Para uso via linha de comando (sem interface), continue usando `python dublador.py` conforme descrito na seção **Execução** acima.

## Pontos de evolução
- Interface CLI (`argparse`) para trocar modelo, idioma e volume sem editar código.
- Logs estruturados por segmento para auditoria de qualidade.
- Testes automatizados para validação de configuração e cenários de fallback.
- Empacotamento em Docker para execução portátil.

## Roadmap curto
- Parametrizar idioma/modelo via CLI.
- Gerar logs por segmento para depuração de sincronia.
- Adicionar testes de sanidade para configuração.
