import json
import os
from typing import List, Optional
from .models import Note, Status, NotePriority, NoteCategory


class Storage:
    def __init__(self, filename="Notes.json"):
        self.filename = filename

    def _ensure_file_exists(self):
        """Creates the file if it does not exist."""
        if not os.path.exists(self.filename):
            with open(self.filename, 'w') as f:
                json.dump([], f)

    def save_notes(self, notes: List[Note]):
        """Saves the list of notes to a file."""
        self._ensure_file_exists()
        with open(self.filename, 'w') as f:
            json.dump([note.to_dict() for note in notes], f, indent=2)

    def load_notes(self) -> List[Note]:
        """Loads notes from a file."""
        self._ensure_file_exists()
        try:
            with open(self.filename, 'r') as f:
                data = json.load(f)
                return [Note.from_dict(note_data) for note_data in data]
        except (json.JSONDecodeError, KeyError):
            return []

    def get_next_id(self) -> int:
        """Generates the next ID for a new note."""
        notes = self.load_notes()
        if not notes:
            return 1
        return max(note.id for note in notes) + 1

    def get_all_tags(self) -> List[str]:
        """Returns a list of all unique tags."""
        notes = self.load_notes()
        all_tags = set()
        for note in notes:
            all_tags.update(note.tags)
        return sorted(list(all_tags))