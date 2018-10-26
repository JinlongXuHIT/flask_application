from flask import session
from flask_migrate import MigrateCommand

from flask_script import Manager

from info import create_application

# app init
app = create_application('develop')
# create 管理器对象
manager = Manager(app)
manager.add_command('mc', MigrateCommand)

if __name__ == '__main__':
    # app.run(debug=True)
    # 管理器启动
    manager.run()
