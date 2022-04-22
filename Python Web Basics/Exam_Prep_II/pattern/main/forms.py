import os

from django import forms

from pattern.main.models import Profile, Note


class ProfileForm(forms.ModelForm):

    class Meta:
        model = Profile
        fields = ('first_name', 'last_name', 'age', 'image_url',)

        labels = {
            'first_name': 'First Name',
            'last_name': 'Last Name',
            'image_url': 'Link to Profile Image'
        }


class CreateNoteForm(forms.ModelForm):

    class Meta:
        model = Note
        fields='__all__'
        labels = {
            'image_url': 'Link to Image'
        }


class EditNoteForm(forms.ModelForm):

    class Meta:
        model = Note
        fields='__all__'
        labels = {
            'image_url': 'Link to Image'
        }


class DeleteNoteForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['disabled'] = 'disabled'
            self.fields[field].required = False

    def save(self, commit = True):
        self.instance.delete()
        return self.instance

    class Meta:
        model=Note
        fields = '__all__'
        labels = {
            'expense_image': 'Link to Image'
        }