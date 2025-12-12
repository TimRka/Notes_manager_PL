import sqlite3
import json
import os
from typing import List, Optional, Tuple
from .models import Note, Status, NotePriority, NoteCategory


class Storage:
    def __init__(self, db_path: str = "notes.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Инициализация базы данных и создание таблицы, если её нет"""
        try:
            # Создаем директорию для базы данных, если её нет
            db_dir = os.path.dirname(self.db_path)
            if db_dir and not os.path.exists(db_dir):
                os.makedirs(db_dir, exist_ok=True)

            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Простая таблица
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS notes (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title TEXT NOT NULL,
                        content TEXT,
                        category TEXT,
                        priority TEXT,
                        tags TEXT,
                        status TEXT,
                        created_at TEXT,
                        updated_at TEXT
                    )
                ''')
                conn.commit()
                print(f"База данных инициализирована: {self.db_path}")

        except sqlite3.Error as e:
            print(f"Ошибка при инициализации базы данных: {e}")
            raise

    def save_notes(self, notes: List[Note]):
        """Сохраняет список заметок в БД"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Очищаем таблицу и вставляем все заметки заново
                cursor.execute('DELETE FROM notes')

                for note in notes:
                    # Проверяем, что даты - это строки
                    created_at = str(note.created_at) if note.created_at else ""
                    updated_at = str(note.updated_at) if note.updated_at else ""

                    cursor.execute('''
                        INSERT INTO notes 
                        (id, title, content, category, priority, tags, status, created_at, updated_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        note.id,
                        note.title,
                        note.content or "",
                        note.category.value if hasattr(note.category, 'value') else str(note.category),
                        note.priority.value if hasattr(note.priority, 'value') else str(note.priority),
                        json.dumps(note.tags, ensure_ascii=False) if note.tags else "[]",
                        note.status.value if hasattr(note.status, 'value') else str(note.status),
                        created_at,
                        updated_at
                    ))

                conn.commit()

        except sqlite3.Error as e:
            print(f"Ошибка при сохранении заметок: {e}")

    def load_notes(self) -> List[Note]:
        """Загружает все заметки из БД"""
        try:
            notes = []
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute('SELECT * FROM notes ORDER BY created_at DESC')
                rows = cursor.fetchall()

                for row in rows:
                    # Создаем Note из строки БД
                    note = Note(
                        id=row[0],
                        title=row[1],
                        content=row[2],
                        category=NoteCategory(row[3]) if row[3] else NoteCategory.other,
                        priority=NotePriority(row[4]) if row[4] else NotePriority.medium,
                        tags=json.loads(row[5]) if row[5] and row[5] != "[]" else [],
                        status=Status(row[6]) if row[6] else Status.active,
                        created_at=row[7],  # Это строка
                        updated_at=row[8]  # Это строка
                    )
                    notes.append(note)

            return notes

        except sqlite3.Error as e:
            print(f"Ошибка при загрузке заметок: {e}")
            return []

    def get_next_id(self) -> int:
        """Генерирует следующий ID для новой заметки"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT MAX(id) FROM notes')
                result = cursor.fetchone()
                max_id = result[0] if result[0] else 0
                return max_id + 1
        except sqlite3.Error:
            return 1

    def get_all_tags(self) -> List[str]:
        """Возвращает список всех уникальных тегов"""
        all_tags = set()

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT tags FROM notes')
                rows = cursor.fetchall()

                for row in rows:
                    if row[0] and row[0] != "[]":
                        try:
                            tags = json.loads(row[0])
                            if isinstance(tags, list):
                                all_tags.update(tags)
                        except json.JSONDecodeError:
                            continue

            return sorted(list(all_tags))
        except sqlite3.Error:
            return []

    def add_note(self, note: Note) -> int:
        """Добавляет одну заметку и возвращает её ID"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                created_at = str(note.created_at) if note.created_at else ""
                updated_at = str(note.updated_at) if note.updated_at else ""

                cursor.execute('''
                    INSERT INTO notes 
                    (title, content, category, priority, tags, status, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    note.title,
                    note.content or "",
                    note.category.value if hasattr(note.category, 'value') else str(note.category),
                    note.priority.value if hasattr(note.priority, 'value') else str(note.priority),
                    json.dumps(note.tags, ensure_ascii=False) if note.tags else "[]",
                    note.status.value if hasattr(note.status, 'value') else str(note.status),
                    created_at,
                    updated_at
                ))

                note_id = cursor.lastrowid
                conn.commit()
                return note_id

        except sqlite3.Error as e:
            print(f"Ошибка при добавлении заметки: {e}")
            return 0

    def update_note(self, note: Note) -> bool:
        """Обновляет существующую заметку"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                updated_at = str(note.updated_at) if note.updated_at else ""

                cursor.execute('''
                    UPDATE notes 
                    SET title = ?, content = ?, category = ?, priority = ?, 
                        tags = ?, status = ?, updated_at = ?
                    WHERE id = ?
                ''', (
                    note.title,
                    note.content or "",
                    note.category.value if hasattr(note.category, 'value') else str(note.category),
                    note.priority.value if hasattr(note.priority, 'value') else str(note.priority),
                    json.dumps(note.tags, ensure_ascii=False) if note.tags else "[]",
                    note.status.value if hasattr(note.status, 'value') else str(note.status),
                    updated_at,
                    note.id
                ))

                conn.commit()
                return cursor.rowcount > 0

        except sqlite3.Error as e:
            print(f"Ошибка при обновлении заметки: {e}")
            return False

    def delete_note(self, note_id: int) -> bool:
        """Удаляет заметку по ID"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM notes WHERE id = ?', (note_id,))
                conn.commit()
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Ошибка при удалении заметки: {e}")
            return False

    def get_note_by_id(self, note_id: int) -> Optional[Note]:
        """Получает заметку по ID"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM notes WHERE id = ?', (note_id,))
                row = cursor.fetchone()

                if row:
                    return Note(
                        id=row[0],
                        title=row[1],
                        content=row[2],
                        category=NoteCategory(row[3]) if row[3] else NoteCategory.other,
                        priority=NotePriority(row[4]) if row[4] else NotePriority.medium,
                        tags=json.loads(row[5]) if row[5] and row[5] != "[]" else [],
                        status=Status(row[6]) if row[6] else Status.active,
                        created_at=row[7],
                        updated_at=row[8]
                    )
                return None
        except sqlite3.Error as e:
            print(f"Ошибка при получении заметки: {e}")
            return None