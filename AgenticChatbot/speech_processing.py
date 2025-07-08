import os
import time
import streamlit as st
from dotenv import load_dotenv
from azure.cognitiveservices import speech as speechsdk
import asyncio

load_dotenv()
speech_key = os.getenv("SPEECH_KEY")
speech_endpoint = os.getenv("SPEECH_ENDPOINT")

def recognize_from_microphone():
    speech_config = speechsdk.SpeechConfig(subscription= speech_key, endpoint= speech_endpoint, speech_recognition_language= "en-US")
    transcriber = speechsdk.transcription.ConversationTranscriber(speech_config)

    done = False
    all_results = []

    def handle_final_result(evt):
        all_results.append(evt.result.text)
        print(evt.result.text)
    
    def stop_cb(evt: speechsdk.SessionEventArgs):
        """
        callback that signals to stop continous transcription upon receiving an event 'evt'
        """
        print(f"CLOSING {evt}")
        nonlocal done
        done = True
    
    transcriber.transcribed.connect(handle_final_result)
    transcriber.session_started.connect(lambda evt: print(f"SESSION STARTED {evt}"))
    transcriber.session_stopped.connect(lambda evt: print(f"SESSION STOPPED {evt}"))
    transcriber.canceled.connect(lambda evt: print(f"CANCELLED {evt}"))

    # Stop continous transcription on either session stopped or cancelled
    transcriber.session_stopped.connect(stop_cb)
    transcriber.canceled.connect(stop_cb)

    transcriber.start_transcribing_async()

    while not done:
        st.session_state["transcription_results"] = all_results
        time.sleep(1)
    
    st.session_state["transcription_results"] = all_results
    return


async def text_to_microphone(text: str):
    audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker= True)
    speech_config = speechsdk.SpeechConfig(subscription= speech_key, endpoint= speech_endpoint)
    speech_config.speech_synthesis_voice_name= 'en-US-JennyNeural'
    
    speech_synthesier = speechsdk.SpeechSynthesizer(speech_config= speech_config, audio_config= audio_config)

    loop = asyncio.get_event_loop()
    speech_synthesis_result = await loop.run_in_executor(None, lambda: speech_synthesier.speak_text_async(text).get())

    if speech_synthesis_result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        print("Speech synthesized for text")
    elif speech_synthesis_result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = speech_synthesis_result.cancellation_details
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            print(f"Error details: {cancellation_details.error_details}")
    
    
