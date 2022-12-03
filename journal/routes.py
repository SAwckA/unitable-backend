import datetime
from core.app import app
from . import db_operations
from . import schemas
from starlette.exceptions import HTTPException # type: ignore # noqa
from auth.dependencies import AccessTokenAuth
from fastapi import Depends
from utils.hash_algs import hash_sum


@app.get('/journal/{journal_id}')
async def get_journal(journal_id: int, date_start: str, date_end: str) -> schemas.Journal:
    """
    Объект журнала со всем изменениями
        TO DO:
            Разбить на
                GET /journal/{id}/students
                GET /journal/{id}/head
                GET /journal/{id}/table
    """
    journal: schemas.Journal = await db_operations.get_journal(
        journal_id=journal_id,
        date_start=date_start,
        date_end=date_end
    )

    if journal.head:
        return journal

    raise HTTPException(
        status_code=404,
        detail="Journal not found"
    )


@app.get('/profile/journals')
async def get_my_journals(credentials: AccessTokenAuth = Depends(AccessTokenAuth)):
    """ Список журналов пользователя """
    return await db_operations.get_journal_list_by_user_id(credentials.user.id)


@app.post('/journal/{journal_id}/change')
async def change_journal(journal_id: int, commit: dict, credentials: AccessTokenAuth = Depends(AccessTokenAuth)):
    """
    Применяет изменения
    <!> Проверяет права на изменения журнала
    TO DO:
        Записать commit в бд целиком как json
        Проверка прав должна быть в другой функции
    """

    head: schemas.JournalHead = await db_operations.get_journal_head_by_id_manually(journal_id)

    if not head:
        raise HTTPException(404, "Journal not found")

    if head.owner_id != credentials.user.id:
        raise HTTPException(403, "Only owner or administrator can edit journal")

    changes = []
    for date in [*commit]:
        for record in commit[date]:
            changes.append(
                (
                    journal_id,
                    record.get('id'),
                    record.get('state'),
                    datetime.datetime.strptime(date, "%Y-%m-%d"),
                    hash_sum(
                        journal_id,
                        record.get('id'),
                        date
                    )
                )
            )

    await db_operations.change_journal_by_id(changes)

    return "OK"


@app.post('/createJournal')
async def create_journal(journal: schemas.CreateJournal,
                         credentials: AccessTokenAuth = Depends(AccessTokenAuth)) -> int:
    """
    Создание журнала
    """

    return await db_operations.create_journal_with_students(journal, credentials.user.id)
