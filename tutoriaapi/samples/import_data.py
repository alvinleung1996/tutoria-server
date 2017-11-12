from decimal import Decimal

from ..models import *

from . import avatars

# Create super user dev0
dev0User = User.create(
    username = 'dev0',
    password = 'dev0dev0',
    email = 'dev0@wecode.com',
    given_name = 'Robot 0',
    family_name = 'WeCode',
    phone_number = '00000000',
    avatar = ''
)
dev0User.is_staff = True
dev0User.is_superuser = True
dev0User.save()

# Create university
hkuUniversity = University.create(
    name = 'HKU'
)

# Create Course code
javaCourseCode = CourseCode.create(
    university = hkuUniversity,
    code = 'COMP2396'
)

seCourseCode = CourseCode.create(
    university = hkuUniversity,
    code = 'COMP3297'
)

dbCourseCode = CourseCode.create(
    university = hkuUniversity,
    code = 'COMP3278'
)

introductionCourseCode = CourseCode.create(
    university = hkuUniversity,
    code = 'ENGG1202'
)

programmingCourseCode = CourseCode.create(
    university = hkuUniversity,
    code = 'ENGG1111'
)

# Create sample users
companyUser = User.create(
    username = 'company',
    password = 'companycompany',
    email = 'admin@mytutors.com',
    given_name = 'MyTutors',
    family_name = '',
    phone_number = '18503999',
    avatar = '',
)
companyUser.add_role(Company)

alvinUser = User.create(
    username = 'alvin',
    password = 'alvinalvin',
    email = 'alvin@wecode.com',
    given_name = 'Alvin',
    family_name = 'Leung',
    phone_number = '12345678',
    avatar = avatars.alvin,
    balance = Decimal('100')
)
alvinUser.add_role(Student)

georgeUser = User.create(
    username = 'george',
    password = 'georgegeorge',
    email = 'george@cs.hku.com',
    given_name = 'George',
    family_name = 'Mitcheson',
    phone_number = '28597068',
    avatar = avatars.george
)
georgeUser.add_role(Tutor,
    type = Tutor.TYPE_CONTRACTED,
    university = hkuUniversity,
    course_codes = [seCourseCode, programmingCourseCode],
    biography = 'Before joining HKU, George accumulated many years of experience in large-scale software engineering and in R&D for real-time systems. He has headed or contributed to development of a wide range of systems spanning fields such as scientific computation, telecommunications, database management systems, control systems and autonomous robotics. This work was carried out principally in Europe and the USA. Between the two he taught for several years at the University of Puerto Rico.',
    subject_tags = ['SE', 'RC']
)

kitUser = User.create(
    username = 'kit',
    password = 'kitkitkit',
    email = 'kit@cs.hku.com',
    given_name = 'CKit',
    family_name = 'Chui',
    phone_number = '28578452',
    avatar = avatars.kit
)
kitUser.add_role(Tutor,
    type = Tutor.TYPE_PRIVATE,
    university = hkuUniversity,
    course_codes = [dbCourseCode, introductionCourseCode],
    biography = 'Dr. Chui received his Ph.D. in Computer Science from the University of Hong Kong. He was selected for the University Outstanding Teaching Award (Individual Award) of the University of Hong Kong in 2015-16. He was selected for the Faculty Outstanding Teaching Award (Individual Award) of the Faculty of Engineering in 2012-13. He has also received the Teaching Excellence Award in the Department of Computer Science in 2011-12, 2012-13, 2013-14 and 2014-15 and the Best Tutor Award in 2007-08, 2008-09 and 2010-11.',
    hourly_rate = Decimal('10'),
    subject_tags = ['DM', 'CB']
)

jollyUser = User.create(
    username = 'jolly',
    password = 'jollyjolly',
    email = 'jolly@cs.hku.com',
    given_name = 'Jolly',
    family_name = 'Chan',
    phone_number = '98765432',
    avatar = avatars.jolly
)
jollyUser.add_role(Student)
jollyUser.add_role(Tutor,
    type = Tutor.TYPE_PRIVATE,
    university = hkuUniversity,
    course_codes = [javaCourseCode, programmingCourseCode],
    biography = 'I am a post-graduate student studying CS',
    hourly_rate = Decimal('30'),
    subject_tags = ['JAVA', 'C++']
)
