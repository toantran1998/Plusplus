
class GROUP:
    RECEPTIONIST = 1
    STUDENT_CARE = 2
    CENTRE_ADMIN = 3
    TEACHER = 4
    STUDENT = 5
    BUSINESS = 6

CENTRE_COLORS = ["#6495ED", "#9FE2BF", "#40E0D0", "#CCCCFF", "#CD5C5C", "#E9967A", "#FF7F50", "#DE3163"]

CHOICE_EMPTY = [('', '---------')]

STUDY_SHIFT_CHOICES = [(1, 'Ca 1 (9h-10h30)'), (2, 'Ca 2 (14h-15h30)'),
                       (3, 'Ca 3 (18h-19h30)'), (4, 'Ca 4 (19h30-21h)')]


COURSES_INFO = {
    'BBST': {'name': 'New BBST', 'des': 'Nắm được tối thiểu 85% kiến thức phát âm và ngữ pháp cơ bản'},
    'GT': {'name': 'Giao tiếp', 'des': 'Có thể trao đổi về các chủ đề quen thuộc với người nước ngoài'},
    'TO1': {'name': 'TO1', 'des': 'TOEIC 450'},
    'TO2': {'name': 'TO2', 'des': 'TOEIC 750'},
    'IE1': {'name': 'IE1', 'des': 'IELTS 3.5'},
    'IE2': {'name': 'IE2', 'des': 'IELTS 5.0'},
    'IE3': {'name': 'IE3', 'des': 'IELTS 6.5'},
}
