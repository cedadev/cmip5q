# django jquery autocomplete widget based on the django snippet http://www.djangosnippets.org/snippets/1097/

from django import forms
from django.utils.safestring import mark_safe
from django.utils.encoding import force_unicode 
from django.core.urlresolvers import reverse
from django.forms.util import ErrorList, ValidationError

CLIENT_CODEJS = """
<input type="text" name="%s_text" id="%s_text"/>
<input type="hidden" name="%s" id="%s" value="" />
<script type="text/javascript">
 $(function() {
        $('#%s_text').autocomplete('%s', {
            dataType: 'json',
            width: 500,
            parse: function(data) {
                return $.map(data, function(row) {
                    return { data:row, value:row[1], result:row[0] };
                });
            }
            });
            $("%s_text").result(
                function(e, data, value) {
                    $("#%s").val(value);
                }
            );
        }
    );
</script>
"""
class ValueAutocompleteField(forms.fields.CharField):
    """
    Autocomplete form field for Model Model
    """
    model = None
    url = None

    def __init__(self, Vocab, vocabname, Value, *args, **kwargs):
        self.vocab=Vocab.objects.get(name=vocabname)
        #self.url=reverse('cmip5q.protoq.views.completionHelper',args=(vocabname,))
        #self.url=reverse('ajax_value',args=(vocabname,))
        #FIXME: I can't work out how to make the above work without circular imports.
        self.url='/ajax/%s'%vocabname
        self.model=Value
        
        super(ValueAutocompleteField, self).__init__(
            widget = AutocompleteWidget(lookup_url=self.url),
            max_length=255,
            *args, **kwargs)

    def clean(self, value):

        try: 
            obj = self.model.objects.filter(vocab=self.vocab).get(pk=value)
        except self.model.DoesNotExist:
            raise ValidationError(u'Invalid item selected')            
        return obj     

class AutocompleteWidget(forms.widgets.TextInput):
    """ widget autocomplete for text fields
    """
    html_id = ''
    def __init__(self, 
                 lookup_url=None, 
                 *args, **kw):
        super(forms.widgets.TextInput, self).__init__(*args, **kw)
        # url for Datasource
        self.lookup_url = lookup_url
       

    def render(self, name, value, attrs=None):
        if value == None:
            value = ''
        html_id = attrs.get('id', name)
        self.html_id = html_id

        lookup_url = self.lookup_url
       
        return mark_safe(CLIENT_CODEJS % (name, html_id, name, html_id, html_id,
                                       lookup_url, html_id, html_id))


    def value_from_datadict(self, data, files, name):
        """
        Given a dictionary of data and this widget's name, returns the value
        of this widget. Returns None if it's not provided.
        """

        return data.get(name, None)