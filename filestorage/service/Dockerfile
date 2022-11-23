FROM python:3

COPY ./app /app
COPY main.py /
COPY requirements.txt /

RUN mkdir /mnt/data
RUN pip3 install --no-cache-dir --upgrade pip
RUN pip3 install --no-cache-dir -r requirements.txt

EXPOSE 9090
CMD ["python3", "./main.py"]
