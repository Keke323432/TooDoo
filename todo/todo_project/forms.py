from django import forms
from .models import Task, Category, Comment, Message
from django.contrib.auth.models import User

class EditForm(forms.ModelForm):
    assigned_to = forms.ModelChoiceField(queryset=User.objects.all(), required=False, widget=forms.Select(attrs={'class': 'form-control'}))
    class Meta:
        model = Task
        fields = ['title', 'due_date', 'category', 'description', 'completed','priority','bookmarked','assigned_to']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', }),
            'description': forms.Textarea(attrs={'class': 'tinymce-editor'}),
            'completed': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'due_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'priority': forms.Select(attrs={'class': 'form-control'}),
            'bookmarked': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'assigned_to':forms.Select(attrs={'class': 'form-control'})
            
        }


class CreateForm(forms.ModelForm):
    assigned_to = forms.ModelChoiceField(
        queryset=User.objects.all(), 
        required=False, 
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = Task
        fields = ['title', 'due_date', 'category', 'description', 'priority', 'assigned_to']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'tinymce-editor'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'due_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'priority': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Get the logged-in user
        super(CreateForm, self).__init__(*args, **kwargs)
        
        # If user is provided, filter categories by the logged-in user for specific cases
        if user:
            self.fields['category'].queryset = Category.objects.all()
        else:
            self.fields['category'].queryset = Category.objects.all()


class TaskCompleteForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['completed']


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'})
        }


class AddCategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'color']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'color': forms.TextInput(attrs={
                'type': 'color',
                'class': 'form-control form-control-color',
                'id': 'exampleColorInput',
                'title': 'Choose your color'
            }),
        }
        labels = {
            'name': 'Category Name',  # Custom label for the name field
            'color': 'Category Color',  # Custom label for the color field
        }

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['body']
        widgets = {
            'body': forms.Textarea(attrs={'class': 'form-control'}),
        }


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = [ 'body']
        widgets = {
            'body': forms.Textarea(attrs={'class': 'form-control', }),
        }
