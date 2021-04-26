
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
    'JVCOOL': {'name':'Java Core', 'des': 'Nắm được tối thiểu 85% kiến thức lập trình cơ bản, có thể lập trình desktop, có thể xin thực tập tại các công ty phần mềm'},
    'PYCOOL': {'name':'Python Core', 'des': 'Nắm được tối thiểu 85% kiến thức lập trình cơ bản, có thể lập trình desktop, có thể xin thực tập tại các công ty phần mềm'},
    'FECOOL': {'name':'Front-end Cơ Bản', 'des': 'Đủ khả năng tự thiết kế giao diện trang web hoàn chỉnh.Sử dụng thành thạo các công nghệ thiết kế giao diện web: HTML 5, CSS3, các CSS Framework & các thư viện JavaScript mới nhất hiện nay'},
    'JVBAOL': {'name':'Lập trình Java Backend', 'des': 'Nắm được kiến thức Java cơ bản cũng như kiến thức về lập trình hướng đối tượng (OOP). Có thể viết được các chương trình java cơ bản như các ứng dụng Console App, Desktop App. Có thể xin làm java fresher hoặc thực tập tại các công ty phần mềm. Có khả năng phân tích dự án, phân tích hướng đối tượng, đặc tả UML – UseCase, ước lượng dự án trong thực tế. Bạn sẽ được đào tạo để trở thành một lập trình Back End chuyên nghiệp'},
    'JVFLOL': {'name':'Lập trình Java Full- stack', 'des': 'Bạn sẽ được cam kết đầu ra hoàn toàn như khóa Back end, thêm vào đó bạn sẽ được cam kết: Có đủ khả năng để thiết kế giao diện Web hoàn chỉnh. Đủ khả năng ứng tuyển lập trình Full Stack tại các công ty lập trình.'},
    'PYWEOL': {'name':'Python Fullstack Web', 'des':'Xây dựng và triển khai được các dự án thực tế liên quan đến Python Web chuyên sâu.Xây dựng và triển khai được các dự án thực tế về CRM, hệ thống học trực tuyến Elearning… Tham gia vào bất kì công ty tuyển dụng lập trình Web Back End Developer, đặc biệt là Python Web với Flask, Django'},
    'DASCOL': {'name':'Data science', 'des': 'Sử dụng thành thạo ngôn ngữ lập trình Python các tool, libraries, framework phục vụ cho lập trình AI. Thiết kế, xây dựng hệ thống học máy Machine Learning bao gồm quá trình rút trích đặc trưng, cách đánh giá dữ liệu, quá trình chọn lựa giải thuật và kĩ thuật đánh giá và cải thiện mô hình. Hiểu và áp dụng hiệu quả các thuật toán, Framework và công nghệ Machine Learning khác nhau cho các vấn đề, yêu cầu khác nhau trong thực tế. Tự tin ứng tuyển vào các vị trí liên quan đến AI khác nhau của các công ty, tập đoàn trong và ngoài nước như: VinGroup,Viettel, FPT, Samsung….Làm việc với framework tensorflow để xử lý data và tạo mô hình học máy.'},
    'DLEAOL' : {'name':'Deep learning ', 'des': 'Sử dụng thành thạo ngôn ngữ lập trình Python các tool, libraries, framework phục vụ cho lập trình AI. Hiểu và áp dụng hiệu quả các thuật toán, Framework và công nghệ Machine Learning khác nhau cho các vấn đề, yêu cầu khác nhau trong thực tế'},
    'AIFLOL': {'name':'AI FULL lộ trình', 'des': 'Bạn sẽ được học và cam kết đầu ra từ khóa Python core đến khóa Deep learning'},
    'TAUTEOL': {'name':'Tự động test với Python', 'des': 'Lập trình Python Cơ bản. Hiểu cấu trúc Selenium Automation Frameworks. Làm việc với Selenium WebDriver Automation sử dụng Python. Thực hiện tự động hóa các Web Application trên Internet bằng Selenium. Viết code trên Python để thiết kế Selenium Testcase. Thực hiện các dự án Selenium Automation Project. Ứng tuyển vào vị trí Selenium Automation Fresher Tester'},
}
