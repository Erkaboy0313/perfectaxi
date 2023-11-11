# Build stage
FROM python:3.10-slim as builder

# Set work directory
WORKDIR /usr/src/app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install build dependencies
RUN apt-get update \
    && apt-get install -y build-essential libpq-dev 

# Install pip dependencies
COPY ./requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /usr/src/app/wheels -r requirements.txt


# Final Stage
FROM python:3.10-slim

# Create the app user and directories
RUN groupadd -r eric && useradd -r -g eric eric
ENV HOME=/home/perfectaxi
WORKDIR $HOME

# Install runtime dependencies
RUN apt-get update && apt-get install -y libpq5 netcat-openbsd
COPY --from=builder /usr/src/app/wheels /wheels
COPY --from=builder /usr/src/app/requirements.txt .
RUN pip install --no-cache /wheels/*

# Copy entrypoint script
COPY ./entrypoint.prod.sh .
RUN sed -i 's/\r$//g' $HOME/entrypoint.prod.sh
RUN chmod +x $HOME/entrypoint.prod.sh

# Copy the project
COPY . $HOME

# Adjust file ownership
RUN chown -R eric:eric $HOME

# Switch to the app user
USER eric

# Run entrypoint script
ENTRYPOINT ["/home/perfectaxi/entrypoint.prod.sh"]