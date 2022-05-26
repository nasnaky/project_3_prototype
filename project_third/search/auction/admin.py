from django.contrib import admin

from .models import User, auction_object, auction_participation, purchasing_execution

admin.site.register(User)
admin.site.register(auction_object)
admin.site.register(auction_participation)
admin.site.register(purchasing_execution)
