FROM python:3.6.5

ADD . /code

WORKDIR /code

RUN git clone https://github.com/NCATS-Tangerine/smartBag.git

RUN pip install -r smartBag/requirements.txt

RUN apt-get update

WORKDIR /smartBag

ENTRYPOINT ["/bin/bash", "-c", "./smartbag run smartapi --port 5000"]

