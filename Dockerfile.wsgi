FROM python:3.9

COPY requirements.txt .
RUN pip install -r requirements.txt

# libgl1.so needed by gunicorn
RUN apt-get update -y && apt-get install -y libgl1

COPY web/ ./

CMD ["gunicorn", "--bind=0.0.0.0", "wsgi:app"]