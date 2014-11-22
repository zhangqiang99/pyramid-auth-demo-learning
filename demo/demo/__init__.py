from pyramid.config import Configurator
from sqlalchemy import engine_from_config

from .models import (
    DBSession,
    Base,
    )
from .models import *

from .security import *
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
########################################################################

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine


    
    authn_policy = AuthTktAuthenticationPolicy('seekrit', hashalg='sha512', callback=groupfinder)	
    authz_policy = ACLAuthorizationPolicy()
    config = Configurator(settings=settings,  root_factory='demo.models.RootFactory')
    config.set_authentication_policy(authn_policy)
    config.set_authorization_policy(authz_policy)

    config.include('pyramid_chameleon')
    config.include('pyramid_jinja2')	
    config.add_static_view('static', 'static', cache_max_age=3600)
########################################################################
    config.add_route('test_page', 	'test')
    config.add_route('home', 		'/')	
    config.add_route('login', 		'/login')
    config.add_route('logout', 		'/logout')
########################################################################
    config.add_route('list_users', 	'/users', factory=UserFactory)
    config.add_route('show_user', 	'/user/{email_address}', factory=UserFactory, traverse='/{email_address}')
    config.add_route('create_user', '/create_user', factory=UserFactory)
########################################################################
    config.add_route('list_articles', 	'/articles', factory=ArticleFactory)
    config.add_route('show_article', 	'/article/{article_id}', factory=ArticleFactory, traverse='/{article_id}')
    config.add_route('create_article', 	'/create_article', factory=ArticleFactory)
    config.add_route('edit_article', 	'/article/{article_id}/edit', factory=ArticleFactory, traverse='/{article_id}')
    config.add_route('delete_article', 	'/article/{article_id}/delete', factory=ArticleFactory, traverse='/{article_id}')
########################################################################
    config.scan()
    return config.make_wsgi_app()
