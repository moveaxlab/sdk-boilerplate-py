# TODO find a structured way to define these
# in order to obtain something like
# from sdkboil import headers
# class A:
#   default_headers = {headers.CONTENT_TYPE : headers.APPLICATION_JSON}
# but probably headers keys and values should be separated

CONTENT_TYPE = 'Content-Type'
ACCEPT = 'Accept'
AUTHORIZATION = 'Authorization'

APPLICATION_JSON = 'application/json'
APPLICATION_FORM_URLENCODED = 'application/x-www-form-urlencoded'
APPLICATION_XML = 'application/xml'
STAR = '*/*'
