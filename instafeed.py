# quick and dirty - get a user's own pictures using the instagram API and flask
from flask import Flask, make_response, request, redirect
app = Flask(__name__)

import local_settings

CONFIG = {
    'client_id': local_settings.instagram_client_id,
    'client_secret': local_settings.instagram_client_secret,
    'redirect_uri': local_settings.instagram_redirect_uri
}

from instagram import client
unauthenticated_api = client.InstagramAPI(**CONFIG)

@app.route("/instas")
def instas():
    access_token = request.cookies.get('instagram_access_token')
    if not access_token or access_token == "":
        url = unauthenticated_api.get_authorize_url()
        redirect_to = redirect(url)
        resp = make_response(redirect_to)
        return resp
    else:
        return load_instas()

def load_instas_old():
    access_token = request.cookies.get('instagram_access_token')
    if not access_token:
        return "hmm...where's that damn access token?"
    api = client.InstagramAPI(access_token=access_token)
    counter = 0
    max_pages = 5
    photos = []
    for page, next in api.user_recent_media(as_generator=True):
        print page
        print next
        print counter
        counter = counter + 1
        if counter > max_pages: 
            break
        for r in page:
            photos.append('<img src="%s"/>' % r.images.get('low_resolution').url)
    return ''.join(photos)

def load_instas():
    photos = []
    access_token = request.cookies.get('instagram_access_token')
    if not access_token:
        return redirect_to_home()
    page, next = get_page(access_token)
    for r in page:
        photos.append('<img src="%s"/>' % r.images.get('low_resolution').url)
    photos.append('<a href="/instas">more</a>')
    return photos

def get_page(access_token):
    """generator that returns the next page of photos
    """
    api = client.InstagramAPI(access_token=access_token)
    for page, next in api.user_recent_media(as_generator=True):
        yield page, next

def redirect_to_home(reset_access_token=False):
    redirect_to = redirect('/instas')
    resp = make_response(redirect_to)
    if reset_access_token:
        resp.set_cookie('instagram_access_token', '')
    return resp

@app.route("/instas/oauth_callback")
def on_callback():
    if request.method != "GET":
        return "oops, can't POST here"
    code = request.args.get('code')
    if not code:
        return "dude, where's my code?"
    access_token = unauthenticated_api.exchange_code_for_access_token(code)
    if not access_token:
        return "couldn't exchange code for access token"
    # save the access token as a cookie
    redirect_to = redirect('/instas')
    resp = make_response(redirect_to)
    resp.set_cookie('instagram_access_token', access_token)
    return resp

if __name__ == '__main__':
    app.run(port=local_settings.port)
