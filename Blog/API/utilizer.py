import argparse
import httpx

def create_request(verb, url, headers, data = None):
    with httpx.Client() as client:
            response = client.request(verb, url, headers = headers, json = data)
    if response.status_code in (200, 201, 202):
        return response.json()
    elif response.status_code == 204:
        return httpx.Response({'message': 'Deleted successfully'})
    return httpx.Response({'error_message': response})

def signup(args):
    url = 'http://127.0.0.1:8000/api/signup/'
    data = {
        "username": args.username,
        "email": args.email,
        "password": args.password,
    }
    headers = {
            'Content-Type': 'application/json',
        }
    return create_request('POST', url, headers=headers, data=data)
    
def login(args):
    url = 'http://127.0.0.1:8000/api/login/'
    data = {
        "username": args.username,
        "password": args.password,
    }
    headers = {
         'Content-Type': 'application/json'
    }
    return create_request('POST', url, headers=headers, data=data)
    
def list_posts(args):
    url = 'http://127.0.0.1:8000/api/get_posts/'
    headers = {
            'Content-Type': 'application/json',
        }
    return create_request('GET', url, headers=headers)

def get_post(args):
    url = f'http://127.0.0.1:8000/api/retireve_post/{args.slug}/'
    headers = {
        'Content-Type': 'application/json',
    }
    return create_request('GET', url, headers=headers)

def create_post(args):
    url = 'http://127.0.0.1:8000/api/create_post/'
    data = {
        "title": args.title,
        "body": args.body,
        "status": args.status
    }
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Token {args.token}'
    }
    return create_request('POST', url, headers=headers, data=data)

def delete_post(args):
    url = f'http://127.0.0.1:8000/api/delete_post/{args.slug}/'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Token {args.token}'
    }
    return create_request('DELETE', url, headers=headers)

def list_comments(args):
    url = f'http://127.0.0.1:8000/api/list-comments/{args.post}/'
    headers = {
        'Content-Type': 'application/json',
    }
    return create_request('GET', url, headers=headers)

def add_comment(args):
    url = f'http://127.0.0.1:8000/api/add-comment/'
    headers = {
        'Content-Type': 'application/json',
    }
    data = {
        "name": args.name,
        "email": args.email,
        "body": args.body,
        "post": args.post
    }
    return create_request('POST', url, headers=headers, data=data)

def main():
    parser = argparse.ArgumentParser(description='Blog API utilizer')

    subparsers = parser.add_subparsers(title='subcommands', dest='subcommand', required=True)

    parser_signup = subparsers.add_parser('signup', help='create new user')
    parser_signup.add_argument('--username', required=True, help='username for new account')
    parser_signup.add_argument('--email', required=True, help='email for new account')
    parser_signup.add_argument('--password', required=True, help='password for new account')

    parser_login = subparsers.add_parser('login', help='login')
    parser_login.add_argument('--username', required=True, help='username for your account')
    parser_login.add_argument('--password', required=True, help='password for your account')

    parser_add_post = subparsers.add_parser('create_post', help='create new post')
    parser_add_post.add_argument('--title', required=True, help='Your post title')
    parser_add_post.add_argument('--body', required=True, help='Your post body')
    parser_add_post.add_argument('--status', required=True, help='published or draft')
    parser_add_post.add_argument('--token', required=True, help='your account token')

    parser_list_posts = subparsers.add_parser('list_posts', help='get all posts')

    parser_get_post = subparsers.add_parser('get_post', help='get post')
    parser_get_post.add_argument('--slug', required=True, help='The post slug')

    parser_delete_post = subparsers.add_parser('delete_post', help='delete your post')
    parser_delete_post.add_argument('--slug', required=True, help='The post slug')
    parser_delete_post.add_argument('--token', required=True, help='your account token')

    parser_list_comments = subparsers.add_parser('list_comments', help='get comments of a post')
    parser_list_comments.add_argument('--post', required=True, help='The post id')

    parser_add_comment = subparsers.add_parser('create_comment', help='create new comment')
    parser_add_comment.add_argument('--name', required=True, help='Your name')
    parser_add_comment.add_argument('--email', required=True, help='your email')
    parser_add_comment.add_argument('--body', required=True, help='comment content')
    parser_add_comment.add_argument('--post', required=True, help='The post id')

    args = parser.parse_args()
    
    if args.subcommand == 'signup':
        print(signup(args))
    elif args.subcommand == 'login':
        print(login(args))
    elif args.subcommand == 'create_post':
        print(create_post(args))
    elif args.subcommand == 'list_posts':
        print(list_posts(args))
    elif args.subcommand == 'get_post':
        print(get_post(args))
    elif args.subcommand == 'delete_post':
        print(delete_post(args))
    elif args.subcommand == 'list_comments':
        print(list_comments(args))
    elif args.subcommand == 'create_comment':
        print(add_comment(args))
    

if __name__ == "__main__":
    main()
