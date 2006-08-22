# -----------------------
# Web application example
# -----------------------

def web_app(request):
    """Get the user's friends and their pictures. This example uses
       the Django web framework, but should be adaptable to others."""

    # Get api_key and secret_key from a file
    fbs = open(FB_SETTINGS).readlines()
    fb = Facebook(fbs[0].strip(), fbs[1].strip())

    # Use the data from the cookie if present
    if 'session_key' in request.session and 'uid' in request.session:
        fb.session_key = request.session['session_key']
        fb.uid = request.session['uid']
    else:
        
        try:
            fb.auth_token = request.GET['auth_token']
        except KeyError:
            # Send user to the Facebook to login
            return HttpResponseRedirect(fb.get_login_url())

        # getSession sets the session_key and uid
        # Store these in the cookie so we don't have to get them again
        fb.auth_getSession()
        request.session['session_key'] = fb.session_key
        request.session['uid'] = fb.uid

    try:
        friend_ids = fb.friends_get()
    except FacebookError, e:
        # Error 102 means the session has expired.
        # Delete the cookie and send the user to Facebook to login
        if e.info['code'] == u'102':
            del request.session['session_key']
            del request.session['uid']
            return HttpResponseRedirect(fb.get_login_url())
        else:
            # Other Facebook errors are possible too. Don't ignore them.
            raise
        
    info = fb.users_getInfo(friend_ids, ['name', 'pic'])
    # info is a list of dictionaries

    # you would never do this in an actual Django application,
    # it's just an example of accessing the results.
    links = []
    for friend in info:
        html = '<a href="%(pic)s">%(name)s</a>' % friend
        links.append(html)

    return render_to_response('template.html', {'links': links})

# ---------------------------
# Desktop application example
# ---------------------------

def desktop_app():
    
    # Get api_key and secret_key from a file
    fbs = open(FB_SETTINGS).readlines()
    facebook = Facebook(fbs[0].strip(), fbs[1].strip())

	facebook.auth_createToken()
	# Show login window
	facebook.login()

	# Login to the window, then press enter
	print 'After logging in, press enter...'
	raw_input()

	facebook.auth_getSession()
	info = facebook.users_getInfo([facebook.uid], ['name', 'birthday', 'affiliations', 'gender'])[0]

	print 'Name: ', info['name']
	print 'ID: ', facebook.uid
	print 'Birthday: ', info['birthday']
	print 'Gender: ', info['gender']

	friends = facebook.friends_get()
	friends = facebook.users_getInfo(friends[0:5], ['name', 'birthday', 'relationship_status'])

	for friend in friends:
		print friend['name'], 'has a birthday on', friend['birthday'], 'and is', friend['relationship_status']

	arefriends = facebook.friends_areFriends([friends[0]['id']], [friends[1]['id']])

	photos = facebook.photos_getAlbums(friends[1]['id'])
	print photos
