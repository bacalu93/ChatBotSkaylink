FROM python:3

WORKDIR /app

COPY requirements.txt /app/requirements.txt
COPY *.py /app/
COPY tests/ /app/tests/


ENV AWS_DEFAULT_REGION 'eu-central-1'
RUN apt-get update && apt-get install poppler-utils libpoppler-dev ffmpeg libsm6 libxext6 tesseract-ocr -y

RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt
RUN pip install pytest

# Run the tests
Run pytest tests/

ENTRYPOINT [ "python", "./update_knowledge_base.py" ]
