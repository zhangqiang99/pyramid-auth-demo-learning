from pyramid.response import Response
from pyramid.view import (
	view_config,
	forbidden_view_config,
	notfound_view_config,
	)

from sqlalchemy.exc import DBAPIError

from .models import (
    DBSession,
    MyModel,
    )
from .models import *
from pyramid.httpexceptions import (
	HTTPFound,
	HTTPNotFound,
	HTTPForbidden,
	)
from pyramid.security import *	
#########################################################################
#########################################################################
#########################################################################
#########################################################################
#########################################################################
@view_config(route_name="home", renderer="templates/home.jinja2")
def home_view(request):	
	logged_in = request.authenticated_userid
	user = User.by_email_address(logged_in)
	
	return dict(user=user)	
#########################################################################
@view_config(route_name="test_page", renderer="templates/test_page.jinja2")
def test_page(request):
	logged_in = request.authenticated_userid
	user = User.by_email_address(logged_in)
	
	return dict(
		name="sadkjasjkd kjsa")	
#########################################################################
#########################################################################
#########################################################################
#########################################################################
@view_config(route_name='login', renderer='templates/login.jinja2')
@forbidden_view_config(renderer='templates/login.jinja2') #这是官方写法
#forbidden_view_config() will be used to customize the default 403 Forbidden page. 
#这种用法是基于官方的教程里面的提供的用法, 任何forbidden都转到login页面来登录
def login(request):
#    next = request.params.get('next') or request.route_url('home')	
    login_url = request.route_url('login')
    referrer = request.url
    if referrer == login_url:
        referrer = '/' # never use the login form itself as came_from

    came_from = request.params.get('came_from', referrer)
    message = ''
    login = ''
    password = ''

    if 'form.submitted' in request.params:
        login = request.params['login']
        password = request.params['password']
        user = User.by_email_address(login)
        if user and user.validate_password(password):
            headers = remember(request, login)
            return HTTPFound(location = came_from,
                             headers = headers)
        message = 'Failed login'

    return dict(
        message = message,
        url = request.application_url + '/login',
        came_from = came_from,
        login = login,
        password = password,
        )
#########################################################################
##       下面是替换版本   测试  view + templates  2个文件的变化

#########################################################################
########################################################################
@view_config(route_name='logout')
def logout(request):
    headers = forget(request)
    return HTTPFound(location = request.route_url('home'),
                     headers = headers)
########################################################################
#########################################################################
#########################################################################
#########################################################################
@view_config(route_name="list_users", renderer="templates/list_users.jinja2",
			permission="view")
def list_users(request):
	users = User.get_users()
	return dict(users=users)
######==================================================================
@view_config(route_name="show_user", renderer="templates/show_user.jinja2",
			permission="view")
def show_user(request):
	email_address = request.matchdict['email_address']
	user = User.by_email_address(email_address)
	return dict(user=user)	
######==================================================================
@view_config(route_name="create_user", renderer="templates/create_user.jinja2")
def create_user(request):
	pass 	
#########################################################################
#########################################################################
#########################################################################
#########################################################################
@view_config(route_name="list_articles", renderer="templates/list_articles.jinja2",
			permission="view")
def list_articles(request):
	articles = Article.get_articles()
	
	return dict(articles=articles)
#########################################################################
@view_config(route_name="show_article", renderer="templates/show_article.jinja2",
			permission="view")
def show_article(request):
#	article_id = request.matchdict['article_id']
#	article = Article.by_article_id(article_id)
	article = request.context
		
	return dict(article=article)
#########################################################################
@view_config(route_name="create_article", renderer="templates/create_article.jinja2",
			permission="create")
def create_article(request):
	logged_in = request.authenticated_userid	
	author = User.by_email_address(logged_in)
	user_id = author.user_id
	
	article = Article(title="", content="", user_id=user_id)
	
	if 'form.submitted' in request.params:
		title =  request.params['title']
		content = request.params['content']
		article = Article(title=title, content=content, user_id=user_id)
		DBSession.add(article)
		DBSession.flush()	
		return HTTPFound(location=request.route_url('show_article', article_id=article.id))
	
	return dict(
		article=article,
		save_url = request.route_url('create_article'))
#########################################################################	
@view_config(route_name="edit_article", renderer="templates/edit_article.jinja2",
			permission="edit")
def edit_article(request):		
	article_id 	= request.matchdict['article_id'] 
	article 	= Article.by_article_id(article_id)  

	if 'form.submitted' in request.params:
		title 	= request.params['title']
		content = request.params['content']		
		article.title 	= title
		article.content = content 
		DBSession.add(article)
		return HTTPFound(location=request.route_url('show_article', article_id=article_id))

	save_url = request.route_url('edit_article', article_id = article_id)
	return dict(
		article = article,
		save_url = save_url)
#########################################################################
@view_config(route_name='delete_article',
			permission="edit")
def delete_article(request):
	article_id = request.matchdict['article_id']
	article = Article.by_article_id(article_id)
	DBSession.delete(article)
	#//如何判断删除成功？ flush() /  if article is None:
	return HTTPFound(location=request.route_url('list_articles'))
#########################################################################
#########################################################################
#########################################################################
#########################################################################
