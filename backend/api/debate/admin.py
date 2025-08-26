from django.contrib import admin
from .models import Room, Theme, Participate, Comment, CommentReadStatus, AIFeedbackSummary,AIFeedbackPrivate

# Register your models here.
admin.site.register(Room)
admin.site.register(Theme)
admin.site.register(Participate)
admin.site.register(Comment)
admin.site.register(CommentReadStatus) 
admin.site.register(AIFeedbackSummary)
admin.site.register(AIFeedbackPrivate)

