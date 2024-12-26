FROM python:3.12-alpine

WORKDIR .
ENV PYTHONPATH=/lib:/src

COPY requirements.txt .
RUN pip install --no-cache-dir -r ./requirements.txt

COPY src ./src
COPY lib ./lib

CMD ["python", "-m", "src"]