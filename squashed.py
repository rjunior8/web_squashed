from flask import Flask, render_template, jsonify, request
import pusher
import random


number = random.randint(1, 99)
min_number, max_number = 0, 100
users = {}

app = Flask(__name__)

pusher_client = pusher.Pusher(
  app_id="PUSHER_APP_ID",
  key="PUSHER_APP_KEY",
  secret="PUSHER_APP_SECRET",
  cluster="PUSHER_APP_CLUSTER",
  ssl=True)

@app.route('/')
def index():
  return render_template("squashed.html")

@app.route("/users_list", methods=["POST"])
def users_list():
  try:
    nick1 = request.form.get("nick")
    if not users:
      users.update({1 : nick1})
    else:
      users.update({len(users) + 1 : nick1})

    return jsonify({"result" : "success"})
  except:
    return jsonify({"result" : "failure"})

@app.route("/message", methods=["POST"])
def message():
  try:
    username = request.form.get("username")
    message = request.form.get("message")

    reply = int(message)

    global min_number
    global max_number

    if reply < number:
        min_number = reply
    elif reply > number:
        max_number = reply

    if reply == number:
      message = "Reply: {} - {} LOSED!".format(reply, username)
    elif number + 1 == max_number and number - 1 == min_number:
      for id_, user in users.items():
        if username == user:
          if id_ + 1 > max(users, key=int):
            message = "Reply: {} - {} HAS BEEN SQUASHED!".format(reply, users[1])
            break
          else:
            message = "Reply: {} - {} HAS BEEN SQUASHED!".format(reply, users[id_ + 1])
            break
    elif reply < number and (reply > min_number or reply == min_number):
      message = "Reply: {} - The number is between {} and {}".format(reply, reply, max_number)
    elif reply < min_number:
      message = "Reply: {} - The number is between {} and {}".format(reply, min_number, max_number)
    elif reply > number and (reply < max_number or reply == max_number):
      message = "Reply: {} - The number is between {} and {}".format(reply, min_number, reply)
    elif reply > max_number:
      message = "Reply: {} - The number is between {} and {}".format(reply, min_number, max_number)

    if len(users) > 1:
      if not message.__contains__("LOSE") and not message.__contains__("HAS"):
        for user_id, nick in users.items():
          if username == nick:
            if user_id + 1 > max(users, key=int):
              message = "{} - Your turn, {}".format(message, users[1])
              break
            else:
              message = "{} - Your turn, {}".format(message, users[user_id + 1])
              break
    else:
      message = "{} - Wait for opponent...".format(message)

    pusher_client.trigger("chat-channel", "new-message", {"username" : username, "message" : message})

    return jsonify({"result" : "success"})
  except:
    return jsonify({"result" : "failure"})

if __name__ == "__main__":
  app.run(debug=True, host="192.168.100.102", port=8888)

