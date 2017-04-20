from django.shortcuts import render, redirect, get_object_or_404, render_to_response

from .models import Venue, Artist, Note, Show
from .forms import VenueSearchForm, NewNoteForm, ArtistSearchForm, UserRegistrationForm, NotesSearchForm

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout

from django.utils import timezone
from django.http import JsonResponse, HttpResponseBadRequest
from django.core.serializers.json import DjangoJSONEncoder
import json

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
@login_required
def new_note(request, show_pk):

    show = get_object_or_404(Show,  pk=show_pk)

    if request.method == 'POST':

        form = NewNoteForm(request.POST, request.FILES)
        if form.is_valid():

            note = form.save(commit=False);
            if note.title and note.text:  # If note has both title and text
                note.user = request.user
                note.show = show
                note.posted_date = timezone.now()
                note.save()
                return redirect('lmn:note_detail', note_pk=note.pk)

    else :
        form = NewNoteForm()

    return render(request, r'lmn/notes/new_note.html' , { 'form' : form , 'show':show })

# user edit notes
@login_required
def edit_notes(request, pk):
    notes = get_object_or_404(Note, pk=pk)
    form = NewNoteForm(request.POST or None, request.FILES, instance=notes)
    if form.is_valid():
        notes = form.save(commit=False)
        notes.save()
        return redirect('lmn:latest_notes')
    else:
        form = NewNoteForm( instance=notes)
        return render(request, r'lmn/notes/edit.html', {'form': form})

def latest_notes(request):
    notes_list = Note.objects.all().order_by('posted_date').reverse()
    paginator = Paginator(notes_list, 10) # Show 10 notes per page

    page = request.GET.get('page')
    try:
        notes = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        notes = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        notes = paginator.page(paginator.num_pages)
    return render(request, r'lmn/notes/note_list.html', {'notes':notes})


def notes_for_show(request, show_pk):   # pk = show pk

    # Notes for show, most recent first
    notes = Note.objects.filter(show=show_pk).order_by('posted_date').reverse()
    show = Show.objects.get(pk=show_pk)  # Contains artist, venue

    return render(request, r'lmn/notes/note_list.html', {'show': show, 'notes':notes } )



def note_detail(request, note_pk):
    note = get_object_or_404(Note, pk=note_pk)
    return render(request, r'lmn/notes/note_detail.html' , {'note' : note })

# A method that deletes notes added by the user4
@login_required
def delete_notes(request, pk):
    notes = get_object_or_404(Note, pk=pk)
    notes.delete()
    return redirect('lmn:latest_notes')


# Ajax for autocompletion when searcing notes not yet working

class NoteJSONEncoder(DjangoJSONEncoder):
    def default(self, obj):
        if isinstance(obj, Note):
            return obj.__dict__


def search_notes(request):

    note = request.GET.get('query')   # This is sent with the AJAX query.

    if note:
        # DB query
        notes = list(Note.objects.filter(title__icontains=note).order_by('text'))
    else:
        # No search query, return everything. Adapt to suit the behavior of your app.
        # Everything could be a lot! You would probably want to limit to (e.g.) the first 30 results
        notes = list(Note.objects.all().order_by('text'))

    # Use PlaceJSONEncoder to convert list of Places to JSON. Return JSON object.
    return JsonResponse(notes, encoder=NoteJSONEncoder, safe=False)
	