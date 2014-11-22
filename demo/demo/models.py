from sqlalchemy import (
    Column,
    Index,
    Integer,
    Text,
    )
from sqlalchemy import *

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    )
from sqlalchemy.orm import *
from sqlalchemy import event

from zope.sqlalchemy import ZopeTransactionExtension

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()
##============================
from pyramid.security import *
import os
from datetime import datetime
from hashlib import sha256
from sqlalchemy.types import *
metadata = Base.metadata
########################################################################
user_group_table = Table('tg_user_group', metadata, 
	Column('user_id', Integer, ForeignKey('tg_user.user_id', onupdate="CASCADE", ondelete="CASCADE"), primary_key=True), 
	Column('group_id', Integer, ForeignKey("tg_group.group_id", onupdate="CASCADE", ondelete="CASCADE"), primary_key=True)
)

class Group(Base):
	__tablename__ = 'tg_group'
	group_id = Column(Integer, autoincrement=True, primary_key=True)
	group_name = Column(Unicode(255), unique=True, nullable=False)
	display_name = Column(Unicode(255))
	created = Column(DateTime, default=datetime.now)
	users = relationship('User', secondary=user_group_table, backref='groups')
	
	def __repr__(self):
		return "<Group: name=%s>" % (self.group_name)
	
	def __unicode__(self):
		return self.group_name
	
	@classmethod
	def get_group(cls, group_name):
		group = DBSession.query(cls).filter(cls.group_name==group_name).one()
		return group
	@classmethod
	def by_group_name(cls, group_name):
		group = DBSession.query(cls).filter_by(group_name=group_name)
		return group
	@classmethod
	def by_group_id(cls, group_id):
		group = DBSession.query(cls).get(group_id)
		return group
				
########################################################################		
class User(Base):
	__tablename__ = 'tg_user'
	user_id = Column(Integer, autoincrement=True, primary_key=True)
	user_name = Column(Unicode(255), unique=True, nullable=False)
	email_address = Column(Unicode(255), unique=True, nullable=False)
	display_name = Column(Unicode(255))
	_password = Column('password', Unicode(255))
	created = Column(DateTime, default=datetime.now)
	
	@property
	def __acl__(self):
		return [
			(Allow, self.email_address, 'view'),
		]

	def __repr__(self):
		return "<User: name=%s, email=%s, display=%s>" % (self.user_name, self.email_address, self.display_name)
	def __unicode__(self):
		return self.display_name or self.user_name	        		

##################
	@classmethod
	def by_email_address(cls, email):
		return DBSession.query(cls).filter_by(email_address=email).first()

	@classmethod
	def by_user_id(cls, user_id):
		return DBSession.query(cls).filter(cls.user_id==user_id).one()
	
	@classmethod
	def get_users(cls):
		users = DBSession.query(cls).all()
		return users
		
	@classmethod
	def get_user(cls, id):
		user = DBSession.query(cls).get(id)
		return user
			
	@classmethod
	def by_user_name(cls, username):
		return DBSession.query(cls).filter_by(user_name=username).first()	
##################
	@classmethod
	def _hash_password(cls, password):
		salt = sha256()
		salt.update(os.urandom(60))
		salt = salt.hexdigest()
		
		hash = sha256()
		hash.update((password+salt).encode('utf-8'))
		hash = hash.hexdigest()
		password = salt + hash
		return password
	def _set_password(self, password):
		self._password = self._hash_password(password)
	def _get_password(self):
		return self._password
	password = synonym('_password', descriptor=property(_get_password, _set_password))	
	
	def validate_password(self, password):
		hash = sha256()
		hash.update((password + self.password[:64]).encode('utf-8'))
		return self.password[64:] == hash.hexdigest()
		
########################################################################
class MyModel(Base):
    __tablename__ = 'models'
    id = Column(Integer, primary_key=True)
    name = Column(Text)
    value = Column(Integer)

Index('my_index', MyModel.name, unique=True, mysql_length=255)
########################################################################
########################################################################
class Article(Base):
	__tablename__ = 'articles'
	id 			= Column(Integer, primary_key=True)
	title 		= Column(String(255), nullable=False)
	content 	= Column(Text)
	created_at 	= Column(DateTime, nullable=False, default=datetime.now())
	edited_at 	= Column(DateTime, nullable=False, default=datetime.now())
	user_id 	= Column(Integer, ForeignKey('tg_user.user_id'))
	author 		= relationship('User', backref=backref("articles", lazy='dynamic'))
	
	@property
	def __acl__(self):
		return [
			(Allow, self.user_id, 'edit'),
		]

	def __init__(self, title, content, user_id):
		self.title = title
		self.content = content
		self.user_id = user_id
		
	@classmethod
	def by_article_id(cls, article_id):
		return DBSession.query(cls).filter_by(id=article_id).first()
	@classmethod
	def by_article_title(cls, article_title):	
		return DBSession.query(cls).filter_by(title=article_title).first()

	@classmethod
	def get_article(cls, key):
		article = DBSession.query(cls).get(key)
		return article	
					
	@classmethod
	def get_articles(cls):
		articles = DBSession.query(cls).all()
		return articles	
@event.listens_for(Article, 'after_update')
def edited_after_update(mapper, connection, target):	
	target.edited_at = datetime.now()
#########################################################################
#########################################################################
class RootFactory(object):
	__acl__ = [
#		(Allow, Everyone, 'view'),
#		(Allow, Authenticated, 'create'),
#		(Allow, Authenticated, 'edit'),
#		(Allow, 'editors', 'edit'),		
		(Allow, 'admins', ALL_PERMISSIONS),		
	]
	
	def __init__(self, request):
		self.request = request

class UserFactory(object):
	__acl__ = [
		(Allow, 'admins', ALL_PERMISSIONS),
	]
	
	def __init__(self, request):
		self.request = request
		
	def __getitem__(self, key):
		user = User.by_email_address(key)
		user.__parent__ = self
		user.__name__ = key
		return user	

class ArticleFactory(object):
	__acl__ = [
		(Allow, Everyone, 'view'),
		(Allow, Authenticated, 'create'),
		(Allow, 'admins', ALL_PERMISSIONS),
	]
	
	def __init__(self, request):
		self.request = request
		
	def __getitem__(self, key):
		article = Article.by_article_id(key)
		article.__parent__ = self
		article.__name__ = key
		return article	
########################################################################
########################################################################
