import json
from datetime import datetime
from enum import Enum


class Status(Enum):
    ACTIVE = "active"
    ARCHIVED = "archived"


class NotePriority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class NoteCategory(Enum):
    WORK = "work"
    PERSONAL = "personal"
    STUDY = "study"
    SHOPPING = "shopping"
    IDEAS = "ideas"
    OTHER = "other"


class Note:
    def __init__(self, id, title, content, category=NoteCategory.OTHER,
                 priority=NotePriority.MEDIUM, tags=None, status=Status.ACTIVE,
                 created_at=None, updated_at=None):
        self.id = id
        self.title = title
        self.content = content
        self.category = category
        self.priority = priority
        self.tags = tags or []
        self.status = status
        self.created_at = created_at or datetime.now().isoformat()
        self.updated_at = updated_at or datetime.now().isoformat()

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'category': self.category.value,
            'priority': self.priority.value,
            'tags': self.tags,
            'status': self.status.value,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data['id'],
            title=data['title'],
            content=data['content'],
            category=NoteCategory(data['category']),
            priority=NotePriority(data['priority']),
            tags=data.get('tags', []),
            status=Status(data['status']),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )

    def update(self, title=None, content=None, category=None, priority=None, tags=None):
        """Обновляет заметку"""
        if title is not None:
            self.title = title
        if content is not None:
            self.content = content
        if category is not None:
            self.category = category
        if priority is not None:
            self.priority = priority
        if tags is not None:
            self.tags = tags

        self.updated_at = datetime.now().isoformat()

    def __str__(self):
        status_icon = "📁" if self.status == Status.ARCHIVED else "📝"
        priority_icon = {
            NotePriority.LOW: "⬇",
            NotePriority.MEDIUM: "●",
            NotePriority.HIGH: "⬆"
        }.get(self.priority, "●")

        category_icon = {
            NoteCategory.WORK: "💼",
            NoteCategory.PERSONAL: "👤",
            NoteCategory.STUDY: "📚",
            NoteCategory.SHOPPING: "🛒",
            NoteCategory.IDEAS: "💡",
            NoteCategory.OTHER: "📄"
        }.get(self.category, "📄")

        tags_str = f" | Tags: {', '.join(self.tags)}" if self.tags else ""
        created = datetime.fromisoformat(self.created_at).strftime("%d.%m.%Y")

        return (f"{status_icon} [{priority_icon}] {category_icon} #{self.id}: {self.title}\n"
                f"   Created: {created}{tags_str}\n"
                f"   {self.content[:100]}{'...' if len(self.content) > 100 else ''}")