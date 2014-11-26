# -*- coding: utf-8 -*-
from django.conf import settings

from django.core.urlresolvers import reverse
from django.template import loader
from django.http import HttpResponse,HttpResponseRedirect,HttpResponseBadRequest
from django.core.exceptions import ObjectDoesNotExist

from django.db.models import Q
from django.template.loader import render_to_string
from django.utils.cache import add_never_cache_headers
from django.utils import simplejson
from django.contrib.auth.models import User

import uuid

logging=settings.LOG


def get_datatables_records(request, querySet, columnIndexNameMap, 
                           jsonTemplatePath = None, *args):
    """
    Usage: 
        querySet: query set to draw data from.
        columnIndexNameMap: field names in order to be displayed.
        jsonTemplatePath: optional template file to generate custom json from.  
                          If not provided it will generate the data directly 
                          from the model.
    """
    
    cols = int(request.GET.get('iColumns',0)) # Get the number of columns
    iDisplayLength =  min(int(request.GET.get('iDisplayLength',10)),100)     #Safety measure. If someone messes with iDisplayLength manually, we clip it to the max value of 100.
    startRecord = int(request.GET.get('iDisplayStart',0)) # Where the data starts from (page)
    endRecord = startRecord + iDisplayLength  # where the data ends (end of page)
    
    # Pass sColumns
    keys = columnIndexNameMap.keys()
    keys.sort()
    colitems = [columnIndexNameMap[key] for key in keys]
    sColumns = ",".join(map(str,colitems))
    
    # Ordering data
    iSortingCols =  int(request.GET.get('iSortingCols',0))
    asortingCols = []
        
    if iSortingCols:
        for sortedColIndex in range(0, iSortingCols):
            sortedColID = int(request.GET.get('iSortCol_'+str(sortedColIndex),0))
            if request.GET.get('bSortable_{0}'.format(sortedColID), 'false')  == 'true':  # make sure the column is sortable first
                sortedColName = columnIndexNameMap[sortedColID]
                sortingDirection = request.GET.get('sSortDir_'+str(sortedColIndex), 'asc')
                if sortingDirection == 'desc':
                    sortedColName = '-'+sortedColName
                asortingCols.append(sortedColName) 
        querySet = querySet.order_by(*asortingCols)

    # Determine which columns are searchable
    searchableColumns = []
    for col in range(0,cols):
        if request.GET.get('bSearchable_{0}'.format(col), False) == 'true': searchableColumns.append(columnIndexNameMap[col])

    # Apply filtering by value sent by user
    customSearch = request.GET.get('sSearch', '').encode('utf-8');
    if customSearch != '':
        outputQ = None
        first = True
        for searchableColumn in searchableColumns:
            kwargz = {searchableColumn+"__icontains" : customSearch}
            outputQ = outputQ | Q(**kwargz) if outputQ else Q(**kwargz)        
        querySet = querySet.filter(outputQ)

    # Individual column search 
    outputQ = None
    for col in range(0,cols):
        if request.GET.get('sSearch_{0}'.format(col), False) > '' and request.GET.get('bSearchable_{0}'.format(col), False) == 'true':
            kwargz = {columnIndexNameMap[col]+"__icontains" : request.GET['sSearch_{0}'.format(col)]}
            outputQ = outputQ & Q(**kwargz) if outputQ else Q(**kwargz)
    if outputQ: querySet = querySet.filter(outputQ)
        
    iTotalRecords = iTotalDisplayRecords = querySet.count() #count how many records match the final criteria
    querySet = querySet[startRecord:endRecord] #get the slice
    sEcho = int(request.GET.get('sEcho',0)) # required echo response
    
    if jsonTemplatePath:
        jstonString = render_to_string(jsonTemplatePath, locals()) #prepare the JSON with the response, consider using : from django.template.defaultfilters import escapejs
        response = HttpResponse(jstonString, mimetype="application/javascript")
    else:
        aaData = []
        a = querySet.values() 
        for row in a:
            rowkeys = row.keys()
            rowvalues = row.values()
            rowlist = []
            for col in range(0,len(colitems)):
                for idx, val in enumerate(rowkeys):
                    if val == colitems[col]:
                        rowlist.append(str(rowvalues[idx]))
            aaData.append(rowlist)
        response_dict = {}
        response_dict.update({'aaData':aaData})
        response_dict.update({'sEcho': sEcho, 'iTotalRecords': iTotalRecords, 'iTotalDisplayRecords':iTotalDisplayRecords, 'sColumns':sColumns})
        response =  HttpResponse(simplejson.dumps(response_dict), mimetype='application/javascript')
    #prevent from caching datatables result
    add_never_cache_headers(response)
    return response



class HTMLdate:
    ''' 
    Handle an HTML date and convert h,m,d into seconds. Used as a mixin 
    class to aid serialisation etc, and usable in other applications too 
    '''
    def __init__(self):
        pass
    def fromstr(self,string):
        '''Load from an HTML encoded string'''
        #1960-09-01T00:00:00Z
        # or -19000-01-01T00:00:00Z
        try:
            d,t=string.strip().split('T')
            bits=d.split('-')
            if len(bits)==3:
                self.yyyy,self.mm,self.dd=bits
            else: 
                self.yyyy,self.mm,self.dd=bits[1:]
                self.yyyy='-'+self.yyyy
            h,m,s=t.split(':')
            ss=int(h)*3600+int(m)*60+int(s[0:-1])# get rid of trailing Z
        except Exception,e:
            raise ValueError('Not a valid HTML time date "%s" (%s)'%(string,e))
    def tostr(self):
        '''Serialise to an HTML encoded string '''
        h=self.ss/3600
        hs=h*3600
        m=(self.ss-hs)/60
        s=self.ss-(hs+m*60)
        return '%s-%s-%sT%s-%s-%sZ'%(self.yyyy,self.mm,self.dd,h,m,s)
       
