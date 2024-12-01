from pathlib import Path
from flask import Flask, request, jsonify, make_response, g
from flask_sqlalchemy import SQLAlchemy
import secrets

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
    def as_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


sessions = {}


def init():
    if not Path('./instance/students.db').exists():
        with app.app_context():
            db.create_all()
            # Debug initialization
            db.session.add(User(username='Teacher', password='password', is_teacher=True))
            db.session.add(User(username='Student1', password='password'))
            db.session.commit()


@app.before_request
def authenticate():
    g.user = None
    token = request.cookies.get('session_token')
    if token and token in sessions:
        g.user = sessions[token]


@app.route('/signin', methods=['POST'])
def sign_in():
    data = request.get_json()
    if not data or 'username' not in data or 'password' not in data:
        return '缺少参数！', 400

    username = data['username']
    password = data['password']
    user = query(User).filter_by(username=username, password=password).first()
    if user:
        token = secrets.token_hex(16)
        sessions[token] = user
        response = make_response({'message': '登录成功！'})
        response.set_cookie('session_token', token, max_age=30 * 24 * 3600)  # 30 days
        return '登录成功！',200
    return '用户名或密码错误！', 401


def teacher_required(func):
    def wrapper(*args, **kwargs):
        if not g.user or not g.user.is_teacher:
            return '认证失败！', 401
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper


@app.route('/data', methods=['POST'])
@teacher_required
def add_data():
    data = request.get_json()
    required_fields = {'account_name', 'push_ups', 'sit_ups', 'pull_ups', 'run_3000m'}
    if not data or not required_fields.issubset(data):
        return '缺少必要参数！', 400

    if query(Score).filter_by(account_name=data['account_name']).first():
        return '不能重复添加！', 409

    db.session.add(Score(**data))
    db.session.commit()
    return '添加成功！', 201


@app.route('/data', methods=['PUT'])
@teacher_required
def update_data():
    data = request.get_json()
    required_fields = {'account_name', 'push_ups', 'sit_ups', 'pull_ups', 'run_3000m'}
    if not data or not required_fields.issubset(data):
        return '缺少必要参数！', 400

    score = query(Score).filter_by(account_name=data['account_name']).first()
    if score:
        score.push_ups = data['push_ups']
        score.sit_ups = data['sit_ups']
        score.pull_ups = data['pull_ups']
        score.run_3000m = data['run_3000m']
        db.session.commit()
        return '成绩更新成功！', 200
    return '找不到该学生的成绩记录！', 404


@app.route('/data', methods=['GET'])
def query_data():
    account_name = request.args.get('account_name')
    if not account_name:
        return '缺少参数！', 400
    if g.user and g.user.is_teacher:
        score = list(query(Score).filter_by(account_name=account_name).first().as_dict().values())
        if score:
            return jsonify(score), 200
        return '找不到该学生的成绩记录！', 404
    elif g.user and g.user.username == account_name:
        score = list(query(Score).filter_by(account_name=account_name).first().as_dict().values())
        if score:
            return jsonify(score), 200
        return '找不到该学生的成绩记录！', 404
    return '认证失败！', 401


@app.route('/get_all_data', methods=['GET'])
@teacher_required
def get_all_data():
    scores = query(Score).all()
    return jsonify([list(i.as_dict().values()) for  i in scores]), 200


@app.route('/data', methods=['DELETE'])
@teacher_required
def del_data():
    account_name = request.args.get('account_name')
    if not account_name:
        return '缺少参数！', 400

    score = query(Score).filter_by(account_name=account_name).first()
    if score:
        db.session.delete(score)
        db.session.commit()
        return '删除成功！', 200
    return '找不到该学生的成绩记录！', 404


init()
app.run(debug=True)