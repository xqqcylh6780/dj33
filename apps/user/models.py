from django.db import models

# Create your models here.


from django.contrib.auth.models import AbstractUser, UserManager as _UserManager

class UserManager(_UserManager):
    def create_superuser(self, username, email=None, password=None, **extra_fields):
        super(UserManager, self).create_superuser(username=username, password=password,
                                                  email=email, **extra_fields)


class Users(AbstractUser):
    objects = UserManager()
    REQUIRED_FIELDS = ['mobile']
    mobile = models.CharField(max_length=11, unique=True, verbose_name='手机号',
                              error_messages={
                                  'unique': '手机号已被注册'}
                              )
    email_active = models.BooleanField(default=False, verbose_name='油箱')
    class Meta:
        db_table = 'tb_users'
        verbose_name = '用户'
        verbose_name_plural = verbose_name
    def __str__(self):
        return self.username
