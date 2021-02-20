$(()=> {
    let $img = $(".form-item .captcha-graph-img img");   // 获取图像
    let $username = $('#user_name'); // 获取用户名
    let $mobile = $('#mobile');  // 选择id为mobile的网页元素，需要定义一个id为mobile
    let sImageCodeId = '';   //默认为空
       // 校验功能
    // 定义一些状态变量
    let isUsernameReady = false,
        isPasswordReady = false,
        isMobileReady = false;
        send_flag = true;    // 短信标记

    genreate();     // 生成验证码
    $img.click(genreate);   // 点击触发新的
    function genreate() {
        sImageCodeId = generateUUID();
        let imageCodeUrl = '/verifications/image_code/' + sImageCodeId + '/';
        // let imageCodeUrl = '/image_code/' +  Math.floor(Math.random(5));
        $img.attr('src', imageCodeUrl)
    }

     // 生成图片UUID验证码
  function generateUUID() {
    let d = new Date().getTime();
    if (window.performance && typeof window.performance.now === "function") {
        d += performance.now(); //use high-precision timer if available
    }
    let uuid = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
        let r = (d + Math.random() * 16) % 16 | 0;
        d = Math.floor(d / 16);
        return (c == 'x' ? r : (r & 0x3 | 0x8)).toString(16);
    });
    return uuid;
  }

    // 2、用户名验证逻辑
    // blur,触发失去焦点事件
  $username.blur(fn_check_username);

      // 3、手机号验证逻辑
  // 手机号校验,光标离开手机号输入框就校验
  $mobile.blur(fn_check_mobile);

     // 判断用户名是否已经注册
  function fn_check_username() {
      // 校验用户名
        isUsernameReady = false;

    let sUsername = $username.val();  // 获取用户名字符串
    if (sUsername === "") {
      message.showError('请输入您的用户名');
      return
    }
    if (!(/^[\u4e00-\u9fa5\w]{5,20}$/).test(sUsername)) {
    // if (!(/^\w{5,20}$/).test(sUsername)) {
      message.showError('请输入5-20个字符的用户名');
      return
    }
    // 发送ajax请求，去后端查询用户名是否存在
    $.ajax({
      url: '/verifications/username/' + sUsername + '/',
      type: 'GET',
      dataType: 'json',
    })
        // 回调函数 done：成功时执行，异常时不会执行。
      .done(function (res) {
          console.log(res);
        if (res["count"] != 0) {
          message.showError( '已注册，请重新输入！')

        } else {
          message.showInfo(res['username'] + '能正常使用！');
            isUsernameReady = true
        }
      })
      //  没有获取到数据， 可以捕获网络错误，fail：失败时执行
      .fail(function () {
        message.showError('服务器超时，请重试！');
      });
  }


   // 判断手机号是否注册
  function fn_check_mobile(){
      isMobileReady = false;
      let sMobile = $mobile.val();  // 获取用户输入的手机号码字符串
      if (sMobile === "") {
          message.showError('手机号不能为空！');
          return
      }
     if (!(/^1[345789]\d{9}$/).test(sMobile)) {
         message.showError('手机号码格式不正确，请重新输入！');
         return
     }
     $.ajax({
         url: '/verifications/mobiles/' + sMobile + '/',
         type: 'GET',
         dataType: 'json',
         async: false
     })
         .done(function (res) {
        if (res.data.count !== 0) {
          message.showError(res.data.mobile + '已注册，请重新输入！');
        } else {
          message.showSuccess(res.data.mobile + '能正常使用！');
          isMobileReady = true;
        }
      })
      .fail(function () {
        message.showError('服务器超时，请重试！');
      });
  }


   // 4、发送短信验证码逻辑
  let $smsCodeBtn = $('.form-item .sms-captcha');  // 获取短信验证码按钮元素，需要定义一个id为input_smscode
let $imgCodeText = $('#input_captcha');  // 获取用户输入的图片验证码元素，需要定义一个id为input_captcha

