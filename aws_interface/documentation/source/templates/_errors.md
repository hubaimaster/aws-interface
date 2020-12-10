# Errors

The AWS Interface uses the following error codes:


Error Code | Message
---------- | -------
{% for error in errors %}{{error.code}} | {{error.message}}
{% endfor %}
