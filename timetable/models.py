from django.db import models
from authentication.models import Student
import icalendar
import uuid
# Create your models here.

def create_acronym(string):
    words_list = string.split()
    acronym = ""
    for word in words_list:
        acronym += word[0]
    return acronym

class Timetable(models.Model):
    timetable_name = models.CharField(max_length=255, blank=True)
    author = models.ForeignKey(Student, on_delete=models.SET_NULL, null=True)
    share_link = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    def __str__(self):
        return self.timetable_name

    @classmethod
    def import_timetable(cls, ics_file, timetable_name=None, author=None):
        try:
            imported_calendar = icalendar.Calendar.from_ical(ics_file.read())
            if author:
                author = Student.objects.get(pk=author)
            timetable = cls.objects.create(timetable_name=timetable_name, author=author)
            Timetable_assignment.objects.create(timetable=timetable, student=author)
            initial_types = Activity_type.generate_generic_types()
            newly_created_types = []
            for activity in imported_calendar.walk("vevent"):
                time_start = activity.get("dtstart").dt
                time_end = activity.get("dtend").dt
                time_duration = time_end-time_start
                description = activity.get("summary")
                description = description.replace("/","-")
                course_acronym = None
                activity_type_name_pl = None
                type_found = False
                teachers = []
                for i, type in enumerate(initial_types):
                    # print(f"{i} - {type}")
                    searched_string = " " + type + " "
                    index = description.find(searched_string)
                    if index != -1:
                        course_acronym, description = description.split(searched_string)[0], description.split(searched_string)[1]
                        activity_type_name_pl = type
                        type_found = True
                        break
                    else:
                        searched_string = type
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
                    attributes_list = attributes_list[2:]
                # teachers_search = True
                for i, attribute in enumerate(attributes_list):
                    upper_letters = sum(map(str.isupper, attribute))
                    if upper_letters == 2:
                        teachers.append(attribute)
                    else:
                        # teachers_search = False
                        break
                # print(f"teachers = {teachers}")
                # print(f"'{activity_type_name_pl}' {type_found}")
                if type_found:
                    # print(activity_type_name_pl)
                    activity_type = Activity_type.objects.get(type_name_pl=activity_type_name_pl)
                else:
                    created_activity_type_name = activity_type_name_pl + str(timetable.id)
                    if created_activity_type_name in newly_created_types:
                        activity_type = Activity_type.objects.get(type_name_pl=created_activity_type_name, type_name=activity_type_name_pl)
                    else:
                        activity_type = Activity_type.objects.create(type_name_pl=created_activity_type_name, type_name=activity_type_name_pl)
                        newly_created_types.append(created_activity_type_name)
                course, created = Course.objects.get_or_create(course_name=course_acronym, course_initials=course_acronym)
                timetable.course_set.add(course)
                activity = Activity.objects.create(time_start=time_start, time_end=time_end, description=description, time_duration=time_duration, timetable=timetable, course=course, activity_type=activity_type)
                teacher_objects = [None] * len(teachers)
                for i, teacher in enumerate(teachers):
                    teacher_objects[i], created = Teacher.objects.get_or_create(teacher_initials=teacher)
                    teacher_objects[i].activity_set.add(activity)
                #Activity.create_activity(time_start, time_end, description, time_duration, timetable, course, activity_type)
                #teacher.activity_set.add(teachers)
            return True, "Timetable imported successfully"
        except Exception as upload_error:
            return False, f"An error occurred while importing the timetable: {str(upload_error)}."

class Teacher(models.Model):
    teacher_initials = models.CharField(max_length=20, unique=True)
    teacher_first_name = models.CharField(max_length=100, null=True)
    teacher_last_name = models.CharField(max_length=100, null=True)
    teacher_link = models.URLField(max_length=200, null=True)
    teacher_mail = models.EmailField(max_length=254, null=True)

    def __str__(self):
        return self.teacher_initials

class Course(models.Model):
    course_initials = models.CharField(max_length=15)
    course_name = models.CharField(max_length=100)
    course_description = models.CharField(max_length=255)
    timetable = models.ManyToManyField(Timetable)
    def __str__(self):
        return self.course_initials

class Activity_type(models.Model):
    type_name_pl = models.CharField(max_length=100, default="def")
    type_name = models.CharField(max_length=100, default=type_name_pl, blank=True)
    type_description = models.CharField(max_length=255, default="This is default type when no information provided")
    type_color = models.CharField(max_length=10, default="#D7D3BA")

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
    def __str__(self):
        return self.type_name

    @classmethod
    def generate_generic_types(cls):

        for i in range(len(cls.type_names)):
            Activity_type.objects.get_or_create(type_name_pl=cls.type_names_pl[i], type_name=cls.type_names[i], type_description=cls.type_descriptions[i], type_color=cls.type_colors[i])
        return cls.type_names_pl

class Activity(models.Model):
    time_start = models.DateTimeField()
    time_end = models.DateTimeField()
    description = models.CharField(max_length=255)
    time_duration = models.DurationField()
    timetable = models.ForeignKey(Timetable, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True, blank=True)
    activity_type = models.ForeignKey(Activity_type, on_delete=models.CASCADE, null=True, blank=True)
    teacher = models.ManyToManyField(Teacher)

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

class Timetable_assignment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, null=True)
    timetable = models.ForeignKey(Timetable, on_delete=models.CASCADE)
    assignment_description = models.CharField(max_length=100)