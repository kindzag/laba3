#!/usr/bin/env python3
"""
Скрипт для анализа репозитория GitHub
Анализирует объём, количество файлов и папок
"""

import os
import sys
import json
from datetime import datetime
from typing import Dict, List, Tuple
import argparse


def get_repo_stats(start_path: str = ".") -> Dict:
    """
    Собирает статистику по репозиторию
    
    Returns:
        Словарь со статистикой
    """
    total_size = 0
    file_count = 0
    dir_count = 0
    files_by_extension = {}
    largest_files = []
    
    # Игнорируемые директории и файлы
    ignore_dirs = {'.git', '.github', '__pycache__', 'node_modules', 'venv', '.venv', '.idea', '.vscode'}
    ignore_files = {'.gitignore', '.DS_Store', 'Thumbs.db', 'report.log', 'report.json'}
    
    for root, dirs, files in os.walk(start_path):
        # Убираем игнорируемые директории
        dirs[:] = [d for d in dirs if d not in ignore_dirs]
        
        # Увеличиваем счётчик директорий
        dir_count += 1
        
        for file in files:
            if file in ignore_files:
                continue
                
            file_path = os.path.join(root, file)
            
            try:
                # Получаем размер файла
                file_size = os.path.getsize(file_path)
                total_size += file_size
                file_count += 1
                
                # Статистика по расширениям
                _, ext = os.path.splitext(file)
                ext = ext.lower() if ext else 'no_extension'
                files_by_extension[ext] = files_by_extension.get(ext, 0) + 1
                
                # Топ 10 самых больших файлов
                largest_files.append((file_path, file_size))
                
            except (OSError, PermissionError):
                # Пропускаем файлы, к которым нет доступа
                continue
    
    # Сортируем файлы по размеру (по убыванию)
    largest_files.sort(key=lambda x: x[1], reverse=True)
    
    # Форматируем размер
    def format_size(size_bytes: int) -> str:
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} TB"
    
    # Форматируем время
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    return {
        'timestamp': current_time,
        'total_size_bytes': total_size,
        'total_size_human': format_size(total_size),
        'file_count': file_count,
        'directory_count': dir_count - 1,  # минус корневая директория
        'total_items': file_count + dir_count - 1,
        'files_by_extension': files_by_extension,
        'largest_files': [
            {
                'path': os.path.relpath(path, start_path),
                'size_bytes': size,
                'size_human': format_size(size)
            }
            for path, size in largest_files[:10]  # топ-10
        ],
        'average_file_size': format_size(total_size / file_count) if file_count > 0 else "0 B"
    }


def save_report(stats: Dict, output_file: str = "report.log") -> None:
    """
    Сохраняет отчёт в файл
    
    Args:
        stats: Статистика репозитория
        output_file: Имя выходного файла
    """
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("=" * 60 + "\n")
        f.write("ОТЧЁТ О СТАТИСТИКЕ РЕПОЗИТОРИЯ\n")
        f.write("=" * 60 + "\n\n")
        
        f.write(f"Время анализа: {stats['timestamp']}\n")
        f.write(f"Всего файлов: {stats['file_count']:,}\n")
        f.write(f"Всего папок: {stats['directory_count']:,}\n")
        f.write(f"Всего элементов: {stats['total_items']:,}\n")
        f.write(f"Общий объём: {stats['total_size_human']}\n")
        f.write(f"Средний размер файла: {stats['average_file_size']}\n")
        
        f.write("\n" + "-" * 60 + "\n")
        f.write("РАСПРЕДЕЛЕНИЕ ПО РАСШИРЕНИЯМ:\n")
        f.write("-" * 60 + "\n")
        
        # Сортируем расширения по количеству файлов
        sorted_extensions = sorted(
            stats['files_by_extension'].items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        for ext, count in sorted_extensions:
            ext_name = ext if ext != 'no_extension' else '(без расширения)'
            percentage = (count / stats['file_count']) * 100 if stats['file_count'] > 0 else 0
            f.write(f"{ext_name:<20} {count:>6} файлов ({percentage:.1f}%)\n")
        
        f.write("\n" + "-" * 60 + "\n")
        f.write("ТОП-10 САМЫХ БОЛЬШИХ ФАЙЛОВ:\n")
        f.write("-" * 60 + "\n")
        
        for i, file_info in enumerate(stats['largest_files'], 1):
            f.write(f"{i:2}. {file_info['path']:<40} {file_info['size_human']:>10}\n")
        
        f.write("\n" + "=" * 60 + "\n")
        f.write("КОНЕЦ ОТЧЁТА\n")
        f.write("=" * 60 + "\n")
    
    print(f"✅ Отчёт сохранён в: {output_file}")
    print(f"📊 Статистика:")
    print(f"   Файлов: {stats['file_count']:,}")
    print(f"   Папок: {stats['directory_count']:,}")
    print(f"   Объём: {stats['total_size_human']}")


def save_json_report(stats: Dict, output_file: str = "report.json") -> None:
    """
    Сохраняет отчёт в JSON формате
    
    Args:
        stats: Статистика репозитория
        output_file: Имя выходного файла
    """
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)
    
    print(f"✅ JSON отчёт сохранён в: {output_file}")


def parse_arguments():
    """Парсинг аргументов командной строки"""
    parser = argparse.ArgumentParser(
        description='Анализ репозитория: статистика файлов и папок',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--path',
        default='.',
        help='Путь к анализируемой директории (по умолчанию: текущая)'
    )
    
    parser.add_argument(
        '--output',
        default='report.log',
        help='Имя выходного файла (по умолчанию: report.log)'
    )
    
    parser.add_argument(
        '--json',
        action='store_true',
        help='Сохранить дополнительный JSON отчёт'
    )
    
    return parser.parse_args()


def main():
    """Основная функция"""
    args = parse_arguments()
    
    print(f"🔍 Анализ репозитория: {args.path}")
    
    try:
        # Сбор статистики
        stats = get_repo_stats(args.path)
        
        # Сохранение отчёта
        save_report(stats, args.output)
        
        # Дополнительный JSON отчёт
        if args.json:
            save_json_report(stats, 'report.json')
        
        return 0
        
    except FileNotFoundError:
        print(f"❌ Ошибка: Директория '{args.path}' не найдена!")
        return 1
    except PermissionError:
        print(f"❌ Ошибка: Нет доступа к директории '{args.path}'!")
        return 1
    except Exception as e:
        print(f"❌ Непредвиденная ошибка: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
