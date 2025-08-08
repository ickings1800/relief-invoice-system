from django.db import models
from django.http import Http404


class MissingCompanyException(Exception):
    pass


class CompanyAwareManager(models.Manager):
    """
    Custom manager that ensures all queries are scoped to the company associated.
    """

    def all(self):
        raise MissingCompanyException("This manager requires a company to be set")

    def get(self, *args, **kwargs):
        if "company_id" not in kwargs and "company" not in kwargs:
            raise MissingCompanyException(
                "company_id or company must be present as a keyword argument in CompanyAwareManager."
            )
        return super().get(*args, **kwargs)

    def filter(self, *args, **kwargs):
        if "company_id" not in kwargs and "company" not in kwargs:
            raise MissingCompanyException(
                "company_id or company must be present as a keyword argument in CompanyAwareManager."
            )
        return super().filter(*args, **kwargs)


def get_company_from_request(request):
    """
    Extract company from request context.
    This should be adapted based on your authentication system.
    """
    from .models import Company

    freshbooks_account_id = request.session.get("freshbooks_account_id")
    if hasattr(request, "user") and request.user.is_authenticated:
        try:
            if freshbooks_account_id:
                return Company.objects.filter(freshbooks_account_id=freshbooks_account_id).first()
        except Company.DoesNotExist:
            raise Http404("Company not found")
    raise Http404("User not authenticated or company not found in session")


def get_object_or_404_with_company(model, company, **kwargs):
    """
    Secure replacement for get_object_or_404 with company filtering.
    """
    obj = model.objects.filter(company=company, **kwargs).first()
    if not obj:
        raise Http404(f"{model.__name__} not found")
    return obj
