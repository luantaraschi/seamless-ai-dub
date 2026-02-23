# Dublador de Vídeo (PT-BR)

Pipeline em Python para:
- extrair áudio do vídeo,
- transcrever com Whisper,
- traduzir com OpenRouter (Gemini Flash),
- gerar voz em português (Edge-TTS ou ElevenLabs),
- sincronizar e renderizar vídeo final dublado.

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

## Roadmap curto
- Parametrizar idioma/modelo via CLI.
- Gerar logs por segmento para depuração de sincronia.
- Adicionar testes de sanidade para configuração.
