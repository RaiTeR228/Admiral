FROM python:3.11-slim
WORKDIR /app
COPY req.txt .
RUN pip3 install -r req.txt
COPY . .
CMD [ "venv/bin/pip", "install", "-r", "req.txt" ]
CMD [ "python","main.py", "run" ]