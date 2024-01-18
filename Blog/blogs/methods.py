from django.utils.crypto import get_random_string
from better_profanity import profanity

def unique_slug_generator(instance, slug):
    posts = instance.__class__
    exist = posts.objects.filter(slug=slug).exists()
    if exist:
        new_slug = "{slug}-{randstr}".format(
                    slug=slug,
                    randstr=get_random_string(length=6)
                )
        return unique_slug_generator(instance, new_slug)
    return slug

def check_bad_words(text):
    count = 0
    words = text.split()
    for word in words:
        if profanity.contains_profanity(word):
            count += 1
    return count
