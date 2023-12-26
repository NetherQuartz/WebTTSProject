FROM python:3.11-slim

WORKDIR /usr/app

ENV TZ Europe/Moscow

ADD requirements.txt .

RUN apt-get update && \
    apt-get install -y ffmpeg && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir --index-url https://download.pytorch.org/whl/cpu torch && \
    rm -rf /var/lib/apt/lists/* /var/cache/apt/archives

ADD webservice webservice
ADD web-resources web-resources
ADD download_model.py .

RUN python ./download_model.py && mv /root/.cache/torch/hub/snakers4_silero-models_master model-files

CMD [ "python", "-m", "webservice" ]
