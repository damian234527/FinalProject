# myapp/management/commands/create_students.py

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from authentication.models import Student

User = get_user_model()

class Command(BaseCommand):
    help = "Create a specified number of student objects"

    def add_arguments(self, parser):
        parser.add_argument("num_students", type=int, help="The number of students to create")
        parser.add_argument("--batch_size", type=int, default=1000, help="The batch size for creating students")

    @transaction.atomic
    def handle(self, *args, **options):
        num_students = options["num_students"]
        batch_size = options["batch_size"]

        for i in range(0, num_students, batch_size):
            batch_end = min(i + batch_size, num_students)

            students_batch = []
            for j in range(i, batch_end):
                student = Student(
                    username=f"student_{j + 1}",
                    first_name=f"First_{j + 1}",
                    last_name=f"Last_{j + 1}",
                    student_mail=f"student_{j + 1}@example.com",
                    password=f"password_{j + 1}",
                    profile_description=f"Profile description for student {j + 1}",
                )
                # timetable = TimetableModel.objects.get(pk=some_timetable_id)
                # student.active_timetable = timetable
                students_batch.append(student)

            Student.objects.bulk_create(students_batch)

        self.stdout.write(self.style.SUCCESS(f"Successfully created {num_students} student objects"))
