import re

import torch

from io import BytesIO

from scipy.io import wavfile
from transliterate import translit
from num2words import num2words
from pydub import AudioSegment


model, _ = torch.hub.load(
    repo_or_dir="./model-files",
    source="local",
    model="silero_tts",
    language="ru",
    speaker="v3_1_ru",
    trust_repo=True
)


def transliterate(text):
    text = text\
        .lower()\
        .replace("c", "к")\
        .replace("th", "t")\
        .replace("ph", "f")\
        .replace("q", "к")\
        .replace("w", "в")\
        .replace("x", "кс")        

    return translit(text, "ru")


def preprocess(text):
    pattern = r"[\d]+[.,]?\d*"
    parts = re.split(pattern, text)
    numbers = re.findall(pattern, text)

    numbers = [num2words(num.replace(",", "."), lang="ru") for num in numbers]

    result = parts.pop(0)
    for part in parts:
        result += numbers.pop(0) + part

    result = transliterate(result)

    return result


def speak(text: str, sample_rate=48000) -> BytesIO:

    audio = model.apply_tts(
        text=preprocess(text),
        speaker="kseniya",
        sample_rate=sample_rate,
        put_accent=True,
        put_yo=True
    )

    wav_file = BytesIO()
    wavfile.write(wav_file, sample_rate, audio.numpy())
    wav_file.seek(0)

    mp3_file = BytesIO()
    AudioSegment.from_file(wav_file).export(mp3_file, format="mp3")
    mp3_file.seek(0)

    return mp3_file
