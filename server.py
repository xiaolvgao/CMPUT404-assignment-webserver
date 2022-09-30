#  coding: utf-8 
import socketserver
import os

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/




class MyWebServer(socketserver.BaseRequestHandler):
    def handle(self):

        self.data = self.request.recv(1024).strip()
        print ("Got a request of: %s\n" % self.data)

        self.decode_data = self.data.decode("utf-8").split(" ")
        self.method = self.decode_data[0]
        self.url = self.decode_data[1]

        # 405
        if self.method.upper() != 'GET':
            self.request.sendall(bytearray('HTTP/1.1 405 Method Not Allowed\r\n', 'utf-8'))
            
        else:
            # if Method is 'GET'
            response = self.parseResponse(self.method, self.url)
            self.request.sendall(response.encode())

    
    def parseResponse(self, method, url):
        path = "./www" + url

        # not-free-tests line 55: test url secure
        url_secure = self.checkUrlSecure(url)
        if not url_secure:
            return self.notFound()

        # 301
        if url[-1] != '/':
            if os.path.isdir(path):
                path = path + "/"
                return self.movedPermanently(url + '/')
        
        if not os.path.isfile(path):
            if path[-1] == '/':
                path = path + "index.html"
            else:
                return self.notFound()
        
        # 404
        if not os.path.exists(path):
            return self.notFound()
        
        # 200 
        # https://www.tutorialspoint.com/http/http_responses.htm
        content = self.readFile(path)
        mime_type = self.getContentType(path)
        response = "HTTP/1.1 200 OK\r\n" + "Content-Type: text/%s; charset=utf-8\r\n\r\n" % mime_type + content + "\r\n"
        return response

    def checkUrlSecure(self, url):
        current = 0
        folders = url.split("/")
        for folder in folders:
            if current < 0:
                return False
            if folder != '..':
                current = current + 1
            else:
                current = current - 1
        return True

    def movedPermanently(self, path):
        # https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/301
        response = "HTTP/1.1 301 Moved Permanently\r\n" + "Location: " + path + "\r\n\n"
        return response

    def notFound(self):
        response = "HTTP/1.1 404 Not found\r\n"
        return response

    def getContentType(self, path):
        # https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/MIME_types
        mime_type_css = "css"
        mime_type_html = "html"
        if os.path.splitext(path)[1] == ".css":
            return mime_type_css
        else:
            return mime_type_html
    
    def readFile(self, filename):
        f = open(filename, 'r')
        content = f.read()
        f.close()
        return content




if __name__ == "__main__":
    # https://ruslanspivak.com/lsbaws-part1/
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
