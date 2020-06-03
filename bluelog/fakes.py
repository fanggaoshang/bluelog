import random
from bluelog.models import Admin, Category, Post, Comment
from bluelog.extensions import db
from sqlalchemy.exc import IntegrityError
from faker import Faker

fake = Faker("zh_CN")


def fake_admin():
    admin = Admin(
        username='admin',
        blog_title='方高上的博客',
        blog_sub_title="这是一个博客网站,用来分享个人博客",
        name='方高上',
        about='欢迎来到方高上的博客网站'
    )
    admin.set_password('545464')
    db.session.add(admin)
    db.session.commit()


def fake_categories(count=10):
    category = Category(name="默认")
    db.session.add(category)
    for i in range(count):
        category = Category(name=fake.word())
        db.session.add(category)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()


def fake_posts(count=50):
    for i in range(count):
        post = Post(
            title=fake.sentence(20),
            body=fake.text(2000),
            category=Category.query.get(random.randint(1, Category.query.count())),
            timestamp=fake.date_time_this_year()
        )
        db.session.add(post)
    db.session.commit()


def fake_comments(count=500):
    for i in range(count):
        comment = Comment(
            author=fake.name(),
            email=fake.email(),
            site=fake.url(),
            body=fake.sentence(),
            reviewed=True,
            timestamp=fake.date_time_this_year(),
            post=Post.query.get(random.randint(1, Post.query.count()))
        )
        db.session.add(comment)
    salt = int(count * 0.1)
    for i in range(salt):
        # 未审核评论
        comment = Comment(
            author=fake.name(),
            email=fake.email(),
            site=fake.url(),
            body=fake.sentence(),
            reviewed=False,
            timestamp=fake.date_time_this_year(),
            post=Post.query.get(random.randint(1, Post.query.count()))
        )
        db.session.add(comment)
        # 管理员发表的评论
        comment = Comment(
            author='fanggaoshang',
            email='fangyingdon@163.com',
            site='fanggaoshang.cn',
            body=fake.sentence(),
            reviewed=True,
            timestamp=fake.date_time_this_year(),
            post=Post.query.get(random.randint(1, Post.query.count()))
        )
        db.session.add(comment)
    db.session.commit()
    # 回复
    for i in range(salt):
        comment = Comment(
            author=fake.name(),
            email=fake.email(),
            site=fake.url(),
            body=fake.sentence(),
            reviewed=True,
            timestamp=fake.date_time_this_year(),
            replied=Comment.query.get(random.randint(1, Comment.query.count())),
            post=Post.query.get(random.randint(1, Post.query.count()))
        )
        db.session.add(comment)
