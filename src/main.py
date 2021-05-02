import os
import azure.functions as func
import json
import requests

from v3.pymessenger.bot import Bot


def main(req: func.HttpRequest) -> func.HttpResponse:
    psmenu = {
        "persistent_menu":[
        {
        "locale":"default",
        "composer_input_disabled": True,
        "call_to_actions":[
            {
                "title":"📖 Get random verse",
                "type":"postback",
                "payload":"random_verse"
            },           
            {
                "title": "💡 Info",
                "type": "postback",
                "payload": "the_info"
            }
        ]
    }
    ]
    }
    gs_data = {
    "get_started":{
        "payload": "get_started"
    }
    }
    global bot
    fb = req.params.get('hub.verify_token')
    if req.method=="GET":
        if fb:
            if fb == os.environ["VERIFY_TOKEN"]:
                return func.HttpResponse(req.params.get('hub.challenge'), status_code=200)
            return func.HttpResponse("error", status_code=403)
        elif fb:
            return func.HttpResponse(os.environ['FB_SECRET'], status_code=200)
        else:
            return func.HttpResponse(
                json.dumps({"stat":"online"}),
                status_code=200
            )
    else:
        try:
            data = req.get_json()
            sendTG(str(data))
            #logging.info(data)
            if data["object"] == "page":
                for entry in data['entry']:
                    for messaging_event in entry['messaging']:
                        MYAPP_TOKEN = os.environ["APP_TOKEN"]
                        bot = Bot(MYAPP_TOKEN)
                        recipient_id = messaging_event['sender']['id']
                        payload = messaging_event["postback"]["payload"]
                        bot.set_persistent_menu(psmenu)
                        bot.set_get_started(gs_data)
                        if payload == "get_started":
                            send_message(recipient_id, "You may also receive daily bible verses through twitter!\n\nThe Daily Verse delivers words of God directly to your devices daily in a simple and easy to read layout. The format of this bot is to give you a short and meaningful daily bible verse to give you strength and inspiration every day.\n\ntwitter.com/ddailyverse")
                        elif payload == "the_info":
                            send_message(recipient_id, "Have a daily dose of spiritual food with The Daily Verse!\n\nThis is made to maximize the advantages of Facebook Messenger because many are using at as a means of communication. It is also a good platform to spread the word of God and to help you on your spiritual journey.\n\nYou can also follow our twitter account twitter.com/ddailyverse")
                        elif payload == "random_verse":
                            send_message(recipient_id, bible_verse())                    
            return func.HttpResponse("success", status_code=200)
        except Exception as e:
            return func.HttpResponse("Errrrrrrrooorrrrrrrr", status_code=500)
            
def send_message(recipient_id, response):
    bot.send_text_message(recipient_id, response)
    return "success"

def bible_verse():
    r = requests.get("https://beta.ourmanna.com/api/v1/get/?format=json&order=random")
    verse = r.json()
    verse_message = verse["verse"]["details"]["text"]
    theverse = verse["verse"]["details"]["reference"]
    toreturn = "\"{}\" - {}".format(verse_message, theverse)
    return toreturn
