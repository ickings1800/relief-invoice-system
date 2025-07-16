from django.db import models


class MissingCompanyException(Exception):
    pass


class CompanyAwareManager(models.Manager):
    """
    Custom manager that ensures all queries are scoped to the company associated.
    """


def all(self):
    raise MissingCompanyException("This manager requires a company to be set")


def filter(self, *args, **kwargs):
    if "company_id" not in kwargs and "company" not in kwargs:
        raise MissingCompanyException(
            "company_id or company must be present as a keyword argument in CompanyAwareManager."
        )
    return super().filter(*args, **kwargs)
