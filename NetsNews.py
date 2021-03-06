# coding=utf8
from flask import Flask, render_template, redirect, url_for
from datetime import datetime
from forms import NewsForm
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:123456@localhost:3306/news?charset=utf8'
app.config['SECRET_KEY'] = 'asdaaw123132%%wq#$'
db = SQLAlchemy(app)


class News(db.Model):
    """ 新闻模型 """
    __tablename__ = 'news'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    img_url = db.Column(db.String(200), nullable=False)
    content = db.Column(db.String(2000), nullable=False)
    is_valid = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)
    news_type = db.Column(db.Enum('推荐', '百家', '本地', '图片'))

    comments = db.relationship('Comments', backref='news',
                               lazy='dynamic')

    def __repr__(self):
        return '<News %r>' % self.title


@app.route('/')
def index():
    # 新闻首页
    news_list = News.query.filter_by(is_valid=1)
    return render_template('index.html', news_list=news_list)


@app.route('/cat/<name>/')
def cat(name):
    # 新闻类别
    news_list = News.query.filter(News.types == name)
    # 查询类别为name的新闻数据
    return render_template('cat.html', name=name, news_list=news_list)


@app.route('/detail/<int:pk>/')
def detail(pk):
    # 新闻详情信息
    new_obj = News.query.get(pk)
    return render_template('detail.html', new_obj=new_obj)


@app.route('/admin/')
@app.route('/admin/<int:page>')
def admin(page=None):
    # 新闻管理首页
    if page is None:
        page = 1
    news_list = News.query.filter_by(is_valid=True).paginate(page=page, per_page=5)
    return render_template('admin/index.html', news_list=news_list)


@app.route('/admin/add/', methods=('GET', 'POST'))
def add():
    # 新增新闻信息
    form = NewsForm()
    if form.validate_on_submit():
        # 获取数据
        new_obj = News(
            title=form.title.data,
            content=form.content.data,
            types=form.types.data,
            image=form.image.data,
            created_at=datetime.now()
        )
        # 保存数据
        db.session.add(new_obj)
        db.session.commit()
        # 文字提示
        # flash
        return redirect(url_for('admin'))
    return render_template('admin/add.html', form=form)


@app.route('/admin/update/<int:pk>/', methods=('GET', 'POST'))
def update(pk):
    # 更新新闻内容
    new_obj = News.query.get(pk)
    # 如果没有数据， 则返回
    if not new_obj:
        # TODO 使用Flash进行文字提示用户
        return redirect(url_for('admin'))
    form = NewsForm(obj=new_obj)
    if form.validate_on_submit():
        # 获取数据
        new_obj.title = form.title.data
        new_obj.content = form.content.data
        # 保存数据
        db.session.add(new_obj)
        db.session.commit()
        return redirect(url_for('admin'))
    return render_template('admin/update.html', form=form)


@app.route('/admin/delete/<int:pk>/', methods=('GET', 'POST'))
def delete(pk):
    # 删除新闻内容
    new_obj = News.query.get(pk)
    if not new_obj:
        return 'no'
    new_obj.is_valid = False
    db.session.add(new_obj)
    db.session.commit()
    return 'yes'


if __name__ == '__main__':
    app.run(debug=True)
