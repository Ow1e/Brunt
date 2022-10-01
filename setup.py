import setuptools
  
  
setuptools.setup(
    name="brunt",
    version="0.1",
    author="Owen Shaule",
    author_email="hello@cyclone.biz",
    packages=["brunt"],
    description="A better and slightly more cool web interface for Flask",
    long_description="SocketIO + Flask, without the annoyance",
    long_description_content_type="text/markdown",
    url="https://github.com/Ow1e/Brunt",
    license='MIT',
    python_requires='>=3.8',
    install_requires=["Flask", "Flask-SocketIO", "simple-websocket"]
)