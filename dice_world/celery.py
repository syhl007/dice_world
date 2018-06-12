# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import os

from celery import Celery

# 设置环境变量
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dice_world.settings')

# 注册Celery的APP
app = Celery('dice_world')
# 绑定配置文件
app.config_from_object('django.conf:settings', namespace='CELERY')

# 自动发现各个app下的tasks.py文件
app.autodiscover_tasks()

