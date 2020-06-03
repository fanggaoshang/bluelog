import os
import click

from bluelog.blueprints.auth import auth_bp
from bluelog.blueprints.admin import admin_bp
from bluelog.blueprints.blog import blog_bp
from flask import Flask, render_template
from bluelog.settings import config
from bluelog.extensions import bootstrap, mail, moment, db, ckeditor, login_manager, csrf
from bluelog.models import Admin, Category, Comment

from flask_login import current_user
from flask_wtf.csrf import CSRFError


def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv('FLASK_CONFIG', 'development')

    app = Flask('bluelog')
    app.config.from_object(config[config_name])

    register_blueprints(app)
    register_extension(app)
    register_logging(app)
    register_shell_context(app)
    register_template_context(app)
    register_errors(app)
    register_commands(app)

    return app


def register_logging(app):
    pass


def register_extension(app):
    bootstrap.init_app(app)
    mail.init_app(app)
    ckeditor.init_app(app)
    db.init_app(app)
    moment.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)


def register_blueprints(app):
    app.register_blueprint(blog_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(admin_bp, url_profix='/admin')


def register_shell_context(app):
    @app.shell_context_processor
    def make_shell_context():
        return dict(db=db)


def register_template_context(app):
    """模板上下文函数"""

    @app.context_processor
    def make_template_context():
        admin = Admin.query.first()
        categories = Category.query.order_by(Category.name).all()
        if current_user.is_authenticated:
            unread_comments = Comment.query.filter_by(reviewed=False).count()
        else:
            unread_comments = None
        return dict(admin=admin, categories=categories, unread_comments=unread_comments)


def register_errors(app):
    @app.errorhandler(400)
    def bad_request(e):
        return render_template('errors/400.html'), 400

    @app.errorhandler(CSRFError)
    def handle_csrf_error(e):
        return render_template('errors/400.html', description=e.description), 400


def register_commands(app):
    @app.cli.command()
    @click.option('--username', prompt=True, help='登录账户')
    @click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True, help='登录密码')
    def init(username, password):
        """创建博客为了你"""

        click.echo("正在初始化数据库")
        db.create_all()

        admin = Admin.query.first()
        if admin:  # 如果数据库中已经有管理员记录就更新用户名和密码
            click.echo('管理员已存在,正在更新...')
            admin.username = username
            admin.set_password(password)
        else:  # 否则创建新的管理员记录
            click.echo('正在创建管理员记录')
            admin = Admin(
                username=username,
                blog_title='博客',
                blog_sub_title='我才是最受欢迎的',
                name='管理员',
                about='新手上路,请多多关注'
            )
            admin.set_password(password)
            db.session.add(admin)

        category = Category.query.first()
        if category is None:
            click.echo("正在创建默认分类...")
            category = Category(name='默认')
            db.session.add(category)

        db.session.commit()
        click.echo('完成')

    @app.cli.command()
    @click.option('--category', default=10, help='')
    @click.option('--post', default=50, help='')
    @click.option('--comment', default=500, help='')
    def forge(category, post, comment):
        """Generates the fake categories, posts, comments."""
        from bluelog.fakes import fake_admin, fake_categories, fake_comments, fake_posts
        db.drop_all()
        db.create_all()

        click.echo('正在生成管理员数据...')
        fake_admin()

        click.echo('正在生成 %d 条分类...' % category)
        fake_categories(category)

        click.echo('正在生成 %d 篇文章...' % post)
        fake_posts(post)

        click.echo('正在生成 %d 条评论...' % comment)
        fake_comments(comment)

        click.echo('完成')