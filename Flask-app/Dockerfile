FROM python:3.10-slim

# Set working directory
WORKDIR /app
COPY . .
RUN pip install --timeout=300 -r requirements.txt
EXPOSE 5000

# Run Flask app
CMD flask --app app.py run
