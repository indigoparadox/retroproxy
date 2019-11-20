
FROM tiangolo/uwsgi-nginx:python3.7-alpine3.7

# Copy app files.
COPY src/static /app/static
COPY src/templates /app/templates
COPY src/*.py /app/
COPY src/uwsgi.ini /app/

# Setup Python dependencies.
COPY requirements.txt .
RUN pip install -r requirements.txt



