from django.test import TestCase

from ..models.userprofile import UserProfile

class UserProfileTest(TestCase):

    def testFields(self):
        username = 'un'
        password = 'pass'
        email = 'a@a.com'
        givenName = 'alvin'
        familyName = 'leung'
        phoneNumber = '12345678'
        avatar = ''
        user = UserProfile.create(
            username = username,
            password = password,
            email = email,
            givenName = givenName,
            familyName = familyName,
            phoneNumber = phoneNumber,
            avatar = avatar
        )

        up = UserProfile.objects.get(user__username=username)
        
        self.assertEqual(up.username, username)
        self.assertEqual(up.email, email)
        self.assertEqual(up.givenName, givenName)
        self.assertEqual(up.familyName, familyName)
        self.assertEqual(up.phoneNumber, phoneNumber)
        self.assertEqual(up.avatar, avatar)
