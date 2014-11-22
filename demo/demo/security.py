from .models import (
	DBSession,
	User,
	Group,
)
##########################################################################

def groupfinder(userid, request):
    user = User.by_email_address(userid)
    if user and user.groups:
        return ['%s' % g.group_name for g in user.groups]
    else:
        return []
