from datetime import datetime, date

from django.core.exceptions import ValidationError
from django.forms import ModelForm, forms

from app_config import settings
from centre.models import Classes


class ClassesForm(ModelForm):
    def clean(self):
        if self.is_valid():
            if 'start_date' in self.data:
                start_date = datetime.strptime(self.data['start_date'], settings.DEFAULT_DATE_FORMAT)
                # 1: 2-5 2: 3-6 3:4-7
                day_in_week_type = int(self.data['day_in_week'])
                if not ('waiting_flag' in self.data):
                    week_day = start_date.weekday()
                    if day_in_week_type == 1 and week_day != 0 and week_day != 3:
                        raise ValidationError("Ngày khai giảng phải là thứ 2 hoặc thứ 5")
                    elif day_in_week_type == 2 and week_day != 1 and week_day != 4:
                        raise ValidationError("Ngày khai giảng phải là thứ 3 hoặc thứ 6")
                    elif day_in_week_type == 3 and week_day != 2 and week_day != 5:
                        raise ValidationError("Ngày khai giảng phải là thứ 4 hoặc thứ 7")

    class Meta:
        model = Classes
        exclude = ("",)


