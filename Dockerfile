FROM python:3 as app

RUN mkdir /work
RUN chmod +wr /work
WORKDIR /work

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY app/ app/

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]
