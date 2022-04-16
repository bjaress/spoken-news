FROM python:3 as requirements

COPY requirements.txt .
RUN pip install -r requirements.txt



FROM requirements as test

COPY requirements-dev.txt .
RUN pip install -r requirements-dev.txt

COPY app/ app/
COPY test/ test/
RUN python -m unittest


FROM requirements as app

RUN mkdir /work
RUN chmod +wr /work
WORKDIR /work

EXPOSE 8000

USER nobody
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
COPY --from=test /app/ app/
