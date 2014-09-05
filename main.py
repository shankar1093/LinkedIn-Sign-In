#linkedin button authentication. On clicking the button, it redirect to the link_auth function.
#go to linkedin developer network and get the required credentials
# CLIENT_ID = 
# CLIENT_SECRET = 
# REDIRECT_URI = 

from flask import Flask
from flask import render_template
from flask import request
from flask import Flask,redirect
import requests
import requests.auth


app = Flask(__name__)
@app.route('/')
def main_page():
    return render_template('index.html')

@app.route('/auth')
def homepage():
    text = '<a class=ui linkedin button" href="%s">Authenticate with linkedin</a>'
    return text % make_authorization_url()


#link auth uses the python-linkedin library. Use this for authentication.
@app.route('/link_auth')
def linkedin_auth():
  authentication = linkedin.LinkedInAuthentication(CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, linkedin.PERMISSIONS.enums.values())
  application = linkedin.LinkedInApplication(authentication)
  return redirect(authentication.authorization_url, code=302)


def make_authorization_url():
    # Generate a random string for the state parameter
    # Save it for use later to prevent xsrf attacks
    from uuid import uuid4
    state = str(uuid4())
    save_created_state(state)
    params = {"response_type": "code",
    		      "client_id": CLIENT_ID,	
              "state": state,
              "scope":"r_fullprofile r_emailaddress r_contactinfo rw_nus",
              "redirect_uri": REDIRECT_URI
	}
    import urllib
    url = "https://www.linkedin.com/uas/oauth2/authorization?" + urllib.urlencode(params)
    return url


# Left as an exercise to the reader.
# You may want to store valid states in a database or memcache,
# or perhaps cryptographically sign them and verify upon retrieval.
def save_created_state(state):
    pass
def is_valid_state(state):
    return True

from flask import abort, request
@app.route('/linkedin_callback')
def linkedin_callback():
	error = request.args.get('error', '')
	if error:
		return "Error: " + error
	state = request.args.get('state', '')
	if not is_valid_state(state):
		#uh-oh, this request wasn't started by us!
		abort(403)
	code = request.args.get('code')
	access_token = get_token(code)
	return get_skills(access_token)

import requests
import requests.auth
def get_token(code):
    # client_auth = requests.auth.HTTPBasicAuth(CLIENT_ID, CLIENT_SECRET)
    post_data = {"code": code,
                 "redirect_uri": REDIRECT_URI,
                 "client_id":CLIENT_ID,
                 "client_secret":CLIENT_SECRET}
    response = requests.post("https://www.linkedin.com/uas/oauth2/accessToken?grant_type=authorization_code",
                             data=post_data)
    token_json = response.json()
    return token_json['access_token']

def get_username(access_token):
	headers= {"Authorization": "bearer" + access_token}
	response = requests.get("https://oauth.reddit.com/api/v1/me", headers=headers)
	me_json = response.json()
	return me_json['name']

import json
from linkedin import linkedin
def get_skills(access_token):
  application = linkedin.LinkedInApplication(token=access_token)
  my_positions = application.get_profile(selectors=['id', 'first-name', 'last-name', 'location', 'distance', 'num-connections', 'skills', 'educations'])
  return "json %s" % json.dumps(my_positions, indent=1)

if __name__ == '__main__':
    app.run(debug=True, port=65010)
