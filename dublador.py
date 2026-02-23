import os
import time
import requests
import asyncio
import edge_tts
import whisper
import warnings
from moviepy import VideoFileClip, AudioFileClip, CompositeAudioClip
from pydub import AudioSegment

# Ignora avisos chatos do Python no terminal
warnings.filterwarnings("ignore")

# ==========================================
# 1. CONFIGURAÇÕES GERAIS
# ==========================================
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
ARQUIVO_VIDEO = os.getenv("ARQUIVO_VIDEO", "parte2.mp4")

# ==========================================
# 2. CHAVE MESTRA: TESTE vs VÍDEO FINAL
# ==========================================
# Deixe False para testar a sincronia de graça. Mude para True para usar ElevenLabs!
USAR_ELEVENLABS = os.getenv("USAR_ELEVENLABS", "false").strip().lower() in {"1", "true", "yes", "sim"}
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")
# ID da voz do Will (Dynamic, Depth) que você escolheu
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "")

def traduzir_trecho(texto_original):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost",
        "X-Title": "Dublador-Python"
    }
    payload = {
        "model": "google/gemini-2.5-flash",
        "messages": [
            {
                "role": "system", 
                "content": "Você é um técnico de manutenção industrial. Traduza esta frase de uma aula técnica da SKF para o Português do Brasil. Seja direto. Retorne APENAS a tradução."
            },
            {"role": "user", "content": texto_original}
        ]
    }
    
    for _ in range(3):
        try:
            resposta = requests.post(url, headers=headers, json=payload, timeout=30)
            dados = resposta.json()
            if "error" in dados:
                print(f"\n⚠️ ERRO DO OPENROUTER: {dados['error']['message']}\n")
                return texto_original
            return dados['choices'][0]['message']['content'].strip()
        except requests.RequestException:
            time.sleep(1)
            
    return texto_original

async def gerar_voz_ia(texto, arquivo_saida):
    if USAR_ELEVENLABS and ELEVENLABS_API_KEY and ELEVENLABS_VOICE_ID:
        print("🎙️ ElevenLabs: Gerando voz ultra-realista com o modelo Turbo v2.5...")
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}"
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": ELEVENLABS_API_KEY
        }
        data = {
            "text": texto,
            "model_id": "eleven_turbo_v2_5", # Modelo super rápido que consome metade dos créditos!
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75
            }
        }
        resposta = requests.post(url, json=data, headers=headers, timeout=30)
        
        if resposta.status_code == 200:
            with open(arquivo_saida, 'wb') as f:
                f.write(resposta.content)
            return # Sai da função pois a ElevenLabs deu conta do recado
        else:
            print(f"⚠️ Erro ElevenLabs ({resposta.status_code})! Usando Edge-TTS como Plano B...")
    elif USAR_ELEVENLABS:
        print("⚠️ USAR_ELEVENLABS=true, mas faltam ELEVENLABS_API_KEY ou ELEVENLABS_VOICE_ID. Usando Edge-TTS...")
            
    # Se USAR_ELEVENLABS for False, ou se a ElevenLabs falhar, usa o Edge grátis:
    comunicador = edge_tts.Communicate(texto, "pt-BR-AntonioNeural")
    await comunicador.save(arquivo_saida)

# ==========================================
# NOVA FUNÇÃO: ACELERAR SEM MUDAR A VOZ (PITCH)
# ==========================================
def acelerar_audio_sem_esquilo(arquivo_mp3, fator):
    # O pydub faz a mágica de encurtar as ondas sonoras sem achatar a frequência
    audio = AudioSegment.from_file(arquivo_mp3)
    # speedup funciona perfeitamente mantendo o timbre humano grave
    audio_rapido = audio.speedup(playback_speed=fator, chunk_size=150, crossfade=25)
    audio_rapido.export(arquivo_mp3, format="mp3")

def main():
    print("🚀 Iniciando o dublador...")
    if not OPENROUTER_API_KEY:
        raise RuntimeError("Defina OPENROUTER_API_KEY no ambiente antes de executar.")

    video = VideoFileClip(ARQUIVO_VIDEO)
    
    print("⏳ Extraindo áudio para a IA ouvir...")
    video.audio.write_audiofile("audio_temp.wav", logger=None)
    
    print("⏳ Whisper: Transcrevendo o inglês...")
    modelo_whisper = whisper.load_model("medium")
    resultado = modelo_whisper.transcribe("audio_temp.wav")
    
    audios_dublados = []
    print("⏳ Traduzindo e gerando vozes para cada frase...")
    
    for i, segmento in enumerate(resultado["segments"]):
        texto_ing = segmento["text"]
        inicio = segmento["start"]
        
        if len(texto_ing.strip()) < 2:
            continue
            
        texto_pt = traduzir_trecho(texto_ing)
        print(f"-> [{inicio:.1f}s] {texto_pt}")
        
        nome_arquivo_voz = f"trecho_{i}.mp3"
        asyncio.run(gerar_voz_ia(texto_pt, nome_arquivo_voz))
        
        # Mede quanto tempo a IA gerou de áudio cru
        audio_temporario = AudioSegment.from_file(nome_arquivo_voz)
        duracao_ia = len(audio_temporario) / 1000.0 # Em segundos
        
        # Descobre quanto tempo a pessoa original (em inglês) levou para falar
        tempo_original_falando = segmento["end"] - inicio
        
        # Se a IA em português demorou MAIS que o original, nós aceleramos a voz dela com a Nova Função!
        if duracao_ia > tempo_original_falando:
            # Calcula o fator de aceleração
            fator_aceleracao = duracao_ia / tempo_original_falando
            # O limite garante que a voz não fique ofegante ou robótica
            fator_aceleracao = min(fator_aceleracao, 1.45) 
            
            # Aplica a aceleração PROTEGENDO O PITCH (não vai afinar a voz)
            acelerar_audio_sem_esquilo(nome_arquivo_voz, fator_aceleracao)
            
        # Posiciona a voz já tratada no tempo exato
        clip_voz = AudioFileClip(nome_arquivo_voz).with_start(inicio)
        audios_dublados.append(clip_voz)

    print("⏳ Mixando áudios e renderizando vídeo final...")
    
    # Abaixa o inglês original para 15% (sintaxe atualizada do MoviePy 2.2.1)
    audio_fundo = video.audio.with_volume_scaled(0.15) 
    
    audio_final = CompositeAudioClip([audio_fundo] + audios_dublados)
    video_final = video.with_audio(audio_final)
    
    nome_saida = ARQUIVO_VIDEO.replace(".mp4", "_DUBLADO.mp4")
    video_final.write_videofile(nome_saida, fps=24, codec="libx264", audio_codec="aac")
    
    # Limpeza da "sujeira"
    os.remove("audio_temp.wav")
    for i in range(len(resultado["segments"])):
        try:
            os.remove(f"trecho_{i}.mp3")
        except OSError:
            pass
            
    print(f"🎉 SUCESSO! Assista o resultado final: {nome_saida}")

if __name__ == "__main__":
    main()
