// Made to be a lightweight framework, made to enhance performance and made to rid Flask developers of JavaScript.

const version = "0.1-alpha";

console.group("Brunt Framework");
console.log("BruntJS Version "+version+"\nMade to make the web fast(er).");
console.group("Initialization");

const start_time = new Date();

// Define SocketIO, will eventually have Brunt sharding with SocketIO for scaling

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

addEventListener('load', (event) => {
    console.info("Loaded website in "+((new Date())-start_time)/1000+" seconds");
    console.groupEnd();
    console.group("SocketIO Runtime");

    const socket = io();

    socket.on("connect", () => {
        console.log("Connected to SocketIO");

        let ping = new Date(); // This will be the base
        socket.emit("ping", {}, (json) => {
            console.info("SocketIO Ping: " + (((new Date()) - ping)) + " milliseconds");
            console.info("Page start -> Brunt Finish: " + (((new Date()) - start_time)) + " milliseconds");
            console.info("Brunt Version: "+json["version"]);
            socket.emit("report", {});
        });
    });

    socket.on("bounce", (json) => {
        setTimeout(function(){
            elems = document.querySelectorAll("[brunting]");
            let list = {}; // Goes by id : list : elements (one peice of data can go to multiple elements)
            let request = {"request": []};
            i = 0;
            while (i < elems.length){
                element = elems.item(i);
                if (element.getAttribute("sub").toLowerCase()!="false"){
                    let point = element.getAttribute("point");
                    if (point in list){
                        list[point]["elems"].push(element);
                        if (element.getAttribute("args")!="{}"){
                            list[point]["args"] = JSON.parse(element.getAttribute("args"))
                        }
                    } else {
                        list[point] = {args : [], elems: [element]};
                        if (element.getAttribute("args")!="{}"){
                            list[point]["args"] = JSON.parse(element.getAttribute("args"))
                        }
                    }
                }
                i++;
            }
    
            for (point in list){
                request["request"].push({name : point, args : list[point]["args"]});
            }
    
            socket.emit("request", request, (json) => {
                for (var resname in json["resources"]){
                    content = json["resources"][resname]
                    for (var element in list[resname]["elems"]){
                        list[resname]["elems"][element].innerHTML = content
                    }
                }
                socket.emit("report", {});
            })
        }, 1000);        
    })
});
