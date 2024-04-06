from transformers import pipeline


def detect_hate_speech(text: str):
    classifier = pipeline(
        "text-classification", model="facebook/roberta-hate-speech-dynabench-r4-target"
    )
    res = classifier(text)
    return res
