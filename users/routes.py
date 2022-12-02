from core.app import app
from . import views
from . import schemas


@app.get('/users/{user_id}')
async def get_user_by_id(user_id: int) -> schemas.UserDetail:
    return await views.users_view(user_id)
