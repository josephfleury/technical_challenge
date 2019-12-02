FROM python:3.7

ENV FLASK_ENV="production"

RUN mkdir -p /app/
ADD application /app/

WORKDIR /app

RUN pip install -r requirements.txt

EXPOSE 8080
EXPOSE 8081

ENTRYPOINT ["gunicorn"]
CMD ["-c", "config/gunicorn.config.py", "app:app"]