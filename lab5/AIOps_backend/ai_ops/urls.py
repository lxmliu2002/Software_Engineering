"""ai_ops URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# 导入所需模块
from django.urls import path
from app import views_auth, views_user, views_file, views_log_prompt, views_llm, views_disk
from django.views.generic import TemplateView

# 注册路由
urlpatterns = [
    path('', TemplateView.as_view(template_name='index.html')),

    # 用户管理模块--miseruser
    # 增加用户
    path("miseruser/addUser", views_user.addUser),
    # 删除用户
    path("miseruser/deleteUser", views_user.deleteUser),
    # 更改用户
    path("miseruser/updateUser", views_user.updateUser),
    # 获取用户信息清单
    path("miseruser/getUserlist", views_user.getUserlist),
    # 获取单个用户信息
    path("miseruser/getUser/<theme>", views_user.getUser, name='userid'),


    # 登录注册模块--miserauth
    # 注册功能
    path("miserauth/register", views_auth.userRegister),
    # 登录功能
    path("miserauth/login", views_auth.userLogin),
    # 获取当前登录信息
    path("miserauth/getloginUser", views_auth.getLoginUser),
    # 退出登录
    path("miserauth/loginout", views_auth.loginOut),

    
    # 文件上传
    path("file/upload", views_file.upload_file),
    
    # 日志异常检测
    path("log/detection", views_log_prompt.log_prompt),
    
    # 大语言模型
    path("model/qianwen", views_llm.qwCompletion),
    
    # 磁盘测试
    path("disk/train/daysAfter", views_disk.train_days_after),
    path("disk/predict/daysAfter", views_disk.predict_days_after),
    path("disk/train/detect", views_disk.train_fault_detect),
    path("disk/predict/detect", views_disk.fault_detect)
]
