import torch


torch.hub.load(
    repo_or_dir="snakers4/silero-models",
    model="silero_tts",
    language="ru",
    speaker="v3_1_ru",
    trust_repo=True
)
