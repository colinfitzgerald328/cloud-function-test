import functions_framework
from google.cloud import storage
import openai
import tempfile
import os

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")


@functions_framework.cloud_event
def hello_gcs(cloud_event):
    data = cloud_event.data
    bucket_name = data["bucket"]
    file_name = data["name"]

    # Create a storage client
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(file_name)

    # Create a temporary file to store the audio
    with tempfile.NamedTemporaryFile(suffix=".mp3") as temp_audio:
        # Download the blob to the temporary file
        blob.download_to_filename(temp_audio.name)

        # Initialize OpenAI client
        client = openai.OpenAI(api_key=OPENAI_API_KEY)

        # Open and transcribe the audio file
        with open(temp_audio.name, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1", file=audio_file, response_format="text"
            )

        print(f"Transcription: {transcript}")

        # # Optionally, save the transcription back to GCS
        # transcript_blob = bucket.blob(f"{file_name}_transcript.txt")
        # transcript_blob.upload_from_string(transcript)
