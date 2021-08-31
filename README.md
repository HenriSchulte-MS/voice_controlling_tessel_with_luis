# Voice-controlling an IoT device with Azure Cognitive Services Language Understanding and a Tessel 2 microcontroller

Prerequisites:
- Azure account with the following resources deployed:
    - Azure KeyVault
    - Azure Cognitive Services
- Visual Studio Code with Azure extension
- Tessel 2

We can control LEDs (or any other device) through voice commands, using Azure Cognitive Services and a Tessel 2 microcontroller. I use the Speech and Language Understanding Python SDKs to transcribe and interpret voice commands. Those are then relayed to the Tessel, controlling a number of colored LEDs.

![diagram](/img/luistessel_diagram.png)

****

## Steps to reproduce

### Create the LUIS model

1. Create a Language Understanding (LUIS) app and authoring resource. As prediction resource, use an existing Language Understanding (or Cognitive Services) resource or create a new one. See https://docs.microsoft.com/en-us/azure/cognitive-services/luis/luis-how-to-start-new-app.
1. Add an entity `LED` of type List and define your colors, including synonyms.
![LED entity](/img/luis_entity.png)
1. Add intents to your LUIS app: `TurnOn`, `TurnOff`, `Blink`.
1. Add example utterances for each intent.
![TurnOn intent](/img/luis_intent.png)
1. Train and publish the model.

### Set up the Tessel
1. [Install the Tessel 2 CLI](https://tessel.github.io/t2-start/index.html). 
1. Connect the Tessel to your device and [configure its network settings](https://tessel.github.io/t2-start/wifi.html) to connect it to the same network as your device.
1. Push the [index.json](/tessel/index.js) to the Tessel with `t2 push index.js`. 
1. Connect colored LEDs to the Tessel. You can use the following pins:
    ```
    'yellow': 0,
    'green': 1,
    'red': 2,
    'blue': 3
    ```
    ![Tessel](/img/tessel.jpg)

### Config and authentication
1. Make sure you have a Cognitive Services or dedicated Speech resource. If not, deploy one. 
1. Deploy an Azure KeyVault resource, if you do not have one already. Using KeyVault for storing secrets is not strictly necessary, but a good practice. 
1. Add the following to your KeyVault:
    - Key to your Speech or Cognitive Services resource
    - LUIS AppID
    - Key to your LUIS prediction or Cognitive Services resource
1. Enter the secret names, service region, LUIS endpoint and Tessel IP in [config.json](/local/config.json).

### Execution
1. Make sure the Tessel is powered and the on-board LEDs are on constantly.
1. Open VSCode and log into your Azure account (not necessary, but easiest way to authenticate).
1. Run [light_controller.py](/local/light_controller.py) in VSCode.
1. When prompted, say a command, e.g. "Turn on the red light". The terminal should now show a transcription of your command and the interpreted intention. The desired LED on the Tessel should change its state accordingly. 
    ```
    Begin speaking...
    Recognized: Enable the green and yellow LED.
    Performing prediction...
    Top intent: TurnOn
    Intents: 
            "TurnOn"
    Entities: {'LED': [['green'], ['yellow']]}
    ```
1. Try controlling multiple lights at once. You can include multiple entities (but not intents) in your command.

****

## FAQ
**Do I need to use a Tessel?**

No. I am using a Tessel for two reasons: It has onboard wifi and I had it lying around. Feel free to replicate this process with, e.g., an Arduino. That will require you to rewrite [index.js](/tessel/index.js) to your target language though.

**Could I run the entire program on the microcontroller?**

Yes, probably! If you attach a microphone to the Tessel, you should be able to modify [index.js](/tessel/index.js) to send the voice commands directly to Cognitive Services.

**Why do we need the Speech service?**

At the moment, I am interpreting the voice commands in two steps, first transcribing them with the Speech service, then interpreting them with Language Understanding. But we don't technically need the first step. Language Understanding also works directly with voice input. I just find that splitting it into separate steps makes for a nicer demo.

**Do I need to use Azure KeyVault?**

No, Azure KeyVault is not necessary, but storing secrets in code is bad practice and I find setting environment variables quite tedious.
If you really don't want to use KeyVault, you can modify [light_controller.py](/local/light_controller.py) to get the secrets another way.

**Do I need to use Visual Studio Code?**

No. I am using VSCode with the Azure extension because it allows me to automatically authenticate with Azure without having to explicitly provide credentials. See the documentation for [DefaultAzureCredential](https://docs.microsoft.com/en-us/python/api/azure-identity/azure.identity.defaultazurecredential?view=azure-python) for alternative ways to authenticate.


