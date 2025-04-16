from django_jsonform.widgets import JSONFormWidget
from django import forms

class CustomJSONFormWidget(JSONFormWidget):
    def render_field(self, name, value, schema, attrs=None):
        attrs = attrs or {}
        if name in ['answer', 'description']:
            attrs.update({'rows': 6, 'cols': 80, 'class': 'vLargeTextField'})
            widget = forms.Textarea(attrs=attrs)
        else:
            attrs.update({'class': 'vTextField'})
            widget = forms.TextInput(attrs=attrs)
        return widget.render(name, value, attrs)