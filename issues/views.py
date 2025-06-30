from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.db.models import Count, Q

from .forms import RegisterForm, IssueForm, CommentForm
from .models import Issue, IssueImage, Comment, Category
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from datetime import timedelta, datetime


# 🔐 Register
def register_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, 'register.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken.")
            return render(request, 'register.html')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
            return render(request, 'register.html')

        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()
        login(request, user)
        return redirect('issue_list')
    return render(request, 'register.html')


# 🔓 Login
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('issue_list')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'login.html')


# 🚪 Logout
def logout_view(request):
    logout(request)
    return redirect('login')


# 📝 Submit Issue
@login_required
def submit_issue(request):
    if request.method == 'POST':
        form = IssueForm(request.POST, request.FILES)
        images = request.FILES.getlist('images')

        if form.is_valid():
            issue = form.save(commit=False)
            issue.created_by = request.user

            try:
                issue.latitude = float(request.POST.get('latitude')) if request.POST.get('latitude') else None
                issue.longitude = float(request.POST.get('longitude')) if request.POST.get('longitude') else None
            except ValueError:
                form.add_error(None, "Please click a valid point on the map.")
                return render(request, 'submit_issue.html', {
                    'form': form,
                    'categories': Category.objects.all()
                })

            issue.save()

            for image in images[:5]:
                IssueImage.objects.create(issue=issue, image=image)

            return redirect('issue_list')
    else:
        form = IssueForm()

    return render(request, 'submit_issue.html', {
        'form': form,
        'categories': Category.objects.all()
    })


# 📋 Issue List with Filters, Comments & Threaded Replies
def issue_list(request):
    keyword = request.GET.get('q', '').strip()
    category_id = request.GET.get('category', '')
    status = request.GET.get('status', '')
    from_date = request.GET.get('from', '')
    to_date = request.GET.get('to', '')

    issues = Issue.objects.all()

    if keyword:
        issues = issues.filter(
            Q(title__icontains=keyword) | 
            Q(description__icontains=keyword) |
            Q(location__icontains=keyword) |
            Q(created_by__username__icontains=keyword)
        )

    if category_id:
        issues = issues.filter(category__id=category_id)

    if status:
        issues = issues.filter(status=status)

    # Date filtering
    if from_date:
        try:
            from_date_obj = datetime.strptime(from_date, '%Y-%m-%d').date()
            issues = issues.filter(created_at__date__gte=from_date_obj)
        except ValueError:
            pass  # Invalid date format, ignore

    if to_date:
        try:
            to_date_obj = datetime.strptime(to_date, '%Y-%m-%d').date()
            issues = issues.filter(created_at__date__lte=to_date_obj)
        except ValueError:
            pass  # Invalid date format, ignore

    issues = issues.annotate(vote_count=Count('upvotes')).order_by('-vote_count', '-created_at')

    # 💬 Handle comments (including threaded)
    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        issue_id = request.POST.get('issue_id')
        parent_id = request.POST.get('parent_id')  # New for replies

        if comment_form.is_valid() and issue_id:
            comment = comment_form.save(commit=False)
            comment.author = request.user
            comment.issue = get_object_or_404(Issue, id=issue_id)

            if parent_id:
                parent_comment = Comment.objects.filter(id=parent_id).first()
                if parent_comment and parent_comment.issue_id == int(issue_id):
                    comment.parent = parent_comment

            comment.save()

            # Optional: Send email to issue creator
            if comment.issue.created_by.email:
                send_mail(
                    subject='💬 New Comment on Your Issue',
                    message=f"A new comment was added to your issue: {comment.issue.title}\n\nComment: {comment.text}",
                    from_email=None,
                    recipient_list=[comment.issue.created_by.email],
                    fail_silently=True,
                )

            return redirect('issue_list')

    else:
        comment_form = CommentForm()

    return render(request, 'issue_list.html', {
        'issues': issues,
        'comment_form': comment_form,
        'categories': Category.objects.all(),
        'keyword': keyword,
        'selected_category': category_id,
        'selected_status': status,
        'from_date': from_date,
        'to_date': to_date
    })


# 👍 Upvote Toggle
@login_required
def upvote_issue(request, issue_id):
    issue = get_object_or_404(Issue, id=issue_id)
    user = request.user

    if user in issue.upvotes.all():
        issue.upvotes.remove(user)
    else:
        issue.upvotes.add(user)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'votes': issue.upvotes.count()})
    return redirect('issue_list')


# ✅ Mark Issue as Resolved
@login_required
def mark_issue_resolved(request, issue_id):
    issue = get_object_or_404(Issue, id=issue_id)
    if request.user == issue.created_by or request.user.is_superuser:
        issue.status = 'Resolved'
        issue.resolved_at = timezone.now()
        issue.save()

        if issue.created_by.email:
            send_mail(
                subject='✅ Your Issue Was Resolved!',
                message=f"Your issue '{issue.title}' has been marked as Resolved.",
                from_email=None,
                recipient_list=[issue.created_by.email],
                fail_silently=True,
            )
    return redirect('issue_list')


# 🗺️ Map Page
def issue_map(request):
    return render(request, 'map.html')


# 🌐 Map JSON API
def issue_data(request):
    issues = Issue.objects.all().values('id', 'title', 'status', 'latitude', 'longitude')
    return JsonResponse(list(issues), safe=False)


# 👤 My Issues
@login_required
def my_issues(request):
    issues = Issue.objects.filter(created_by=request.user).order_by('-created_at')
    return render(request, 'my_issues.html', {'issues': issues})

@login_required
def issue_detail(request, issue_id):
    issue = get_object_or_404(Issue, id=issue_id)
    now = timezone.now()

    if issue.status == 'Resolved' and issue.resolved_at:
        duration = issue.resolved_at - issue.created_at
        duration_text = f"✅ Resolved in {duration.days} days"
    else:
        duration_text = f"⏳ Open for {(now - issue.created_at).days} days"

    comment_form = CommentForm()
    top_level_comments = issue.comments.filter(parent__isnull=True)

    return render(request, 'issue_detail.html', {
        'issue': issue,
        'duration_text': duration_text,
        'comment_form': comment_form,
        'top_level_comments': top_level_comments
    })

@require_POST
@login_required
def ajax_post_comment(request):
    text = request.POST.get("text", "").strip()
    issue_id = request.POST.get("issue_id")
    parent_id = request.POST.get("parent_id")

    if not text or not issue_id:
        return JsonResponse({'error': 'Invalid input'}, status=400)

    issue = get_object_or_404(Issue, id=issue_id)
    parent = Comment.objects.filter(id=parent_id).first() if parent_id else None

    comment = Comment.objects.create(
        issue=issue,
        author=request.user,
        text=text,
        parent=parent
    )

    return JsonResponse({
        "id": comment.id,
        "author": comment.author.username,
        "text": comment.text,
        "parent_id": parent.id if parent else None,
        "created": comment.created_at.strftime("%d %b %Y %H:%M")
    })