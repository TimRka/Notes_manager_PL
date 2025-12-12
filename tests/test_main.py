# tests/test_main.py
import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import argparse

# Добавляем корневую директорию проекта в путь для импорта
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import main


class TestMain(unittest.TestCase):
    """Тесты для main.py"""

    def setUp(self):
        """Настройка перед каждым тестом"""
        self.test_args = ['test_script.py']

    @patch('main.Storage')
    @patch('main.Commands')
    @patch('sys.argv', ['script.py', 'add', 'Test Title', 'Test Content'])
    def test_main_add_command_basic(self, mock_commands, mock_storage):
        """Тест команды add с минимальными аргументами"""
        # Создаем моки
        mock_storage_instance = MagicMock()
        mock_storage.return_value = mock_storage_instance

        mock_commands_instance = MagicMock()
        mock_commands.return_value = mock_commands_instance
        mock_commands_instance.add_note.return_value = "Note added"

        # Захватываем вывод
        with patch('builtins.print') as mock_print:
            main()

            # Проверяем, что Commands был создан с правильным storage
            mock_commands.assert_called_once_with(mock_storage_instance)

            # Проверяем, что add_note был вызван с правильными аргументами
            mock_commands_instance.add_note.assert_called_once_with(
                title='Test Title',
                content='Test Content',
                category='other',
                priority='medium',
                tags=None
            )

            # Проверяем вывод
            mock_print.assert_called_once_with("Note added")

    @patch('main.Storage')
    @patch('main.Commands')
    @patch('sys.argv', ['script.py', 'add', 'Test', 'Content', '-c', 'work', '-p', 'high', '-t', 'tag1', 'tag2'])
    def test_main_add_command_full(self, mock_commands, mock_storage):
        """Тест команды add со всеми аргументами"""
        mock_storage_instance = MagicMock()
        mock_storage.return_value = mock_storage_instance

        mock_commands_instance = MagicMock()
        mock_commands.return_value = mock_commands_instance
        mock_commands_instance.add_note.return_value = "Note added"

        with patch('builtins.print') as mock_print:
            main()

            mock_commands_instance.add_note.assert_called_once_with(
                title='Test',
                content='Content',
                category='work',
                priority='high',
                tags=['tag1', 'tag2']
            )

    @patch('main.Storage')
    @patch('main.Commands')
    @patch('sys.argv', ['script.py', 'list'])
    def test_main_list_command_default(self, mock_commands, mock_storage):
        """Тест команды list с аргументами по умолчанию"""
        mock_storage_instance = MagicMock()
        mock_storage.return_value = mock_storage_instance

        mock_commands_instance = MagicMock()
        mock_commands.return_value = mock_commands_instance
        mock_commands_instance.list_notes.return_value = "Note list"

        with patch('builtins.print') as mock_print:
            main()

            mock_commands_instance.list_notes.assert_called_once_with(
                category=None,
                priority=None,
                status='active',
                show_content=False
            )

    @patch('main.Storage')
    @patch('main.Commands')
    @patch('sys.argv', ['script.py', 'list', '-c', 'work', '-p', 'high', '-s', 'archived', '--full'])
    def test_main_list_command_with_args(self, mock_commands, mock_storage):
        """Тест команды list со всеми аргументами"""
        mock_storage_instance = MagicMock()
        mock_storage.return_value = mock_storage_instance

        mock_commands_instance = MagicMock()
        mock_commands.return_value = mock_commands_instance

        with patch('builtins.print'):
            main()

            mock_commands_instance.list_notes.assert_called_once_with(
                category='work',
                priority='high',
                status='archived',
                show_content=True
            )

    @patch('main.Storage')
    @patch('main.Commands')
    @patch('sys.argv', ['script.py', 'search', 'test', '--in', 'title'])
    def test_main_search_command(self, mock_commands, mock_storage):
        """Тест команды search"""
        mock_storage_instance = MagicMock()
        mock_storage.return_value = mock_storage_instance

        mock_commands_instance = MagicMock()
        mock_commands.return_value = mock_commands_instance

        with patch('builtins.print'):
            main()

            mock_commands_instance.search_notes.assert_called_once_with(
                search_term='test',
                search_in='title'
            )

    @patch('main.Storage')
    @patch('main.Commands')
    @patch('sys.argv', ['script.py', 'delete', '1'])
    def test_main_delete_command(self, mock_commands, mock_storage):
        """Тест команды delete"""
        mock_storage_instance = MagicMock()
        mock_storage.return_value = mock_storage_instance

        mock_commands_instance = MagicMock()
        mock_commands.return_value = mock_commands_instance

        with patch('builtins.print'):
            main()

            mock_commands_instance.delete_note.assert_called_once_with(1)

    @patch('main.Storage')
    @patch('main.Commands')
    @patch('sys.argv', ['script.py', 'archive', '2'])
    def test_main_archive_command(self, mock_commands, mock_storage):
        """Тест команды archive"""
        mock_storage_instance = MagicMock()
        mock_storage.return_value = mock_storage_instance

        mock_commands_instance = MagicMock()
        mock_commands.return_value = mock_commands_instance

        with patch('builtins.print'):
            main()

            mock_commands_instance.archive_note.assert_called_once_with(2)

    @patch('main.Storage')
    @patch('main.Commands')
    @patch('sys.argv', ['script.py', 'edit', '3', '--title', 'New Title', '--content', 'New Content'])
    def test_main_edit_command(self, mock_commands, mock_storage):
        """Тест команды edit"""
        mock_storage_instance = MagicMock()
        mock_storage.return_value = mock_storage_instance

        mock_commands_instance = MagicMock()
        mock_commands.return_value = mock_commands_instance

        with patch('builtins.print'):
            main()

            mock_commands_instance.edit_note.assert_called_once_with(
                note_id=3,
                title='New Title',
                content='New Content',
                category=None,
                priority=None,
                tags=None
            )

    @patch('main.Storage')
    @patch('main.Commands')
    @patch('sys.argv', ['script.py', 'tags'])
    def test_main_tags_command(self, mock_commands, mock_storage):
        """Тест команды tags"""
        mock_storage_instance = MagicMock()
        mock_storage.return_value = mock_storage_instance

        mock_commands_instance = MagicMock()
        mock_commands.return_value = mock_commands_instance

        with patch('builtins.print'):
            main()

            mock_commands_instance.list_tags.assert_called_once()

    @patch('main.Storage')
    @patch('main.Commands')
    @patch('sys.argv', ['script.py'])
    def test_main_no_command_shows_help_and_list(self, mock_commands, mock_storage):
        """Тест запуска без команды (показывает справку и список заметок)"""
        mock_storage_instance = MagicMock()
        mock_storage.return_value = mock_storage_instance

        mock_commands_instance = MagicMock()
        mock_commands.return_value = mock_commands_instance
        mock_commands_instance.list_notes.return_value = "Note list"

        # Мокаем parser.print_help и print
        with patch('argparse.ArgumentParser.print_help') as mock_print_help, \
                patch('builtins.print') as mock_print:
            main()

            # Проверяем, что была показана справка
            mock_print_help.assert_called_once()

            # Проверяем, что был вызван list_notes
            mock_commands_instance.list_notes.assert_called_once_with()

            # Проверяем, что был вывод списка заметок
            self.assertTrue(mock_print.call_count >= 2)

    @patch('main.Storage')
    @patch('main.Commands')
    @patch('sys.argv', ['script.py', 'unknown'])
    def test_main_unknown_command(self, mock_commands, mock_storage):
        """Тест неизвестной команды"""
        mock_storage_instance = MagicMock()
        mock_storage.return_value = mock_storage_instance

        mock_commands_instance = MagicMock()
        mock_commands.return_value = mock_commands_instance
        # Симулируем, что команда неизвестна
        mock_commands_instance.add_note.return_value = "Неизвестная команда"

        with patch('builtins.print') as mock_print:
            # Мокаем parse_args чтобы вернуть неизвестную команду
            with patch('argparse.ArgumentParser.parse_args') as mock_parse:
                mock_args = MagicMock()
                mock_args.command = 'unknown'
                mock_args.title = 'test'
                mock_args.content = 'test'
                mock_args.category = 'other'
                mock_args.priority = 'medium'
                mock_args.tags = None
                mock_parse.return_value = mock_args

                main()

                # Проверяем, что была выведена ошибка
                mock_print.assert_called_with("Неизвестная команда")

    @patch('main.Storage')
    @patch('main.Commands')
    @patch('sys.argv', ['script.py', 'add', 'Test', 'Content'])
    @patch('sys.exit')
    def test_main_exception_handling(self, mock_exit, mock_commands, mock_storage):
        """Тест обработки исключений"""
        mock_storage_instance = MagicMock()
        mock_storage.return_value = mock_storage_instance

        mock_commands_instance = MagicMock()
        mock_commands.return_value = mock_commands_instance
        # Симулируем исключение в add_note
        mock_commands_instance.add_note.side_effect = Exception("Test error")

        with patch('builtins.print') as mock_print:
            main()

            # Проверяем, что ошибка была напечатана
            mock_print.assert_called_with("Ошибка: Test error")
            # Проверяем, что sys.exit был вызван с кодом 1
            mock_exit.assert_called_once_with(1)


if __name__ == '__main__':
    unittest.main()