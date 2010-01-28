# django jquery autocomplete widget based on the django snippet http://www.djangosnippets.org/snippets/1097/

from django import forms
from django.utils.safestring import mark_safe
from django.utils.encoding import force_unicode 
from django.core.urlresolvers import reverse
from django.forms.util import ErrorList, ValidationError

import logging

# See http://docs.jquery.com/Plugins/Autocomplete/autocomplete#url_or_dataoptions for autocomplete options
CLIENT_CODEJS = """
<input type="text" name="%s_text" id="%s_text" %s value="%s" />
<input type="hidden" name="%s" id="%s" value="%s" />
<script type="text/javascript">
 $(function() {
        $('#%s_text').autocomplete('%s', {
            dataType: 'json',
            minchars: 3,
            max: 200,
            cacheLength: 20,
            width: 500,
            parse: function(data) {
                return $.map(data, function(row) {
                    return { data:row, value:row[1], result:row[0] };
                });
            }
            }).result(
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

    def __init__(self, Vocab, vocabname, Value, size=0, *args, **kwargs):
       
        #self.url=reverse('cmip5q.protoq.views.completionHelper',args=(vocabname,))
        #self.url=reverse('ajax_value',args=(vocabname,))
        #FIXME: I can't work out how to make the above work without circular imports.
        self.url='/ajax/%s'%vocabname
        self.vocab=Value.objects.filter(vocab=Vocab.objects.get(name=vocabname))
        
        super(ValueAutocompleteField, self).__init__(
            widget = AutocompleteWidget(self.vocab,lookup_url=self.url,size=size),
            max_length=255,
            *args, **kwargs)

    def clean(self, value):
        logging.debug('saving autocomplete %s'%value)
        try: 
            obj = self.vocab.get(pk=value)
        except Exception,e:
            raise Exception,e
            #raise ValidationError(u'Invalid item selected')            
        return obj     

class AutocompleteWidget(forms.widgets.TextInput):
    """ widget autocomplete for text fields
    """
    html_id = ''
    def __init__(self,vocab,
                 lookup_url=None, size=0,
                 *args, **kw):
        super(forms.widgets.TextInput, self).__init__(*args, **kw)
        # url for Datasource
        self.lookup_url = lookup_url
        self.vocab=vocab
        self.size=size
       

    def render(self, name, value, attrs):
        if value == None:
            value = ''
        html_id = attrs.get('id', name)
        self.html_id = html_id
        logging.debug('render value [%s] attributes %s'%(value,attrs))
        if value:
            vv=self.vocab.get(id=value)
        else: vv=''

        lookup_url = self.lookup_url
        
        if self.size<>0:
            sizestr='size="%s"'%self.size
        else: sizestr=''
       
        return mark_safe(CLIENT_CODEJS % (name, html_id, sizestr, vv, name, html_id, value, html_id,
                                       lookup_url,  html_id))


    def value_from_datadict(self, data, files, name):
        """
        Given a dictionary of data and this widget's name, returns the value
        of this widget. Returns None if it's not provided.
        """

        return data.get(name, None)