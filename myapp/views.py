from django.shortcuts import render,redirect
from django.contrib.auth.models import User,auth
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

from django.contrib import messages
from .models import Profile,Post,LikePost,FollowersCount
from itertools import chain
import random

# Create your views here.


@login_required(login_url='signin')
def index(request):

    user_object=User.objects.get(username=request.user.username)
    user_profile=Profile.objects.get(user=user_object)

    feed=[]

    user_following=FollowersCount.objects.filter(follower=request.user.username)


    for following in user_following:
        feed_lists=Post.objects.filter(user=following)
        feed.append(feed_lists)
    
    feed_list=list(chain(*feed))

    user_all=User.objects.all()
    user_following_all=[]

    for user in user_following:
        users_list=User.objects.get(username=user.user)
        user_following_all.append(users_list)

    new_suggestions_list=[x for x in list(user_all) if (x not in list(user_following_all))]
    current_user=User.objects.get(username=request.user.username)
    final_suggestions_list=[x for x in list(new_suggestions_list) if (x is not current_user)]
    random.shuffle(final_suggestions_list)

    username_profile_lists=[]

    for user in final_suggestions_list:
        profile_lists=Profile.objects.filter(id_user=user.id)
        username_profile_lists.append(profile_lists)
    
    final_profile_lists=list(chain(*username_profile_lists))


    return render(request,'index.html', {'user_profile' : user_profile, 'posts':feed_list, 'suggestions_list': final_profile_lists[:4]})

@login_required(login_url='signin')
def profile(request,pk):

    user_object=User.objects.get(username=pk)
    user_profile=Profile.objects.get(user=user_object)
    user_posts=Post.objects.filter(user=pk)
    user_posts_length=len(user_posts)

    follower=request.user.username
    user=pk

    follower_indicator=FollowersCount.objects.filter(follower=follower,user=user).first()
    indicator=False

    if follower_indicator: 
        indicator=True

    followers=FollowersCount.objects.filter(user=pk)
    following=FollowersCount.objects.filter(follower=pk)

    followers_count=len(followers)
    following_count=len(following)

    context={
        'user_object':user_object,
        'user_profile':user_profile,
        'user_posts': user_posts,
        'user_posts_length':user_posts_length,
        'indicator' : indicator,
        'followers_count':followers_count,
        'following_count':following_count,
    }
    return render(request,'profile.html',context)

@login_required(login_url='signin')
def follow(request):
    follower=request.POST['follower']
    user=request.POST['user']

    if FollowersCount.objects.filter(follower=follower,user=user).first():
        follower_object=FollowersCount.objects.get(follower=follower,user=user)
        follower_object.delete()
        return redirect('/profile/'+user)
    else:
        new_follower=FollowersCount.objects.create(follower=follower,user=user)
        new_follower.save()
        return redirect('/profile/'+user)
    

@login_required(login_url='signin')
def search(request):

    user_object=User.objects.get(username=request.user.username)
    user_profile=Profile.objects.get(user=user_object)

    if request.method=='POST':
        username=request.POST['username']
        user_object=User.objects.filter(username__icontains=username)

        username_profile=[]
        username_profile_list=[]

        for user in user_object:
            username_profile.append(user.id)
        
        for user in user_object:
            profile_lists=Profile.objects.filter(id_user=user.id)
            username_profile_list.append(profile_lists)


        username_profile_lists=list(chain(*username_profile_list))

    return render(request,'search.html',{'user_profile':user_profile,'username_profile_lists':username_profile_lists})



@login_required(login_url='signin')
def like_post(request):
    username=request.user.username
    post_id=request.GET.get('post_id')

    post=Post.objects.get(id=post_id)
    like_filter=LikePost.objects.filter(username=username,post_id=post_id).first()



    if like_filter==None :
        new_like=LikePost.objects.create(username=username,post_id=post_id)
        new_like.save()
        post.no_of_likes=post.no_of_likes+1
        post.save()
        return redirect('/')
    else:
        like_filter.delete()
        post.no_of_likes=post.no_of_likes-1
        post.save()
        return redirect('/')



def signup(request):
    if request.method=="POST":
        username=request.POST['username']
        email=request.POST['email']
        password=request.POST['password']
        password2=request.POST['password2']

        if password==password2:
            if User.objects.filter(email=email).exists():
                messages.info(request, 'Email already taken')
                return redirect('signup')
            elif User.objects.filter(username=username).exists():
                messages.info(request, 'Username already taken')
                return redirect('signup')
            
            user=User.objects.create_user(username=username, email=email, password=password)
            user.save()

            user_login=auth.authenticate(username=username, password=password)
            auth.login(request,user_login)

            user_model=User.objects.get(username=username)
            new_profile=Profile.objects.create(user=user_model, id_user=user_model.id)
            new_profile.save()
            return redirect('settings')
        else:
            messages.info(request,'password not matching')
            return redirect('signup')

    else:
        return render(request,'signup.html')
    
@login_required(login_url='signin')
def upload(request):

    if request.method=="POST":
        user=request.user.username
        caption=request.POST['caption']
        image=request.FILES.get('image_upload')

        new_post=Post.objects.create(user=user,caption=caption,image=image)
        new_post.save()

    return redirect('/')

    
@login_required(login_url='signin')
def settings(request):

    user_profile=Profile.objects.get(user=request.user)


    if request.method=="POST" : 

        bio = request.POST['bio']
        location = request.POST['location']
        if request.FILES.get('image') ==None:
            image=user_profile.profileimg
        else:
            image=request.FILES.get('image')
        
        user_profile.bio=bio
        user_profile.location=location
        user_profile.profileimg=image
        user_profile.save()

        return redirect('settings')


    return render(request, 'setting.html', {'user_profile':user_profile})
    
    
def signin(request) : 
    if request.method=="POST":
        username=request.POST['username']
        password=request.POST['password']
        user=auth.authenticate(username=username, password=password)

        if user is not None:
            auth.login(request,user)
            return redirect('/')
        else :
            messages.info(request,'Credentials Invalid')
            return redirect('signin')
    else : 
        return render(request,'signin.html')

@login_required(login_url='signin')
def logout(request):
    auth.logout(request)
    return redirect('signin')
