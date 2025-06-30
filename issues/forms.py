from django import forms
from django.contrib.auth.models import User
from .models import Issue, Comment

# 🔐 User Registration Form
class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-input'}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-input'}))

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm = cleaned_data.get("confirm_password")

        if password and confirm and password != confirm:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data


# 📝 Issue Submission Form
class IssueForm(forms.ModelForm):
    class Meta:
        model = Issue
        fields = ['title', 'description', 'category', 'location']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'form-input',
                'placeholder': field.label
            })


# 💬 Comment Form (Threaded)
class CommentForm(forms.ModelForm):
    parent = forms.ModelChoiceField(
        queryset=Comment.objects.all(),
        required=False,
        widget=forms.HiddenInput()
    )

    class Meta:
        model = Comment
        fields = ['text', 'parent']
        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'form-input',
                'rows': 2,
                'placeholder': 'Write your comment...'
            }),
        }
