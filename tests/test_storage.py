# tests/test_storage.py
import unittest
import tempfile
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from notebook.storage import Storage
from notebook.models import Note, Status, NotePriority, NoteCategory


class TestStorageBasic(unittest.TestCase):
    """Базовые тесты для storage.py"""

    def setUp(self):
        """Настройка перед каждым тестом"""
        # Используем один файл для всех тестов класса
        self.db_file = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        self.db_file.close()
        self.storage = Storage(db_path=self.db_file.name)

    def tearDown(self):
        """Очистка после каждого теста"""
        # Закрываем все соединения вручную
        if hasattr(self, 'storage'):
            del self.storage

        # Удаляем файл
        import time
        time.sleep(0.1)  # Даем время на закрытие соединений
        try:
            os.unlink(self.db_file.name)
        except:
            pass

    def test_init_creates_table(self):
        """Тест создания таблицы при инициализации"""
        # Просто проверяем, что Storage создается без ошибок
        notes = self.storage.load_notes()
        self.assertEqual(notes, [])

    def test_add_and_load_notes(self):
        """Тест добавления и загрузки заметок"""
        note = Note(
            id=1,
            title="Test Note",
            content="Test content",
            category=NoteCategory.WORK,
            priority=NotePriority.HIGH,
            tags=["tag1"],
            status=Status.ACTIVE,
            created_at="2024-01-01",
            updated_at="2024-01-01"
        )

        # Добавляем заметку
        note_id = self.storage.add_note(note)
        self.assertEqual(note_id, 1)

        # Загружаем заметки
        notes = self.storage.load_notes()
        self.assertEqual(len(notes), 1)
        self.assertEqual(notes[0].title, "Test Note")

    def test_update_note(self):
        """Тест обновления заметки"""
        # Сначала добавляем
        note = Note(
            id=1,
            title="Original",
            content="Content",
            category=NoteCategory.WORK,
            priority=NotePriority.HIGH,
            tags=[],
            status=Status.ACTIVE
        )

        self.storage.add_note(note)

        # Обновляем
        updated_note = Note(
            id=1,
            title="Updated",
            content="New content",
            category=NoteCategory.PERSONAL,
            priority=NotePriority.LOW,
            tags=["tag"],
            status=Status.ARCHIVED
        )

        result = self.storage.update_note(updated_note)
        self.assertTrue(result)

        # Проверяем
        notes = self.storage.load_notes()
        self.assertEqual(len(notes), 1)
        self.assertEqual(notes[0].title, "Updated")
        self.assertEqual(notes[0].status, Status.ARCHIVED)

    def test_delete_note(self):
        """Тест удаления заметки"""
        # Добавляем две заметки
        note1 = Note(id=1, title="Note 1", content="Content")
        note2 = Note(id=2, title="Note 2", content="Content")

        self.storage.add_note(note1)
        self.storage.add_note(note2)

        # Удаляем первую
        result = self.storage.delete_note(1)
        self.assertTrue(result)

        # Проверяем
        notes = self.storage.load_notes()
        self.assertEqual(len(notes), 1)
        self.assertEqual(notes[0].id, 2)

    def test_get_note_by_id(self):
        """Тест получения заметки по ID"""
        note = Note(id=1, title="Test", content="Content")
        self.storage.add_note(note)

        found = self.storage.get_note_by_id(1)
        self.assertIsNotNone(found)
        self.assertEqual(found.title, "Test")

        # Проверяем несуществующий ID
        not_found = self.storage.get_note_by_id(999)
        self.assertIsNone(not_found)


class TestStorageAdvanced(unittest.TestCase):
    """Продвинутые тесты для storage.py"""

    def setUp(self):
        self.db_file = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        self.db_file.close()
        self.storage = Storage(db_path=self.db_file.name)

    def tearDown(self):
        if hasattr(self, 'storage'):
            del self.storage
        import time
        time.sleep(0.1)
        try:
            os.unlink(self.db_file.name)
        except:
            pass

    def test_get_next_id(self):
        """Тест получения следующего ID"""
        # Пустая база
        self.assertEqual(self.storage.get_next_id(), 1)

        # Добавляем заметку
        note = Note(id=1, title="Test", content="Content")
        self.storage.add_note(note)

        # Следующий ID должен быть 2
        self.assertEqual(self.storage.get_next_id(), 2)

    def test_get_all_tags(self):
        """Тест получения всех тегов"""
        # Добавляем заметки с тегами
        notes = [
            Note(id=1, title="Note 1", content="", tags=["python", "test"]),
            Note(id=2, title="Note 2", content="", tags=["python", "code"]),
            Note(id=3, title="Note 3", content="", tags=["test", "debug"])
        ]

        for note in notes:
            self.storage.add_note(note)

        tags = self.storage.get_all_tags()

        # Проверяем уникальность и сортировку
        expected = sorted(["python", "test", "code", "debug"])
        self.assertEqual(tags, expected)

    def test_save_notes_overwrites(self):
        """Тест что save_notes перезаписывает данные"""
        # Сохраняем первую заметку
        note1 = Note(id=1, title="First", content="Content")
        self.storage.save_notes([note1])

        # Проверяем
        notes = self.storage.load_notes()
        self.assertEqual(len(notes), 1)
        self.assertEqual(notes[0].title, "First")

        # Сохраняем другую заметку
        note2 = Note(id=2, title="Second", content="Content")
        self.storage.save_notes([note2])

        # Должна остаться только вторая
        notes = self.storage.load_notes()
        self.assertEqual(len(notes), 1)
        self.assertEqual(notes[0].title, "Second")


if __name__ == '__main__':
    unittest.main()