FROM python:3.12.3-slim-bullseye

ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# RUN python3 -m ensurepip --upgrade
WORKDIR /elec_lca/
ADD src/ ./src
ADD .env .
EXPOSE 8000
ENV PYTHONPATH="/elec_lca"
CMD python src/microservice/main.py