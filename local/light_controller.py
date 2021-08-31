from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
import azure.cognitiveservices.speech as speechsdk
from azure.cognitiveservices.language.luis.runtime import LUISRuntimeClient
from msrest.authentication import CognitiveServicesCredentials
import requests
import json
from pathlib import Path

def read_config():
    # Read config.json file in the same folder as this script
    config_path = Path(__file__).parent.joinpath('config.json')
    config = json.loads(config_path.read_text())
    return config

def get_keyvault_client(keyvault_uri):
    credential = DefaultAzureCredential()
    keyvault_client = SecretClient(vault_url=keyvault_uri, credential=credential)
    return keyvault_client

def get_secret(secret_name):
    secret = keyvault_client.get_secret(secret_name).value
    return secret

def get_speech_recognizer(secret_name, service_region):
    # Get key from keyvault
    speech_key = get_secret(secret_name)

    # Get speech client
    speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config)
    return speech_recognizer

def recognize_speech():
    # Recognize microphone input
    print("Begin speaking...")
    result = speech_recognizer.recognize_once()

    # Print result
    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
        print("Recognized: {}".format(result.text))
        return result.text
    elif result.reason == speechsdk.ResultReason.NoMatch:
        print("No speech could be recognized: {}".format(result.no_match_details))
    elif result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = result.cancellation_details
        print("Speech Recognition canceled: {}".format(cancellation_details.reason))
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            print("Error details: {}".format(cancellation_details.error_details))

def get_luis_runtime_client(secret_name, luis_endpoint):
    # Get secrets from keyvault
    luis_key = get_secret(secret_name)

    # Get runtime client
    luis_credentials = CognitiveServicesCredentials(luis_key)
    luis_client = LUISRuntimeClient(endpoint=luis_endpoint, credentials=luis_credentials)
    return luis_client

def interpret_command(query):
    # Perform prediction
    print('Performing prediction...')
    prediction_request = {'query': query}
    prediction_response = luis_client.prediction.get_slot_prediction(luis_app_id, 'Production', prediction_request)

    # Print results
    print('Top intent: {}'.format(prediction_response.prediction.top_intent))
    print('Intents: ')
    for intent in prediction_response.prediction.intents:
        print('\t{}'.format (json.dumps (intent)))
    print('Entities: {}'.format (prediction_response.prediction.entities))

    return prediction_response.prediction

if __name__ == '__main__':
    # Auth and setup
    config = read_config()
    keyvault_client = get_keyvault_client(config['keyvault_url'])
    speech_recognizer = get_speech_recognizer(config['speech_secret_name'], config['speech_service_region'])
    luis_app_id = get_secret(config['luis_app_id_secret_name'])
    luis_client = get_luis_runtime_client(config['luis_secret_name'], config['luis_endpoint'])
    url = config['tessel_address']

    while True:
        voice_command = recognize_speech() # Speech to text
        prediction = interpret_command(voice_command) # Text to intention

        if 'LED' in prediction.entities:
            # Extract entities and intent
            leds = prediction.entities['LED']
            intent = prediction.top_intent

            # Assign the recognized intent to each LED mentioned
            body = {}
            for color in [x[0] for x in leds]:
                body[color] = intent

            # Post the command to the tessel
            response = requests.post(url, data=json.dumps(body))
            print(response.text)
        else:
            print('Could not identify a known LED in the command.')

        input('Press any key to issue another command or Ctrl+C to quit.')