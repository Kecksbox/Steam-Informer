from google.cloud import texttospeech
import tempfile
import time
import os


def generate_audio_from_text(ssml):
    """MBE"""

    # Create an environment variable, which is needed for the tts to work properly
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = r'./service_account.json'

    # Create a text to speech client
    client = texttospeech.TextToSpeechClient()

    # Create the text used to generate audio with the ssml
    input_text = texttospeech.types.SynthesisInput(ssml=ssml)  # change to text when deploying

    # Specify the voice used
    # Note: the voice can also be specified by name.
    # Names of voices can be retrieved with client.list_voices().
    voice = texttospeech.types.VoiceSelectionParams(
        language_code='en-US',
        name='en-US-Wavenet-D'
    )

    # Configure the audio parameters
    audio_config = texttospeech.types.AudioConfig(
        pitch=0.00,
        speaking_rate=1.00,
        audio_encoding="LINEAR16")

    # Create the audio from the input text
    # Note: The response's audio_content is binary.
    response = client.synthesize_speech(input_text, voice, audio_config)

    # Create an audio file
    with open(os.path.join(tempfile.gettempdir(), time.strftime("%Y%m%d-%H%M%S"))+'.wav', 'wb') as out:

        # Write the binary to the audio file
        out.write(response.audio_content)

        # Return the name of the file
        return out.name
