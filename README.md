# GitHub Repository Analyzer

Автоматический анализ репозитория с помощью GitHub Actions.

##  Что анализируется
- Количество файлов и папок
- Общий объём репозитория
- Распределение по расширениям файлов
- Топ-10 самых больших файлов

##  Как работает
При каждом push в ветку main/master:
1. Запускается GitHub Action
2. Скрипт анализирует репозиторий
3. Создаётся файл `report.log` с отчётом
4. Создаётся файл `report.json` с данными
5. Оба файла коммитятся обратно в репозиторий

##  Структура
github/workflows/analyze.yml # GitHub Action
analyze_repo.py # Скрипт анализа
report.log # Отчёт (генерируется)
report.json # JSON данные (генерируется)

##  Локальный запуск

python analyze_repo.py
python analyze_repo.py --json
python analyze_repo.py --output custom.log


# ** ШАГ 6 Создаем .gitignore

nano .gitignore
# Отчёты анализа (будут генерироваться GitHub Actions)
report.log
report.json

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
venv/
env/
.venv/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~



