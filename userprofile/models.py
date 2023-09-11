from django.contrib.auth.models import User
from django.db import models
from django.core.validators import FileExtensionValidator


class  Userprofile(models.Model):
    user = models.OneToOneField(User, related_name='userprofile', on_delete=models.CASCADE)
    image = models.ImageField(default='default.jpg', upload_to='profile', validators=[FileExtensionValidator(['png', 'jpg'])])
    is_vendor = models.BooleanField(default=False)
    def __str__(self):
        return self.user.username 
    



