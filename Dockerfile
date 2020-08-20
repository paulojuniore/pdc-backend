FROM python:3

WORKDIR /api

COPY . /api

RUN pip install -r requirements.txt

ENTRYPOINT ["python3"]

CMD ["run.py"]