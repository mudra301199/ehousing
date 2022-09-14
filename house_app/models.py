from django.db import models

class UserRole(models.Model):
    Role = models.CharField(max_length=10)

    class Meta:
        db_table = 'userrole'

    def __str__(self) -> str:
        return self.Role

class Master(models.Model):
    UserRole = models.ForeignKey(UserRole, on_delete=models.CASCADE)
    Email = models.EmailField(unique=True)
    Password = models.CharField(max_length=12)
    IsActive = models.BooleanField(default=False)
    RegDate = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'master'

    def __str__(self) -> str:
        return self.Email

gender_choices = (
    ('m', 'male'),
    ('f', 'female'),
)
class Profile(models.Model):
    Master = models.ForeignKey(Master, on_delete=models.CASCADE)
    ProfileImage = models.FileField(upload_to='profiles/', default='user.png')
    FullName = models.CharField(max_length=25, default='', blank=True)
    Gender = models.CharField(max_length=5, choices=gender_choices)
    BirthDate = models.DateField(auto_created=True, default='1991-01-01')
    Mobile = models.CharField(max_length=10, default='', blank=True)
    HouseNumber = models.CharField(max_length=10, default='', blank=True)
    Society = models.TextField(max_length=50, default='Trishul Society')
    Pincode = models.CharField(max_length=6, default='380008')
    City = models.CharField(max_length=25, default='Ahmedabad')
    Country = models.CharField(max_length=25, default='India')
    State = models.CharField(max_length=25, default='Gujarat')

    class Meta:
        db_table = 'profile'
    
class Visitor(models.Model):
    Master = models.ForeignKey(Master, on_delete=models.CASCADE)
    Gender = models.CharField(max_length=5, choices=gender_choices)
    Mobile = models.CharField(max_length=10, default='', blank=True)

    class Meta:
        db_table = 'visitor'

class Watchman(models.Model):
    Master = models.ForeignKey(Master, on_delete=models.CASCADE)
    ProfileImage = models.FileField(upload_to='profiles/', default='user.png')
    FullName = models.CharField(max_length=25, default='', blank=True)
    BirthDate = models.DateField(auto_created=True, default='1991-01-01')
    Gender = models.CharField(max_length=5, choices=gender_choices)
    Mobile = models.CharField(max_length=10, default='', blank=True)
    Address = models.TextField(max_length=150, default='', blank=True)

    class Meta:
        db_table = 'watchman'
