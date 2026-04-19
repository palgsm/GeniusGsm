from django.db import models

class EmailCheck(models.Model):
    email = models.EmailField()
    is_valid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.email
