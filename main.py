from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

app = Flask(__name__)
app.config.from_pyfile("./mydev.cfg")

db = SQLAlchemy(app)


class Author(db.Model):
    __tablename__ = "tbl_author"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    books = db.relationship("Book", backref="author")


class Book(db.Model):
    __tablename__ = "tbl_books"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    author_id = db.Column(db.Integer, db.ForeignKey("tbl_author.id"))


with app.app_context():
    # db.drop_all()
    db.create_all()


class AuthorBooksForm(FlaskForm):
    author_name = StringField(label=u"author_name", validators=[DataRequired()])
    book_name = StringField(label=u"book_name", validators=[DataRequired()])
    submit = SubmitField(label=u"提交")


@app.route("/")
def manager_index():
    # 创建表单对象
    form = AuthorBooksForm()
    # 查询数据库
    authors = Author.query.all()
    # 渲染模板
    return render_template("index.html", authors=authors, form=form)


@app.route("/submit-book")
def add_book():
    author_name = request.args.get("author_name")
    book_name = request.args.get("book_name")
    author_query = Author.query.filter_by(name=author_name).all()
    if len(author_query) == 0:
        author = Author(name=author_name)
        db.session.add(author)
        db.session.commit()
        author_id = author.id
    else:
        author_id = author_query[0].id
    book = Book(name=book_name, author_id=author_id)
    db.session.add(book)
    db.session.commit()
    return redirect(url_for("manager_index"))


@app.route("/delete-book/<int:id>")
def delete_book(id):
    book = Book.query.get(id)
    db.session.delete(book)
    db.session.commit()
    return redirect(url_for("manager_index"))


if __name__ == '__main__':
    app.run(host="127.0.0.1", port=8080, debug=True)
