FROM python:3.11-slim
WORKDIR /app
COPY req.txt .
RUN pip3 install -r req.txt
COPY . .
CMD [ "python","main.py" ]