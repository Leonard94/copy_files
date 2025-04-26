# -*- coding: utf-8 -*-
# Импортируем необходимые модули
from pathlib import Path
import shutil
import re
import os  # Добавлен для обработки ошибок доступа

# --- Константы для путей ---
# Папка, откуда копируем файлы (используйте необработанные строки r'' или двойные слеши \\ для Windows)
SOURCE_DIRECTORY = Path('./backend')
# Папка, куда копируем файлы
DESTINATION_DIRECTORY = Path('./delete_backend')
# -------------------------

# --- Конфигурация ---
CONFIG = {
    # Расширения файлов, которые нужно копировать
    'FILE_EXTENSIONS': ['.js', '.ts', '.jsx', '.tsx', '.sql', '.py', '.java', '.cs', '.html', '.css', '.scss', '.json', '.yaml', '.yml', '.md'],
    # Имена директорий, содержимое которых нужно полностью игнорировать
    'EXCLUDED_DIRS': ['node_modules', 'dist', 'build', 'target', 'out', 'bin', 'obj', '.git', '.svn', '.vscode', '.idea', 'venv', '__pycache__'],
    # Паттерны в ИМЕНАХ файлов, которые нужно игнорировать (даже если расширение подходит)
    'EXCLUDED_PATTERNS': ['.d.ts', '.min.js', '.log', 'package-lock.json'],
    # Конкретные имена файлов, которые нужно копировать ВСЕГДА (если они не в исключенной папке/паттерне)
    'INCLUDE_SPECIFIC_FILES': ['Dockerfile', '.dockerignore', 'docker-compose.yml', 'docker-compose.yaml', 'dockerfile']
}
# --------------------

def get_unique_filename(destination_dir: Path, filename: str, add_txt_to_dockerfile: bool = False) -> Path:
    # Специальная обработка для Dockerfile - добавляем расширение .txt
    if add_txt_to_dockerfile and filename.lower() == 'dockerfile':
        filename = 'Dockerfile.txt'
    
    filepath = destination_dir / filename

    if not filepath.exists():
        return filepath

    # Если файл уже существует, генерируем новое имя
    name = filepath.stem
    suffix = filepath.suffix
    counter = 1

    while True:
        # Формируем новое имя файла с счетчиком
        # Для файлов без расширения (как Dockerfile), stem будет именем, suffix пустым
        if suffix:
            new_filename = f"{name}_{counter}{suffix}"
        else:
             # Если расширения нет, добавляем счетчик к имени
             new_filename = f"{name}_{counter}"

        new_filepath = destination_dir / new_filename

        if not new_filepath.exists():
            return new_filepath # Нашли свободное имя

        counter += 1 # Увеличиваем счетчик и пробуем снова

def should_skip_dir(dir_path: Path) -> bool:
    try:
        # dir_path.parts дает кортеж компонентов пути ('C:', 'Users', 'Project', 'node_modules', 'some_lib')
        return any(part in CONFIG['EXCLUDED_DIRS'] for part in dir_path.parts)
    except Exception as e:
        print(f"Предупреждение: Не удалось проверить путь директории '{dir_path}' на исключения: {e}")
        return False # На всякий случай не пропускаем, если проверка не удалась

def should_skip_file(file_path: Path) -> bool:
    """
    Проверяет, нужно ли пропустить файл на основе списка EXCLUDED_PATTERNS.
    Ищет любой из паттернов как подстроку в имени файла.

    Args:
        file_path: Путь к файлу (объект Path).

    Returns:
        bool: True если файл нужно пропустить (содержит исключенный паттерн).
    """
    try:
        return any(pattern in file_path.name for pattern in CONFIG['EXCLUDED_PATTERNS'])
    except Exception as e:
        print(f"Предупреждение: Не удалось проверить имя файла '{file_path.name}' на исключенные паттерны: {e}")
        return False # На всякий случай не пропускаем

def is_specific_file(file_name: str) -> bool:
    """
    Проверяет, входит ли имя файла в список специальных файлов для копирования.
    Проверка нечувствительна к регистру.

    Args:
        file_name: Имя файла для проверки.

    Returns:
        bool: True если файл входит в список спецфайлов.
    """
    return any(file_name.lower() == specific_file.lower() for specific_file in CONFIG['INCLUDE_SPECIFIC_FILES'])

