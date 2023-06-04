FROM python:3.9

WORKDIR /backend

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000

ENV FLASK_APP=backend

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "backend:app"]
