#!/usr/bin/env python3
import argparse
import sys
from notebook.storage import Storage
from notebook.commands import Commands


def main():
    storage = Storage()
    commands = Commands(storage)

    parser = argparse.ArgumentParser(description="Блокнот - управление заметками")
    subparsers = parser.add_subparsers(dest='command', help='Доступные команды')

    # Команда добавления
    add_parser = subparsers.add_parser('add', help='Добавить новую заметку')
    add_parser.add_argument('title', help='Заголовок заметки')
    add_parser.add_argument('content', help='Текст заметки')
    add_parser.add_argument('-c', '--category',
                            choices=['work', 'personal', 'study', 'shopping', 'ideas', 'other'],
                            default='other', help='Категория заметки')
    add_parser.add_argument('-p', '--priority', choices=['low', 'medium', 'high'],
                            default='medium', help='Приоритет заметки')
    add_parser.add_argument('-t', '--tags', nargs='+', help='Теги через пробел')

    # Команда списка
    list_parser = subparsers.add_parser('list', help='Показать список заметок')
    list_parser.add_argument('-c', '--category',
                             choices=['work', 'personal', 'study', 'shopping', 'ideas', 'other'],
                             help='Фильтр по категории')
    list_parser.add_argument('-p', '--priority', choices=['low', 'medium', 'high'],
                             help='Фильтр по приоритету')
    list_parser.add_argument('-s', '--status', choices=['active', 'archived'],
                             default='active', help='Статус заметок')
    list_parser.add_argument('--full', action='store_true',
                             help='Показать полное содержимое')

    # Команда поиска
    search_parser = subparsers.add_parser('search', help='Поиск заметок')
    search_parser.add_argument('search_term', help='Текст для поиска')
    search_parser.add_argument('--in', dest='search_in',
                               choices=['title', 'content', 'tags', 'all'],
                               default='all', help='Где искать')

    # Команда удаления
    delete_parser = subparsers.add_parser('delete', help='Удалить заметку')
    delete_parser.add_argument('note_id', type=int, help='ID заметки')

    # Команда архивации
    archive_parser = subparsers.add_parser('archive', help='Архивировать заметку')
    archive_parser.add_argument('note_id', type=int, help='ID заметки')

    # Команда редактирования
    edit_parser = subparsers.add_parser('edit', help='Редактировать заметку')
    edit_parser.add_argument('note_id', type=int, help='ID заметки')
    edit_parser.add_argument('--title', help='Новый заголовок')
    edit_parser.add_argument('--content', help='Новый текст')
    edit_parser.add_argument('-c', '--category',
                             choices=['work', 'personal', 'study', 'shopping', 'ideas', 'other'],
                             help='Новая категория')
    edit_parser.add_argument('-p', '--priority', choices=['low', 'medium', 'high'],
                             help='Новый приоритет')
    edit_parser.add_argument('-t', '--tags', nargs='+', help='Новые теги')

    # Команда тегов
    tags_parser = subparsers.add_parser('tags', help='Показать все теги')

    args = parser.parse_args()

    if not args.command:
        # Если команда не указана, показываем справку и список заметок
        parser.print_help()
        print("\n" + "=" * 50)
        result = commands.list_notes()
        print(result)
        return

    try:
        if args.command == 'add':
            result = commands.add_note(
                title=args.title,
                content=args.content,
                category=args.category,
                priority=args.priority,
                tags=args.tags
            )
        elif args.command == 'list':
            result = commands.list_notes(
                category=args.category,
                priority=args.priority,
                status=args.status,
                show_content=args.full
            )
        elif args.command == 'search':
            result = commands.search_notes(
                search_term=args.search_term,
                search_in=args.search_in
            )
        elif args.command == 'delete':
            result = commands.delete_note(args.note_id)
        elif args.command == 'archive':
            result = commands.archive_note(args.note_id)
        elif args.command == 'edit':
            result = commands.edit_note(
                note_id=args.note_id,
                title=args.title,
                content=args.content,
                category=args.category,
                priority=args.priority,
                tags=args.tags
            )
        elif args.command == 'tags':
            result = commands.list_tags()
        else:
            result = "Неизвестная команда"

        print(result)

    except Exception as e:
        print(f"Ошибка: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()