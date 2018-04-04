# -*- coding:utf-8 -*-
from datetime import datetime
from django.db import models
from django.contrib.contenttypes.models import ContentType


class PermissionManager(models.Manager):

    def get_content_type(self, obj):
        """
        Получение модели в которой хранится объект
        :param obj: Объект из модели
        :return: Модель
        """
        return ContentType.objects.get_for_model(obj)

    def get_for_model(self, obj):
        """
        Получение прав свяханных с объектом
        :param obj: Объект из модели
        :return: Квересет прав для данного объекта
        """
        return self.filter(content_type=self.get_content_type(obj))

    def for_query(self, approved=True, old_right=False, waiting=False):
        """
        Запрос на доступ:      approved = False; waiting= True, old_right = Не важно (юзер может снова попросить доступ)
        Старые права:          approved = False; old_right = True; waiting = Не важно (юзер может снова попросить доступ)
        Есть доступ:           approved = True; old_right = False; waiting=False
        :param approved: Переменная отвечает за доступ к редактированию
        :param old_right: Переменная овтечает за старые права
        :param waiting: Переменная отвечает за права которые ожидают подтверждения
        :return:
        """
        return self.select_related('content_type', 'user', 'last_admin').filter(approved=approved,
                                                                           old_right=old_right, waiting=waiting)

    def for_object(self, obj, approved=True, old_right=False, waiting=False):
        """
        Запрос на доступ:      approved = False; waiting= True, old_right = Не важно (юзер может снова попросить доступ)
        Старые права:          approved = False; old_right = True; waiting = Не важно (юзер может снова попросить доступ)
        Есть доступ:           approved = True; old_right = False; waiting=False
        :param obj: Объект из модели
        :param approved: Переменная отвечает за доступ к редактированию
        :param old_right: Переменная овтечает за старые права
        :param waiting: Переменная отвечает за права которые ожидают подтверждения
        :return: Возвращает квересет в зависимости значений переменных
        """
        return self.get_for_model(obj).select_related('content_type', 'user', 'last_admin').filter(object_id=obj.id,
                                                                                              approved=approved,
                                                                                              old_right=old_right,
                                                                                              waiting=waiting)

    def for_user(self, user):
        """
        :param user: Пользователь
        :return: Возвращает квересет всех прав пользователя
        """
        return self.select_related('content_type', 'user', 'last_admin').filter(user=user)

    def for_user_with_obj(self, user, obj):
        """
        :param user: Пользователь
        :param obj: Объект из модели
        :return: Возвращает квересет всех прав пользователя
        """
        perms = self.get_for_model(obj)
        return perms.select_related('content_type', 'user', 'last_admin').filter(user=user)\
            .values('codename', 'content_type', 'object_id')

    def for_approved(self, user):
        """
        :param user: Пользователь
        :return: Возвращает квересет разрешенных прав
        """
        return self.select_related('content_type').filter(user=user, approved=True, old_right=False, waiting=False)\
            .values('codename', 'content_type', 'object_id', 'date_requested')

    def for_waiting(self, user):
        """
        :param user: Пользователь
        :return: Возвращает квересет прав, которые ожидают подтверждения
        """
        return self.select_related('content_type').filter(user=user, approved=False, waiting=True)\
            .values('codename', 'content_type', 'object_id', 'date_requested')

    def for_old_right(self, user):
        """
        :param user: Пользователь
        :return: Возвращает квересет прав, которые были удалены
        """
        return self.select_related('content_type', 'user', 'last_admin').filter(user=user, approved=False, old_right=True)\
            .values('codename', 'content_type', 'object_id', 'date_change')

    def for_approved_is_true(self, user, last_admin):
        """
        Метод подтверждения прав
        :param user: пользователь
        :param last_admin: Админ, кто разрешил доступ
        :return: Метод ничего не возвращает
        """
        perms = self.filter(user=user, waiting=True)
        for right in perms:
            right.approve(last_admin)

    def delete_objects_permissions(self, user, obj):
        """
        Полное удаление права через объект
        :param user: Пользователь
        :param obj: Объект из модели
        :return:
        """
        perms = self.for_user_with_obj(user, obj)
        perms.delete()

    def delete_object(self, user, content_type, object_id):
        """
        Переносим право в список удаленных прав
        :param user: Пользователь
        :param content_type: id модели
        :param object_id: id объекта
        :return:
        """
        perms = self.filter(user=user, content_type=content_type, object_id=object_id)
        if perms:
            perm = perms.first()
            perm.approved = False
            perm.waiting = False
            perm.old_right = True
            perm.date_change = datetime.now()
            perm.save()

