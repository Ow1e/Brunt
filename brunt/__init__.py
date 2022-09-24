from flask_socketio import SocketIO, emit
import json
from time import sleep

BRUNT_VERSION = "0.1-alpha"

class Property:
    def __init__(self, name : str, callback, type : str, apply : str, args : dict, subscribe = False, extentions = {}) -> None:
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
        Args: Arguments for the callback (Dictionary only)
        Subscribe: Can be set to `False` or to to a integer in mileseconds for reloading data
        Extentions: A dictionary containing custom values
            Images: {"classes": [], "width": 0, "height": 0}
        """
        self.name = name
        self.callback = callback
        self.type = type
        self.apply = apply
        self.args = args
        self.subscribe = subscribe
        self.extentions = extentions

    def dupe(self):
        return Property(self)

    def set_args(self, newargs):
        self.args = newargs

class Brunt:
    def __init__(self, app, subscribing = True) -> None:
        self.__app = app
        self.callbacks = {}

        io = SocketIO(app) 
        self.socket = io
        """
            CLIENT > Server = {request: {myapp.saysomething: {myargs : this, etc, etc}, etc, etc}, etc, etc}
            SERVER > Client = {"receive": {myapp.saysomething: "My String"}}
        """

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
                    cache[i["name"]] = self.callbacks[i["name"]](**i["args"])
            return {"resources": cache}

    def get(self, property : Property):
        if not property.name in self.callbacks:
            self.setup_callback(property)
        if property.apply == "text":
            args = f"args='{json.dumps(property.args)}'"
            base = f'<brunt brunting point="{property.name}" type="{property.type}" apply="{property.apply}" {args} sub={property.subscribe}></brunt>'
            base = base.replace("><", f">{property.callback(**property.args)}<", 1)
            return base

    def setup_callback(self, property : Property):
        self.callbacks[property.name] = property.callback

    def js(self):
        return '''<script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js" integrity="sha512-q/dWJ3kcmjBLU4Qc47E4A9kTB4m3wuTY7vkFJDTZKjTs8jhyGQnaUrxa0Ytd0ssMZhbNua9hE+E7Qv1j+DyZwA==" crossorigin="anonymous"></script>\n<script src="/static/brunt.js"></script>'''
