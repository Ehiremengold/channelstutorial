from django.db import models
from django.conf import settings
from django.urls import reverse
from django.utils.timezone import now
User = settings.AUTH_USER_MODEL

# Category


class Category(models.Model):
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True)

    class Meta:
        verbose_name_plural = "categories"
        ordering = ('name', )

    def get_absolute_url(self):
        return reverse('post_by_category', args=[self.slug])

    def __str__(self):
        return self.name


class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='author')
    slug = models.SlugField(max_length=200, unique=True, editable=False)
    content = models.TextField(max_length=200, blank=True)
    file = models.FileField(upload_to="media_contents/")
    created = models.DateTimeField(auto_now_add=True, editable=False)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)


    def get_post_file_filename(self):
        return str(self.file)[str(self.file).index(f'Post_File/{self.pk}/'):]

    def get_delete_url(self):
        return f"{self.slug}/delete"

    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return self.author


