FROM python:3.9-alpine

RUN mkdir /gregbot
WORKDIR /gregbot

# Keep this before copying source in order to keep compilation times sane and take advantage of image caching
ADD Pipfile .
ADD Pipfile.lock .
RUN apk add gcc libxml2-dev libxslt-dev musl-dev openssl-dev libffi-dev libjpeg-turbo-dev libwebp libwebp-dev rust cargo git
RUN python -m pip install pipenv
RUN pipenv install

# Rename the selfbot fork to avoid namespace collision
RUN mv "$(pipenv --venv)/src/discord-py-self/discord" "$(pipenv --venv)/src/discord-py-self/discordself"

ADD . .

CMD ["pipenv", "run", "python", "./main.py"]
