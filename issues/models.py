from django.db import models
from django.contrib.auth.models import User

# 🏷️ Category Model
class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


# 📌 Main Issue Model
class Issue(models.Model):
    STATUS_CHOICES = [
        ('Open', 'Open'),
        ('In Progress', 'In Progress'),
        ('Resolved', 'Resolved'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)

    location = models.CharField(max_length=255)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Open')

    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='issues')
    created_at = models.DateTimeField(auto_now_add=True)

    # ✅ NEW: When it got resolved (for timeline tracking)
    resolved_at = models.DateTimeField(null=True, blank=True)

    upvotes = models.ManyToManyField(User, related_name='issue_upvotes', blank=True)

    def vote_count(self):
        return self.upvotes.count()

    def __str__(self):
        return f"{self.title} ({self.status})"


# 🖼️ Supporting Multiple Images
class IssueImage(models.Model):
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='issue_images/')

    def __str__(self):
        return f"Image for {self.issue.title}"


# 💬 Threaded Comment Model
class Comment(models.Model):
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()
    parent = models.ForeignKey('self', null=True, blank=True, related_name='replies', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']  # 📅 Ensure consistent comment order

    def __str__(self):
        return f'Comment by {self.author.username} on {self.issue.title}'
