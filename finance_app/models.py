from django.db import models
from django.contrib.auth.models import User

# Categories fixed or expandable
CATEGORY_CHOICES = [
    ('Food', 'Food'),
    ('Rent', 'Rent'),
    ('Travel', 'Travel'),
    ('Utilities', 'Utilities'),
    ('Salary', 'Salary'),
    ('Other', 'Other'),
]

class Category(models.Model):
    name = models.CharField(max_length=50)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    type = models.CharField(max_length=10, choices=[('Income', 'Income'), ('Expense', 'Expense')])
    date = models.DateField()
    notes = models.TextField(blank=True, null=True)
    is_recurring = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.title} | {self.amount} ({self.type})"


    class Meta:
        ordering = ['-date']