def clear_destination():
    """
    Очищает папку назначения перед копированием.
    Использует константу DESTINATION_DIRECTORY.
    """
    dest_dir = DESTINATION_DIRECTORY
    print(f"\n--- Очистка папки назначения: {dest_dir.resolve()} ---")
    if dest_dir.exists():
        print(f"Папка существует. Попытка удаления...")
        try:
            # Рекурсивно удаляем содержимое папки и саму папку
            shutil.rmtree(dest_dir, ignore_errors=False) # ignore_errors=False чтобы видеть ошибки
            print("Папка успешно удалена.")
        except PermissionError:
             print(f"ОШИБКА: Нет прав для удаления папки {dest_dir} или ее содержимого.")
             print("Возможно, файл из этой папки открыт в другой программе.")
             return False # Сигнализируем об ошибке
        except OSError as e:
            print(f"ОШИБКА: Не удалось удалить папку {dest_dir}: {e}")
            return False # Сигнализируем об ошибке
    else:
        print("Папки не существует, очистка не требуется.")

    # Создаем папку заново (или если ее не было)
    try:
        dest_dir.mkdir(parents=True, exist_ok=True) # parents=True создает родительские папки, exist_ok=True не вызывает ошибку, если папка уже есть
        print("Папка назначения успешно создана (или уже существовала).")
        return True # Успех
    except PermissionError:
        print(f"ОШИБКА: Нет прав для создания папки {dest_dir}.")
        return False # Сигнализируем об ошибке
    except OSError as e:
         print(f"ОШИБКА: Не удалось создать папку {dest_dir}: {e}")
         return False # Сигнализируем об ошибке

