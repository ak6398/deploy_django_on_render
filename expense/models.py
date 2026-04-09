from django.db import models

# Create your models here.
class UserDetail(models.Model):
    FullName = models.CharField(max_length=100)
    Email = models.EmailField(max_length=100, unique=True, db_index=True)  # ✅ Added index
    Password = models.CharField(max_length=50)
    RegDate = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.FullName

    class Meta:
        indexes = [
            models.Index(fields=['Email']),  
        ]
    
class Expense(models.Model):
    UserId = models.ForeignKey(UserDetail, on_delete=models.CASCADE, db_index=True)
    ExpenseDate = models.DateField(max_length=50, null=True, blank=True)
    ExpenseItem = models.CharField(max_length=100)
    ExpenseCost = models.CharField(max_length=100)
    NoteDate = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.ExpenseItem} {self.ExpenseCost}"

    class Meta:
        
        indexes = [
            models.Index(fields=['UserId']),
            models.Index(fields=['UserId', '-NoteDate']),  # For sorting/pagination
        ]
        #  Optimize queryset ordering
        ordering = ['-NoteDate']