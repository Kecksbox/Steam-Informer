from google.cloud import texttospeech
import tempfile
import time
import os

def generateAudio(ssml):
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = r'C:\Users\Malte\PycharmProjects\OPTC\service_account2.json'

    client = texttospeech.TextToSpeechClient()

    input_text = texttospeech.types.SynthesisInput(ssml=ssml) #change to text when deploying

    # Note: the voice can also be specified by name.
    # Names of voices can be retrieved with client.list_voices().
    voice = texttospeech.types.VoiceSelectionParams(
        language_code = 'en-US',
        name = 'en-US-Wavenet-D'
    )

    audio_config = texttospeech.types.AudioConfig(
        pitch = 0.00,
        speaking_rate = 1.00,
        audio_encoding="LINEAR16")

    response = client.synthesize_speech(input_text, voice, audio_config)

    # The response's audio_content is binary.

    with open(os.path.join(tempfile.gettempdir(), time.strftime("%Y%m%d-%H%M%S"))+'.mp3', 'wb') as out:
        out.write(response.audio_content)
        print(os.path.join(tempfile.gettempdir(), time.strftime("%Y%m%d-%H%M%S"))+'.mp3')
        return out.name