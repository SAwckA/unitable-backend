from pydantic import BaseModel # type: ignore # noqa


class Student(BaseModel):
    """
    Объект студента
    Используется в журнале, как список
    """
    id: int
    name: str


class StateRecord(BaseModel):
    """Объект из базы"""
    pass


class CreateJournal(BaseModel):
    """
    Форма для создания журнала
    Используется в принимаемом запросе
    """
    groupName: str
    eduName: str
    studentsList: list[str]


class JournalHead(BaseModel):
    """
    Шапка журнала
    Использвется как часть объекта целого журнала
    """
    name: str
    edu: str
    owner_id: int


class Journal(BaseModel):
    """
    Объект журнала
    Используется для возвращаемого значения в запросе GET /journal/{id}
    """
    students: list[Student] | list = []
    table: dict = {}
    head: JournalHead | None = None
