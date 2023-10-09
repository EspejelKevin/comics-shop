FROM python:3.11-slim-buster

WORKDIR /comicDetails

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

ENV AUTODYNATRACE_CAPTURE_HEADERS=True
ENV AUTOWRAPT_BOOTSTRAP=autodynatrace
ENV TZ=America/Mexico_City
ENV SERVICE_NAME=comicDetails
ENV NAMESPACE=catalogs
ENV API_VERSION=v1
ENV IMAGE_VERSION=v1
ENV ENABLE_DOCS=true
ENV RELOAD=true
ENV DEVELOPER_PORTAL_HTTP_ERRORS=https://coppel-developer-app.com/errors
ENV MARVEL_API_PUBLIC_KEY=f559f02009199fb73e31dabc8a7e45e2
ENV MARVEL_API_PRIVATE_KEY=da392f96a25f03ca33669e43a08ee9a6c48b7e62


EXPOSE 8002
CMD ["python", "src/main.py"]