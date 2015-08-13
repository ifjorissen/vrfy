from vrfy.settings import TEST
import ldap3
from ldap3 import ASYNC, SYNC, ALL_ATTRIBUTES, Server, Connection, SUBTREE, ALL

def ldap_lookup_user(username):
  # print("lookup called with {!s}".format(username))
  #to do: make this asynchronous
  if TEST:
    result = {
      "cn": [
        "Isabella F Jorissen",
        "ijorissen"
      ],
      "eduPersonAffiliation": [
        "student"
      ],
      "eduPersonEntitlement": [
        "cascade",
        "thesis-vpn"
      ],
      "eduPersonPrimaryAffiliation": "student",
      "eduPersonPrincipalName": "isjoriss@REED.EDU",
      "gecos": "Isabella F Jorissen",
      "gidNumber": 503,
      "givenName": [
        "Isabella"
      ],
      "homeDirectory": "/afs/reed.edu/user/i/s/isjoriss",
      "loginShell": "/bin/bash",
      "mail": [
        "isjoriss@reed.edu"
      ],
      "objectClass": [
        "top",
        "inetOrgPerson",
        "eduPerson",
        "ReedCollegePerson",
        "posixAccount",
        "inetLocalMailRecipient"
      ],
      "rcLocalHomeDirectory": "/home/isjoriss",
      "rcMiddleName": [
        "F"
      ],
      "sn": [
        "Jorissen"
      ],
      "uid": [
        "isjoriss"
      ],
      "uidNumber": 39878}
  else:
    server = Server('ldap.reed.edu', port=389, get_info=ALL)
    con = Connection(server, auto_bind=True)
    query = 'uid={!s},ou=people,dc=reed,dc=edu'.format(username)
    con.search(search_base = query, search_filter = '(objectClass=*)', search_scope = SUBTREE, attributes=ALL_ATTRIBUTES)
    result = con.response[0]['attributes']
  return result