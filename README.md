cspace-django-project
====================

This is a simple example Django project that can be configured to connect to an instance
of the CollectionSpace services.

This is essentially an archetype for creating Django projects (websites) that are
setup to run CollectionSpace-related webapp applications.

It comes with an example webapp, named "service",
which essentially is a proxy for calls to the CollectionSpace services layer.

So instead of:

https://pahma.cspace.berkeley.edu/cspace-services/collectionobjects/f235fa96-3ebb-4c66-812f-1142f46fa966

you can allow (authentication or unauthenticated) connections to the same object at:

https://my.example.server/cspace_django_project/service/collectionobjects/f235fa96-3ebb-4c66-812f-1142f46fa966

The use of the "back-end" CollectionSpace authentication provider is optional, but is the main reason for
existence of this Django project.

See the README.txt file in the /cspace_django_site/authn directory for instructions on setting it up.
