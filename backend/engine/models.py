"""Placeholder models for SHAND engine.

For the MVP we do not persist assumptions, but these models document
future storage design and make the codebase reviewable.
"""
from django.db import models


class AssumptionRecord(models.Model):
    text = models.TextField()
    type = models.CharField(max_length=50)
    risk = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "engine"
