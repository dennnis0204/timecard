from django.http import JsonResponse

from timecardapp.models import TimeCards, Wages, Settings
from timecardapp.serializers import TimeCardsSerializer, WagesSerializer, SettingsSerializer

from django.views.generic.list import ListView
from django.views.generic import TemplateView

from datetime import datetime, date, time, timedelta
import time as timeX
import calendar

from django.contrib.auth.models import User



class IndexView(ListView):
    default_year = date.today().year
    default_month = date.today().month
    model = TimeCards
    # template_name = 'timecardapp/index.html'

    def estimation(self, *args, **kwargs):
        user = self.request.user
        year, month = self.get_year_month()
        month_pay = 0
        overtime = 0
        total_time = 0

        time_at_work = datetime.combine(date.min, time.min)
        overtime_at_work = datetime.combine(date.min, time.min)
        one_day_overtime = datetime.combine(date.min, time.min)
        overtime_norm = datetime.combine(date.min, time.min)
        weekend = datetime.combine(date.min, time.min)

        obj = Settings.objects.all().get(user=user)
        overtime_norm = overtime_norm + timedelta(seconds=(obj.overtime_hours*3600 + obj.overtime_minutes*60))

        objs = TimeCards.objects.all().filter(entry_date__year = year, entry_date__month = month, user = user)
        for obj in objs:
            entry_date = obj.entry_date
            week_day = calendar.weekday(entry_date.year, entry_date.month, entry_date.day)

            one_day_total_time = datetime.combine(date.min, obj.total_time)
            time_at_work = time_at_work + timedelta(seconds=(one_day_total_time.hour*3600 + one_day_total_time.minute*60))

            if (week_day == 5 or week_day == 6):
                weekend = weekend + timedelta(seconds=(one_day_total_time.hour*3600 + one_day_total_time.minute*60))

            # print('overtime_norm < one_day_total_time', overtime_norm, type(overtime_norm), one_day_total_time, type(one_day_total_time))
            if (overtime_norm < one_day_total_time):
                one_day_overtime = one_day_total_time - timedelta(seconds=(overtime_norm.hour*3600 + overtime_norm.minute*60))
                overtime_at_work = overtime_at_work + timedelta(seconds=(one_day_overtime.hour*3600 + one_day_overtime.minute*60))
                # print('one_overtime', overtime_at_work)

            month_pay += obj.pay

        total_time_hour = (time_at_work.day - 1) * 24 + time_at_work.hour
        total_time_minute = time_at_work.minute

        overtime_hour = (overtime_at_work.day - 1) * 24 + overtime_at_work.hour
        overtime_minute = overtime_at_work.minute

        weekend_hour = (weekend.day - 1) * 24 + weekend.hour
        weekend_minute = weekend.minute

        print('time_at_work', time_at_work, type(time_at_work), total_time_hour, total_time_minute)
        # print('overtime_at_work', overtime_at_work, type(overtime_at_work))

        return total_time_hour, total_time_minute, overtime_hour, overtime_minute, weekend_hour, weekend_minute, month_pay
    
    # def days_hours_minutes(td):
    #     return td.days, td.seconds//3600, (td.seconds//60)%60

    def get_template_names(self):
        if self.request.user.is_authenticated:
            return ['timecardapp/index.html']
        else:
            return ['timecardapp/signin.html']


    def get_year_month(self, *args, **kwargs):
        year = self.kwargs.get('year', self.default_year)
        month = self.kwargs.get('month', self.default_month)
        return year, month

    
    def get_json(self):
        if self.request.user.is_authenticated:
            user = self.request.user
            year, month = self.get_year_month()
            total_time_hour, total_time_minute, overtime_hour, overtime_minute, weekend_hour, weekend_minute, month_pay = self.estimation()
            obj = TimeCards.objects.all().filter(entry_date__year = year, entry_date__month = month, user = user)
            table_data = TimeCardsSerializer(obj, many=True)
            response_data = {
                'totalTimeHour': total_time_hour,
                'totalTimeMinute': total_time_minute,
                'overtimeHour': overtime_hour,
                'overtimeMinute': overtime_minute,
                'weekendHour': weekend_hour,
                'weekendMinute': weekend_minute,
                'monthPay': month_pay,
                'tableData': table_data.data
            }
            return response_data
        else:
            return None
    
    # def get_next_last_month(self, *args, **kwargs):        
    #     year, month = self.get_year_month()
    #     request_month = date(year = year, month = month, day = 1)
    #     last_month = request_month - timedelta(days = 1)
    #     next_month = request_month + timedelta(days = 35)
    #     return request_month, last_month, next_month

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     if self.request.user.is_authenticated:
    #         year, month = self.get_year_month() 
    #         request_month, last_month, next_month = self.get_next_last_month()
    #         context.update({
    #             'year': year,
    #             'month': month,
    #             'last_month': last_month,
    #             'request_month': request_month,
    #             'next_month': next_month,
    #         })

    #         total_time_hour, total_time_minute, overtime, weekend_hour, weekend_minute, month_pay = self.estimation()
    #         context.update({
    #             'totalTimeHour': total_time_hour,
    #             'totalTimeMinute': total_time_minute,
    #             'overtime': overtime,
    #             'weekendHour': weekend_hour,
    #             'weekendMinute': weekend_minute,
    #             'monthPay': month_pay,
    #         })

    #         context['table_data'] = self.get_json()

    #     return context


    def get(self, request, *args, **kwargs):
        print(request.COOKIES);
        # just for test closest_date.wage
        # if self.request.user.is_authenticated:
        #     user = self.request.user
        #     entry_date = date(2018, 5, 4)
        #     closest_date = Wages.objects.all().filter(user=user).filter(increase_date__lte=entry_date).order_by('increase_date').last()
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        user = self.request.user
        form = request.POST
        if ('preferences' in form):
            return JsonResponse(get_preferences(request), safe=False)
        if ('first_load' in form):
            # timeX.sleep(5)
            return JsonResponse(self.get_json(), safe=False)
        if ('delete' in form):
            del_date = date(int(form.get('year', 2000)), int(form.get('month', 1)), int(form.get('day', 1)))
            try:
                obj = TimeCards.objects.all().get(entry_date = del_date, user = user)
                obj.delete()
            except (KeyError, TimeCards.DoesNotExist):
                return JsonResponse({'deleted': False})
            return JsonResponse(self.get_json(), safe=False)

        elif ('add' in form):
            entry_date = date(int(form.get('year', 2019)), int(form.get('month', 1)), int(form.get('day', 1)))
            time_in = time(int(form.get('time_in_hour', 8)), int(form.get('time_in_minute', 00)))
            time_out = time(int(form.get('time_out_hour', 16)), int(form.get('time_out_minute', 00)))
            break_time = time(int(form.get('break_hour', 0)), int(form.get('break_minute', 0)))
            duration = datetime.combine(date.min, time_out) - datetime.combine(date.min, time_in)

            # for night shift, example 22:00 - 06:00
            if (time_out < time_in):
                duration += timedelta(days = 1)

            duration = datetime.combine(date.min, (datetime.min + duration).time()) - datetime.combine(date.min, break_time)
            time_at_work = time(duration.seconds//3600, (duration.seconds//60)%60)
            time_at_work_decimal = duration.seconds / 3600

            # searching the actual wage rate for entry_date
            closest_date = Wages.objects.all().filter(user=user).filter(increase_date__lte=entry_date).order_by('increase_date').last()
            if (not closest_date):
                response = {'redirectUrl': '/preferences'}
                return JsonResponse(response)
            actual_wage = closest_date.wage
            pay = round(time_at_work_decimal * actual_wage, 2)


            try:
                new_obj = TimeCards(time_in=time_in, time_out=time_out, break_time=break_time, total_time=time_at_work, pay=pay, entry_date=entry_date, user=user)
                #look up for the same date
                obj = TimeCards.objects.all().get(entry_date=entry_date, user=user)
                #if exist then delete old date
                obj.delete()
                #saving new date
                new_obj.save()
            except (KeyError, TimeCards.DoesNotExist):
                #if does not exist just saving date
                new_obj.save()

            return JsonResponse(self.get_json(), safe=False)






class Preferences(ListView):
    template_name = 'timecardapp/preferences.html'
    model = Wages

    def post(self, request, *args, **kwargs):
        form = request.POST
        if ('first_load' in form):
            return JsonResponse(self.get_json(), safe=False)
        if ('break_load' in form):
            print('break_load')
            return JsonResponse(get_preferences(request), safe=False)
        if ('round_time_load' in form):
            print('round_time_load')
            return JsonResponse(get_preferences(request), safe=False)
        if ('overtime_load' in form):
            print('overtime_load')
            return JsonResponse(get_preferences(request), safe=False)
        if ('break_change' in form):
            if self.request.user.is_authenticated:
                user = self.request.user
                break_type = (form.get('break_type', 'noBreak'))
                break_duration = (form.get('break_duration', 15))
                print('break_duration', break_duration)
                try:
                    obj = Settings.objects.all().get(user=user)
                    print(break_type, break_duration, obj)
                    obj.break_type = break_type
                    obj.break_duration = break_duration
                    obj.save()
                except (KeyError, Settings.DoesNotExist):
                    new_obj = Settings(break_type=break_type, break_duration=break_duration, user=user)
                    new_obj.save()
                return JsonResponse(get_preferences(request), safe=False)
        if ('round_time_change' in form):
            if self.request.user.is_authenticated:
                user = self.request.user
                round_time = (form.get('round_time', "15"))
                try:
                    obj = Settings.objects.all().get(user=user)
                    obj.round_time = round_time
                    obj.save()
                except (KeyError, Settings.DoesNotExist):
                    new_obj = Settings(round_time=round_time, user=user)
                    new_obj.save()
                return JsonResponse(get_preferences(request), safe=False)
        if ('overtime_change' in form):
            if self.request.user.is_authenticated:
                user = self.request.user
                calculate_overtime = convert_trueTrue_falseFalse(form.get('calculate_overtime', True))
                overtime_hours = form.get('overtime_hours', 8)
                overtime_minutes = form.get('overtime_minutes', 0)
                try:
                    obj = Settings.objects.all().get(user=user)
                    obj.calculate_overtime = calculate_overtime
                    obj.overtime_hours = overtime_hours
                    obj.overtime_minutes = overtime_minutes
                    obj.save()
                except (KeyError, Settings.DoesNotExist):
                    new_obj = Settings(calculate_overtime=calculate_overtime, overtime_hours=overtime_hours, overtime_minutes=overtime_minutes)
                    new_obj.save()
                return JsonResponse(get_preferences(request), safe=False)
        
        if ('add' in form):
            print('add')
            if self.request.user.is_authenticated:
                # get user, wage and date ------------------------#
                user = self.request.user
                wage = float(form.get('wage', 0))
                entry_date = (form.get('date', '2050-1-1'))
                entry_date = datetime.strptime(entry_date, '%Y-%m-%d').date()
                #---------------------------------------------------#

                # if entry_date already exist --------------------#
                if (Wages.objects.all().filter(user=user).filter(increase_date=entry_date)):
                    return JsonResponse(self.get_json(), safe=False)
                #-------------------------------------------------#

                nearest_last_date = Wages.objects.all().filter(user=user).filter(increase_date__lt=entry_date).order_by('increase_date').last()
                nearest_next_date = Wages.objects.all().filter(user=user).filter(increase_date__gt=entry_date).order_by('increase_date').first()

                if (nearest_last_date):
                    new_nearest_last_date = Wages(user=nearest_last_date.user, wage=nearest_last_date.wage, increase_date=nearest_last_date.increase_date,
                    last_date=(entry_date - timedelta(days = 1)))
                    nearest_last_date.delete()
                    new_nearest_last_date.save()
                if (nearest_next_date):
                    new_wage_obj = Wages(user=user, wage=wage, increase_date=entry_date, last_date=(nearest_next_date.increase_date - timedelta(days = 1)))
                else:
                    new_wage_obj = Wages(user=user, wage=wage, increase_date=entry_date, last_date=date(2050, 1, 1))

                # update pay fields -----------------------------------------------#
                card_obj = TimeCards.objects.all().filter(user=user).filter(entry_date__gte=new_wage_obj.increase_date).filter(entry_date__lte=new_wage_obj.last_date)
                for obj in card_obj:
                    time_at_work_decimal = obj.total_time.hour + obj.total_time.minute / 60
                    
                    obj.pay = round(time_at_work_decimal * new_wage_obj.wage, 2)
                    print(obj.total_time.hour, obj.total_time.minute, time_at_work_decimal, obj.pay)
                    obj.save()
                #------------------------------------------------------------------#

                new_wage_obj.save()
                return JsonResponse(self.get_json(), safe=False)

        elif ('del' in form):
            print('del')
            if self.request.user.is_authenticated:
                # get user and date------------------#
                user = self.request.user
                entry_date = (form.get('date', '2050-1-1'))
                entry_date = datetime.strptime(entry_date, '%Y-%m-%d').date()
                #------------------------------------#

                wage_obj = Wages.objects.all().filter(user=user).get(increase_date=entry_date)
                if (wage_obj):
                    nearest_last_date = Wages.objects.all().filter(user=user).filter(increase_date__lt=entry_date).order_by('increase_date').last()
                    nearest_next_date = Wages.objects.all().filter(user=user).filter(increase_date__gt=entry_date).order_by('increase_date').first()
                    if (nearest_last_date and nearest_next_date):
                        new_nearest_last_date = Wages(user=nearest_last_date.user, wage=nearest_last_date.wage, increase_date=nearest_last_date.increase_date,
                    last_date=(nearest_next_date.increase_date - timedelta(days = 1)))
                        nearest_last_date.delete()
                        new_nearest_last_date.save()
                    elif (nearest_last_date and not nearest_next_date):
                        new_nearest_last_date = Wages(user=nearest_last_date.user, wage=nearest_last_date.wage, increase_date=nearest_last_date.increase_date,
                    last_date=date(2050, 1, 1))
                        nearest_last_date.delete()
                        new_nearest_last_date.save()

                    # update pay fields ---------------------#
                    card_obj = TimeCards.objects.all().filter(user=user).filter(entry_date__gte=wage_obj.increase_date).filter(entry_date__lte=wage_obj.last_date)
                    for obj in card_obj:
                        if (nearest_last_date):
                            time_at_work_decimal = obj.total_time.hour + obj.total_time.minute / 24
                            obj.pay = round(time_at_work_decimal * new_nearest_last_date.wage)
                        else:
                            obj.pay = -1
                        obj.save()
                    #----------------------------------------#

                    wage_obj.delete()
                    return JsonResponse(self.get_json(), safe=False)
        else:
            return JsonResponse(self.get_json(), safe=False)

    def get_json(self):
        if self.request.user.is_authenticated:
            user = self.request.user
            obj = Wages.objects.all().filter(user = user)
            wage_table_data = WagesSerializer(obj, many=True)
            response_data = {
                'tableData': wage_table_data.data
            }
            return response_data
        else:
            return None


class PrivacyEnglish(TemplateView):
    template_name = 'timecardapp/privacy_en.html'

class PrivacyPolish(TemplateView):
    template_name = 'timecardapp/privacy_pl.html'

class PrivacyRussian(TemplateView):
    template_name = 'timecardapp/privacy_ru.html'


def convert_trueTrue_falseFalse(input):
    if input.lower() == 'false' or input == False:
        return False
    elif input.lower() == 'true' or input == True:
        return True
    else:
        raise ValueError("...")




def get_preferences(request):
    if request.user.is_authenticated:
        user = request.user
        obj = Settings.objects.all().filter(user=user)
        if (not obj):
            obj = Settings(user=user, break_type="noBreak", break_duration=15, round_time=15, calculate_overtime=True, overtime_hours=8, overtime_minutes=0)
            obj.save()
            obj = Settings.objects.all().filter(user=user)
            print('new_obj=', obj)
        preferences = SettingsSerializer(obj, many=True)
        obj2 = Wages.objects.all().filter(user=user)
        if (not obj2):
            rate_exist = False
        else:
            rate_exist = True

        response_data = {
            'preferences': {
                'break': {
                    'breakType': preferences.data[0].get("break_type", "noBreak"),
                    'breakDuration': preferences.data[0].get("break_duration")
                },
                'roundTime': preferences.data[0].get("round_time"),
                'overtime': {
                    'calculateOvertime': preferences.data[0].get("calculate_overtime", True),
                    'overtimeHours': preferences.data[0].get("overtime_hours", 8),
                    'overtimeMinutes': preferences.data[0].get("overtime_minutes", 0),
                },
                'rateExist': rate_exist
            }
        }
        return response_data
    else:
        return None
    
    