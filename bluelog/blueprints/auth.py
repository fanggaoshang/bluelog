from flask import Blueprint, flash, redirect, url_for, render_template
from flask_login import current_user, login_user, logout_user
from bluelog.forms import LoginForm
from bluelog.models import Admin
from bluelog.utils import redirect_back

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("blog.index"))

    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        remember = form.remember.data
        admin = Admin.query.first()
        if admin:
            # 如果管理员存在, 验证用户名和密码
            if username == admin.username and admin.validate_password(password):
                login_user(admin, remember)     # 登入用户
                flash('欢迎回来', 'info')
                return redirect_back()
            flash('无效的用户名或密码', 'warning')
        else:
            flash('无效的', 'warning')
    return render_template('auth/login.html', form=form)


@auth_bp.route('/logout')
def logout():
    logout_user()
    flash('退出成功', 'info')
    return redirect_back()
