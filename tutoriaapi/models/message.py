from django.db import models

from . import user

class Message(models.Model):

    @classmethod
    def create(cls, send_user, receive_user, title, content, read=False):
        return cls.objects.create(
            send_user = send_user,
            receive_user = receive_user,
            title = title,
            content = content,
            read = read
        )
        

    send_user = models.ForeignKey('User', on_delete=models.SET_NULL, related_name='send_message_set', related_query_name='send_message', null=True)

    receive_user = models.ForeignKey('User', on_delete=models.SET_NULL, related_name='receive_message_set', related_query_name='receive_message', null=True)

    title = models.CharField(max_length=100)
    content = models.TextField()

    read = models.BooleanField(default=False)

    def __str__(self):
        return 'From "{0}" to "{1}": {2}'.format(self.send_user.get_full_name(), self.receive_user.get_full_name(), self.title)
    