# tests/test_commands.py
import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Добавляем корневую директорию проекта в путь для импорта
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from notebook.commands import Commands
from notebook.models import Note, Status, NotePriority, NoteCategory


class TestCommands(unittest.TestCase):
    """Тесты для commands.py"""

    def setUp(self):
        """Настройка перед каждым тестом"""
        # Создаем мок Storage
        self.mock_storage = MagicMock()
        self.commands = Commands(self.mock_storage)

        # Создаем тестовые заметки
        self.test_note1 = Note(
            id=1,
            title="Test Note 1",
            content="Test content 1",
            category=NoteCategory.WORK,
            priority=NotePriority.HIGH,
            tags=["tag1", "tag2"],
            status=Status.ACTIVE,
            created_at="2024-01-01T10:00:00",
            updated_at="2024-01-01T10:00:00"
        )

        self.test_note2 = Note(
            id=2,
            title="Test Note 2",
            content="Test content 2",
            category=NoteCategory.PERSONAL,
            priority=NotePriority.MEDIUM,
            tags=["tag2", "tag3"],
            status=Status.ACTIVE,
            created_at="2024-01-02T10:00:00",
            updated_at="2024-01-02T10:00:00"
        )

        self.test_note3 = Note(
            id=3,
            title="Archived Note",
            content="Archived content",
            category=NoteCategory.STUDY,
            priority=NotePriority.LOW,
            tags=["study"],
            status=Status.ARCHIVED,
            created_at="2024-01-03T10:00:00",
            updated_at="2024-01-03T10:00:00"
        )

    def test_init(self):
        """Тест инициализации Commands"""
        self.assertEqual(self.commands.storage, self.mock_storage)

    def test_add_note_success(self):
        """Тест успешного добавления заметки"""
        # Настраиваем моки
        self.mock_storage.load_notes.return_value = []
        self.mock_storage.get_next_id.return_value = 1

        result = self.commands.add_note(
            title="Test Title",
            content="Test Content",
            category="work",
            priority="high",
            tags=["tag1", "tag2"]
        )

        # Проверяем вызовы
        self.mock_storage.load_notes.assert_called_once()
        self.mock_storage.get_next_id.assert_called_once()
        self.mock_storage.save_notes.assert_called_once()

        # Проверяем результат
        self.assertIn("Заметка добавлена (ID: 1): Test Title", result)

    def test_add_note_default_values(self):
        """Тест добавления заметки со значениями по умолчанию"""
        self.mock_storage.load_notes.return_value = []
        self.mock_storage.get_next_id.return_value = 1

        result = self.commands.add_note(
            title="Test Title",
            content="Test Content"
            # category по умолчанию "other"
            # priority по умолчанию "medium"
            # tags по умолчанию None
        )

        self.assertIn("Заметка добавлена", result)
        # Проверяем, что сохранение вызвано с заметкой
        saved_notes = self.mock_storage.save_notes.call_args[0][0]
        self.assertEqual(len(saved_notes), 1)
        self.assertEqual(saved_notes[0].title, "Test Title")
        self.assertEqual(saved_notes[0].category, NoteCategory.OTHER)
        self.assertEqual(saved_notes[0].priority, NotePriority.MEDIUM)
        self.assertEqual(saved_notes[0].tags, [])

    def test_add_note_invalid_category(self):
        """Тест добавления заметки с невалидной категорией"""
        result = self.commands.add_note(
            title="Test",
            content="Content",
            category="invalid_category",
            priority="medium"
        )

        # Проверяем сообщение об ошибке
        self.assertIn("Ошибка: Неверная категория 'invalid_category'", result)
        self.assertIn("Допустимые значения:", result)
        # Проверяем, что сохранение не вызывалось
        self.mock_storage.save_notes.assert_not_called()

    def test_add_note_invalid_priority(self):
        """Тест добавления заметки с невалидным приоритетом"""
        result = self.commands.add_note(
            title="Test",
            content="Content",
            category="work",
            priority="invalid_priority"
        )

        self.assertIn("Ошибка: Неверный приоритет 'invalid_priority'", result)
        self.assertIn("Допустимые значения: low, medium, high", result)
        self.mock_storage.save_notes.assert_not_called()

    def test_add_note_case_insensitive(self):
        """Тест добавления заметки с разным регистром"""
        self.mock_storage.load_notes.return_value = []
        self.mock_storage.get_next_id.return_value = 1

        result = self.commands.add_note(
            title="Test",
            content="Content",
            category="WORK",  # В верхнем регистре
            priority="HIGH"  # В верхнем регистре
        )

        # Должно работать несмотря на регистр
        self.assertIn("Заметка добавлена", result)

    def test_list_notes_empty(self):
        """Тест вывода списка заметок, когда их нет"""
        self.mock_storage.load_notes.return_value = []

        result = self.commands.list_notes()

        self.assertEqual(result, "Нет заметок")
        self.mock_storage.load_notes.assert_called_once()

    def test_list_notes_no_filters(self):
        """Тест вывода списка заметок без фильтров"""
        notes = [self.test_note1, self.test_note2, self.test_note3]
        self.mock_storage.load_notes.return_value = notes

        result = self.commands.list_notes()

        # Проверяем основные элементы вывода
        # Внимание: архивные заметки НЕ показываются по умолчанию (status='active')
        # Поэтому будет показано только 2 заметки (test_note1 и test_note2)
        self.assertIn("=== Найдено заметок: 2 ===", result)
        self.assertIn("Test Note 1", result)
        self.assertIn("Test Note 2", result)
        self.assertNotIn("Archived Note", result)  # Архивная заметка не показывается
        self.assertIn("─" * 50, result)

    def test_list_notes_filter_by_category(self):
        """Тест фильтрации заметок по категории"""
        notes = [self.test_note1, self.test_note2, self.test_note3]
        self.mock_storage.load_notes.return_value = notes

        # Фильтруем по категории work
        result = self.commands.list_notes(category="work")

        self.assertIn("=== Найдено заметок: 1 ===", result)
        self.assertIn("Test Note 1", result)
        self.assertNotIn("Test Note 2", result)  # Другая категория
        self.assertNotIn("Archived Note", result)  # Другая категория

    def test_list_notes_filter_by_priority(self):
        """Тест фильтрации заметок по приоритету"""
        notes = [self.test_note1, self.test_note2, self.test_note3]
        self.mock_storage.load_notes.return_value = notes

        # Фильтруем по приоритету high
        result = self.commands.list_notes(priority="high")

        self.assertIn("=== Найдено заметок: 1 ===", result)
        self.assertIn("Test Note 1", result)
        self.assertNotIn("Test Note 2", result)  # Другой приоритет
        self.assertNotIn("Archived Note", result)  # Другой приоритет

    def test_list_notes_filter_by_status(self):
        """Тест фильтрации заметок по статусу"""
        notes = [self.test_note1, self.test_note2, self.test_note3]
        self.mock_storage.load_notes.return_value = notes

        # Фильтруем по статусу archived
        result = self.commands.list_notes(status="archived")

        self.assertIn("=== Найдено заметок: 1 ===", result)
        self.assertIn("Archived Note", result)
        self.assertNotIn("Test Note 1", result)  # Другой статус
        self.assertNotIn("Test Note 2", result)  # Другой статус

    def test_list_notes_with_show_content(self):
        """Тест вывода списка с полным содержимым"""
        notes = [self.test_note1]
        self.mock_storage.load_notes.return_value = notes

        result = self.commands.list_notes(show_content=True)

        # Проверяем, что есть полный текст (когда контент длинный)
        # В нашем случае контент короткий, но все равно проверяем структуру
        self.assertIn("Test Note 1", result)

    def test_list_notes_invalid_category_filter(self):
        """Тест фильтрации с невалидной категорией"""
        notes = [self.test_note1]
        self.mock_storage.load_notes.return_value = notes

        result = self.commands.list_notes(category="invalid_category")

        self.assertIn("Ошибка: Неверная категория 'invalid_category'", result)

    def test_list_notes_invalid_priority_filter(self):
        """Тест фильтрации с невалидным приоритетом"""
        notes = [self.test_note1]
        self.mock_storage.load_notes.return_value = notes

        result = self.commands.list_notes(priority="invalid_priority")

        self.assertIn("Ошибка: Неверный приоритет 'invalid_priority'", result)

    def test_list_notes_invalid_status_filter(self):
        """Тест фильтрации с невалидным статусом"""
        notes = [self.test_note1]
        self.mock_storage.load_notes.return_value = notes

        result = self.commands.list_notes(status="invalid_status")

        self.assertIn("Ошибка: Неверный статус 'invalid_status'", result)

    def test_list_notes_no_matches(self):
        """Тест фильтрации, когда нет совпадений"""
        notes = [self.test_note1, self.test_note2]
        self.mock_storage.load_notes.return_value = notes

        # Фильтруем по категории, которой нет
        result = self.commands.list_notes(category="study")

        self.assertEqual(result, "Заметки не найдены по заданным критериям")

    def test_search_notes_empty(self):
        """Тест поиска, когда нет заметок"""
        self.mock_storage.load_notes.return_value = []

        result = self.commands.search_notes("test")

        self.assertEqual(result, "Нет заметок")

    def test_search_notes_in_title(self):
        """Тест поиска по заголовку"""
        notes = [self.test_note1, self.test_note2]
        self.mock_storage.load_notes.return_value = notes

        result = self.commands.search_notes("Note 1", search_in="title")

        self.assertIn("=== Результаты поиска: 'note 1' (1 найдено) ===", result)
        self.assertIn("Test Note 1", result)
        self.assertNotIn("Test Note 2", result)

    def test_search_notes_in_content(self):
        """Тест поиска по содержимому"""
        notes = [self.test_note1, self.test_note2]
        self.mock_storage.load_notes.return_value = notes

        result = self.commands.search_notes("content 2", search_in="content")

        self.assertIn("=== Результаты поиска: 'content 2' (1 найдено) ===", result)
        self.assertIn("Test Note 2", result)
        self.assertNotIn("Test Note 1", result)

    def test_search_notes_in_tags(self):
        """Тест поиска по тегам"""
        notes = [self.test_note1, self.test_note2]
        self.mock_storage.load_notes.return_value = notes

        result = self.commands.search_notes("tag3", search_in="tags")

        self.assertIn("=== Результаты поиска: 'tag3' (1 найдено) ===", result)
        self.assertIn("Test Note 2", result)
        self.assertNotIn("Test Note 1", result)

    def test_search_notes_in_all(self):
        """Тест поиска по всем полям"""
        notes = [self.test_note1, self.test_note2]
        self.mock_storage.load_notes.return_value = notes

        result = self.commands.search_notes("test", search_in="all")

        self.assertIn("Результаты поиска", result)
        # Обе заметки содержат "test" в названии
        self.assertIn("Test Note 1", result)
        self.assertIn("Test Note 2", result)

    def test_search_notes_case_insensitive(self):
        """Тест поиска с разным регистром"""
        notes = [self.test_note1]
        self.mock_storage.load_notes.return_value = notes

        # Ищем в верхнем регистре
        result = self.commands.search_notes("TEST", search_in="all")

        self.assertIn("Результаты поиска", result)
        self.assertIn("Test Note 1", result)

    def test_search_notes_no_results(self):
        """Тест поиска без результатов"""
        notes = [self.test_note1, self.test_note2]
        self.mock_storage.load_notes.return_value = notes

        result = self.commands.search_notes("nonexistent", search_in="all")

        self.assertEqual(result, "Заметки по запросу 'nonexistent' не найдены")

    def test_delete_note_success(self):
        """Тест успешного удаления заметки"""
        notes = [self.test_note1, self.test_note2]
        self.mock_storage.load_notes.return_value = notes.copy()

        result = self.commands.delete_note(1)

        # Проверяем результат
        self.assertEqual(result, "Заметка удалена: #1 - Test Note 1")

        # Проверяем, что save_notes вызван с обновленным списком
        saved_notes = self.mock_storage.save_notes.call_args[0][0]
        self.assertEqual(len(saved_notes), 1)
        self.assertEqual(saved_notes[0].id, 2)  # Осталась только вторая заметка

    def test_delete_note_not_found(self):
        """Тест удаления несуществующей заметки"""
        notes = [self.test_note1, self.test_note2]
        self.mock_storage.load_notes.return_value = notes

        result = self.commands.delete_note(999)

        self.assertEqual(result, "Ошибка: Заметка с ID #999 не найдена")
        # Проверяем, что save_notes не вызывался
        self.mock_storage.save_notes.assert_not_called()

    def test_archive_note_success(self):
        """Тест успешного архивирования заметки"""
        notes = [self.test_note1, self.test_note2]
        self.mock_storage.load_notes.return_value = notes

        result = self.commands.archive_note(1)

        # Проверяем результат
        self.assertEqual(result, "Заметка архивирована: #1 - Test Note 1")

        # Проверяем, что заметка была обновлена
        saved_notes = self.mock_storage.save_notes.call_args[0][0]
        archived_note = next(n for n in saved_notes if n.id == 1)
        self.assertEqual(archived_note.status, Status.ARCHIVED)

    def test_archive_note_already_archived(self):
        """Тест архивирования уже архивированной заметки"""
        notes = [self.test_note3]  # Уже архивирована
        self.mock_storage.load_notes.return_value = notes

        result = self.commands.archive_note(3)

        self.assertEqual(result, "Заметка #3 уже в архиве")
        # Проверяем, что save_notes не вызывался (не было изменений)
        self.mock_storage.save_notes.assert_not_called()

    def test_archive_note_not_found(self):
        """Тест архивирования несуществующей заметки"""
        notes = [self.test_note1, self.test_note2]
        self.mock_storage.load_notes.return_value = notes

        result = self.commands.archive_note(999)

        self.assertEqual(result, "Ошибка: Заметка с ID #999 не найдена")
        self.mock_storage.save_notes.assert_not_called()

    def test_edit_note_success_partial(self):
        """Тест успешного частичного редактирования заметки"""
        notes = [self.test_note1]
        self.mock_storage.load_notes.return_value = notes

        result = self.commands.edit_note(
            note_id=1,
            title="Updated Title",
            content="Updated Content"
        )

        self.assertEqual(result, "Заметка обновлена: #1 - Updated Title")

        # Проверяем изменения
        saved_notes = self.mock_storage.save_notes.call_args[0][0]
        updated_note = saved_notes[0]
        self.assertEqual(updated_note.title, "Updated Title")
        self.assertEqual(updated_note.content, "Updated Content")
        # Остальные поля не изменились
        self.assertEqual(updated_note.category, NoteCategory.WORK)
        self.assertEqual(updated_note.priority, NotePriority.HIGH)
        self.assertEqual(updated_note.tags, ["tag1", "tag2"])

    def test_edit_note_success_full(self):
        """Тест успешного полного редактирования заметки"""
        notes = [self.test_note1]
        self.mock_storage.load_notes.return_value = notes

        result = self.commands.edit_note(
            note_id=1,
            title="New Title",
            content="New Content",
            category="personal",
            priority="low",
            tags=["newtag1", "newtag2"]
        )

        self.assertEqual(result, "Заметка обновлена: #1 - New Title")

        saved_notes = self.mock_storage.save_notes.call_args[0][0]
        updated_note = saved_notes[0]
        self.assertEqual(updated_note.title, "New Title")
        self.assertEqual(updated_note.content, "New Content")
        self.assertEqual(updated_note.category, NoteCategory.PERSONAL)
        self.assertEqual(updated_note.priority, NotePriority.LOW)
        self.assertEqual(updated_note.tags, ["newtag1", "newtag2"])

    def test_edit_note_not_found(self):
        """Тест редактирования несуществующей заметки"""
        notes = [self.test_note1]
        self.mock_storage.load_notes.return_value = notes

        result = self.commands.edit_note(note_id=999, title="New Title")

        self.assertEqual(result, "Ошибка: Заметка с ID #999 не найдена")
        self.mock_storage.save_notes.assert_not_called()

    def test_edit_note_invalid_category(self):
        """Тест редактирования с невалидной категорией"""
        notes = [self.test_note1]
        self.mock_storage.load_notes.return_value = notes

        result = self.commands.edit_note(
            note_id=1,
            category="invalid_category"
        )

        self.assertIn("Ошибка: Неверная категория 'invalid_category'", result)
        self.mock_storage.save_notes.assert_not_called()

    def test_edit_note_invalid_priority(self):
        """Тест редактирования с невалидным приоритетом"""
        notes = [self.test_note1]
        self.mock_storage.load_notes.return_value = notes

        result = self.commands.edit_note(
            note_id=1,
            priority="invalid_priority"
        )

        self.assertIn("Ошибка: Неверный приоритет 'invalid_priority'", result)
        self.mock_storage.save_notes.assert_not_called()

    def test_edit_note_with_none_values(self):
        """Тест редактирования с None значениями (должно игнорироваться)"""
        notes = [self.test_note1]
        self.mock_storage.load_notes.return_value = notes
        original_title = self.test_note1.title

        # Пытаемся обновить с None
        result = self.commands.edit_note(
            note_id=1,
            title=None,
            content=None,
            category=None,
            priority=None,
            tags=None
        )

        # Должно успешно завершиться без изменений (кроме updated_at)
        self.assertEqual(result, "Заметка обновлена: #1 - Test Note 1")
        saved_notes = self.mock_storage.save_notes.call_args[0][0]
        self.assertEqual(saved_notes[0].title, original_title)  # Не изменилось

    def test_list_tags_empty(self):
        """Тест вывода тегов, когда их нет"""
        self.mock_storage.get_all_tags.return_value = []
        self.mock_storage.load_notes.return_value = []

        result = self.commands.list_tags()

        self.assertEqual(result, "Теги не найдены")

    def test_list_tags_with_data(self):
        """Тест вывода тегов с данными"""
        self.mock_storage.get_all_tags.return_value = ["tag1", "tag2", "tag3"]

        # Настраиваем load_notes для подсчета заметок по тегам
        notes = [
            Note(id=1, title="Note 1", content="", tags=["tag1", "tag2"]),
            Note(id=2, title="Note 2", content="", tags=["tag2", "tag3"]),
            Note(id=3, title="Note 3", content="", tags=["tag1"])
        ]
        self.mock_storage.load_notes.return_value = notes

        result = self.commands.list_tags()

        # Проверяем вывод
        self.assertIn("=== Все теги ===", result)
        self.assertIn("#tag1 (2 заметок)", result)
        self.assertIn("#tag2 (2 заметок)", result)
        self.assertIn("#tag3 (1 заметок)", result)

    def test_list_tags_sorted(self):
        """Тест вывода тегов в отсортированном порядке"""
        # Storage.get_all_tags() возвращает уже отсортированный список
        self.mock_storage.get_all_tags.return_value = ["apple", "banana", "zebra"]
        self.mock_storage.load_notes.return_value = []

        result = self.commands.list_tags()

        # Проверяем вывод (теги должны быть отсортированы)
        lines = result.split('\n')
        # Первая строка - заголовок
        self.assertEqual(lines[0], "=== Все теги ===")
        # Далее теги в алфавитном порядке
        self.assertIn("#apple (0 заметок)", lines[1])
        self.assertIn("#banana (0 заметок)", lines[2])
        self.assertIn("#zebra (0 заметок)", lines[3])


if __name__ == '__main__':
    unittest.main()