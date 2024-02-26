#!/bin/bash

# Запуск сервера
uvicorn src.main:app --proxy-headers --host 0.0.0.0 --port 8000 --reload