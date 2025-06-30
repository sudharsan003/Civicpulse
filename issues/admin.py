from django.contrib import admin
from .models import Category, Issue
from django.core.mail import send_mail

# ✅ Define admin actions (for bulk updates)
def mark_as_resolved(modeladmin, request, queryset):
    for issue in queryset:
        old_status = issue.status
        issue.status = 'Resolved'
        issue.save()

        # 📧 Send email for each updated issue
        if issue.created_by.email and old_status != 'Resolved':
            send_mail(
                subject='✅ Your Issue Was Resolved!',
                message=f"Hi, your issue '{issue.title}' was marked as Resolved by an admin.",
                from_email=None,
                recipient_list=[issue.created_by.email],
                fail_silently=True,
            )

mark_as_resolved.short_description = "✅ Mark selected issues as Resolved"

def mark_as_in_progress(modeladmin, request, queryset):
    for issue in queryset:
        old_status = issue.status
        issue.status = 'In Progress'
        issue.save()

        if issue.created_by.email and old_status != 'In Progress':
            send_mail(
                subject='🛠️ Your Issue Is In Progress',
                message=f"Hi, your issue '{issue.title}' is now being worked on.",
                from_email=None,
                recipient_list=[issue.created_by.email],
                fail_silently=True,
            )

mark_as_in_progress.short_description = "🛠️ Mark selected issues as In Progress"

def reset_status_to_open(modeladmin, request, queryset):
    for issue in queryset:
        old_status = issue.status
        issue.status = 'Open'
        issue.save()

        if issue.created_by.email and old_status != 'Open':
            send_mail(
                subject='🔄 Your Issue Was Reopened',
                message=f"Hi, your issue '{issue.title}' status has been reset to Open.",
                from_email=None,
                recipient_list=[issue.created_by.email],
                fail_silently=True,
            )

reset_status_to_open.short_description = "🔁 Reset selected issues to Open"

# ✅ Category Admin
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']

# ✅ Issue Admin with status change tracking
@admin.register(Issue)
class IssueAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'category', 'location', 'status', 'created_by', 'created_at']
    list_display_links = ('title',)
    list_filter = ['status', 'category']
    search_fields = ['title', 'description', 'location']
    actions = [mark_as_resolved, mark_as_in_progress, reset_status_to_open]

    # 🔔 Track status changes and send email when updated manually
    def save_model(self, request, obj, form, change):
        if change:
            previous = Issue.objects.get(pk=obj.pk)
            if previous.status != obj.status:
                # ✅ Status was changed by admin
                if obj.created_by.email:
                    send_mail(
                        subject='🔔 Your Issue Status Changed',
                        message=f"Hi, your issue '{obj.title}' status changed from '{previous.status}' to '{obj.status}'.",
                        from_email=None,
                        recipient_list=[obj.created_by.email],
                        fail_silently=True,
                    )
        super().save_model(request, obj, form, change)
