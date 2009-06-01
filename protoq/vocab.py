def vocab(listv,term,relationship):
    ''' For a given term in a list, find relationships - dummy example'''
    lists={'components':(
        ('gcm','component','atmosphere'),
        ('atmosphere','component','radiation'),
        ('atmosphere','component','advection'),
        ('radiation','component','lw'),
        ('radiation','component','sw'))}
    if listv not in lists: return None
    r=[]
    for i in lists['listv']:
        if i[0]==term:r.append(i[1])
    return r