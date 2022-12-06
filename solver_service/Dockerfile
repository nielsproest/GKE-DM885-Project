#FROM python:3.9

#COPY requirements.txt /

#RUN pip install --no-cache-dir --upgrade -r requirements.txt

#COPY ./app /app

#CMD ["uvicorn", "main:app", "--host=0.0.0.0", "--port", "8080"]

FROM python:3.9

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./app /code/app

WORKDIR /code/app

CMD ["uvicorn", "main:app", "--host=0.0.0.0", "--port", "5432"]