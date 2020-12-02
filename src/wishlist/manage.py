from flask.cli import FlaskGroup

from app import create_app
from app.models import db, User, Book
from tests.data import USER_1, BOOK_1, BOOK_2


cli = FlaskGroup(create_app=create_app)


@cli.command("create_db")
def create_db():
    db.drop_all()
    db.create_all()
    db.session.commit()


@cli.command("seed_db")
def seed_db():
    db.session.add_all([
        User(**USER_1),
        Book(**BOOK_1),
        Book(**BOOK_2)
    ])
    db.session.commit()


if __name__ == "__main__":
    cli()
