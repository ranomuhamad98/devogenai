import http.client

from django.db import models


class API(models.Model):

    def get_employee():
        conn = http.client.HTTPSConnection("dummy.restapiexample.com")
        payload = ''
        headers = {}
        conn.request("GET", "/api/v1/employees", payload, headers)
        res = conn.getresponse()
        data = res.read()

        return data.decode("utf-8")

