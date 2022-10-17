import cgi

form = cgi.FieldStorage()

user = form.getvalue('user')
password = form.getvalue('pass')
confirmedPassword = form.getvalue('confPass')

print(user + ' ' + password)