def atomuri():
    ''' Return a uri, put here in one place ... just in case '''
    return '%s'%uuid.uuid1()

def render_badrequest(template,variables):
    """
    Returns a HttpResponseBadRequest whose content is filled with the result of calling
    django.template.loader.render_to_string() with the passed arguments.
    """
    
    httpresponse_kwargs = {'mimetype':'text/html'}
    
    return HttpResponseBadRequest(loader.render_to_string(template,variables), **httpresponse_kwargs)

def gracefulNotFound(method):
    ''' Used to decororate view methods to handle not found gracefully '''
    def trap(*args,**kwargs):
        try:
            return method(*args,**kwargs)
        except ObjectDoesNotExist,e:
            return render_badrequest('error.html',{'message':e})
    return trap

def RemoteUser(request,document):
    ''' Assign a metadata maintainer if we have one '''
    key='REMOTE_USER'
    #if key in request.META:
        #user=request.META[key]
        #document.metadataMaintainer=ResponsibleParty( ...)
        #document.save()
    return document

class RingBuffer:
    def __init__(self, size):
        self.data = [None for i in xrange(size)]
    def append(self, x):
        self.data.pop(0)
        self.data.append(x)
    def get(self):
        return self.data

def sublist(alist,n):
    ''' Take a list, and return a list of lists, where each of the sublists has n members
    except possibly the last '''
    nn=len(alist)
    nsubs=nn/n
    fragment=0
    if nsubs*n<nn:fragment=1
    blist=[]
    for i in range(nsubs):
        blist.append(alist[i*n:(i+1)*n])
    if fragment:
        blist.append(alist[nsubs*n:])
    return blist


def get_user(request):
    """
    Get and return the user from username, userid or authenticated_user
    object in request.authenticated_user.

    @param request: django request object
    @return: If the user is authenticated return an instance of User
    @type return: django Model object or None
    """
    import json

    try:
        override_user = settings.SECURITY_OVERRIDE_USER
        if override_user:
            logging.debug('User override enabled, user set to %s' % override_user)
            return User.objects.get(username=override_user)
        else:
            raise Exception
    except:
        pass

    try:
        user_data = json.loads(request.authenticated_user['user_data'])
        username = user_data['userkey']
        logging.debug('Getting user from dj_security_middleware.  username=%s' % username)

        return User.objects.get(username=username)
    except Exception:
        return None

def check_user_authorised(request, centre_id):

    # Exported from NDG-security policy file
    centre_to_group = {
        1: 'cmip5q_ncas',
        3: 'cmip5q_ncar',
        5: 'cmip5q_mohc',
        7: 'cmip5q_gfdl',
        9: 'cmip5q_ipsl',
        11: 'cmip5q_mpim',
        13: 'cmip5q_admin',
        15: 'cmip5q_any',
        17: 'cmip5q_norclim',
        19: 'cmip5q_mri',
        21: 'cmip5q_utnies',
        23: 'cmip5q_inm',
        25: 'cmip5q_nimr',
        27: 'cmip5q_lasg',
        29: 'cmip5q_csiro',
        31: 'cmip5q_cnrm_cerfacs',
        33: 'cmip5q_cccma',
        35: 'cmip5q_cawcr',
        39: 'cmip5q_any',
        37: 'cmip5q_cmabcc',
        41: 'cmip5q_ecearth',
        113: 'cmip5q_nasagiss',
        121: 'cmip5q_ccsm',
        123: 'cmip5q_cmcc',
        125: 'cmip5q_gcess',
        127: 'cmip5q_fio',
        129: 'cmip5q_rsmas',
        202: 'cmip5q_ncep',
        209: 'cmip5q_nasagmao',
        211: 'cmip5q_lasg',
        217: 'cmip51_inpe',
        }

    centre_id = int(centre_id)
    centre_group = centre_to_group[centre_id]
    logging.debug('check_user_authorised: centre_id = %d, centre_group = %s' % 
                  (centre_id, centre_group))
    if centre_group == 'cmip5q_any':
        logging.debug('check_user_authorised: centre_id policy is ANY => ALLOW')
        return True

    user = get_user(request)
    if user is None:
        logging.debug('check_user_authorised: no valid user => DENY')
        return False

    user_groups = [g.name for g in user.groups.iterator()]
    logging.debug('check_user_authorised: User %s has groups %s' % 
                  (user.username, user_groups))
    if 'cmip5q_all' in user_groups:
        logging.debug('check_user_authorised: in group cmip5q_all => ALLOW')
        return True
    
    if centre_group in user_groups:
        logging.debug('check_user_authorised: in group %s => ALLOW' % 
                      centre_group)
        return True
    else:
        logging.debug('check_user_authorised: not in group %s => DENY' %
                      centre_group)
        return False
