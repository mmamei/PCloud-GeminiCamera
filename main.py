from flask import Flask, request, redirect
from datetime import datetime
from google.cloud import storage, texttospeech
import vertexai
from vertexai.generative_models import GenerativeModel, Part
import os
import random
import json
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'credentials.json'
vertexai.init(project='plcoud2024', location="europe-west8")
model = GenerativeModel(model_name="gemini-1.0-pro-vision")

app = Flask(__name__)
storage_client = storage.Client.from_service_account_json('credentials.json')
speech_client = texttospeech.TextToSpeechClient()
@app.route('/')
def main():
    return redirect('static/camera.html')


def get_description(uri):
    response = model.generate_content(
        [
            Part.from_uri(
                uri,
                mime_type="image/jpeg",
            ),
            "Dimmi cosa c'è nell'immagine. Descrivi in particolare la collocazione degli oggetti. Inizia con: Vedo...",
        ]
    )
    return response.text

def read_description(txt):
    synthesis_input = texttospeech.SynthesisInput(text=txt)
    voice = texttospeech.VoiceSelectionParams(
        language_code="it-IT",
        ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
    )
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )
    response = speech_client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )
    # The response's audio_content is binary.
    #os.remove("static/output.mp3")
    f = f"static/output{random.randint(1,1000)}.mp3"
    with open(f, "wb") as out:
        # Write the response to the output file.
        out.write(response.audio_content)
    return f

@app.route('/upload',methods=['POST'])
def upload():
    # check if the post request has the file part
    file = request.files['file']
    bucket = storage_client.bucket('upload-gemini-camera')
    blob = bucket.blob('image')
    blob.upload_from_string(file.read(), content_type=file.content_type)

    uri = f'gs://upload-gemini-camera/image'
    res = get_description(uri)
    f = read_description(res)
    return json.dumps([res,f'/{f}'])


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=222, debug=True, ssl_context='adhoc')