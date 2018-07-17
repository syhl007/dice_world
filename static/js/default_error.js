$.ajaxSetup({
        error: function (xhr) {
            console.log('error_gl');
            alert('登录状态已失效，返回登录页面');
            window.location.reload();
        }
    });