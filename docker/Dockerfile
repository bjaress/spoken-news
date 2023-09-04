FROM python:3.10-alpine as requirements

COPY requirements.txt .
RUN pip install -r requirements.txt



FROM requirements as test

COPY requirements-dev.txt .
RUN pip install -r requirements-dev.txt

COPY api/ api/
COPY test/ test/
RUN python -m unittest
# run without --check to reformat if needed
RUN black --check api test

FROM requirements as api

RUN mkdir /work
RUN chmod +wr /work
WORKDIR /work

USER nobody
COPY docker/entrypoint.sh entrypoint.sh
ENTRYPOINT ["./entrypoint.sh"]

COPY --from=test /api/ api/
