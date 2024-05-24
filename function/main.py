
def upload(request):

    if request.method == 'OPTIONS':
        print('------ options')
        # Allows GET requests from any origin with the Content-Type
        # header and caches preflight response for an 3600s
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET,POST',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Max-Age': '3600',
            'Access-Control-Allow-Credentials': 'true'
        }
        return ('', 204, headers)



    from flask import Flask, request, redirect
    from datetime import datetime
    from google.cloud import storage, texttospeech
    import vertexai
    from vertexai.generative_models import GenerativeModel, Part
    import os
    import random
    import json
    import datetime
    #os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'credentials.json'
    vertexai.init(project='geminicamera', location="europe-west8")
    model = GenerativeModel(model_name="gemini-1.0-pro-vision")

    storage_client = storage.Client()#.from_service_account_json('credentials.json')
    speech_client = texttospeech.TextToSpeechClient()
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
        name = f"output{random.randint(1,1000)}.mp3"
        #f = f"/tmp/{name}"
        #with open(f, "wb") as out:
            # Write the response to the output file.
            #out.write(response.audio_content)

        bucket = storage_client.bucket('upload-gemini-camera-2')
        blob = bucket.blob(name)
        blob.upload_from_string(response.audio_content, content_type="audio/mpeg")

        serving_url = blob.generate_signed_url(
            version="v4",
            expiration=datetime.timedelta(minutes=15),  # This URL is valid for 15 minutes
            method="GET")  # Allow GET requests using this URL.
        print(serving_url)
        return serving_url



        # check if the post request has the file part
    file = request.files['file']
    bucket = storage_client.bucket('upload-gemini-camera-2')
    blob = bucket.blob('image')
    blob.upload_from_string(file.read(), content_type=file.content_type)

    uri = f'gs://upload-gemini-camera-2/image'
    res = get_description(uri)
    url = read_description(res)

    headers = {
        'Access-Control-Allow-Origin': '*'
    }


    return json.dumps([res,url], 200, headers)