def copy_files():
    """
    Основная функция для поиска и копирования файлов.
    Использует глобальные константы и CONFIG.
    """
    source_dir = SOURCE_DIRECTORY
    dest_dir = DESTINATION_DIRECTORY

    # --- Первичные проверки ---
    print(f"--- Запуск скрипта копирования ---")
    print(f"Исходная директория: {source_dir.resolve()}")
    print(f"Директория назначения: {dest_dir.resolve()}")

    if not source_dir.exists() or not source_dir.is_dir():
        print(f"\nОШИБКА: Исходная директория '{source_dir}' не найдена или не является папкой.")
        print("Пожалуйста, проверьте путь в константе SOURCE_DIRECTORY.")
        return # Прерываем выполнение

    if not source_dir.is_absolute():
         print(f"Предупреждение: Исходный путь '{source_dir}' относительный. Убедитесь, что скрипт запускается из правильной рабочей директории.")
    if not dest_dir.is_absolute():
         print(f"Предупреждение: Путь назначения '{dest_dir}' относительный.")

    # --- Очистка папки назначения ---
    if not clear_destination():
        print("\nОШИБКА: Не удалось подготовить папку назначения. Копирование прервано.")
        return # Прерываем, если очистка не удалась

    # --- Вывод конфигурации ---
    print("\n--- Параметры копирования ---")
    print(f"Расширения для копирования: {CONFIG['FILE_EXTENSIONS']}")
    print(f"Специфичные файлы для копирования: {CONFIG['INCLUDE_SPECIFIC_FILES']}")
    print(f"Исключаемые директории (по имени): {CONFIG['EXCLUDED_DIRS']}")
    print(f"Исключаемые паттерны в именах файлов: {CONFIG['EXCLUDED_PATTERNS']}")

    # --- Инициализация статистики ---
    stats = {
        'total_items_scanned': 0,
        'files_scanned': 0,
        'dirs_scanned': 0,
        'skipped_dir_exclusion': 0,      # Пропущено из-за папки в EXCLUDED_DIRS
        'skipped_pattern_exclusion': 0,  # Пропущено из-за паттерна в EXCLUDED_PATTERNS
        'skipped_type_mismatch': 0,      # Пропущено т.к. не подходит ни расширение, ни спец. имя
        'copied_files': 0,
        'renamed_due_to_collision': 0,
        'copy_errors': 0
    }

    print("\n--- Начало сканирования и копирования ---")
    try:
        # Рекурсивно обходим все элементы в исходной директории
        # rglob('*') найдет и файлы, и папки
        for item in source_dir.rglob('*'):
            stats['total_items_scanned'] += 1

            # Определяем, файл это или папка
            is_dir = False
            try:
                 is_dir = item.is_dir()
            except OSError as e:
                 print(f"Предупреждение: Ошибка доступа при проверке типа элемента '{item}': {e}. Пропускаем.")
                 stats['copy_errors'] += 1 # Считаем как ошибку
                 continue # Пропускаем элемент, если не можем определить тип

            if is_dir:
                stats['dirs_scanned'] += 1
                # Проверяем, не нужно ли пропустить эту директорию целиком
                if should_skip_dir(item):
                    # Важно: rglob сам по себе не пропустит содержимое исключенной папки,
                    # но эта проверка может быть полезна для статистики или доп. логики
                    # print(f"Директория {item.relative_to(source_dir)} находится в исключенной зоне.")
                    # Ничего не делаем, rglob продолжит обход, но файлы из нее будут отфильтрованы ниже
                    pass # Просто для ясности, что мы ее заметили
                continue # Переходим к следующему элементу, папки не копируем

            # Если это не папка, считаем, что это файл (или ссылка и т.д.)
            stats['files_scanned'] += 1

            # --- Фильтрация файлов ---

            # 1. Проверка на исключенную директорию (проверяем ПУТЬ к файлу)
            # Файл может быть не в самой исключенной папке, а в ее подпапке
            if should_skip_dir(item.parent):
                # print(f"Пропуск (в исключенной дир.): {item.relative_to(source_dir)}")
                stats['skipped_dir_exclusion'] += 1
                continue

            # 2. Проверка на тип файла (расширение или специальное имя)
            is_target_extension = item.suffix.lower() in CONFIG['FILE_EXTENSIONS'] # Сравниваем в нижнем регистре
            # Используем новую функцию для проверки специальных файлов (регистронезависимо)
            is_specific_file_match = is_specific_file(item.name)

            if not (is_target_extension or is_specific_file_match):
                # Файл не подходит ни по расширению, ни по имени
                # print(f"Пропуск (не тот тип): {item.relative_to(source_dir)}")
                stats['skipped_type_mismatch'] += 1
                continue

            # 3. Проверка на исключенный паттерн в имени файла
            if should_skip_file(item):
                # print(f"Пропуск (искл. паттерн): {item.relative_to(source_dir)}")
                stats['skipped_pattern_exclusion'] += 1
                continue

            # --- Копирование файла ---
            # Если все проверки пройдены, копируем файл
            try:
                # Проверяем, является ли файл Dockerfile (регистронезависимо)
                is_dockerfile = item.name.lower() == 'dockerfile'
                
                # Получаем уникальное имя файла для папки назначения
                # Передаем флаг, нужно ли добавить .txt к Dockerfile
                dest_file = get_unique_filename(dest_dir, item.name, add_txt_to_dockerfile=is_dockerfile)

                # Копируем файл, сохраняя метаданные (например, время модификации)
                shutil.copy2(item, dest_file) # copy2 сохраняет метаданные
                stats['copied_files'] += 1

                # Проверяем, было ли имя изменено при копировании
                if dest_file.name != item.name:
                    stats['renamed_due_to_collision'] += 1
                    print(f"Скопирован (переименован): {item.relative_to(source_dir)} -> {dest_file.name}")
                else:
                    print(f"Скопирован: {item.relative_to(source_dir)} -> {dest_file.name}")

            except PermissionError:
                print(f"ОШИБКА КОПИРОВАНИЯ (нет прав): {item.relative_to(source_dir)}")
                stats['copy_errors'] += 1
            except Exception as copy_error:
                # Ловим другие возможные ошибки при копировании
                print(f"ОШИБКА КОПИРОВАНИЯ файла {item.relative_to(source_dir)}: {copy_error}")
                stats['copy_errors'] += 1

        # --- Вывод итоговой статистики ---
        print("\n--- Статистика выполнения ---")
        print(f"Всего элементов просканировано: {stats['total_items_scanned']}")
        print(f"  Из них папок: {stats['dirs_scanned']}")
        print(f"  Из них файлов: {stats['files_scanned']}")
        print("-" * 20)
        print(f"Пропущено файлов:")
        print(f"  Из-за нахождения в исключенной директории: {stats['skipped_dir_exclusion']}")
        print(f"  Из-за неподходящего типа (расширение/имя): {stats['skipped_type_mismatch']}")
        print(f"  Из-за исключенного паттерна в имени: {stats['skipped_pattern_exclusion']}")
        print("-" * 20)
        print(f"Скопировано файлов: {stats['copied_files']}")
        print(f"  Из них переименовано (из-за коллизий имен): {stats['renamed_due_to_collision']}")
        print(f"Ошибок при доступе/копировании: {stats['copy_errors']}")
        print("--- Операция завершена ---")

    except PermissionError as e:
         print(f"\nКРИТИЧЕСКАЯ ОШИБКА: Отказано в доступе при сканировании директории {source_dir}. Проверьте права доступа.")
         print(f"Ошибка: {e}")
    except Exception as e:
        # Ловим общие ошибки на уровне всего процесса
        print(f"\nПроизошла непредвиденная ошибка во время сканирования/копирования: {e}")
        # Можно добавить вывод traceback для отладки
        # import traceback
        # traceback.print_exc()


# Точка входа в скрипт
if __name__ == "__main__":
    # Вызываем основную функцию копирования
    copy_files()