import random
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from myapp.models import Profile, Post, LikePost, FollowersCount  # Adjust the imports if needed
import requests

class Command(BaseCommand):
    help = 'Generate sample user data, posts, likes, and followers'

    def handle(self, *args, **kwargs):
        self.create_users(100)
        self.create_posts(200)
        self.create_likes(300)
        self.create_followers(100)

    def create_users(self, count):
        for i in range(count):
            username = f'user{i}'
            password = 'password123'
            email = f'user{i}@example.com'
            
            # Check if the user already exists
            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(username=username, email=email, password=password)
                
                # Create a corresponding profile
                Profile.objects.create(user=user, bio=f'This is the bio of user{i}',id_user=user.id)
                self.stdout.write(self.style.SUCCESS(f'Created user {username}'))
            else:
                self.stdout.write(self.style.WARNING(f'Username {username} already exists. Skipping...'))

    def create_posts(self, count):
        users = list(User.objects.all())
        for i in range(count):
            user = random.choice(users)
            # Fetch a random image URL from the Lorem Picsum API
            image_url = self.get_random_image_url()
            Post.objects.create(
                user=user,
                image=image_url,
                caption=f'This is post {i} by {user.username}',
                no_of_likes=random.randint(0, 100)
            )
        self.stdout.write(self.style.SUCCESS(f'Created {count} posts.'))

    def get_random_image_url(self):
        # Fetch a random image URL from Lorem Picsum
        response = requests.get('https://picsum.photos/200')
        return response.url
    

    def create_likes(self, count):
        users = list(User.objects.all())
        posts = list(Post.objects.all())
        for i in range(count):
            user = random.choice(users)
            post = random.choice(posts)
            LikePost.objects.get_or_create(username=user.username, post_id=post.id)
        self.stdout.write(self.style.SUCCESS(f'Created {count} likes.'))

    def create_followers(self, count):
        users = list(User.objects.all())
        for i in range(count):
            follower = random.choice(users)
            followed = random.choice(users)
            if follower != followed:
                FollowersCount.objects.get_or_create(follower=follower, user=followed)
        self.stdout.write(self.style.SUCCESS(f'Created {count} follower relationships.'))
