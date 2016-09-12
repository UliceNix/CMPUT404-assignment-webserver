#  coding: utf-8
import inspect
import os.path
import SocketServer

# Copyright 2013 Abram Hindle, Alice Wu, Eddie Antonio Santos
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


class MyWebServer(SocketServer.BaseRequestHandler):
    __message501 = ("HTTP/1.1 501 Not Implemented\n"
                   + "Content-Type text/html\n\n" +
                   "<!DOCTYPE html>\n" +
                   "<html><body><h1>501 Not Implemented</h1></br>"
                   + "Server only supports GET.</body></html></br>\n\n")

    __message404 = ("HTTP/1.1 404 Not Found\n"
                   + "Content-Type: text/html\n\n"
                   + "<!DOCTYPE html>\n"
                   + "<html><body><h1>404 Not Found</h1></body></html></br>\n\n")

    def handle(self):
        self.data = self.request.recv(1024).strip()

        # Prepare request data first
        self.__extractRequestData(self.data)

        # Only allow GET method
        self.__checkMethod()

        # If HTTP method is correct, then proceed to retrieving files
        self.__serveFile()

    def __checkMethod(self):
        if (self.__requestMethod != "GET"):
            self.request.sendall(self.__message501)
            return

    def __serveFile(self):
        self.message = ""
        {0: self.__serve404, 1: self.__serveFileFromPath,
         2: self.__handleRedirect}.get(self.__handlePath(
            self.__requestFilePath))()

        self.request.sendall(self.message)
        return

    def __serve404(self):
        self.message = self.__message404

    def __handleRedirect(self):
        newLocation = self.__requestURL + "/"
        self.message += ("HTTP/1.1 301 Moved Permanently\n"
                       + "Content-Type: text/html\n"
                       + "Location: " + newLocation + "\n\n"
                       + "<!DOCTYPE html>\n"
                       + "<html><body><h1>301 Moved Permanently</h1></br>"
                       + "<a href='"+ newLocation + "'>Click to"
                       + " get redirected</a></body></html></br>\n\n")

    def __serveFileFromPath(self):
        if (self.__requestFilePath):

            self.__requestFileType = self.__requestFilePath.split(".")[-1] \
                                         .lower()

            if self.__requestFileType not in ["html", "css"]:
                self.__requestFileType = "plain"

            self.message +=  ("HTTP/1.1 200 OK\n" + "Content-Type: text/"
                            + self.__requestFileType + "\n\n"
                            + open(self.__requestFilePath).read())

    def __extractRequestData(self, request):
        self.__request = request.splitlines()
        self.__requestData = self.__request[0].split() \
                             if (self.__request) else []

        if (self.__requestData):
            self.__requestMethod = self.__requestData[0].upper()
            self.__currentDir = os.path.dirname(
                                os.path.abspath(
                                inspect.getfile(inspect.currentframe())))
            if (len(self.__requestData) > 1 and self.__requestData[1]):
                self.__requestURL = self.__requestData[1]
                self.__requestFilePath = self.__currentDir + "/www" \
                                         + self.__requestURL
        else:
            self.__requestMethod = ""
            self.__currentDir = ""
            self.__requestFilePath = ""
            self.__requestURL = ""

    def __handlePath(self, path):
        dirPath = path + "index.html"

        if self.__validateAbsPath(path):
            return 1
        elif self.__validateAbsPath(dirPath):
            self.__requestFilePath = dirPath
            return 1
        elif self.__validateAbsPath(path + "/index.html"):
            return 2
        else:
            return 0

    def __validateAbsPath(self, path):
        return os.path.isfile(path) \
               and self.__currentDir in os.path.realpath(path)

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    SocketServer.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = SocketServer.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
