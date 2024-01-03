from pathlib import Path
from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from rich.prompt import Confirm

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///students.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key'

db = SQLAlchemy(app)
query = db.session.query


class User(db.Model):
    username = db.Column(db.String(50), unique=True, primary_key=True)
    password = db.Column(db.String(50), nullable=False)
    is_teacher = db.Column(db.Boolean, default=False)


class Score(db.Model):
    account_name = db.Column(db.String(50), db.ForeignKey('user.username'), primary_key=True)
    push_ups = db.Column(db.Integer, nullable=False)
    sit_ups = db.Column(db.Integer, nullable=False)
    pull_ups = db.Column(db.Integer, nullable=False)
    run_3000m = db.Column(db.Float, nullable=False)


def init():
    if not Path('./instance/students.db').exists():
        with app.app_context():
            db.create_all()
            count: int = -1
            accounts = int(input('数据库服务器初始化，你需要新建多少个用户？'))
            if accounts == -1:  # For Debug
                list_to_add = [User(username='Teacher', password='password', is_teacher=True),
                               User(username='Student1', password='password'),
                               User(username='Student2', password='password'),
                               User(username='Student3', password='password'),
                               User(username='Student4', password='password'),
                               User(username='Student5', password='password'),
                               Score(account_name='Student1', push_ups=17, sit_ups=23, pull_ups=4, run_3000m=13.5 * 60),
                               Score(account_name='Student2', push_ups=8, sit_ups=14, pull_ups=1, run_3000m=16.2 * 60),
                               Score(account_name='Student3', push_ups=12, sit_ups=18, pull_ups=2, run_3000m=14.8 * 60),
                               Score(account_name='Student4', push_ups=5, sit_ups=10, pull_ups=0, run_3000m=17.3 * 60),
                               Score(account_name='Student5', push_ups=20, sit_ups=25, pull_ups=5, run_3000m=12.8 * 60),
                               ]
                for i in list_to_add:
                    db.session.add(i)
                db.session.commit()
                return

            while (count := count + 1) != accounts:
                username = input('用户名: ')
                password = input('密码: ')
                is_teacher = Confirm().ask('是否为老师?', default=False)
                if username and password:
                    user = User(username=username, password=password, is_teacher=is_teacher)
                    db.session.add(user)
                db.session.commit()


@app.route('/data', methods=['POST'])
def add_data():
    if query(User).filter_by(username=request.form.get('username'),
                             password=request.form.get('password'),
                             is_teacher=True
                             ).first() is not None:
        if query(Score).filter_by(account_name=request.form.get('account_name')).first() is not None:
            return '不能重复添加', 409
        db.session.add(Score(account_name=request.form.get('account_name'),
                             push_ups=request.form.get('push_ups'),
                             sit_ups=request.form.get('sit_ups'),
                             pull_ups=request.form.get('pull_ups'),
                             run_3000m=request.form.get('run_3000m')))
        db.session.commit()
        return '添加成功', 201
    else:
        return '账户的用户名或密码错误导致无权限访问', 401


@app.route('/data', methods=['PUT'])
def update_data():
    if query(User).filter_by(username=request.form.get('username'),
                             password=request.form.get('password'),
                             is_teacher=True
                             ).first() is not None:
        score = query(Score).filter_by(account_name=request.form.get('account_name')).first()
        if score:
            score.push_ups = int(request.form.get('push_ups'))
            score.sit_ups = int(request.form.get('sit_ups'))
            score.pull_ups = int(request.form.get('pull_ups'))
            score.run_3000m = float(request.form.get('run_3000m'))
            db.session.commit()
            return '成绩更新成功！', 200
        else:
            return '找不到该学生的成绩记录！', 404
    else:
        return '账户的用户名或密码错误导致无权限访问', 401


@app.route('/data', methods=['GET'])
def query_data():
    if query(User).filter_by(username=request.form.get('username'),
                             password=request.form.get('password'),
                             is_teacher=True
                             ).first() is not None:
        score = (query(Score.push_ups, Score.sit_ups, Score.pull_ups, Score.run_3000m)
                 .filter_by(account_name=request.form.get('account_name')).first())
        if score is None:
            return '找不到该学生的成绩记录！', 404
        return jsonify(list(score)), 200
    elif query(User).filter_by(username=request.form.get('username'),
                               password=request.form.get('password'),
                               ).first() is not None:
        if request.form.get('username') != request.form.get('account_name'):
            return '你只能查询你自己的成绩！', 403
        else:
            score = (query(Score.push_ups, Score.sit_ups, Score.pull_ups, Score.run_3000m)
                     .filter_by(account_name=request.form.get('account_name')).first())
            return jsonify(list(score))
    else:
        return '认证失败！', 401


@app.route('/data', methods=['DELETE'])
def del_data():
    if query(User).filter_by(username=request.form.get('username'),
                             password=request.form.get('password'),
                             is_teacher=True
                             ).first() is not None:
        data = query(Score).filter_by(account_name=request.form.get('account_name')).first()
        if data is None:
            return '找不到该学生的成绩记录！', 404
        db.session.delete(data)
        db.session.commit()
        return '删除成功', 200
    else:
        return '删除失败！', 401


@app.route('/get_all_data', methods=['GET'])
def get_all_data():
    if query(User).filter_by(username=request.form.get('username'),
                             password=request.form.get('password'),
                             is_teacher=True
                             ).first() is not None:
        datas = query(Score.account_name, Score.push_ups, Score.sit_ups, Score.pull_ups, Score.run_3000m).all()
        return jsonify([tuple(i) for i in datas]), 200
    else:
        return '认证失败！', 401


init()
