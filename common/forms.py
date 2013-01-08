from django import forms

class FormMixinTag(forms.Form):
    def __init__(self, *args, **kwargs):
        form = super(FormMixinTag, self).__init__(*args, **kwargs)
        self.fields['_form_name'] = forms.CharField(widget = forms.HiddenInput, initial = self.__class__.__name__.lower())

        return form


class FormModelMixinTag(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        form = super(FormModelMixinTag, self).__init__(*args, **kwargs)
        self.fields['_form_name'] = forms.CharField(widget = forms.HiddenInput, initial = self.__class__.__name__.lower())

        return form

