import asyncpg  # type: ignore # noqa
import datetime
import json
from core.app import db
from . import schemas


async def __get_journal_students(conn: asyncpg.Connection, journal_id) -> list[schemas.Student] | list:
    """
    Список студентов
    <!> Используется только при составлении объекта журнала (get_journal())
    <!> Принимает уже открытое соединение с бд, не реализует открытие нового
        TO DO:
            Тип list[<nothing>]
    """
    sql = "select id, name from public.student where journal_id=$1"

    students = await conn.fetch(sql, journal_id)

    if students:
        return [schemas.Student(**dict(x)) for x in students]

    return []


async def __get_journal_head(conn: asyncpg.Connection, journal_id) -> schemas.JournalHead | None:
    """
    Шапка журнала
    <!> Используется только при составлении объекта журнала (get_journal())
    <!> Принимает уже открытое соединение с бд, не реализует открытие нового
    """
    sql = """select name, edu, owner_id from public.group_journal where id=$1"""

    head = await conn.fetchrow(sql, journal_id)

    if head:
        return schemas.JournalHead(**dict(head))
    return None


async def get_journal_table(conn: asyncpg.Connection, journal_id: int, date_start: str, date_end: str) -> dict:
    """
    Таблица журнала
    <!> Используется только при составлении объекта журнала (get_journal())
    <!> Принимает уже открытое соединение с бд, не реализует открытие нового
        TO DO:
            Возвращаемый тип
    """
    sql = """select json_object_agg(
        date_day, states
               ) from (
            select date_day, json_agg(obj) as states from (
                select date_day, json_build_object(
                    'state', state,
                    'id', student_id
                    ) as obj
                from group_journal_state
                    where
                        group_journal_id=$1
                        AND
                        date_day >= $2
                        AND
                        date_day <= $3
                ) tmp
            group by date_day
        order by date_day
    ) as journal;"""

    table: str = await conn.fetchval(sql,
                                     journal_id,
                                     datetime.datetime.strptime(date_start, "%Y-%m-%d"),
                                     datetime.datetime.strptime(date_end, "%Y-%m-%d"))

    if table:
        return json.loads(table)

    return {}


async def get_journal(journal_id: int, date_start: str, date_end: str) -> schemas.Journal:
    """
    Составление объекта журнала
    Содержит 3 select запроса, разбитых на подпрограммы, работающие на 1 соединении
    """
    conn: asyncpg.Connection

    async with db.pool.acquire() as conn:
        students: list[schemas.Student] | list = await __get_journal_students(
            conn=conn,
            journal_id=journal_id
        )

        table: dict = await get_journal_table(
            conn=conn,
            journal_id=journal_id,
            date_start=date_start,
            date_end=date_end
        )

        head: schemas.JournalHead | None = await __get_journal_head(
            conn=conn,
            journal_id=journal_id
        )

    return schemas.Journal(
        head=head,
        table=table,
        students=students
    )


async def get_journal_head_by_id_manually(journal_id) -> schemas.JournalHead | None:
    """
    Выборка шапки журнала
    Название журнала, ВУЗ, создатель журнала
    Повторение функции get_journal_head, но с открытием нового соединения
    """

    conn: asyncpg.Connection
    sql = """select name, edu, owner_id from public.group_journal where id=$1"""
    async with db.pool.acquire() as conn:
        head = await conn.fetchrow(sql, journal_id)

    if head:
        return schemas.JournalHead(**dict(head))
    return None


async def get_journal_list_by_user_id(user_id: int) -> list:
    """ Возвращает список журналов по id пользователя
        TO DO:
            Создать объект журнала, тогда ворзражает list[JournalShort] | list[None]
    """
    conn: asyncpg.Connection

    sql = """select id, name, edu from public.group_journal where owner_id=$1"""

    async with db.pool.acquire() as conn:
        journal_list = await conn.fetch(sql, user_id)

    return journal_list


async def change_journal_by_id(changes: list[tuple]) -> None:
    """
    Изменение в таблице состояний журнала
    Состоит из 2 запросов в одной транзакции
        TO DO:
            Объединить 2 запроса в 1
    """
    conn: asyncpg.Connection

    sql = """insert into public.group_journal_state(
        group_journal_id, 
        student_id, 
        state, 
        date_day, 
        record_sum
    ) values ($1, $2, $3, $4, $5)
    ON CONFLICT(record_sum) DO 
    UPDATE
        SET state = excluded.state;
    """

    async with db.pool.acquire() as conn:
        async with conn.transaction():
            await conn.executemany(sql, changes)

            """
            Очиска нулевых состояний
                TO DO:
                    Перенести это всё в один запрос (который выше)
            """

            await conn.execute("delete from public.group_journal_state where state=0;")

    return None


async def create_journal_with_students(journal: schemas.CreateJournal, user_id: int) -> int:
    """
    Создание нового журнала и запись относящихся к нему студентов
    Содержит 2 запроса в одной транзакции
    Возвращает id нового журнала
        TO DO:
            Объединение в один запрос
    """
    conn: asyncpg.Connection

    async with db.pool.acquire() as conn:
        async with conn.transaction():
            journal_id: asyncpg.Record = await conn.fetchrow(
                "insert into public.group_journal(name, edu, owner_id) values ($1, $2, $3) RETURNING id",
                journal.groupName,
                journal.eduName,
                user_id)

            await conn.executemany("""insert into public.student(journal_id, name) values ($1, $2)""",
                                   ((journal_id.get('id'), x) for x in journal.studentsList))

    return journal_id.get('id')
