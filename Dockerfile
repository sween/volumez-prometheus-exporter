FROM python:3.8

ADD src /src

RUN pip install prometheus_client
RUN pip install requests

WORKDIR /src


ENV PYTHONPATH '/src/'
ENV PYTHONBUFFERED=1

ENV VLZ_USER 'secret'
ENV VLZ_PASS 'tenant'
ENV VLZ_USERPOOLID 'userpoolid'
ENV VLZ_CLIENTID 'clientid'
ENV VLZ_POLLING 'polling'

RUN pip install -r requirements.txt


CMD ["python" , "/src/volumez_exporter.py"]
