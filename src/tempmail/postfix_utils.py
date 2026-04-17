"""
Script to update Postfix virtual mailbox maps whenever a new inbox is created
This is called whenever a new TempInbox is created
"""

import subprocess
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

VIRTUAL_MAILBOXES_FILE = '/etc/postfix/virtual_mailboxes'
VIRTUAL_ALIASES_FILE = '/etc/postfix/virtual_aliases'


def update_postfix_maps():
    """Update Postfix virtual mailbox and alias maps"""
    from tempmail.models import TempInbox
    
    try:
        # Get all active inboxes
        inboxes = TempInbox.objects.filter(is_expired=False)
        
        # Generate virtual_mailboxes content
        mailboxes_content = "# Virtual Mailbox Mapping for GeniusGsm\n"
        mailboxes_content += "# Format: user@domain username/\n"
        mailboxes_content += "# Auto-generated - do not edit manually\n\n"
        
        # Add catch-all at top
        mailboxes_content += "@geniusgsm.com @geniusgsm.com\n"
        
        for inbox in inboxes:
            username = inbox.email.split('@')[0]
            mailboxes_content += f"{inbox.email} {username}/\n"
        
        # Write mailboxes file
        with open(VIRTUAL_MAILBOXES_FILE, 'w') as f:
            f.write(mailboxes_content)
        
        logger.info(f"Updated {VIRTUAL_MAILBOXES_FILE} with {inboxes.count()} inboxes")
        
        # Compile the database
        result = subprocess.run(
            ['postmap', VIRTUAL_MAILBOXES_FILE],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            logger.error(f"Failed to postmap {VIRTUAL_MAILBOXES_FILE}: {result.stderr}")
            return False
        
        # Reload postfix
        result = subprocess.run(
            ['postfix', 'reload'],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            logger.error(f"Failed to reload postfix: {result.stderr}")
            return False
        
        logger.info("Postfix maps updated and reloaded successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error updating postfix maps: {e}")
        return False


if __name__ == '__main__':
    update_postfix_maps()
