import uuid
import random
from http.server import BaseHTTPRequestHandler, HTTPServer
class Game(object):
    def __init__(self):
        self.games_reset()
    
    def games_reset(self):
        self.players = {}
        self.iter = 0
        self.topic = ""
        self.leader = None
        self.impostor = None
    
    def add_player(self, id = None):
        if id == None:
            id = str(uuid.uuid1())
        self.players[id] = True      
        return id  
    
    def pick_player(self):
        if len(self.players)  <= 1:
            return None
        temp = random.choice(list(self.players.keys()))
        if temp == self.leader:
            return self.pick_player()
        return temp
    
    def pick_leader(self):
        self.topic = ""
        self.iter += 1
        self.leader = self.pick_player()
        return self.leader

    def pick_impostor(self):
        self.impostor = self.pick_player()
        return self.impostor

    def update_topic(self, topic):
        self.topic = topic
        topic

    def my_topic(self, player):
        if self.topic == "":
            return "Topic isn't set yet, please wait for the leader to set the topic or for someone to start the game."
        if player == self.impostor:
            return "XXXXXXXXXX"
        return self.topic
class GameContainer:
    class __GameContainerSingleton(object):
        def __init__(self):
            self.games = {}

        def add_game(self, id=None):
            if id==None:
                id = str(uuid.uuid1())
            self.games[id] = Game()
            return id

        def __getitem__(self, id):
            if id in self.games:
                return self.games[id]
            self.add_game(id)
            return self.games[id]

        def __setitem__(self, id, game):
            self.games[id] = game

    instance = None
    def __init__(self):
        if not GameContainer.instance:
            self.__game_init()
    def __game_init(self):
        GameContainer.instance = GameContainer.__GameContainerSingleton()
 
    def get_or_new_game(self, name):
        if not GameContainer.instance:
            self.__game_init()
        return self.instance[name]

    def set_game(self, name, obj):
        if not GameContainer.instance:
            self.__game_init()
        self.instance[name]=obj

class myHandler(BaseHTTPRequestHandler, GameContainer):
    def do_GET(self):
        self.send_response(200)     
        self.send_header('Content-type','text/html')
        self.end_headers() 
        if self.path.startswith('/join'):
            self.do_join()
        elif self.path.startswith('/next'):
            self.do_next()
        elif self.path.startswith('/topic'):
            self.do_topic()
        elif self.path.startswith('/status'):
            self.do_state()

    def get_forms(self):
        temp = self.path.split("?")
        if len(temp) < 2:
            return {}
        return {xx:yy for xx,yy in [x.split("=") for x in temp[-1].split("&")]}

    def do_state(self):
        x = self.get_forms()
        if ("g" not in x) or ("p" not in x):
            self.do_join()
        g= x["g"]
        p = x["p"]
        game = self.get_or_new_game(g)
        topic = game.my_topic(p)
        leader = "false" if ((p == game.leader) and (len(game.topic) == 0)) else "true"
        out = """<!DOCTYPE html>
        <html><body>
        <div id="custom">
        The topic is: {}
        </div> <br> <div id="game"><button type="button" id="hider" onclick="toggleDiv('custom')">Show+Hide</button>
        <div id="leader">
        If you're the leader, you can set the topic:
        <textarea id="newTopic" rows="1"></textarea><br>
        <button id="topicSubmit" onclick="newTopic()">Submit Topic</button>
        </div><br>
        <br><button type="button" id="refreshNext" onclick="nextRound()">Refresh/Next Round</button></div>
        </body>
        <script>
        function toggleDiv(id) {{
        var toggle = document.getElementById(id);
        toggle.style.display = toggle.style.display == "none" ? "block" : "none";}}
        if({}){{
            toggleDiv('leader');
        }};
        function newTopic(){{
        var topic = document.getElementById("newTopic").value;
        window.location.href = '/topic?g={}&p={}&topic='+topic;}}
        function nextRound(){{
        window.location.href = '/next?g={}&p={}';}}
        </script>
        <html>""".format(topic, leader, g,p,g,p)
        self.wfile.write(bytes(out, "utf-8"))

    def do_join(self):
        x = self.get_forms()
        g = str(uuid.uuid1())
        if "g" in x:
            g = x["g"]
        game = self.get_or_new_game(g)
        p = game.add_player()
        self.set_game(g,game)
        self.wfile.write(bytes("<!doctype html>\n<html><body><a href=/status?g={}&p={}>go here</a></body></html>".format(g,p), "utf-8"))
   
    def do_next(self):
        x = self.get_forms()
        g = 0
        p = 0 
        if "g" in x:
            g= x["g"]
        if "p" in x:
            p = x["p"]
        game = self.get_or_new_game(g)
        if (game.leader == p) or (game.leader == None):
            game.pick_leader()
            game.pick_impostor()
            self.set_game(g,game)
        self.wfile.write(bytes("<meta http-equiv='Refresh' content='0; url=/status?g={}&p={}'/>".format(g,p), "utf-8"))
    
    def do_topic(self):
        x = self.get_forms()
        g = 0
        p = 0 
        topic = ""
        if "g" in x:
            g= x["g"]
        if "p" in x:
            p = x["p"]
        if "topic" in x:
            topic = x["topic"]
        game = self.get_or_new_game(g)
        if game.leader == p and game.topic == "":
            game.update_topic(topic)
            self.set_game(g,game)
        self.wfile.write(bytes("<meta http-equiv='Refresh' content='0; url=/status?g={}&p={}'/>".format(g,p), "utf-8"))
       

