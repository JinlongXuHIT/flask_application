from flask import session
from flask import current_app
from info.modules.home import home_bp
import  logging
@home_bp.route('/', methods=['GET', 'POST'])
def index():
    # strict_redis.set('name', 'zs')
    # logging.error('raise a error')
    current_app.logger.error('raise a error')
    return 'index'