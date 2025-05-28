import os
from dotenv import load_dotenv
import azure.cognitiveservices.speech as speechsdk

def recognize_from_microphone():
    speech_config = speechsdk.SpeechConfig(subscription= os.environ.get('SPEECH_KEY'), endpoint= os.environ.get('SPEECH_ENDPOINT'))
    speech_config.speech_recognition_language="en-US"

    audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)
    speechsdk.transcription.ConversationTranscriber(speech_config=speech_config, audio_config= audio_config)

    print("Speak into your microphone.")
    speech_recognition_result = speech_recognizer.recognize_once_async().get()

    if speech_recognition_result.reason == speechsdk.ResultReason.RecognizedSpeech:
        print("Recognized: {}".format(speech_recognition_result.text))
    elif speech_recognition_result.reason == speechsdk.ResultReason.NoMatch:
        print("No speech could be recognized: {}".format(speech_recognition_result.no_match_details))
    elif speech_recognition_result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = speech_recognition_result.cancellation_details
        print("Speech Recognition canceled: {}".format(cancellation_details.reason))
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            print("Error details: {}".format(cancellation_details.error_details))
            print("Did you set the speech resource key and endpoint values?")


load_dotenv()
speech_key = os.getenv("SPEECH_KEY")
speech_endpoint = os.getenv("SPEECH_ENDPOINT")
recognize_from_microphone()