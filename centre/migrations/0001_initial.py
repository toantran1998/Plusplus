# Generated by Django 3.1.7 on 2021-03-31 09:47

import datetime
import django.core.validators
from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='StudentLostConfirm',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'verbose_name': 'HV mất cam kết',
                'verbose_name_plural': 'HV mất cam kết',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='StudentOffFromTwoDays',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'verbose_name': 'HV nghỉ nhiều',
                'verbose_name_plural': 'HV nghỉ nhiều',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='StudentOffYesterday',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'verbose_name': 'HV nghỉ hôm qua',
                'verbose_name_plural': 'HV nghỉ hôm qua',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='StudyShiftSchedule',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'verbose_name': 'Lịch học',
                'verbose_name_plural': 'Lịch học',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Tasks',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'verbose_name': 'Việc cần làm',
                'verbose_name_plural': 'Việc cần làm',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Centre',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default=None, max_length=255, unique=True, verbose_name='Tên')),
                ('address', models.CharField(default=None, max_length=255, verbose_name='address')),
                ('created_date_time', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_date_time', models.DateTimeField(auto_now=True, null=True)),
            ],
            options={
                'verbose_name': 'Trung tâm',
                'verbose_name_plural': 'Trung tâm',
                'db_table': 'centre',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Classes',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(blank=True, default=None, max_length=255, null=True, unique=True, verbose_name='Mã lớp học')),
                ('name', models.CharField(max_length=255, verbose_name='Tên lớp học')),
                ('day_in_week', models.IntegerField(choices=[(1, 'Thứ 2-5'), (2, 'Thứ 3-6'), (3, 'Thứ 4-7')], default=None, verbose_name='Lịch học')),
                ('start_date', models.DateField(default=None, null=True, verbose_name='Ngày khai giảng')),
                ('study_shift_select', models.IntegerField(choices=[(1, 'Ca 1 (9h-10h30)'), (2, 'Ca 2 (14h-15h30)'), (3, 'Ca 3 (18h-19h30)'), (4, 'Ca 4 (19h30-21h)')], default=None, verbose_name='Ca học')),
                ('end_date', models.DateField(blank=True, default=None, null=True, verbose_name='Ngày kết thúc')),
                ('classes_order_no', models.IntegerField(default=0, editable=False)),
                ('waiting_flag', models.BooleanField(default=False, verbose_name='Lớp chờ')),
                ('created_date_time', models.DateTimeField(default=django.utils.timezone.now, editable=False, null=True, verbose_name='Ngày tạo')),
                ('updated_date_time', models.DateTimeField(default=django.utils.timezone.now, editable=False, null=True)),
            ],
            options={
                'verbose_name': 'Lớp học',
                'verbose_name_plural': 'Lớp học',
                'db_table': 'classes',
                'ordering': ['-waiting_flag'],
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='ClassesStudents',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('next_course_code', models.CharField(blank=True, default=None, editable=False, max_length=255, null=True, verbose_name='Mã khóa tiếp theo')),
                ('study_start_date', models.DateField(editable=False, null=True)),
                ('note', models.CharField(blank=True, default=None, max_length=255, null=True, verbose_name='Ghi chú')),
                ('commitment', models.CharField(blank=True, default=None, max_length=255, null=True, verbose_name='Cam kết')),
                ('assessment', models.CharField(blank=True, default=None, max_length=255, null=True, verbose_name='Đánh giá')),
                ('state', models.IntegerField(blank=True, choices=[(1, 'Chờ xếp lớp'), (2, 'Đã nhận lớp'), (3, 'Tốt nghiệp'), (4, 'Bảo lưu (1 tháng)'), (5, 'Bảo lưu (6 tháng)'), (6, 'Rút quyền'), (7, 'Hủy')], default=1, null=True, verbose_name='Trạng thái')),
                ('added_study_shift', models.BooleanField(default=False, verbose_name='Đã thêm vào buổi học')),
                ('created_date_time', models.DateTimeField(default=django.utils.timezone.now, editable=False, null=True)),
                ('updated_date_time', models.DateTimeField(default=django.utils.timezone.now, editable=False, null=True)),
            ],
            options={
                'db_table': 'classes_student',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='ClassesTeachers',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('assessment', models.CharField(blank=True, default=None, max_length=255, null=True, verbose_name='Đánh giá')),
                ('note', models.CharField(blank=True, default=None, max_length=255, null=True, verbose_name='Ghi chú')),
                ('added_study_shift', models.BooleanField(default=False, verbose_name='Đã thêm vào buổi học')),
                ('created_date_time', models.DateTimeField(default=django.utils.timezone.now, editable=False, null=True)),
                ('updated_date_time', models.DateTimeField(default=django.utils.timezone.now, editable=False, null=True)),
            ],
            options={
                'db_table': 'classes_teacher',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='ClassRoom',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('class_room_code', models.CharField(default=None, max_length=10, unique=True, verbose_name='Mã phòng học')),
                ('name', models.CharField(max_length=255, verbose_name='Tên phòng học')),
                ('address', models.CharField(max_length=255, verbose_name='Địa chỉ')),
                ('size', models.IntegerField(default=0, null=True, validators=[django.core.validators.MinValueValidator(1)], verbose_name='Số ghế')),
                ('created_date_time', models.DateTimeField(default=django.utils.timezone.now, editable=False, null=True)),
                ('updated_date_time', models.DateTimeField(default=django.utils.timezone.now, editable=False, null=True)),
            ],
            options={
                'verbose_name': 'Phòng học',
                'verbose_name_plural': 'Phòng học',
                'db_table': 'class_room',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(default=None, max_length=255, unique=True, verbose_name='Mã khóa học')),
                ('name', models.CharField(max_length=255, verbose_name='Tên khóa học')),
                ('cost', models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(1)], verbose_name='Giá gốc')),
                ('night_cost', models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(1)], verbose_name='Giá ca ngày')),
                ('daytime_cost', models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(1)], verbose_name='Giá ca tối')),
                ('study_shift_count', models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(1)], verbose_name='Số buổi học')),
                ('description', models.CharField(blank=True, default=None, max_length=255, null=True, verbose_name='Mô tả')),
                ('created_date_time', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_date_time', models.DateTimeField(auto_now=True, null=True)),
            ],
            options={
                'verbose_name': 'Bảng giá',
                'verbose_name_plural': 'Bảng giá',
                'db_table': 'course',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='CourseSurvey',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('assessment_category', models.IntegerField(choices=[(1, 'Kiến thức chuyên môn'), (2, 'Kỹ năng truyền dạt(diễn đạt rõ ràng, sinh động...)'), (3, 'Phương pháp giảng dạy (thảo luận, chuẩn bị tài liệu...)'), (4, 'Những ý kiến góp ý/ đánh giá khác dành cho Giáo viên để nâng cao chất lượng giảng dạy')], default=None, verbose_name='Danh mục đánh giá')),
                ('assessment', models.IntegerField(blank=True, choices=[(1, 'Tốt'), (2, 'Khá'), (3, 'Trung bình'), (4, 'Kém')], default=1, null=True, verbose_name='Đánh giá')),
                ('explain', models.CharField(blank=True, default=None, max_length=255, null=True, verbose_name='Giải thích')),
                ('created_date_time', models.DateTimeField(default=django.utils.timezone.now, editable=False, null=True)),
                ('updated_date_time', models.DateTimeField(default=django.utils.timezone.now, editable=False, null=True)),
            ],
            options={
                'verbose_name': 'Khảo sát khóa học',
                'verbose_name_plural': 'Khảo sát khóa học',
                'db_table': 'course_survey',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='CourseTeacherAssessment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('assessment_category', models.IntegerField(choices=[(1, 'Bạn biết đến Khóa học của Odin qua kênh tư vấn nào:'), (2, 'Bạn có cảm nhận sự khác biệt về trải nghiệm khóa học so với thông tư vấn ban đầu hay không?'), (3, 'Khóa học liên quan tới công việc/ việc học của bạn ở mức độ nào?'), (4, 'Khóa học có đạt được tính ứng dụng cao?'), (5, 'Tôi có thể áp dụng khóa học này dễ dàng hơn nếu nội dung được cải tiến')], default=None, verbose_name='Danh mục đánh giá')),
                ('assessment', models.IntegerField(blank=True, choices=[(1, 'Tốt'), (2, 'Khá'), (3, 'Trung bình'), (4, 'Kém')], default=None, null=True, verbose_name='Đánh giá')),
                ('explain', models.CharField(blank=True, default=None, max_length=255, null=True, verbose_name='Giải thích')),
                ('created_date_time', models.DateTimeField(default=django.utils.timezone.now, editable=False, null=True)),
                ('updated_date_time', models.DateTimeField(default=django.utils.timezone.now, editable=False, null=True)),
            ],
            options={
                'verbose_name': 'Đánh giá giáo viên',
                'verbose_name_plural': 'Đánh giá giáo viên',
                'db_table': 'course_teacher_assessment',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='FeedBackTeachingQuality',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('assessment_category', models.IntegerField(blank=True, choices=[(1, 'Sử dụng công cụ hỗ trợ (hình ảnh/video) hiệu quả'), (2, 'Giọng nói lưu loát, rõ ràng'), (3, 'Truyền năng lượng tốt trong lớp học'), (4, 'Hướng dẫn HV một cách dễ hiểu và rõ ràng'), (5, 'Tổng hợp và nhấn mạnh các nội dung chính của bài'), (6, 'Đưa ra câu hỏi và tương tác với HV'), (7, 'Quan tâm và chữa lỗi cho học viên với câu trả lời sai'), (8, 'Hỗ trợ và hướng dẫn HV khi gặp khó khăn'), (9, 'Khuyến khích HV trong quá trình học'), (10, 'Giao nhiệm vụ phù hợp với trình độ của HV'), (11, 'Ưu điểm'), (12, 'Nhược điểm')], default=None, null=True, verbose_name='Danh mục đánh giá')),
                ('assessment', models.CharField(blank=True, default=None, max_length=255, null=True, verbose_name='Đánh giá')),
                ('explain', models.CharField(blank=True, default=None, max_length=255, null=True, verbose_name='Giải thích')),
                ('created_date_time', models.DateTimeField(default=django.utils.timezone.now, editable=False, null=True)),
                ('updated_date_time', models.DateTimeField(default=django.utils.timezone.now, editable=False, null=True)),
            ],
            options={
                'verbose_name': 'Đánh giá chất lượng giảng dạy',
                'verbose_name_plural': 'Đánh giá chất lượng giảng dạy',
                'db_table': 'feed_back_teaching_quality',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Issues',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, default=None, max_length=255, null=True, verbose_name='Tiêu đề')),
                ('content', models.TextField(blank=True, default=None, max_length=255, null=True, verbose_name='Nội dung')),
                ('category', models.IntegerField(blank=True, choices=[(1, 'Bảo hành'), (2, 'Bảo lưu'), (3, 'Hỗ trợ học tập'), (4, 'Khiếu nại'), (5, 'Rút quyền lợi'), (6, 'Khác')], default=None, null=True, verbose_name='Phân loại')),
                ('state', models.IntegerField(blank=True, choices=[(1, 'Chờ xử lý'), (2, 'Đang xử lý'), (3, 'Hoàn thành'), (4, 'Huỷ')], default=None, null=True, verbose_name='Trạng thái')),
                ('call_date', models.DateField(default=datetime.datetime(2021, 3, 31, 9, 47, 41, 140574), verbose_name='Ngày gọi')),
                ('created_date_time', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_date_time', models.DateTimeField(auto_now=True, null=True)),
            ],
            options={
                'verbose_name': 'Issues',
                'verbose_name_plural': 'Quản lý Issues',
                'db_table': 'issues',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='StudentTestResult',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('point', models.IntegerField(default=None, null=True, validators=[django.core.validators.MaxValueValidator(10), django.core.validators.MinValueValidator(0)], verbose_name='Điểm')),
                ('note', models.CharField(blank=True, default=None, max_length=255, null=True, verbose_name='Ghi chú')),
                ('created_date_time', models.DateTimeField(default=django.utils.timezone.now, editable=False, null=True)),
                ('updated_date_time', models.DateTimeField(default=django.utils.timezone.now, editable=False, null=True)),
            ],
            options={
                'verbose_name': 'Kết quả test',
                'verbose_name_plural': 'Kết quả test',
                'db_table': 'student_test_result',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='StudyShift',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_no', models.IntegerField(default=None, verbose_name='STT buổi')),
                ('main_content', models.TextField(blank=True, null=True, verbose_name='Nội dung chính')),
                ('session_date', models.DateField(default=None, verbose_name='Ngày diễn ra')),
                ('from_time', models.TimeField(default=None, verbose_name='Thời gian bắt đầu')),
                ('to_time', models.TimeField(default=None, verbose_name='Thời gian kết thúc')),
                ('home_work_content', models.TextField(blank=True, null=True, verbose_name='Nội dung BTVN')),
                ('study_shift_select', models.IntegerField(blank=True, choices=[(1, 'Ca 1 (9h-10h30)'), (2, 'Ca 2 (14h-15h30)'), (3, 'Ca 3 (18h-19h30)'), (4, 'Ca 4 (19h30-21h)')], default=None, null=True, verbose_name='Ca học')),
                ('created_date_time', models.DateTimeField(default=django.utils.timezone.now, editable=False, null=True)),
                ('updated_date_time', models.DateTimeField(default=django.utils.timezone.now, editable=False, null=True)),
            ],
            options={
                'verbose_name': 'Buổi học',
                'verbose_name_plural': 'Buổi học',
                'db_table': 'study_shift',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='StudyShiftStudent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('attendance', models.BooleanField(default=False, verbose_name='Điểm danh')),
                ('leave_request', models.BooleanField(default=False, verbose_name='Nghỉ có phép')),
                ('assessment', models.CharField(blank=True, default=None, max_length=255, null=True, verbose_name='Đánh giá')),
                ('home_work', models.BooleanField(default=False, verbose_name='BTVN')),
                ('note', models.CharField(blank=True, default=None, max_length=255, null=True, verbose_name='Ghi chú')),
                ('created_date_time', models.DateTimeField(default=django.utils.timezone.now, editable=False, null=True)),
                ('updated_date_time', models.DateTimeField(default=django.utils.timezone.now, editable=False, null=True)),
            ],
            options={
                'verbose_name': 'Điểm danh học viên',
                'verbose_name_plural': 'Điểm danh học viên',
                'db_table': 'study_shift_student',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='StudyShiftTeacher',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('assessment_category', models.IntegerField(blank=True, choices=[(1, 'Trang phục'), (2, 'Đến lớp đúng giờ'), (3, 'Hoàn thành sổ đầu bài'), (4, 'Giữ gìn cơ sở vật chất'), (5, 'Bàn giao đầy đủ trang thiết bị'), (6, 'Gửi handout đúng giờ & đúng tiêu đề'), (7, 'Khác')], default=None, null=True, verbose_name='Danh mục đánh giá')),
                ('assessment', models.BooleanField(default=False, verbose_name='Đánh giá')),
                ('explain', models.CharField(blank=True, default=None, max_length=255, null=True, verbose_name='Giải thích')),
                ('created_date_time', models.DateTimeField(default=django.utils.timezone.now, editable=False, null=True)),
                ('updated_date_time', models.DateTimeField(default=django.utils.timezone.now, editable=False, null=True)),
            ],
            options={
                'verbose_name': 'Đánh giá giáo viên',
                'verbose_name_plural': 'Đánh giá giáo viên',
                'db_table': 'study_shift_teacher',
                'managed': True,
            },
        ),
    ]
