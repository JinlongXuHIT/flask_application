from flask import session, render_template
from flask import current_app
from info.modules.home import home_bp
import  logging
@home_bp.route('/', methods=['GET', 'POST'])
def index():
    # strict_redis.set('name', 'zs')
    # logging.error('raise a error')
    # current_app.logger.error('raise a error')
    return render_template('index.html')

@home_bp.route('/favicon.ico', methods=['GET', 'POST'])
def favicon():
    return  current_app.send_static_file('./news/favicon.ico')