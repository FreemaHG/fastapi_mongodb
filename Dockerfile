FROM python:3.11-slim

COPY requirements.txt /src/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /src/requirements.txt

COPY ./src /src

COPY ./docker /docker

# Разрешаем Docker выполнять команды в ./docker/<file>.sh (bash-команды),
# используемые для загрузки демонстрационных данных и запуска сервера
RUN chmod a+x docker/*.sh

#CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload", "--reload-dir", "/src"]