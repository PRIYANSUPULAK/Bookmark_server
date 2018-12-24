import requests
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import unquote,parse_qs
#making a  dictionary
memory={}

form= '''
        <!DOCTYPE html>
        <html>
        <head>
        <title>Bookmark Server</title>
        </head>
        <body>
            <form method="POST">
            <label>Long URL
            <input type=text name="longuri">
            </label>
            <br>
            <label>Shortname
            <input type=text name="shortname">
            </label>
            <br>
            <button type="submit">Save</button>
            </form>
            <br>
            <p>URIs , I Know</p>
            <list>
<pre>
{}
</pre>
            </list>
            </body>
            </html>
    '''


def checkURI(uri,timeout=10):
    try:
        r=requests.get(uri,timeout=timeout)
        #If the GET status is 200, Return TRUE
        return r.status_code==200
    except requests.RequestException:
        return False

class shortener(BaseHTTPRequestHandler):
    def do_GET(self):
        #Strip off '/' and we have entire string
        name= unquote(self.path[1:])

        if name:
            # We know that name! send a redirect to it.
            if name in memory:
                self.send_response(303)
                self.send_header('Location',memory[name])
                self.end_headers()
            else:
            # We don't know that name! Send a 404 Requestself.
                self.send_response(404)
                self.send_header("content-type","text/plain, charset=utf-8")
                self.end_headers()
                self.wfile.write("I don't know '{}' ." .format(name).encode())
        else:
            #send the form to root path
            self.send_response(200)
            self.send_header("content-type","text/html; charset=utf-8")
            self.end_headers()
            know="\n".join("{0} : {1}".format(key,memory[key]) for key in sorted(memory.keys()))
            self.wfile.write(form.format(know).encode())

    def do_POST(self):
        #Decoding the form data
        length=int(self.headers.get("content-length",0))
        body=self.rfile.read(length).decode()
        params=parse_qs(body)
        #checking that the user sumbitted the form fields

        if "longuri" not in params or "shortname" not in params:
            self.send_response(400)
            self.send_header("content-type",'text/plain; charset=utf-8')
            self.end_headers()
            self.wfile.write("Missing form fields!".encode())
            return

        longuri=params["longuri"][0]
        shortname=params["shortname"][0]
        #If the give URI exists
        if checkURI(longuri):
            memory[shortname]=longuri

            #serve a redirect to the format
            self.send_response(303)
            self.send_header('Location','/')
            self.end_headers()
        else:
            self.send_response(404)
            self.send_header("content-type","text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write("Couldn't fetch '{}' . ".format(longuri).encode())



if __name__=='__main__':
    server_address=('',8000)
    httpd=HTTPServer(server_address,shortener)
    httpd.serve_forever()
