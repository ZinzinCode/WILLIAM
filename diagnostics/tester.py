def whisper_test():
    result = transcribe_test_audio("test.wav")
    assert "bonjour" in result.lower()

def tts_test():
    result = synthesize_text("Bonjour.")
    assert result is not None

def llm_test():
    response = query_llm("Bonjour, que fais-tu ?")
    assert len(response) > 10

modules = {
    "whisper": whisper_test,
    "tts": tts_test,
    "llm": llm_test,
}
