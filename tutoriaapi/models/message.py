from datetime import datetime

from django.db import models
from django.utils import timezone as djtimezone

from . import user

class Message(models.Model):

    @classmethod
    def create(cls, send_user, receive_user, title, content, time=None, read=False):
        if time is None:
            time = datetime.now(tz=djtimezone.get_default_timezone())
        
        messgae = cls.objects.create(
            send_user = send_user,
            receive_user = receive_user,
            title = title,
            content = content,
            time = time,
            read = read
        )

        log = (
            '\n\n\n'
            '=================================================\n'
            'Sender: ' + (send_user.full_name if send_user is not None else 'System') + '\n'
            'Receiver: ' + (receive_user.full_name if receive_user is not None else 'System') + '\n'
            'Time: ' + str(time) + '\n'
            'Title: ' + title + '\n'
            '-------------------------------------------------\n'
            + content + '\n'
            '=================================================\n'
            '\n\n\n'
        )
        print(log)

        return messgae
        

    send_user = models.ForeignKey('User', on_delete=models.SET_NULL, related_name='send_message_set', related_query_name='send_message', null=True, blank=True)

    receive_user = models.ForeignKey('User', on_delete=models.SET_NULL, related_name='receive_message_set', related_query_name='receive_message', null=True)

    title = models.CharField(max_length=100)
    content = models.TextField()

    time = models.DateTimeField()

    read = models.BooleanField(default=False)

    def __str__(self):
        send_user_name = self.send_user.full_name if self.send_user is not None else 'System'
        return 'From "{0}" to "{1}": {2}'.format(send_user_name, self.receive_user.full_name, self.title)
    