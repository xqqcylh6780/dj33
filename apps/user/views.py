import json
import re

from django.contrib import auth
from django.contrib.auth import login, logout
from django.http import HttpResponseForbidden, HttpResponse
from django.shortcuts import render, redirect

# Create your views here.
from django.urls import reverse
from django.views import View
from django_redis import get_redis_connection

from user.forms import LoginForm
from user.models import Users
from utils.res_code import res_json, Code, error_map


class LoginView(View):
    def get(self,request):
        return render(request, 'users/login.html')

    def post(self, request):
        js_str = request.body
        if not js_str:
            return res_json(errno=Code.PARAMERR, errmsg=error_map[Code.PARAMERR])
        data_dict = json.loads(js_str)
        form = LoginForm(data=data_dict, request=request)
        if form.is_valid():
            # 表单验证成工处理
            return res_json(errno=Code.OK)
        else:
            # 表单验证失败处理
            msg_list = []
            for i in form.errors.get_json_data().values():
                msg_list.append(i[0].get('message'))
            msg_str = '/'.join(msg_list)
            return res_json(errno=Code.PARAMERR, errmsg=msg_str)


# 在users目录下的views.py文件中定义如下类视图：
class RegisterView(View):
    """
    username
    password
    password_ret
    mobile
    sms_code
    """

    def get(self, request):
        return render(request, 'users/register.html')

    def post(self, request):
        """
         "username": sUsername,
        "password": sPassword,
         "password_repeat": sPasswordRepeat,
         "mobile": sMobile,
         "sms_code": sSmsCode
        :param request:
        :return:
        """
        data_dict = request.body
        data_dict = json.loads(data_dict)

        username = data_dict.get('username')
        password = data_dict.get('password')
        password2 = data_dict.get('password_repeat')
        mobile = data_dict.get('mobile')
        sms_code = data_dict.get('sms_code')

        # 1.非空
        if not all([username, password, password2, mobile, sms_code]):
            return HttpResponseForbidden('填写数据不完整')
        # 2.用户名
        if not re.match('^[\u4e00-\u9fa5\w]{5,20}$', username):
            return HttpResponseForbidden('用户名为5-20个字符')
        if Users.objects.filter(username=username).count() > 0:
            return HttpResponseForbidden('用户名已经存在')
        # 密码
        if not re.match('^[0-9A-Za-z]{6,20}$', password):
            return HttpResponseForbidden('密码为6-20个字符')
        # 确认密码
        if password != password2:
            return HttpResponseForbidden('两个密码不一致')
        # 手机号
        if not re.match('^1[3456789]\d{9}$', mobile):
            return HttpResponseForbidden('手机号错误')
        if Users.objects.filter(mobile=mobile).count() > 0:
            return HttpResponseForbidden('手机号存在')
        # 短信验证码
        # 1.读取redis中的短信验证码
        redis_cli = get_redis_connection('verify_codes')
        sms_code_redis = redis_cli.get('sms_{}'.format(mobile))
        # 2.判断是否过期
        if sms_code_redis is None:
            return HttpResponseForbidden('短信验证码已经过期')
        # 3.删除短信验证码，不可以使用第二次
        redis_cli.delete('sms_' + mobile)
        redis_cli.delete('send_flag_' + mobile)
        # 4.判断是否正确
        if sms_code_redis.decode() != sms_code:
            return HttpResponseForbidden('短信验证码错误')
        # 处理
        # 1.创建用户对象
        user = Users.objects.create_user(
            username=username,
            password=password,
            mobile=mobile
        )
        # 2.状态保持
        login(request, user)
        # 向cookie中写用户名，用于客户端显示
        response = res_json(errmsg='恭喜你，注册成功！')
        return response


class LogoutView(View):
    """
    """
    def get(self, request):
        logout(request)
        return redirect(reverse("user:login"))
