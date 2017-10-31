from django.test import TestCase

from ..models.userprofile import UserProfile
from ..models.roles import StudentRole, TutorRole
from ..models.university import University
from ..models.coursecode import CourseCode

class RolesTest(TestCase):

    def testStudentRoleFields(self):
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
        
        up.addConcreteRole(StudentRole)

        self.assertIsNotNone(up.getConcreteRole(StudentRole))


    def testTutorRoleFields(self):
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

        u = University.create('HKU')
        cc = CourseCode.create('COMP2049')
        sts = ['tag0', 'tag1']
        
        up.addConcreteRole(
            TutorRole,
            type=TutorRole.TYPE_PRIVATE,
            activated=True,
            subjectTags=sts,
            university=u,
            courseCode=cc
        )

        self.assertIsNotNone(up.getConcreteRole(TutorRole))
        
        tr = up.getConcreteRole(TutorRole)

        self.assertEqual(tr.type, TutorRole.TYPE_PRIVATE)
        self.assertTrue(tr.activated)
        self.assertEqual(tr.university.name, u.name)
        self.assertEqual(tr.courseCode.code, cc.code)
        self.assertListEqual(list(map(lambda t: t.tag, tr.subjectTags)), sts)
