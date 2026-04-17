"""
Django signals for TempMail app
Automatically update Postfix maps when new inboxes are created
"""

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import TempInbox
from .postfix_utils import update_postfix_maps
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=TempInbox)
def update_postfix_on_inbox_create(sender, instance, created, **kwargs):
    """Update Postfix maps whenever a new inbox is created"""
    if created:
        logger.info(f"New inbox created: {instance.email}, updating Postfix maps...")
        success = update_postfix_maps()
        if success:
            logger.info(f"✅ Postfix maps updated successfully")
        else:
            logger.error(f"❌ Failed to update Postfix maps for {instance.email}")


@receiver(post_delete, sender=TempInbox)
def update_postfix_on_inbox_delete(sender, instance, **kwargs):
    """Update Postfix maps whenever an inbox is deleted"""
    logger.info(f"Inbox deleted: {instance.email}, updating Postfix maps...")
    success = update_postfix_maps()
    if success:
        logger.info(f"✅ Postfix maps updated successfully")
    else:
        logger.error(f"❌ Failed to update Postfix maps after deletion")
