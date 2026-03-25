FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_DEFAULT_TIMEOUT=180

WORKDIR /app

ARG PIP_INDEX_URL=https://pypi.org/simple

RUN apt-get update \
	&& apt-get install -y --no-install-recommends build-essential python3-dev \
	&& rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --retries 10 --timeout 180 -i ${PIP_INDEX_URL} --upgrade pip setuptools wheel \
	&& pip install --no-cache-dir --retries 10 --timeout 180 -i ${PIP_INDEX_URL} -r /app/requirements.txt

COPY backend /app/backend

EXPOSE 8000

CMD ["uvicorn","backend.main:app","--host","0.0.0.0","--port","8000"]
