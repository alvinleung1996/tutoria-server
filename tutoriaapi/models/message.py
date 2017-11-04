from django.db import models

from . import user

class Message(models.Model):

    @classmethod
    def create(cls, send_user, receive_user, content, read=False):
        return cls.objects.create(
            send_user = send_user,
            receive_user = receive_user,
            content = content,
            read = False
        )

    send_user = models.ForeignKey('User', on_delete=models.SET_NULL, related_name='send_message_set', related_query_name='send_message', null=True)

    receive_user = models.ForeignKey('User', on_delete=models.SET_NULL, related_name='receive_message_set', related_query_name='receive_message', null=True)

    content = models.TextField()

    read = models.BooleanField(default=False)

    def __str__(self):
        return 'From "{0}" to "{1}"'.format(self.send_user.get_full_name(), self.receive_user.get_full_name())
    