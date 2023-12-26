import re

import torch

from io import BytesIO

from scipy.io import wavfile
from transliterate import translit
from num2words import num2words


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

    mem_file = BytesIO()
    wavfile.write(mem_file, sample_rate, audio.numpy())
    mem_file.seek(0)

    return mem_file
