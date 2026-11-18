from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Post, Comment
from accounts.utils import log_activity


@receiver(post_save, sender=Post)
def on_post_saved(sender, instance, created, **kwargs):
    action = "post_create" if created else "post_update"
    log_activity(
        None, action,
        user=instance.author,
        post_id=instance.pk,
        title=instance.title,
        status=instance.status,
    )


@receiver(post_delete, sender=Post)
def on_post_deleted(sender, instance, **kwargs):
    log_activity(
        None, "post_delete",
        user=instance.author,
        post_id=instance.pk,
        title=instance.title,
    )


@receiver(post_save, sender=Comment)
def on_comment_saved(sender, instance, created, **kwargs):
    if created:
        log_activity(
            None, "comment_create",
            user=instance.author,
            comment_id=instance.pk,
            post_id=instance.post_id,
            post_title=instance.post.title,
        )


@receiver(post_delete, sender=Comment)
def on_comment_deleted(sender, instance, **kwargs):
    log_activity(
        None, "comment_delete",
        user=instance.author,
        comment_id=instance.pk,
        post_title=instance.post.title,
    )