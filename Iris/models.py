# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.
from django.db import models
from django.utils.encoding import python_2_unicode_compatible

@python_2_unicode_compatible
class Master(models.Model):
    Room = models.PositiveIntegerField(primary_key=True, )
    Occupancy = models.IntegerField(blank=False)
    Occupied = models.IntegerField(blank=False, default=0)

    def __str__(self):
        return self.Room
