FROM python:3.12.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . /app/inkai
RUN useradd --uid 10001 --create-home minemind
USER minemind
EXPOSE 8088
CMD ["python", "-m", "inkai.server"]
