FROM python:3.12-slim

WORKDIR /usr/src/app

COPY ./requirements.txt .

RUN pip install -i https://mirror-pypi.runflare.com/simple --no-cache-dir --upgrade -r ./requirements.txt

COPY ./app .

CMD ["fastapi", "dev", "--host", "0.0.0.0", "--port", "8000"]