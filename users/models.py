"""customized user model
"""
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin

from map.models import ParkingSpace
from .managers import UserManager


# * Create your models here.
class User(AbstractBaseUser, PermissionsMixin):
    """customized user class"""

    email = models.EmailField(verbose_name="email", max_length=60, unique=True)
    username = models.CharField(max_length=30, unique=True)
    date_joined = models.DateTimeField(verbose_name="Date Joined", default=timezone.now)
    # * Save an avatar image for a user in path avatars/<username>_avatar
    avatar = models.ImageField(
        upload_to="avatars/",
        height_field=None,
        width_field=None,
        max_length=101,
        default="avatars/ParKrowdDefaultAvatar.jpg",
    )

    description = models.TextField(blank=True)

    # * is_superuser : User can create, edit, and delete ANY object (models)
    is_superuser = models.BooleanField(default=False)
    # * is_staff : User can login to site
    is_staff = models.BooleanField(default=False)
    # * is_admin : User is treated as non-superuser staff member.
    # * Admins can be customized to have certain permissions.
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    # * is_verified: To indicate whether the user has been verified by Admin
    is_verified = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

    def __str__(self):
        return f"Email: {self.email}\n" f"Username: {self.username}\n"

    @staticmethod
    def has_perm(perm, obj=None, **kwargs):
        """TODO: why overriding the original implementation here"""
        return True

    @staticmethod
    def has_module_perms(app_label, **kwargs):
        """TODO: why overriding the original implementation here"""
        return True


class Post(models.Model):
    title = models.CharField(max_length=200)
    post = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(verbose_name="Date created", default=timezone.now)
    parking_space = models.ForeignKey(ParkingSpace, on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class Comment(models.Model):
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    created_at = models.DateTimeField(verbose_name="Date created", default=timezone.now)

    def __str__(self):
        return (
            f"Comment created by {self.author.username} under Post '{self.post.title}'"
        )


class UserVerification(models.Model):
    status_list = [
        ("submitted", "Submitted"),
        ("in_progress", "In progress"),
        ("cancelled", "Cancelled"),
        ("verified", "Verified"),
    ]
    username = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="verification"
    )
    business_name = models.CharField(max_length=200)
    business_type = models.CharField(max_length=200)
    business_address = models.CharField(max_length=200)
    uploaded_file = models.FileField(upload_to="verification_files/")
    submitted_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(default=timezone.now, editable=False)
    status = models.CharField(max_length=200, choices=status_list, default="submitted")

    def save(self, *args, **kwargs):
        # Update the updated_at whenever the object is saved / modified
        self.updated_at = timezone.now()
        super(UserVerification, self).save(*args, **kwargs)

    class Meta:
        # Set the default ordering to be the descending order of submission time
        ordering = ["-submitted_at"]


class UserWatchedParkingSpace(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    parking_space = models.ForeignKey(
        ParkingSpace,
        on_delete=models.CASCADE,
    )
    threshold = models.IntegerField(default=80)
