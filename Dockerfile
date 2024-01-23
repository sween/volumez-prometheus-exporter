FROM python:3.8

ADD src /src

RUN pip install prometheus_client
RUN pip install requests

WORKDIR /src


ENV PYTHONPATH '/src/'
ENV VOLUMEZ_TOKEN 'secret'

CMD ["python" , "/src/volumez_exporter.py"]
