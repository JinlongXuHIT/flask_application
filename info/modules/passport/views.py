import random
import re

from flask import request, abort, current_app, make_response, Response, jsonify

from info import strict_redis
from info.lib.captcha.pic_captcha import captcha
from info.lib.yuntongxun.sms import CCP
from info.modules.passport import passport_bp
from info.utils.response_code import RET, error_map


@passport_bp.route('/get_img_code', methods=['GET', 'POST'])
def get_img_code():
    # 获取request中的参数: 图片id
    img_code_id = request.args.get('img_code_id')
    # 校验参数
    if not  img_code_id:
        return abort(403)

    #  调用第三方接口生成验证码,保存id 和 验证文字
    img_name, img_text, img_bytes = captcha.generate_captcha()
    try:
        strict_redis.set('img_code_id'+img_code_id,img_text,ex=300)
        print(img_text)
    except Exception as e:
        current_app.logger.error(e)
        return abort(500)
    # return  img_bytes
    # 调用第三方接口生成他\验证图片,response 图片
    response = make_response(img_bytes)  # type: Response
    response.content_type = 'image/jpeg'
    return response


@passport_bp.route('/get_sms_code', methods=['GET', 'POST'])
def get_sms_code():
    # 获取参数: 图片id 输入的验证图片文本 手机号
    img_code_id = request.json.get('img_code_id')
    img_code = request.json.get('img_code')
    mobile = request.json.get('mobile')
    print(mobile,img_code,img_code_id)
    # 校验是否有参数
    if not all([img_code_id,img_code,mobile]):
        return jsonify(errno = RET.PARAMERR,errmsg = error_map[RET.PARAMERR])
    print('2')
    # 校验手机格式
    if not re.match(r'1[35678]\d{9}$',mobile):
        return jsonify(errno = RET.PARAMERR,errmsg= error_map[RET.PARAMERR])
    print('3')
    # 根据id读取数据库文本,校验图片是否正确.
    try:
        real_img_code = strict_redis.get('img_code_id' + img_code_id)
        print(4)
    except Exception as e:
        print(5)
        current_app.logger.error(e)
        return jsonify(errno = RET.PARAMERR,errmsg = error_map[RET.PARAMERR])
    print(6)
    if real_img_code != img_code.upper():
        print(real_img_code)
        print(img_code.upper())
        print(7)
        return jsonify(errno = RET.PARAMERR,errmsg = error_map[RET.PARAMERR])

    # 正确后 调用第三方内容发送短信
    rand_num = '%04d' % random.randint(0,9999)
    # 打印验证码,用于测试使用
    current_app.logger.info('短信验证码为:%s' % rand_num)
    # 发送短信
    response_code = CCP().send_template_sms(mobile,[rand_num,5],1)
    print(response_code)
    if response_code != 0:
        print(8)
        return jsonify(errno = RET.PARAMERR,errmsg = error_map[RET.PARAMERR])
    # 保存短信验证码
    try:
        strict_redis.set('sms_code_id'+mobile,rand_num,ex=600)
        print(9)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno = RET.DBERR,errormsg = error_map[RET.DBERR])
    # return json
    print(10)
    return jsonify(errno = RET.OK,errmsg = error_map[RET.OK])


