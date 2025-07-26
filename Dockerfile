# Use Python 3.13 slim
FROM python:3.13-slim

# Definir variáveis de ambiente
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Criar e definir diretório de trabalho
WORKDIR /app

# Copiar arquivos de dependências
COPY requirements.txt .
COPY Pipfile* ./

# Instalar dependências
RUN pip install --no-cache-dir pipenv && \
    pipenv install --deploy --system && \
    pip uninstall -y pipenv

# Copiar código fonte
COPY . .

# Expor porta
EXPOSE 8000

# Comando para iniciar a aplicação
CMD ["gunicorn", "--worker-class", "eventlet", "-w", "1", "--bind", "0.0.0.0:8000", "wsgi:app"]
