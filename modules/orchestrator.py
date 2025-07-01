import asyncio
from stt import stt_module
from nlp import nlp_module
from tts import tts_module
from memory import Memory
from logs import log_event, log_error

memory = Memory()

async def main_loop():
    while True:
        try:
            audio = await stt_module.listen()
            log_event("stt", "audio_received")
            text = await stt_module.transcribe(audio)
        except Exception as e:
            log_error("stt", str(e))
            text = input("STT failed, type your query: ")

        intent = nlp_module.analyze_intent(text)
        log_event("nlp", f"intent: {intent}")
        response = nlp_module.generate_response(text, memory)
        memory.save_short_term(text, response)
        await tts_module.speak(response)
        log_event("tts", "response_spoken")

if __name__ == "__main__":
    asyncio.run(main_loop())