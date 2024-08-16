FROM python:3.9-slim

ENV APP_HOME /app
WORKDIR $APP_HOME
COPY . ./

RUN pip install --no-cache-dir -r requirements.txt
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

ENV PYTHONUNBUFFERED True

ENV PORT 8501
EXPOSE $PORT

# Run the Streamlit app
ENTRYPOINT ["sh", "-c", "streamlit run Home.py --server.port=$PORT --server.address=0.0.0.0"]

# Healthcheck to ensure the service is running
HEALTHCHECK CMD curl --fail http://localhost:$PORT/_stcore/health || exit 1
