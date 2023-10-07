FROM python:3.11-slim-buster

COPY . /

RUN pip install -r requirements.txt

ENV AUTODYNATRACE_CAPTURE_HEADERS=True
ENV AUTOWRAPT_BOOTSTRAP=autodynatrace
ENV TZ=America/Mexico_City

EXPOSE 8002
CMD ["python", "src/main.py"]