$smsCodeBtn.click(function () {
    // 判断手机号是否输入
    if (send_flag) {
        send_flag = false;
        // 判断手机号码是否准备好
        if (!isMobileReady) {
            fn_check_mobile();
            return
        }
    let text = $imgCodeText.val()
    if (!text) {
        message.showError('请填写验证码！');
        return
    }

    if (!sImageCodeId) {
      message.showError('图片UUID为空');
      return
    }     // 正常
    let SdataParams = {
      "mobile": $mobile.val(),   // 获取用户输入的手机号
      "text": text,   // 获取用户输入的图片验证码文本
      "image_code_id": sImageCodeId  // 获取图片UUID
    };
    // 向后端发送请求
    $.ajax({
      // 请求地址
      url: "/verifications/sms_code/",
      // 请求方式
      type: "POST",
      // 向后端发送csrf token
      headers: {
                // 根据后端开启的CSRFProtect保护，cookie字段名固定为X-CSRFToken
                "X-CSRFToken": getCookie("csrftoken")
      },

      data: JSON.stringify(SdataParams),
      // data: JSON.stringify(SdataParams),
      // 请求内容的数据类型（前端发给后端的格式）
      contentType: "application/json; charset=utf-8",
      // 响应数据的格式（后端返回给前端的格式）
      dataType: "json",
    })

      .done(function (res) {
          console.log(res);

        if (res.errno === "0") {
          // 倒计时60秒，60秒后允许用户再次点击发送短信验证码的按钮
           message.showSuccess('短信验证码发送成功');
          let num = 60;
          // 设置一个计时器
          let t = setInterval(function () {
            if (num === 1) {
              // 如果计时器到最后, 清除计时器对象
              clearInterval(t);
              // 将点击获取验证码的按钮展示的文本恢复成原始文本
              $smsCodeBtn.html("获取验证码");
              send_flag = true;
            } else {
              num -= 1;
              // 展示倒计时信息
              $smsCodeBtn.html(num + "秒");
            }
          }, 1000);
        }
        else {
          message.showError(res.errmsg);
          send_flag = true;
        }
      })

      .fail(function(){
        message.showError('服务器超时，请重试！');
      });
    }

})

     // 5、注册逻辑
    let $register = $('.form-contain');  // 获取注册表单元素

    $register.submit(function (e) {
    // 阻止默认提交操作
    e.preventDefault();

    // 获取用户输入的内容
    let sUsername = $username.val();  // 获取用户输入的用户名字符串
        message.showSuccess(sUsername);

    let sPassword = $("input[name=password]").val();
    console.log(sPassword);

    let sPasswordRepeat = $("input[name=password_repeat]").val();
    console.log(sPassword)

    let sMobile = $mobile.val();  // 获取用户输入的手机号码字符串
    let sSmsCode = $("input[name=sms_captcha]").val();

    // 判断用户名是否已注册
    if (!isUsernameReady) {
        fn_check_username();
      return
    }

    // 判断手机号是否为空，是否已注册
    if (!isMobileReady) {
        fn_check_mobile();
      return
    }



    // 判断用户输入的密码是否为空
    if ((!sPassword) || (!sPasswordRepeat)) {
      message.showError('密码或确认密码不能为空');
      return
    }

    // const reg = /^(?![^A-Za-z]+$)(?![^0-9]+$)[\x21-x7e]{6,18}$/
    // 以首字母开头，必须包含数字的6-18位
    // 判断用户输入的密码和确认密码长度是否为6-20位
      if (!(/^[0-9A-Za-z]{6,20}$/).test(sPassword)){
         message.showError('请输入6到20位密码');
          return
      }


    // 判断用户输入的密码和确认密码是否一致
    if (sPassword !== sPasswordRepeat) {
      message.showError('密码和确认密码不一致');
      return
    }



    // 判断用户输入的短信验证码是否为6位数字
    if (!(/^\d{6}$/).test(sSmsCode)) {
      message.showError('短信验证码格式不正确，必须为6位数字！');
      return
    }

    // 发起注册请求
    // 1、创建请求参数
    let SdataParams = {
      "username": sUsername,
      "password": sPassword,
      "password_repeat": sPasswordRepeat,
      "mobile": sMobile,
      "sms_code": sSmsCode
    };

      alert(SdataParams)
    // 2、创建ajax请求
    $.ajax({
      // 请求地址
      url: "/user/register/",  // url尾部需要添加/
      // 请求方式
      type: "POST",
      data: JSON.stringify(SdataParams),
   headers: {
              // 根据后端开启的CSRFProtect保护，cookie字段名固定为X-CSRFToken
       "X-CSRFToken": getCookie("csrftoken")
       },
      // 请求内容的数据类型（前端发给后端的格式）
      contentType: "application/json; charset=utf-8",
      // 响应数据的格式（后端返回给前端的格式）
      dataType: "json",

    })
      .done(function (res) {
        if (res.errno === "0") {
          // 注册成功
          message.showSuccess('恭喜你，注册成功！');
           setTimeout(() => {
            // 注册成功之后重定向到主页
            window.location.href = '/user/login/';
          }, 1500)
        } else {
          // 注册失败，打印错误信息
          message.showError(res.errmsg);
        }
      })
      .fail(function(){
        message.showError('服务器超时，请重试！');
      });

  });

  // get cookie using jQuery
  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      let cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
        let cookie = jQuery.trim(cookies[i]);
        // Does this cookie string begin with the name we want?
        if (cookie.substring(0, name.length + 1) === (name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }
});
