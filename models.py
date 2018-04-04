# -*- coding:utf-8 -*-
from datetime import datetime

from django.db import models
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext as _

from apps.accounts.models import User
from apps.permission.managers import PermissionManager


class SecurityPermission(models.Model):
    codename = models.CharField(_('codename'), max_length=100)
    short_name = models.CharField(_(u'Название модуля'), max_length=100)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    user = models.ForeignKey(User, null=True, blank=True, related_name='permissions')
    last_admin = models.ForeignKey(User, null=True, blank=True, related_name='approved_permissions')

    approved = models.BooleanField(_(u'Подтверждено'), default=False)
    waiting = models.BooleanField(_(u'Ожидание подтверждения'), default=False)
    old_right = models.BooleanField(_(u'Удалено'), default=False)

    date_requested = models.DateTimeField(_(u'Дата создания'), default=datetime.now)
    date_change = models.DateTimeField(_(u'Дата последненго изменения админом'), blank=True, null=True)
    # date_approved = models.DateTimeField(_(u'Дата последненго разрешенного доступа'), blank=True, null=True)

    objects = PermissionManager()

    def __unicode__(self):
        return u'%s' % self.codename

    class Meta:
        verbose_name = u'Права доступа'
        verbose_name_plural = u'Права доступа'
        # unique_together = ("codename", "object_id", "content_type", "user", "group")

    def save(self, *args, **kwargs):
        try:
            """ 
            Вызываем метод, которое возвращает полное название - (Раздел + к чему предоставляется доступ) 
            Метод get_name_for_right доступен от класса apps.constructor.models.BaseModel
            """
            self.codename = self.content_object.get_name_for_right()
        except:
            self.codename = self.content_object or u'не найдено'
        try:
            self.short_name = self.content_object.get_short_name()
        except:
            self.short_name = u'не найдено'
        super(SecurityPermission, self).save(*args, **kwargs)

    def approve(self, admin):
        """
        Метод подтверждения прав
        :param creator: Админ, кто разрешил доступ
        :return: Вызов функции сохранения
        """
        self.approved = True
        self.waiting = False
        self.old_right = False
        self.last_admin = admin
        self.date_change = datetime.now()
        self.save()

    def get_user_full_name(self):
        """ ФИО пользователя """
        if self.user:
            return self.user.get_full_name()
        return u'Пользователь не найден'
    get_user_full_name.short_description = u'Пользователь'
    get_user_full_name.allow_tags = True
