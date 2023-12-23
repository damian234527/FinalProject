from django.db import models
from authentication.models import Student
import icalendar
from datetime import datetime
# Create your models here.

def create_acronym(string):
    words_list = string.split()
    acronym = ""
    for word in words_list:
        acronym += word[0]
    return acronym

class Timetable(models.Model):
    timetable_name = models.CharField(max_length=255)
    author = models.ForeignKey(Student, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.timetable_name

    @classmethod
    def import_timetable(cls, ics_file, timetable_name=None, author=None):
        try:
            imported_calendar = icalendar.Calendar.from_ical(ics_file.read())
            timetable = cls.objects.create(timetable_name=timetable_name, author=author)
            if author:
                student, created = Student.objects.get(id=author)
            else:
                student = author
            Timetable_assignment.objects.create(timetable=timetable, student=student)
            initial_types = Activity_type.generate_generic_types()
            for activity in imported_calendar.walk("vevent"):
                time_start = activity.get("dtstart").dt
                time_end = activity.get("dtend").dt
                time_duration = time_end-time_start
                description = activity.get("summary")
                description = description.replace("/","-")
                course_acronym = None
                activity_type_name_pl = None
                type_found = False
                rooms = []
                teachers = []
                print("tets")
                for i, type in enumerate(initial_types):
                    print(f"tets{i} - {type}")
                    searched_string = " " + type + " "
                    index = description.find(searched_string)
                    if index != -1:
                        course_acronym, description = description.split(searched_string)[0], description.split(searched_string)[1]
                        activity_type_name_pl = type
                        type_found = True
                        break
                attributes_list = description.split()
                if not type_found:
                    if attributes_list[0] == "*":
                        attributes_list[0] += attributes_list.pop(1)
                    course_acronym = attributes_list[0]
                    activity_type_name_pl=attributes_list[1]
                else:
                    for i, attribute in enumerate(attributes_list):
                        any_digit = any(char.isdigit() for char in attribute)
                        if any_digit:
                            rooms.append(attribute)
                        else:
                            upper_leters = sum(map(str.isupper, attribute))
                            if upper_leters == 2:
                                teachers.append(attribute)
                print(f"rooms = {rooms}")
                print("\n\n\n")
                print(f"teachers = {teachers}")
                activity_type, created = Activity_type.objects.get_or_create(type_name_pl=activity_type_name_pl)
                course, created = Course.objects.get_or_create(course_name=course_acronym, course_initials=course_acronym)
                timetable.course_set.add(course)
                Activity.create_activity(time_start, time_end, description, time_duration, timetable, course, activity_type)
            return True, "Timetable imported successfully"
        except Exception as upload_error:
            return False, f"An error occurred while importing the timetable: {str(upload_error)}."

class Course(models.Model):

    course_initials = models.CharField(max_length=15)
    course_name = models.CharField(max_length=100)
    timetable = models.ManyToManyField(Timetable)
    def __str__(self):
        return self.course_initials


class Activity_type(models.Model):
    type_name_pl = models.CharField(max_length=100, default="def")
    type_name = models.CharField(max_length=100, default="default", blank=True)
    type_description = models.CharField(max_length=255, default="This is default type when no information provided")
    type_color = models.CharField(max_length=10, default="#FFFFFF")

    def __str__(self):
        return self.type_name

    @staticmethod
    def get_initial_types():
        type_names_pl = ["wyk",
                      "ćw",
                      "lab",
                      "proj",
                      "sem",
                      "exam"]

    @classmethod
    def generate_generic_types(cls):
        type_names = ["lecture",
                      "classes",
                      "laboratories",
                      "project",
                      "seminar",
                      "exam"]
        type_names_pl = ["wyk",
                      "ćw",
                      "lab",
                      "proj",
                      "sem",
                      "exam"]
        type_descriptions = ["Formal presentation or discourse delivered by lecturer.",
                             "More practical activity than lecture where students receive instruction and engage in learning activities related to a particular subject.",
                             "Type of activity where students may apply theoretical knowledge through hands-on activities.",
                             "Leads students to prepare a project. Work can take place individually or in groups.",
                             "Provides an opportunity for participants to engage in interactive learning, share ideas, and explore topics in depth. Seminars are often more participatory than traditional lectures.",
                             "Exam placeholder"]
        type_colors = ["#27AB4D",
                       "#273BAB",
                       "#91214E",
                       "#8B9669",
                       "#C2C042",
                       "#FF0000"]
        for i in range(len(type_names)):
            Activity_type.objects.get_or_create(type_name_pl=type_names_pl[i], type_name=type_names[i], type_description=type_descriptions[i], type_color=type_colors[i])
        return type_names_pl

class Activity(models.Model):
    time_start = models.DateTimeField()
    time_end = models.DateTimeField()
    description = models.CharField(max_length=255)
    time_duration = models.DurationField()
    timetable = models.ForeignKey(Timetable, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True, blank=True)
    activity_type = models.ForeignKey(Activity_type, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.description

    @classmethod
    def create_activity(cls, time_start, time_end, description, time_duration, timetable, course, activity_type):
        cls.objects.create(time_start=time_start,
                                        time_end=time_end,
                                        description=description,
                                        time_duration=time_duration,
                                        timetable=timetable,
                                        course=course,
                                        activity_type=activity_type)

class Teacher(models.Model):
    teacher_initials = models.CharField(max_length=20)
    teacher_first_name = models.CharField(max_length=100)
    teacher_last_name = models.CharField(max_length=100)
    teacher_link = models.URLField(max_length=200)
    teacher_mail = models.EmailField(max_length=254)

    def __str__(self):
        return self.teacher_initials


class Timetable_assignment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, null=True)
    timetable = models.ForeignKey(Timetable, on_delete=models.CASCADE)
    assignment_description = models.CharField(max_length=100)

