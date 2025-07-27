FROM --platform=linux/amd64 python:3.9-slim-buster
WORKDIR /app
RUN pip install pdfminer.six
COPY main.py .
RUN mkdir -p input output
ENTRYPOINT ["python", "main.py"]
