from app.managers.base import BaseCRUD
from app.models.users import User


class Users(BaseCRUD[User]):
    model = User