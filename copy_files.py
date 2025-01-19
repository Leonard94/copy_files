from pathlib import Path
import shutil
import re

CONFIG = {
    'FILE_EXTENSIONS': ['.js', '.ts', '.jsx', '.tsx', '.sql'],
    'EXCLUDED_DIRS': ['node_modules', 'dist'],
    'EXCLUDED_PATTERNS': ['.d.ts'],
    'SOURCE_DIR': './back',
    'DESTINATION_DIR': './delete'
}

def get_unique_filename(destination_dir: Path, filename: str) -> Path:
    filepath = destination_dir / filename
    
    if not filepath.exists():
        return filepath

    name = filepath.stem
    suffix = filepath.suffix
    counter = 1

    while True:
        new_filename = f"{name}_{counter}{suffix}"
        new_filepath = destination_dir / new_filename
        
        if not new_filepath.exists():
            return new_filepath
        
        counter += 1

def should_skip_dir(dir_path: Path) -> bool:
    return any(excluded in dir_path.parts for excluded in CONFIG['EXCLUDED_DIRS'])

def should_skip_file(file_path: Path) -> bool:
    """
    Проверяет, нужно ли пропустить файл
    
    Args:
        file_path: Путь к файлу
    
    Returns:
        bool: True если файл нужно пропустить
    """
    return any(pattern in file_path.name for pattern in CONFIG['EXCLUDED_PATTERNS'])

def clear_destination():
    """
    Очищает папку назначения
    """
    dest_dir = Path(CONFIG['DESTINATION_DIR'])
    if dest_dir.exists():
        print(f"Очистка папки {dest_dir}...")
        shutil.rmtree(dest_dir)
    dest_dir.mkdir(parents=True, exist_ok=True)
    print("Папка назначения очищена")

def copy_files():
    """
    Основная функция для копирования файлов
    """
    source_dir = Path(CONFIG['SOURCE_DIR'])
    dest_dir = Path(CONFIG['DESTINATION_DIR'])
    
    print(f"Исходная директория: {source_dir.absolute()}")
    print(f"Директория существует: {source_dir.exists()}")
    print(f"Ищем файлы с расширениями: {CONFIG['FILE_EXTENSIONS']}")
    print(f"Исключаем файлы с паттернами: {CONFIG['EXCLUDED_PATTERNS']}")
    
    clear_destination()
    
    stats = {
        'total_files': 0,
        'skipped_files': 0,
        'copied_files': 0,
        'renamed_files': 0
    }

    try:
        for ext in CONFIG['FILE_EXTENSIONS']:
            for source_file in source_dir.rglob(f'*{ext}'):
                stats['total_files'] += 1
                
                # Пропускаем файлы из исключенных директорий
                if should_skip_dir(source_file.parent):
                    continue
                
                # Пропускаем файлы с исключенными паттернами
                if should_skip_file(source_file):
                    stats['skipped_files'] += 1
                    print(f"Пропущен файл: {source_file.name}")
                    continue
                
                # Получаем уникальное имя файла
                dest_file = get_unique_filename(dest_dir, source_file.name)
                
                # Копируем файл
                shutil.copy2(source_file, dest_file)
                stats['copied_files'] += 1
                
                # Считаем переименованные файлы
                if dest_file.stem != source_file.stem:
                    stats['renamed_files'] += 1
                
                print(f"Скопирован файл: {source_file.name} -> {dest_file.name}")

        # Выводим статистику
        print("\nСтатистика:")
        print(f"Всего найдено файлов: {stats['total_files']}")
        print(f"Пропущено файлов: {stats['skipped_files']}")
        print(f"Скопировано файлов: {stats['copied_files']}")
        print(f"Переименовано файлов: {stats['renamed_files']}")

    except Exception as e:
        print(f"Произошла ошибка: {e}")

if __name__ == "__main__":
    copy_files()
