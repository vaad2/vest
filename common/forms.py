from django import forms


class FormMixinTag(forms.Form):
    def __init__(self, *args, **kwargs):
        form = super(FormMixinTag, self).__init__(*args, **kwargs)
        self.fields['_form_name'] = forms.CharField(widget=forms.HiddenInput, initial=self.__class__.__name__.lower())

        return form


class FormModelMixinTag(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        form = super(FormModelMixinTag, self).__init__(*args, **kwargs)
        self.fields['_form_name'] = forms.CharField(widget=forms.HiddenInput, initial=self.__class__.__name__.lower())

        return form



def decorator_placeholder(method):
    def dc_method(self, *args, **kwargs):
        method(self, *args, **kwargs)
        for field_name in self.fields:
            field = self.fields.get(field_name)
            if field:
                if type(field.widget) in (forms.TextInput, forms.DateInput):
                    field.widget = forms.TextInput(attrs={'placeholder': field.label})

    return dc_method