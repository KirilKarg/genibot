# logReader.py
import re
import time
import os
from datetime import datetime
from pathlib import Path
from colorama import init
from rich.console import Console
from rich.table import Table
from rich.live import Live

# Инициализация цветов для Windows
init(autoreset=True)


class LogReader:
    def __init__(self, file_path, start_date=None):
        self.file_path = Path(file_path)
        self.start_date = start_date
        self.console = Console()
        self.log_buffer = []

        self.log_pattern = re.compile(
           r"(?P<datetime>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}) - "
            r"(?P<module>[\w\.]+) - "
            r"(?P<level>\w+) - "
            r"(?P<message>.+)"
           )

        if not self.file_path.exists():
            raise FileNotFoundError(f"File {self.file_path} not found")

        self.last_size = self.get_initial_position()

    def get_color(self, level):
        """Возвращает цвет для уровня логирования"""
        colors = {
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'bold red',
            'DEBUG': 'cyan'
        }
        return colors.get(level.upper(), 'white')

    def get_initial_position(self):
        """Определяет начальную позицию для чтения файла"""
        if self.start_date:
            # Ищем первую запись с указанной датой
            with open(self.file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if match := self.log_pattern.match(line):
                        log_date = datetime.strptime(
                            match['datetime'], '%Y-%m-%d %H:%M:%S,%f')
                        if log_date.date() >= self.start_date.date():
                            return f.tell() - len(line.encode('utf-8'))
                return os.path.getsize(self.file_path)
        else:
            # Начинаем с конца файла
            return os.path.getsize(self.file_path)

    def tail(self):
        """Генератор, возвращающий новые строки лога"""
        try:
            while True:
                with open(self.file_path, 'r', encoding='utf-8') as f:
                    current_size = os.path.getsize(self.file_path)

                    # Если файл уменьшился (был очищен)
                    if current_size < self.last_size:
                        self.last_size = 0

                    f.seek(self.last_size)

                    while True:
                        line = f.readline()
                        if not line:
                            break
                        yield line

                    self.last_size = f.tell()
                    time.sleep(0.5)

        except Exception as e:
            self.console.print(f"[bold red]Ошибка: {str(e)}")
            exit(1)


    def parse_log_line(self, line):
        """Парсит строку лога в структурированные данные"""
        match = self.log_pattern.match(line)
        if match:
            log_date = datetime.strptime(
                match['datetime'], '%Y-%m-%d %H:%M:%S,%f')
            if not self.start_date or log_date >= self.start_date:
                return match.groupdict()
        return None

    def run(self):
        """Основной цикл чтения логов"""
        self.console.print(f"[bold green]Мониторинг логов: {self.file_path}\n")
        MAX_BUFFER_SIZE = 50  # Фиксированный размер буфера

        with Live(refresh_per_second=12, vertical_overflow="visible") as live:
            try:
                while True:
                    table = self.create_table()
                    live.update(table)

                    line = next(self.tail())
                    if log_entry := self.parse_log_line(line):
                        if len(self.log_buffer) >= MAX_BUFFER_SIZE:
                            self.log_buffer.pop(0)
                        self.log_buffer.append(log_entry)

                    time.sleep(0.1)

            except KeyboardInterrupt:
                self.console.print("\n[bold yellow]Мониторинг остановлен")

    def create_table(self):
        """Создает новую таблицу с текущими данными"""
        table = Table(
            show_header=True,
            header_style="bold magenta",
            show_lines=True,
            expand=True
        )
        table.add_column("Время", width=18, no_wrap=True)
        table.add_column("Уровень", width=10, justify="center")
        table.add_column("Модуль", width=25, no_wrap=True)
        table.add_column("Сообщение", no_wrap=False)

        for log in self.log_buffer:
            level_color = self.get_color(log['level'])
            table.add_row(
                log['datetime'],
                f"[{level_color}]{log['level']}",
                log['module'],
                log['message']
            )

        return table


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description='Мониторинг логов в реальном времени')
    parser.add_argument('-f', '--file', default='bot.log',
                        help='Путь к файлу логов')
    parser.add_argument('-d', '--date',
                        help='Дата начала в формате ГГГГ-ММ-ДД')

    args = parser.parse_args()

    start_date = None
    if args.date:
        try:
            start_date = datetime.strptime(args.date, '%Y-%m-%d')
        except ValueError:
            print("Некорректный формат даты. Используйте ГГГГ-ММ-ДД")
            exit(1)

    LogReader(args.file, start_date).run()
