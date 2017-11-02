from django.test import TestCase

from ..models.userprofile import UserProfile
from ..models.roles import StudentRole, TutorRole
from ..models.university import University
from ..models.course_code import CourseCode

from datetime import datetime, timedelta, timezone

class BlackenOutSessionTest(TestCase):


    def testBlackenSessionFields(self):
        username = 'un'
        password = 'pass'
        email = 'a@a.com'
        givenName = 'alvin'
        familyName = 'leung'
        phoneNumber = '12345678'
        avatar = ''

        up = UserProfile.create(
            username = username,
            password = password,
            email = email,
            givenName = givenName,
            familyName = familyName,
            phoneNumber = phoneNumber,
            avatar = avatar
        )
        tr = up.addConcreteRole(
            TutorRole,
            type=TutorRole.TYPE_PRIVATE,
            activated=True,
            university=University.create('HKU'),
            courseCode=CourseCode.create('COMP2049')
        )

        sdt = datetime.now(timezone.utc)
        edt = sdt + timedelta(hours=1)
        tr.addBlackenOutSession(sdt, edt)

        session = up.getConcreteRole(TutorRole).blackenOutSessions[0]
        self.assertEqual((session.startDate-sdt).total_seconds(), 0)
        self.assertEqual((session.endDate-edt).total_seconds(), 0)
        self.assertEqual(session.userProfiles[0], up)

