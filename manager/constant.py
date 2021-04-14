
class GROUP:
    RECEPTIONIST = 1
    STUDENT_CARE = 2
    CENTRE_ADMIN = 3
    TEACHER = 4
    STUDENT = 5
    BUSINESS = 6

CENTRE_COLORS = ["#6495ED", "#9FE2BF", "#40E0D0", "#CCCCFF", "#CD5C5C", "#E9967A", "#FF7F50", "#DE3163"]

CHOICE_EMPTY = [('', '---------')]

STUDY_SHIFT_CHOICES = [(1, 'Ca 1 (19h-21h)'), (2, 'Ca 2 (19h30-21h30)'),
                       (3, 'Ca 3 (18h-20h)'), (4, 'Ca 4 (18h30-21h30)'),
                       (5, 'Ca 5 (21h-23h)'), (6, 'Ca 6 (20h-22h)')]


COURSES_INFO = {
    'Python Core': {'name': 'Python Core', 'des': 'Nắm được tối thiểu 85% kiến thức cơ bản'},
    'Java Core': {'name': 'Java Core', 'des': 'Nắm được tối thiểu 85% kiến thức cơ bản'},
    'TO1': {'name': 'TO1', 'des': 'TOEIC 450'},
    'TO2': {'name': 'TO2', 'des': 'TOEIC 750'},
    'IE1': {'name': 'IE1', 'des': 'IELTS 3.5'},
    'IE2': {'name': 'IE2', 'des': 'IELTS 5.0'},
    'IE3': {'name': 'IE3', 'des': 'IELTS 6.5'},
}
