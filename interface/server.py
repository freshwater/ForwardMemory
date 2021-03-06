
import http.server

import os
import uuid
import json

import retro_module


class Server(http.server.BaseHTTPRequestHandler):
    files_cache = {}
    modules = {}

    def request_process(self, request):
        request_name = request["Request"]
        client_id = request["ClientId"]

        if request_name == "Initial":
            Server.modules[client_id] = retro_module.RetroModule2()

            return {
                'Data': Server.modules[client_id].interface_json()
            }

        elif request_name == "Event":
            Server.modules[client_id].event_process(request)

            return {
                'Data': Server.modules[client_id].interface_json()
            }

        elif request_name == "Inspection":
            return Server.modules[client_id].inspection_process(request)

        else:
            raise NotImplementedError(request)

    def request_process0(self, request):
        request_name = request["Request"]
        client_id = request["ClientId"]

        if request_name == "ResourceURL":
            client_id = request['ClientId']
            game = request['Game']

            random_key = uuid.uuid4()

            # todo convenient file name

            if request['ResourceType'] == '.bk2 Replay Data':
                actions_commitment_intervals = Server.environments[client_id].actions_commitment_intervals()
                actions = sum([[action]*interval for action, interval in actions_commitment_intervals], [])

                folder = f'/tmp/{random_key}'
                os.makedirs(folder)

                environment = retro_server.RetroClient(game=game,
                                                       bk2_location=folder,
                                                       actions=actions)

                environment.close()
                print(os.listdir(folder))

                return f'/{random_key}/{os.listdir(folder)[0]}'

            elif request['ResourceType'] == '.json Action Sequence':
                actions_commitment_intervals = Server.environments[client_id].actions_commitment_intervals()
                actions = sum([[action]*interval for action, interval in actions_commitment_intervals], [])

                with open(f'/tmp/{random_key}.json', 'w') as file:
                    file.write(json.dumps(actions))

                return f'/{random_key}.json'

            elif request['ResourceType'] == '.mp4 Replay Video':
                actions_commitment_intervals = Server.environments[client_id].actions_commitment_intervals()
                actions = sum([[action]*interval for action, interval in actions_commitment_intervals], [])

                folder = f'/tmp/{random_key}'
                os.makedirs(folder)

                environment = retro_server.RetroClient(game=game,
                                                       bk2_location=folder,
                                                       actions=actions)

                environment.close()
                print(os.listdir(folder))

                replay_file = f'/tmp/{random_key}/{os.listdir(folder)[0]}'
                import subprocess
                video_being_written = f'/tmp/{random_key}/video_being_written.mp4'
                video_file = f'/tmp/{random_key}/video.mp4'
                # It looks like ffmpeg streams to the file or otherwise takes a bit of time to write it.
                # Use && so that the completed video file only exists after the writing is fully complete.
                # This makes it easier to just poll for the file on the client.
                subprocess.Popen(f'python3 playback_movie.py {replay_file} && mv {video_being_written} {video_file}',
                                 shell=True)

                return f'/{random_key}/video.mp4'

        raise NotImplementedError(request)


    def do_POST(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/json')
        self.end_headers()

        length = int(self.headers['Content-Length'])
        data = self.rfile.read(length)
        request = json.loads(data)

        print("Request")
        print(json.dumps(request).encode()[:800])

        import time
        t0 = time.time()
        response = self.request_process(request)

        self.wfile.write(json.dumps(response).encode())


    def do_GET(self):
        print(">>", self.path)

        content_types = {
            '.js': 'application/javascript',
            '.css': 'text/css',
            '.html': 'text/html',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.mp4': 'video/mp4',
            '.webm': 'video/webm'
        }

        import os.path
        extension = os.path.splitext(self.path)[1]

        # SinglePageSingleSession
        #   a | b |
        #   c | | d
        ## SinglePageMultipleSession ?
        ##   a | b |
        ##   a | | b
        ## MultiplePageSingleSession ?
        ##   a | a |
        ##   b | | b
        # MultiplePageMultipleSession
        #   a | a |
        #   a | | a

        # if user_state_preservation_mode == 'None':
        #    pass
        # elif user_state_preservation_mode == 'CrossPageSessionOnly':
        #    pass
        # elif user_state_preservation_mode == 'UserOnly':
        #    pass
        # elif user_state_preservation_mode == 'CrossPageSessionAndUser':
        #    pass

        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            if not Server.files_cache.get('/server_directory/index.html'):
                with open('/server_directory/index.html', 'rb') as file:
                    Server.files_cache['/server_directory/index.html'] = file.read()

            self.wfile.write(Server.files_cache['/server_directory/index.html'])

        elif self.path == '/favicon.ico':
            self.wfile.write("WE DONT HAVE IT".encode())

        elif extension in ['.js', '.css', '.html', '.gif'] or (extension == '.png' and '/textures/' in self.path):
            self.send_response(200)
            self.send_header('Content-type', content_types[extension])
            self.end_headers()

            if not Server.files_cache.get(self.path):
                with open('/server_directory' + self.path, 'rb') as file:
                    Server.files_cache[self.path] = file.read()

            self.wfile.write(Server.files_cache[self.path])

        elif extension == '.png':
            self.send_response(200)
            self.send_header('Content-Type', content_types['.png'])
            self.send_header('Cache-Control', 'max-age=3')
            self.end_headers()

            with open('/tmp' + self.path, 'rb') as file:
                self.wfile.write(file.read())

        elif extension in ['.bk2', '.json', '.mp4', '.mkv', '.webm']:
            if not os.path.exists('/tmp' + self.path):
                self.send_response(404)
            else:
                self.send_response(200)
                self.send_header('Content-Type', content_types[extension])
                self.send_header('Content-Disposition', 'attachment')
                self.end_headers()

                with open('/tmp' + self.path, 'rb') as file:
                    self.wfile.write(file.read())

        else:
            raise NotImplementedError(f"self.path . {extension}")


def run(port=80):
    print("Listening on port", str(port) + ".")

    httpd = http.server.HTTPServer(('', port), Server)
    httpd.serve_forever()


run()
