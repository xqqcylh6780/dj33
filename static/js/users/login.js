$(function () {
    let $login = $('.form-contain');

    $login.submit(function (e) {
        e.preventDefault();
        let sUsername = $('input[name=telephone]').val();

        if(sUsername === ''){
            message.showError('用户名不能为空！')
            return
        }

        if (!(/^[\u4e00-\u9fa5\w]{5,20}$/.test(sUsername))){
            message.showError('请输入5-20位字符的用户名')
            return
        }
        // 密码验证

        let sPassword = $('input[name=password]').val();

        if(!sPassword){
            message.showError('密码不能为空!')
            return
        }

        // 验证用户名  6
        if(sPassword.length<6 || sPassword.length>20) {
            message.showError('密码长度需要在6-20之间');
            return
        }

        let status = $("input[type='checkbox']").is(':checked');

        // g构造参数
        let sData ={
            'user_account' : sUsername,
            'password':sPassword,
            'remember':status
        };


        $.ajax({
            url:'/user/login/',
            type:'POST',
            data:JSON.stringify(sData),
            headers: {
              // 根据后端开启的CSRFProtect保护，cookie字段名固定为X-CSRFToken
        "X-CSRFToken": getCookie("csrftoken")
       },
            contentType:'application/json; charset=utf-8',
            dataType:'json',
        })

            .done(function (res) {
                if(res.errno==='0'){
                    message.showSuccess('贵宾，恭喜您登录成功！');
                    setTimeout(function () {
                        window.location.href = '/news/';
                    },1500)
                }else {
                    message.showError(res.errmsg)
                }

            })
            .fail(function () {
                message.showError('服务器超时，请重试！')
            })

    })
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
