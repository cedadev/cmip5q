The CMIP5 Metadata Questionnaire
================================

A Django application which gathers detailed metadata about numerical models used in the
5th Coupled Model Intercomparrison Project (CMIP5)


Notes on refactored deployment
------------------------------

Post version 1.7 this application has been adapted to manage authorisation and  authentication in conjunction with dj_security_middleware[1].  The settings.py needs to be configured to use an external login service.  Authorisation groups are maintained in the Django auth database which is visible under the application path `/cmip5/auth`.  The module `cmip5q.protoq.policy` is a simple mapping between Centre ids and auth groups used to restrict access to each centre's questionnaire.

[1]: http://proj.badc.rl.ac.uk/ndg/browser/mauRepo/dj_security_middleware


TODO
----

**WARNING**: There is a hard-coded file reference to an XSLT document in ```cmip5q/cmip5q/xsl/schematron-report.xsl```.  This needs changing if the deployment is moved.

