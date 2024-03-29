
FROM alpine:3.7
RUN apk add --no-cache python3 py3-pip

# Temporarily install files for Python C extension compiles.
RUN apk add --no-cache --virtual .build-deps python3-dev gcc musl-dev

# Copy app files.
COPY . /app/
WORKDIR /app/
RUN pip3 install --upgrade pip
RUN pip3 install .

# Remove temporarily installed files.
RUN apk del .build-deps

CMD ["python3", "-m", "retroproxy", "-a", "0.0.0.0"]
