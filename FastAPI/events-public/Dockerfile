FROM python:3-slim

ENV PYTHONUNBUFFERED True

ENV APP_HOME /app
WORKDIR $APP_HOME
COPY . ./

ENV PORT 9000
EXPOSE $PORT

RUN pip install --no-cache-dir -r src/requirements.txt

# As an example here we're running the web service with one worker on uvicorn.
CMD exec uvicorn src.main:app --host 0.0.0.0 --port $PORT --workers 1
