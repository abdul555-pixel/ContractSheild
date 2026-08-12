FROM python:3.12-slim

WORKDIR /analysis

RUN pip install --no-cache-dir slither-analyzer

RUN useradd --create-home analyzer

RUN mkdir -p /analysis/input \
    && chown -R analyzer:analyzer /analysis

USER analyzer

CMD ["slither", "--help"]