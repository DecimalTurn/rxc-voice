from django.contrib import admin

from .models import (Election, Proposal, Delegate)

# Register your models here.

admin.site.register(Election)
admin.site.register(Proposal)
admin.site.register(Delegate)
# admin.site.register(AnonVoter)
