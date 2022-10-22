from django.contrib.auth

class LoginHandler(BaseHandler):

#Interface  for login API

model = User
allowed_methods = ('POST',)

@staticmethod
def resource_uri():
    return ('api3_login_handler', [])

@log_request
def create(self, request):

    #Returns authentication token

    try: data = simplejson.loads(request.raw_post_data)
    except:
        msg = {'message':"Username or Password Not Present", 'response':  { 'user' : " " } }
        return sendResponse("BAD_REQUEST",msg)

    uname = data.get('username', '')
    passw = data.get('password', '')

    if(uname == ""):
        msg = {'message':"The server did not understand the request",'status': "BAD_REQUEST", 'response':  { 'user' : " " } }
        return sendResponse("BAD_REQUEST",msg);

    if(passw == ""):
        msg = {'message':"The server did not understand the request",'response':  { 'user' : " " } }
     return sendResponse("BAD_REQUEST",msg);

    userobj = authenticate(username=uname, password=passw);
    if user is None:
         error = True;
         msg = { 'error': error, 'message':"Authentication Failed", 'response':  { 'user' : " " }  , 'status': "BAD_REQUEST", }
         return sendResponse("FORBIDDEN",msg)
    else:
            unique_token = uuid.uuid4()
            unique_token = str(unique_token);
            error = False
            profile = {}
            profile["id"] = userobj.id
            profile["token"] = unique_token;
            profile['username'] = userobj.uname;
            profile['useremail']= user_email;
            message = { 'error': error, 'message':"Authentication Successfully", 'response': { 'user' : profile } , 'status': "ACCEPTED", }
            return sendResponse("ALL_OK",message)