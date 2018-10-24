from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
class Config:
    DEBUG = True
    SQLAlchemy

# 从类对象a加载配置信息
app.config.from_object(Config)
@app.route('/', methods=['GET', 'POST'])
def index():
    pass
if __name__ == '__main__':
    app.run(debug=True)