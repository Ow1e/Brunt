from flask_socketio import SocketIO, emit
from flask import escape
import json
from time import sleep

BRUNT_VERSION = "0.1-alpha"

def filter_dummy(name, args):
    """Takes in kwargs of name, args. Takes out True/False"""
    return True

class Property:
    def __init__(self, name : str, callback, type : str, apply : str, subscribe = False, extentions = {}) -> None:
        """
        Brunt fetch property
        ```python
        brunt = Brunt(app)

        def my_func():
            return mybase64image

        myprop = Property("user", my_func, "onload", "href", {"user": "@owen"})
        ```

        Name: The name of the property (these must not be dynamic)  
        Callback: The function to callback too  
        Type: Can be `onload`, `lazy` or `instant`  
        Apply: Can be `text` or `href` (Extention support?)  
        Subscribe: Can be set to `False` or to to a integer in mileseconds for reloading data
        """
        self.name = name
        self.callback = callback
        self.type = type
        self.apply = apply
        self.subscribe = subscribe
        self.extentions = extentions

    def dupe(self):
        return Property(self)

class Brunt:
    def __init__(self, app, filter = filter_dummy) -> None:
        self.__app = app
        self.callbacks = {}
        self.properties = {}
        self.filter = filter

        io = SocketIO(app) 
        self.socket = io
        """
            CLIENT > Server = {request: {myapp.saysomething: {myargs : this, etc, etc}, etc, etc}, etc, etc}
            SERVER > Client = {"receive": {myapp.saysomething: "My String"}}
        """

        @app.context_processor
        def inject_brunt():
            return {"brunt": self.web}

        @io.on("ping")
        def ping(json):
            return {"pong": True, "version": BRUNT_VERSION}

        @io.on("report")
        def report(json):
            sleep(1)
            emit("bounce")

        @io.on("request")
        def resource(json):
            cache = {}
            for i in json.get("request", {}):
                if i["name"] in self.callbacks:
                    if self.filter(name=i["name"], args=i["args"]):
                        if i["args"]==[]:
                            cache[i["name"]] = self.callbacks[i["name"]]()
                        else:
                            cache[i["name"]] = self.callbacks[i["name"]](**i["args"])
                    else:
                        emit("reject", {"name": i["name"]})
            return {"resources": cache}

    def get(self, property : Property, arguments):
        if not property.name in self.callbacks:
            self.setup_callback(property)

        general = f"args='{json.dumps(arguments)}' "+f'point="{property.name}" type="{property.type}" apply="{property.apply}" sub={property.subscribe}'
        if property.apply == "text":
            base = f'<brunt brunting {general}></brunt>'
            base = base.replace("><", f">{property.callback(**arguments)}<", 1)
            return base
        else:
            return general

    def add_prop(self, property : Property):
        self.setup_callback(property)
        self.properties[property.name] = property

    def web(self, name, args = {}):
        property = self.properties[name]
        return self.get(property, args)

    def setup_callback(self, property : Property):
        self.callbacks[property.name] = property.callback

    def js(self):
        return '''<script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js" integrity="sha512-q/dWJ3kcmjBLU4Qc47E4A9kTB4m3wuTY7vkFJDTZKjTs8jhyGQnaUrxa0Ytd0ssMZhbNua9hE+E7Qv1j+DyZwA==" crossorigin="anonymous"></script>\n<script src="/static/brunt.js"></script>'''
