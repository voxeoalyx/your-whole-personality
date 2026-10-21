FROM python:3.12-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
RUN groupadd --gid 10001 app && useradd --uid 10001 --gid app --no-create-home app && mkdir /state && chown app:app /state
COPY --chown=app:app server.py serve_public.py container_entrypoint.py protection.py game.py investigator.py model_client.py qloo_client.py scoring.py signals.py ./
COPY --chown=app:app static/ ./static/
COPY --chown=app:app data/ ./data/
EXPOSE 10000
CMD ["python", "container_entrypoint.py"]
