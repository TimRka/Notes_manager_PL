import argparse
from typing import List
from datetime import datetime
from .models import Note, Status, NotePriority, NoteCategory
from .storage import Storage


class Commands:
    def __init__(self, storage: Storage):
        self.storage = storage

    def add_note(self, title: str, content: str, category: str = "other",
                 priority: str = "medium", tags: List[str] = None) -> str:
        """Добавляет новую заметку"""
        notes = self.storage.load_notes()

        # Валидация категории
        try:
            note_category = NoteCategory(category.lower())
        except ValueError:
            valid_categories = [cat.value for cat in NoteCategory]
            return f"Ошибка: Неверная категория '{category}'. Допустимые значения: {', '.join(valid_categories)}"

        # Валидация приоритета
        try:
            note_priority = NotePriority(priority.lower())
        except ValueError:
            return f"Ошибка: Неверный приоритет '{priority}'. Допустимые значения: low, medium, high"

        new_note = Note(
            id=self.storage.get_next_id(),
            title=title,
            content=content,
            category=note_category,
            priority=note_priority,
            tags=tags or []
        )

        notes.append(new_note)
        self.storage.save_notes(notes)
        return f"Заметка добавлена (ID: {new_note.id}): {title}"

    def list_notes(self, category: str = None, priority: str = None,
                   status: str = "active", show_content: bool = False) -> str:
        """Показывает список заметок с фильтрацией"""
        notes = self.storage.load_notes()

        if not notes:
            return "Нет заметок"

        # Фильтрация
        filtered_notes = notes

        if category:
            try:
                category_filter = NoteCategory(category.lower())
                filtered_notes = [n for n in filtered_notes if n.category == category_filter]
            except ValueError:
                valid_categories = [cat.value for cat in NoteCategory]
                return f"Ошибка: Неверная категория '{category}'. Допустимые значения: {', '.join(valid_categories)}"

        if priority:
            try:
                priority_filter = NotePriority(priority.lower())
                filtered_notes = [n for n in filtered_notes if n.priority == priority_filter]
            except ValueError:
                return f"Ошибка: Неверный приоритет '{priority}'. Допустимые значения: low, medium, high"

        if status:
            try:
                status_filter = Status(status.lower())
                filtered_notes = [n for n in filtered_notes if n.status == status_filter]
            except ValueError:
                return f"Ошибка: Неверный статус '{status}'. Допустимые значения: active, archived"

        if not filtered_notes:
            return "Заметки не найдены по заданным критериям"

        # Сортировка по дате создания (новые сначала)
        filtered_notes.sort(key=lambda x: x.created_at, reverse=True)

        result = []
        result.append(f"=== Найдено заметок: {len(filtered_notes)} ===")

        for note in filtered_notes:
            result.append("─" * 50)
            result.append(str(note))
            if show_content and len(note.content) > 100:
                result.append(f"   Полный текст: {note.content}")

        return "\n".join(result)

    def search_notes(self, search_term: str, search_in: str = "all") -> str:
        """Поиск заметок по ключевым словам"""
        notes = self.storage.load_notes()

        if not notes:
            return "Нет заметок"

        search_term = search_term.lower()
        found_notes = []

        for note in notes:
            matches = False

            if search_in in ["all", "title"] and search_term in note.title.lower():
                matches = True
            elif search_in in ["all", "content"] and search_term in note.content.lower():
                matches = True
            elif search_in in ["all", "tags"] and any(search_term in tag.lower() for tag in note.tags):
                matches = True

            if matches:
                found_notes.append(note)

        if not found_notes:
            return f"Заметки по запросу '{search_term}' не найдены"

        # Сортировка по релевантности (можно улучшить)
        found_notes.sort(key=lambda x: x.created_at, reverse=True)

        result = [f"=== Результаты поиска: '{search_term}' ({len(found_notes)} найдено) ==="]
        for note in found_notes:
            result.append("─" * 50)
            result.append(str(note))

        return "\n".join(result)

    def delete_note(self, note_id: int) -> str:
        """Удаляет заметку"""
        notes = self.storage.load_notes()

        for i, note in enumerate(notes):
            if note.id == note_id:
                deleted_title = note.title
                del notes[i]
                self.storage.save_notes(notes)
                return f"Заметка удалена: #{note_id} - {deleted_title}"

        return f"Ошибка: Заметка с ID #{note_id} не найдена"

    def archive_note(self, note_id: int) -> str:
        """Архивирует заметку"""
        notes = self.storage.load_notes()

        for note in notes:
            if note.id == note_id:
                if note.status == Status.ARCHIVED:
                    return f"Заметка #{note_id} уже в архиве"
                note.status = Status.ARCHIVED
                note.updated_at = datetime.now().isoformat()
                self.storage.save_notes(notes)
                return f"Заметка архивирована: #{note_id} - {note.title}"

        return f"Ошибка: Заметка с ID #{note_id} не найдена"

    def edit_note(self, note_id: int, title: str = None, content: str = None,
                  category: str = None, priority: str = None, tags: List[str] = None) -> str:
        """Редактирует существующую заметку"""
        notes = self.storage.load_notes()

        for note in notes:
            if note.id == note_id:
                # Валидация категории
                note_category = None
                if category:
                    try:
                        note_category = NoteCategory(category.lower())
                    except ValueError:
                        valid_categories = [cat.value for cat in NoteCategory]
                        return f"Ошибка: Неверная категория '{category}'. Допустимые значения: {', '.join(valid_categories)}"

                # Валидация приоритета
                note_priority = None
                if priority:
                    try:
                        note_priority = NotePriority(priority.lower())
                    except ValueError:
                        return f"Ошибка: Неверный приоритет '{priority}'. Допустимые значения: low, medium, high"

                note.update(
                    title=title,
                    content=content,
                    category=note_category,
                    priority=note_priority,
                    tags=tags
                )

                self.storage.save_notes(notes)
                return f"Заметка обновлена: #{note_id} - {note.title}"

        return f"Ошибка: Заметка с ID #{note_id} не найдена"

    def list_tags(self) -> str:
        """Показывает все используемые теги"""
        tags = self.storage.get_all_tags()

        if not tags:
            return "Теги не найдены"

        result = ["=== Все теги ==="]
        for tag in tags:
            # Находим заметки с этим тегом
            notes_with_tag = [note for note in self.storage.load_notes() if tag in note.tags]
            result.append(f"#{tag} ({len(notes_with_tag)} заметок)")

        return "\n".join(result)