from django import forms


class CreateNewAccountForm(forms.Form):
    user_name = forms.CharField(max_length=128)
    user_password = forms.CharField(max_length=128)
    user_email = forms.EmailField()
    user_first_name = forms.CharField()
    user_last_name = forms.CharField()
    user_student_email = forms.EmailField()
    user_description = forms.CharField()

class LoginForm(forms.Form):
    user_name = forms.CharField(max_length=128)
    user_password = forms.CharField(max_length=128)