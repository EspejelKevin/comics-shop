FROM python:3.11-slim-buster

WORKDIR /layaway

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

ENV AUTODYNATRACE_CAPTURE_HEADERS=True
ENV AUTOWRAPT_BOOTSTRAP=autodynatrace
ENV TZ=America/Mexico_City
ENV SERVICE_NAME=layaway
ENV NAMESPACE=orders
ENV API_VERSION=v1
ENV IMAGE_VERSION=v1
ENV ENABLE_DOCS=true
ENV RELOAD=true
ENV DEVELOPER_PORTAL_HTTP_ERRORS=https://coppel-developer-app.com/errors
ENV SECRET_KEY=algo-super-hiper-mega-secretisimo-legalisimo
ENV ALGORITHM=HS256
ENV URL_LOGIN_KEY=http://userauth:8000/users/api/v1/keys
ENV URL_GET_COMIC_BY_ID=http://comicdetails:8002/catalogs/api/v1/records

EXPOSE 8001
CMD ["python", "src/main.py"]