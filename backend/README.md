


Start environment:

```
pipenv install
pipenv shell
```


Prepare database models:

```
python manage.py makemigrations
python manage.py migrate
```


Load database with test data:

```
python manage.py flush
python load_data.py
```

Interact with orm:

```
python manage.py shell_plus
>>> groups = DocumentGroup.objects.all()
>>> groups[0].document_set.all()
>>> for group in groups:
>>>     bytes = sum([grp.bytes for grp in group.document_set.all()])
>>>     group.bytes = bytes
```

Run the server:

```
python manage.py runserver
```
