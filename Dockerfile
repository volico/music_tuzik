FROM python:3.10-slim

ENV ENV_FILE=""

ENV TOKEN=""
ENV DOWNLOAD_PATH="./audio"
ENV MAX_QUEUE_SIZE=30
ENV COMMAND_PREFIX="/"
ENV MESSAGES='{"not_in_voice_channel":"Im not in a voice channel","user_not_in_voice_channel":"You are not in a voice channel","unsupported_url":"Unsupported url","queue_full":"Queue is full, please wait fors track to finish","start_playing":"{} plays: '{}'","move_to_another_channel":"Bot was moved to {} channel"}'
ENV MESSAGE_HISTORY_LENGTH=10

WORKDIR /usr/muzik-tuzik

COPY src ./src
COPY requirements.txt .
COPY envs ./envs
COPY main.py .
COPY settings.py .

RUN apt-get update && apt upgrade && apt-get install -y curl && apt install -y ffmpeg
RUN curl -L https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp -o /usr/local/bin/yt-dlp && \
    chmod a+rx /usr/local/bin/yt-dlp  # Make executable
RUN pip install -r requirements.txt

CMD python main.py
