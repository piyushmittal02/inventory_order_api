from models.user import User


def find_user_by_username(username):
    return User.query.filter_by(username=username).first()