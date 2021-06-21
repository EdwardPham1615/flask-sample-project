FROM python:3.8-slim

WORKDIR /opt/app
RUN apt-get update && apt-get install -y build-essential python-dev

COPY requirements.txt ./requirements.txt
RUN pip3 install --no-cache-dir -r ./requirements.txt

COPY ./index_api ./index_api

COPY ./search_api ./search_api

COPY ./tests ./tests

COPY ./run.sh ./run.sh

COPY ./config ./config

COPY ./extensions ./extensions

COPY ./health_check.py ./health_check.py

COPY ./app.py ./app.py

ENV PORT 8080
ENV NUMBER_PROCESS 4
RUN chmod +x run.sh

CMD ["./run.sh"]
