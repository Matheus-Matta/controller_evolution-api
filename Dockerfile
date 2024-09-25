# Usar a imagem do Python 3.9
FROM python:3.10-slim

# Definir o diretório de trabalho no container
WORKDIR /app

# Copiar os arquivos de requirements
COPY requirements.txt .

# Criar o diretório para os arquivos estáticos
RUN mkdir -p /app/static /app/staticfiles

# Instalar dependências do sistema e Python em uma única camada
RUN apt-get update && apt-get install -y \
    libpq-dev gcc python3-dev musl-dev \
    && pip install --no-cache-dir -r requirements.txt \
    && apt-get clean

# Copiar o código-fonte do Django para o container
COPY . .

# Expor a porta 8000 para o servidor web do Django
EXPOSE 8000

# Comando padrão para o Django (pode ser sobrescrito no docker-compose)
CMD ["sh", "-c", "python manage.py collectstatic --noinput && python manage.py makemigrations && python manage.py migrate && python manage.py runserver 0.0.0.0:8888"]