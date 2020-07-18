from setuptools import setup

setup(
	name='pyQiwiP2P',
	version='1.0a2',
	packages=['pyqiwip2p', 'pyqiwip2p.types', 'pyqiwip2p.notify'],
	url='https://github.com/WhiteApfel/pyQiwiP2P',
	license='Mozilla Public License 2.0',
	author='WhiteApfel pfel.cc',
	author_email='white@pfel.ru',
	description='pyQiwiP2P',
	install_requires=['cherrypy', 'phonenumbers', 'email_validator']
)
