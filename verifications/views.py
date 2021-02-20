import json
import random

from django.http import HttpResponse, JsonResponse

# Create your views here.
import logging
from django_redis import get_redis_connection
from django.views import View

from user.models import Users
from utils.captcha.captcha import captcha
from utils.res_code import res_json, Code
from utils.yuntongxun.sms import CCP

logger = logging.getLogger('django')

class ImageCode(View):
    def get(self, request, image_code_id):
        text, image = captcha.generate_captcha()
        con_redis = get_redis_connection(alias='verify_codes')
        img_key = "img_{}".format(image_code_id).encode('utf-8')
        con_redis.setex(img_key, 300, text)
        logger.info("Image code: {}".format(text))
        return HttpResponse(content=image, content_type="image/jpg")


class CheckUsernameView(View):
    def get(self, request, username):
        data = {
            'username': username,
            'count': Users.objects.filter(username=username).count()
        }
        return JsonResponse(data=data)


class CheckMobilView(View):
    """
    Check whether the user exists
    GET mobiles/(?P<mobile>1[3-9]\d{9})/
    """
    def get(self, request, mobile):
        data = {
            'mobile': mobile,
            'count': Users.objects.filter(mobile=mobile).count()
        }
        return JsonResponse({'data':data})


class SMSCodeView(View):
    """短信验证码"""

    def post(self, request):
        """
        :param reqeust: 请求对象
        :param mobile: 手机号
        :return: JSON
        """
        # 接收参数
        json_str = request.body
        dict_data = json.loads(json_str)

        image_code_client = dict_data.get('text')
        uuid = dict_data.get('image_code_id')
        mobile = dict_data.get('mobile')
        # 校验参数
        if not all([image_code_client, uuid, mobile]):
            return res_json(errno=Code.PARAMERR, errmsg='参数错误')
        # 创建连接到redis的对象
        redis_conn = get_redis_connection('verify_codes')
        # 提取数据库的图形验证码
        image_code_server = redis_conn.get('img_%s' % uuid)
        if image_code_server is None:
            # 图形验证码过期或者不存在
            return res_json(errno=Code.PARAMERR, errmsg='参数错误')
        # 删除图形验证码，避免恶意测试图形验证码
        try:
            redis_conn.delete('img_%s' % uuid)
        except Exception as e:
            logger.error(e)
        # 对比图形验证码
        image_code_server = image_code_server.decode()  # bytes转字符串
        if image_code_client.lower() != image_code_server.lower():  # 转小写后比较
            return res_json(errno=Code.PARAMERR, errmsg='输入图形验证码有误')

        # 生成短信验证码：生成6位数验证码
        sms_code = '%06d' % random.randint(0, 999999)
        logger.info(sms_code)

        # 限定频繁发送验证码
        send_flag = redis_conn.get('send_flag_%s' % mobile)
        if send_flag:
            return res_json(errno=Code.DATAEXIST, errmsg='发送短信过于频繁')

        redis_conn.setex('sms_%s' % mobile, 300, sms_code)
        # 重新写入send_flag
        redis_conn.setex('send_flag_%s' % mobile, 60, 1)
        # 执行请求
        # 发送短信
        logger.info('短信验证码: {}'.format(sms_code))
        logging.info('发送短信正常[mobile:%s sms_num:%s]' % (mobile, sms_code))

        # 发送短信验证码
        ccp = CCP()
        ccp.send_template_sms(mobile, [sms_code, 5], 1)
        # 响应结果
        return res_json(errmsg='短信验证码发送成功')