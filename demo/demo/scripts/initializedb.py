import os
import sys
import transaction

from sqlalchemy import engine_from_config

from pyramid.paster import (
    get_appsettings,
    setup_logging,
    )

from pyramid.scripts.common import parse_vars

from ..models import (
    DBSession,
    MyModel,
    Base,
    )
from ..models import *    
    


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri> [var=value]\n'
          '(example: "%s development.ini")' % (cmd, cmd))
    sys.exit(1)


def main(argv=sys.argv):
    if len(argv) < 2:
        usage(argv)
    config_uri = argv[1]
    options = parse_vars(argv[2:])
    setup_logging(config_uri)
    settings = get_appsettings(config_uri, options=options)
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.create_all(engine)
    with transaction.manager:
        model = MyModel(name='one', value=1)
        DBSession.add(model)
########
        u = User()
        u.user_name = 'manager'
        u.display_name = 'Example manager'
        u.email_address = 'manager@somedomain.com'
        u.password = 'managepass'

        u1 = User()
        u1.user_name = 'look'
        u1.display_name = 'Look Example manager'
        u1.email_address = 'look@gmail.com'
        u1.password = 'lookpass'

        u2 = User()
        u2.user_name = 'black'
        u2.display_name = 'black manager'
        u2.email_address = 'black@gmail.com'
        u2.password = 'blackpass'

        u3 = User()
        u3.user_name = 'demo'
        u3.display_name = 'demo manager'
        u3.email_address = 'demo@gmail.com'
        u3.password = 'demopass'
        
        DBSession.add_all([u, u1, u2, u3])
	######### admins--group        #################
        mm = User()
        mm.user_name = 'admin'
        mm.display_name = 'admin manager'
        mm.email_address = 'admin@gmail.com'
        mm.password = 'adminpass'
        nn = User()
        nn.user_name = 'root'
        nn.display_name = 'root manager'
        nn.email_address = 'root@gmail.com'
        nn.password = 'rootpass'    
        
        a = Group()
        a.group_name = 'admins'
        a.display_name = 'admins'        
        a.users.append(m)
        a.users.append(n)
        # admins-group   (admin/root)   
        DBSession.add_all([mm, nn, a])     
        ########## editors--group         ##############
        
        pp = User()
        pp.user_name = 'pp'
        pp.display_name = 'pp--editor'
        pp.email_address = 'pp@gmail.com'
        pp.password = 'pppass'   

        qq = User()
        qq.user_name = 'qq'
        qq.display_name = 'qq--editor'
        qq.email_address = 'qq@gmail.com'
        qq.password = 'qqpass'                       

        e = Group()
        e.group_name = 'editors'
        e.display_name = 'editors'
        e.users.append(pp)
        e.users.append(qq)
        # editors-group  (pp/qq)        
        DBSession.add_all([pp, qq, e])
        ##########################################

        a1 = Article(title="11111111111", content="sdakjskdkjds", user_id=u.user_id)
        a2 = Article(title="1222221111", content="sdakjskdkjds", user_id=u1.user_id)
        a3 = Article(title="33333311", content="sdakjskdkjds", user_id=u2.user_id)
        a4 = Article(title="44444444444", content="sdakjskdkjds", user_id=pp.user_id)
        a5 = Article(title="55511", content="sdakjskdkjds", user_id=u1.user_id)
        a6 = Article(title="demo---u3----33333311", content="demo---u3----sdakjskdkjds", user_id=u3.user_id)
        a7 = Article(title="demo---u3----44444444444", content="demo---u3----sdakjskdkjds", user_id=u3.user_id)
        a8 = Article(title="mm----------66666661", content="sdakjskdkjds", user_id=mm.user_id)
        
        DBSession.add_all([a1, a2, a3, a4, a5, a6, a7, a8])
#########################################################################
