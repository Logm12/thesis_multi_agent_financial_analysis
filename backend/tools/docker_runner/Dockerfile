FROM python:3.12-slim

# Enforce clean non-root runtime environment
RUN groupadd -g 1000 sandbox && useradd -u 1000 -g sandbox -s /bin/sh -m sandbox

# Install required numerical libraries
RUN pip install --no-cache-dir pandas numpy matplotlib jinja2

WORKDIR /home/sandbox
USER sandbox

# Input stream execution entry point
ENTRYPOINT ["python", "-u", "-c"]
