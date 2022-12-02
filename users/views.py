from starlette.exceptions import HTTPException
from . import schemas
from . import db_operations


async def users_view(user_id: int) -> schemas.UserDetail:
    """"""
    user = await db_operations.get_user_by_id(user_id)

    if user is None:
        raise HTTPException(status_code=404,
                            detail="User not found")
    return user
