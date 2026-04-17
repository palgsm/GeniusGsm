"""
Dovecot Mail Reader Module
Reads email directly from Dovecot Maildir storage
"""
import os
import email
from pathlib import Path
from email.parser import BytesParser
from email.policy import default
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

VMAIL_ROOT = "/var/vmail/geniusgsm.com"


class DovecotMailReader:
    """Read emails directly from Dovecot Maildir format"""
    
    @staticmethod
    def get_inbox_path(username: str) -> Path:
        """Get the INBOX path for a user"""
        return Path(VMAIL_ROOT) / username / "new"
    
    @staticmethod
    def get_archive_path(username: str) -> Path:
        """Get the archive (cur) path for a user"""
        return Path(VMAIL_ROOT) / username / "cur"
    
    @staticmethod
    def list_users() -> List[str]:
        """List all users in the Dovecot mailbox"""
        try:
            vmail_path = Path(VMAIL_ROOT)
            if not vmail_path.exists():
                return []
            
            users = [
                d.name for d in vmail_path.iterdir()
                if d.is_dir() and (d / "new").exists()
            ]
            return sorted(users)
        except Exception as e:
            logger.error(f"Error listing users: {e}")
            return []
    
    @staticmethod
    def get_email_files(username: str, include_read: bool = True) -> List[Tuple[Path, bool]]:
        """
        Get all email files for a user
        Returns list of (path, is_new) tuples
        """
        files = []
        
        # Get new (unread) emails
        new_path = DovecotMailReader.get_inbox_path(username)
        if new_path.exists():
            for file in new_path.glob("*"):
                if file.is_file():
                    files.append((file, True))
        
        # Get archived (read) emails if requested
        if include_read:
            cur_path = DovecotMailReader.get_archive_path(username)
            if cur_path.exists():
                for file in cur_path.glob("*"):
                    if file.is_file():
                        files.append((file, False))
        
        return sorted(files, key=lambda x: x[0].stat().st_mtime, reverse=True)
    
    @staticmethod
    def parse_email(file_path: Path) -> Optional[Dict]:
        """Parse an email file and extract its content"""
        try:
            with open(file_path, 'rb') as f:
                parser = BytesParser(policy=default)
                message = parser.parse(f)
            
            # Extract email data
            subject = message.get('Subject', '(No Subject)')
            from_addr = message.get('From', 'unknown@unknown.com')
            to_addr = message.get('To', '')
            date_str = message.get('Date', '')
            message_id = message.get('Message-ID', '')
            
            # Parse body
            body_text = ''
            body_html = ''
            
            if message.is_multipart():
                for part in message.walk():
                    if part.get_content_type() == 'text/plain':
                        body_text = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                    elif part.get_content_type() == 'text/html':
                        body_html = part.get_payload(decode=True).decode('utf-8', errors='ignore')
            else:
                if message.get_content_type() == 'text/plain':
                    body_text = message.get_payload(decode=True).decode('utf-8', errors='ignore')
                elif message.get_content_type() == 'text/html':
                    body_html = message.get_payload(decode=True).decode('utf-8', errors='ignore')
            
            # Get file stats
            file_stats = file_path.stat()
            
            return {
                'filename': file_path.name,
                'path': str(file_path),
                'subject': subject,
                'from': from_addr,
                'to': to_addr,
                'date': date_str,
                'message_id': message_id,
                'body_text': body_text.strip(),
                'body_html': body_html.strip(),
                'size_bytes': file_stats.st_size,
                'received_at': datetime.fromtimestamp(file_stats.st_mtime),
            }
        except Exception as e:
            logger.error(f"Error parsing email {file_path}: {e}")
            return None
    
    @staticmethod
    def get_user_emails(username: str, include_read: bool = True) -> List[Dict]:
        """Get all emails for a user"""
        emails = []
        
        files = DovecotMailReader.get_email_files(username, include_read)
        for file_path, is_new in files:
            email_data = DovecotMailReader.parse_email(file_path)
            if email_data:
                email_data['is_new'] = is_new
                emails.append(email_data)
        
        return emails
    
    @staticmethod
    def move_to_archive(username: str, filename: str) -> bool:
        """Move email from new to cur (mark as read)"""
        try:
            new_path = DovecotMailReader.get_inbox_path(username) / filename
            cur_path = DovecotMailReader.get_archive_path(username) / (filename + ":2,")
            
            if new_path.exists():
                new_path.rename(cur_path)
                logger.info(f"Moved {filename} to archive for {username}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error moving email to archive: {e}")
            return False
    
    @staticmethod
    def delete_email(username: str, filename: str) -> bool:
        """Delete an email file"""
        try:
            new_path = DovecotMailReader.get_inbox_path(username) / filename
            cur_path = DovecotMailReader.get_archive_path(username) / filename
            
            if new_path.exists():
                new_path.unlink()
                logger.info(f"Deleted {filename} from new for {username}")
                return True
            elif cur_path.exists():
                cur_path.unlink()
                logger.info(f"Deleted {filename} from cur for {username}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting email: {e}")
            return False
    
    @staticmethod
    def get_email_count(username: str) -> int:
        """Get total email count for a user"""
        emails = DovecotMailReader.get_email_files(username, include_read=True)
        return len(emails)
    
    @staticmethod
    def get_unread_count(username: str) -> int:
        """Get unread email count for a user"""
        emails = DovecotMailReader.get_email_files(username, include_read=False)
        # Only count files in 'new' directory
        return sum(1 for _, is_new in emails if is_new)