def main():
    port = 8000
    server = HTTPServer(('', port), myHandler)
    server.serve_forever()


if __name__ == "__main__":
    main()

"""
(defun gp-seg (g p)
  (format nil "?g=~A&p=~A" g p))

(hunchentoot:define-easy-handler (status :uri "/status") (g p)
  (setf (hunchentoot:content-type*) "text/html")
  (let* ((p (parse-integer p))
	 (g (parse-integer g))
	 (game (get-or-new-game g))
	 (path (gp-seg g p))
	 (leader? (= (game-leader game) p))
	 (topic-set? (not (string= "" (game-topic game)))))
    (format nil  (my-topic game p) (if (and leader? (not topic-set?)) "" "toggleDiv('leader')\;") path path
)))

(hunchentoot:define-easy-handler (join :uri "/join") (g)
  (setf (hunchentoot:content-type*) "text/html")
  (let* ((g (if g g "0"))
	 (game (get-or-new-game (parse-integer g)))
         (game (add-player game))
	 (p (game-players game)))
    (format nil "<!doctype html><html><body><a href=/status~A>go here</a></body></html>"  (gp-seg g p))))

(hunchentoot:define-easy-handler (next :uri "/next") (g p)
  (setf (hunchentoot:content-type*) "text/html")
  (let* ((game (get-or-new-game (parse-integer g)))
	 (leader (game-leader game))
         (leader? (= (parse-integer p) leader)))
    (when (or leader? (>= 0 leader))
          (pick-leader game)
          (pick-impostor game)
          )
      '(let* ((players (game-players game))
	     (faker (game-impostor game))
	     (topic (game-topic game)))
	(format *error-output* "game ~A, leader ~A, players ~A, impostor ~A, topic ~A" g leader players faker topic))
    (format nil "<meta http-equiv='Refresh' content='0; url=/status~A'/>"
	    (gp-seg g p))))

(hunchentoot:define-easy-handler (topic :uri "/topic") (g p topic)
  (setf (hunchentoot:content-type*) "text/html")
  (let* ((game (get-or-new-game (parse-integer g)))
         (leader? (= (parse-integer p) (game-leader game))))
    (when leader?
          (update-topic game topic)
          )
        (format nil "<meta http-equiv='Refresh' content='0; url=/status~A'/>" (gp-seg g p))
        ))

"""
