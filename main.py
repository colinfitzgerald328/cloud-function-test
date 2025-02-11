import functions_framework
from google.cloud import storage
from openai import OpenAI
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

    # List of supported audio extensions for Whisper API
    supported_extensions = [
        ".flac",
        ".m4a",
        ".mp3",
        ".mp4",
        ".mpeg",
        ".mpga",
        ".oga",
        ".ogg",
        ".wav",
        ".webm",
    ]

    # Check file extension
    file_extension = os.path.splitext(file_name)[1].lower()
    if file_extension not in supported_extensions:
        print(f"Unsupported file extension: {file_extension}")
        return

    # Create a temporary file with the original extension
    with tempfile.NamedTemporaryFile(
        suffix=file_extension, delete=False
    ) as temp_audio:
        try:
            # Download the blob to the temporary file
            blob.download_to_filename(temp_audio.name)

            # Initialize OpenAI client
            client = OpenAI(api_key=OPENAI_API_KEY)

            # Open and transcribe the audio file
            with open(temp_audio.name, "rb") as audio_file:
                transcript = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    response_format="verbose_json"
                )
            print(f"Transcription: {transcript}")

        finally:
            # Clean up the temporary file
            if os.path.exists(temp_audio.name):
                os.unlink(temp_audio.name)

    # Optionally, save the transcription back to GCS
    # transcript_blob = bucket.blob(f"{file_name}_transcript.txt")
    # transcript_blob.upload_from_string(transcript)
