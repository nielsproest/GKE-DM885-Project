FROM python:3

WORKDIR .

ADD app /
COPY main.py /
COPY requirements.txt /

RUN mkdir /mnt/data
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "./main.py"]