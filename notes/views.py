from django.shortcuts import render, get_object_or_404, redirect
from .forms import NoteForm, AddExistingNoteForm
from .models import Note, Note_assignment
from django.http import HttpResponse
from django.contrib import messages
from timetable.models import Course
from django.db.models import Q

def sort_by_course(assigned_notes):
    courses_ids = assigned_notes.values_list("course_id", flat=True).distinct()
    courses = Course.objects.filter(id__in=courses_ids).order_by("course_name")
    notes_by_course = {}
    for course in courses:
        notes_for_course = assigned_notes.filter(course_id=course.id)
        notes_for_course = notes_for_course.order_by('timetable')
        notes_by_course[course] = notes_for_course
    return notes_by_course

def user_notes(request):
    if request.user.is_authenticated:
        assigned_notes = Note_assignment.objects.filter(student_id=request.user.id)
        user_notes = Note.objects.filter(Q(id__in=assigned_notes.values("note_id")) & Q(is_active=True))
        notes_by_course = sort_by_course(user_notes)
        print(notes_by_course)
        return render(request, "notes/notes_list_private.html", {"notes_by_course": notes_by_course})

def public_notes(request):
    not_assigned_notes = Note_assignment.objects.filter(student_id=None)
    public_notes = Note.objects.filter(Q(id__in=not_assigned_notes.values("note_id")) & Q(is_active=True))
    notes_by_course = sort_by_course(public_notes)
    return render(request, "notes/notes_list_public.html", {"notes_by_course": notes_by_course})

def inactive_notes(request):
    not_active_notes = Note_assignment.objects.filter(Q(student_id=request.user.id) | Q(student_id=None))
    inactive_notes = Note.objects.filter(Q(id__in=not_active_notes.values("note_id")) & Q(is_active=False))
    notes_by_course = sort_by_course(inactive_notes)
    return render(request, "notes/notes_list_inactive.html", {"notes_by_course": notes_by_course})

def details(request, note_id):
    note = Note.objects.get(pk=note_id)
    return render(request, "notes/details.html", {"note": note})

def main(request):
    return render(request, "notes/notes.html")

def add_note(request):
    user = request.user if request.user.is_authenticated else None
    if request.method == "POST":
        new_note_form = NoteForm(user, request.POST)
        if new_note_form.is_valid():
            if user:
                new_note = new_note_form.save(commit=False)
                new_note.author = user
                new_note.save()
            else:
                new_note_form.save()
            return HttpResponse(status=204, headers={'HX-Trigger': 'note_changed'})
    else:
        new_note_form = NoteForm(user)
        return render(request, "notes/add_note.html", {"new_note_form": new_note_form})
def edit_note(request, note_id):
    current_note = get_object_or_404(Note, pk=note_id)
    if request.method == "POST":
        edit_note_form = NoteForm(request.POST, instance=current_note)
        if edit_note_form.is_valid():
            edit_note_form.save()
            return HttpResponse(status=204, headers={'HX-Trigger': 'note_changed'})
    else:
        edit_note_form = NoteForm(instance=current_note)
        return render(request, "notes/add_note.html", {"edit_note_form": edit_note_form})

def share_note(request, note_id):
    note = Note.objects.get(pk=note_id)
    share_link = note.share_link
    author = note.author
    return render(request, "notes/share_note.html",
                  {"share_link": share_link, "author": author, "note_id": note_id})

def delete_note(request, note_id):
    try:
        note = get_object_or_404(Note, pk = note_id)
        note.delete()
        return HttpResponse(status=204, headers={'HX-Trigger': 'note_changed'})
    except Exception as e:
        messages.error(request, "Something went wrong when deleting note: ", e)

def remove_note(request, note_id):
    try:
        note = get_object_or_404(Note, pk = note_id)
        note.delete()
        return HttpResponse(status=204, headers={'HX-Trigger': 'note_changed'})
    except Exception as e:
        messages.error(request, "Something went wrong when deleting note: ", e)

def assign_note(request):
    user = request.user if request.user.is_authenticated else None
    if user:
        if request.method == "POST":
            add_note_form = AddExistingNoteForm(request.POST)
            if add_note_form.is_valid():
                entered_link = add_note_form.cleaned_data["note_link"]
                note = get_object_or_404(Note, share_link=entered_link)
                try:
                    Note_assignment.objects.create(note=note, student=user)
                except:
                    if Note_assignment.objects.filter(note=note, student=user).exists():
                        messages.warning(request, "Given note already added")
                    else:
                        messages.error(request, "Something went wrong")
                messages.success(request, "Timetable added successfully")
                return HttpResponse(status=204)
        else:
            add_note_form = AddExistingNoteForm()
        return render(request, "notes/add_existing_note.html", {"add_note_form": add_note_form})

def change_status(request, note_id):
    note = get_object_or_404(Note, pk=note_id)
    note.is_active = not note.is_active
    note.save()
    return redirect("notes:main")