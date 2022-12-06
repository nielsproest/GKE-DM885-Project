FROM python

copy . /app
copy requirements.txt /app
WORKDIR /app
RUN pip install --upgrade pip

RUN pip install -r requirements.txt
CMD ["python", "app.py"]
