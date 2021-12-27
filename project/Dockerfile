FROM python:3.6
LABEL maintainer="Fausto Almeida"

EXPOSE 3111

COPY ./techtrends /app
WORKDIR /app
RUN pip install -r requirements.txt
RUN python init_db.py

# command to run on container start
CMD [ "python3", "app.py" ]
