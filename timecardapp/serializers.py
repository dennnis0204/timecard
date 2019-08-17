from timecardapp.models import TimeCards
import serpy


class CustomTimeField(serpy.Field):
    def to_value(self, value):
        time_dict = {}
        time_dict.update({
            "hour": value.strftime("%H"),
            "minute": value.strftime("%M"),
        })
        return time_dict

class CustomDateField(serpy.Field):
    def to_value(self, value):
        date_dict = {}
        date_dict.update({
            "year": value.strftime("%Y"),
            "month": value.strftime("%m"),
            "day": value.strftime("%d")
        })
        return date_dict
        # return value.day

class CustomDateFieldTwo(serpy.Field):
    def to_value(self, value):
        date = value.strftime("%d") + "/" + value.strftime("%m") + "/" + value.strftime("%Y")
        return date

class TimeCardsSerializer(serpy.Serializer):
    id = serpy.IntField()
    entry_date = CustomDateField()
    time_in = CustomTimeField()
    time_out = CustomTimeField()
    break_time = CustomTimeField()
    total_time = CustomTimeField()
    pay = serpy.FloatField()

class WagesSerializer(serpy.Serializer):
    id = serpy.IntField()
    wage = serpy.FloatField()
    increase_date = CustomDateFieldTwo()
    last_date = CustomDateFieldTwo()

class SettingsSerializer(serpy.Serializer):
    id = serpy.IntField()
    break_type = serpy.StrField()
    break_duration = serpy.IntField()
    round_time = serpy.IntField()
