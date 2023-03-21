import json
import random

from flask import Flask, request
from flask_ngrok import run_with_ngrok

app = Flask(__name__)
run_with_ngrok(app)

player_class = {
    'rogue': {
        'name': 'Лучник',
        'img': '997614/69eaa6520acbf2fd8db8'
    },
    'warrior': {
        'name': 'Воин',
        'img': '937455/a8ab9c3e5b0254e2f15c'
    },
    'mage': {
        'name': 'Маг',
        'img': '997614/f2f41b083cb5a56771d5'
    }
}

enemy_list = [
    {'name': 'Гоблин', 'img': '213044/db5809a1e195f2920280'},
    {'name': 'Оборотень', 'img': '1652229/3626c19b6865571bc91e'},
    {'name': 'Мумия', 'img': '1540737/4ffaec56deb39b1dfa3a'}
]


def offer_class(user_id, req, res):
    for entity in req['request']['nlu']['entities']:
        if entity['type'] == 'YANDEX.FIO':
            if name := entity['value'].get('first_name'):
                name = name.capitalize()
                session_state[user_id]['first_name'] = name
                res['response']['text'] = f"Приятно познакомиться {name}! Выбери свой класс"
                res['response']['card'] = {
                    'type': 'ItemsList',
                    'header': {'text': f"Приятно познакомиться, {name}! Выбери свой класс"},
                    'items': [
                        {
                            'image_id': player_class['warrior']['img'],
                            'title': player_class['warrior']['name'],
                            'description': 'Меч - грозное оружие',
                            'button': {
                                'text': 'Выбрать воина',
                                'payload': {
                                    'class': 'warrior'
                                }
                            }
                        },
                        {
                            'image_id': player_class['mage']['img'],
                            'title': player_class['mage']['name'],
                            'description': 'Фаербол - грозное оружие',
                            'button': {
                                'text': 'Выбрать мага',
                                'payload': {
                                    'class': 'mage'
                                }
                            }
                        },
                        {
                            'image_id': player_class['rogue']['img'],
                            'title': player_class['rogue']['name'],
                            'description': 'Лук - грозное оружие',
                            'button': {
                                'text': 'Выбрать лучника',
                                'payload': {
                                    'class': 'rogue'
                                }
                            }
                        }
                    ],
                    'footer': {
                        'text': "Не ошибись с выбором!"
                    }
                }
                session_state[user_id] = {
                    'state': 2
                }
                return
    else:
        res['response']['text'] = 'Не расслышала имя. Повторите, пожалуйста'


def offer_adventure(user_id, req, res):
    try:
        selected_class = req['request']['payload']['class']
    except KeyError:
        res['response']['text'] = 'Пожалуйста, выберите класс'
        return
    session_state[user_id].update({
        'class': selected_class,
        'state': 3
    })
    res['response'] = {
        'text': f"{selected_class.capitalize()} - отличный выбор!",
        'card': {
            'type': 'BigImage',
            'image_id': player_class[selected_class]['img'],
            'title': f"{selected_class.capitalize()} - отличный выбор!"
        },
        'buttons': [
            {
                'title': 'В бой',
                'payload': {'fight': True},
                'hide': True
            },
            {
                'title': 'Завершить приключение',
                'payload': {'fight': False},
                'hide': True
            }
        ]
    }


def offer_fight(user_id, req, res):
    try:
        answer = req['request']['payload']['fight']
    except KeyError:
        res['response']['text'] = 'Пожалуйста, выберите действие'
        return
    if answer:
        enemy = random.choice(enemy_list)
        session_state[user_id]['state'] = 4
        res['response'] = {
            'text': f"Ваш противник - {enemy['name']}",
            'card': {
                'type': 'BigImage',
                'image_id': enemy['img'],
                'title': f"Ваш противник - {enemy['name']}"
            },
            'buttons': [
                {
                    'title': 'Ударить',
                    'payload': {'fight': True},
                    'hide': True
                },
                {
                    'title': 'Убежать',
                    'payload': {'fight': False},
                    'hide': True
                }
            ]
        }
    else:
        end_game(user_id, req, res)


def end_game(user_id, req, res):
    try:
        answer = req['request']['payload']['fight']
    except KeyError:
        res['response']['text'] = 'Пожалуйста, выберите действие'
        return
    if not answer:
        res['response']['text'] = 'Ваше приключение закончилось, не успев начаться'
    else:
        res['response']['text'] = 'Вы победили противника, о Вашем подвиге не забудут'
    res['response']['end_session'] = True


@app.route('/post', methods=['POST'])
def get_alice_request():
    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False
        }
    }

    handle_dialog(request.json, response)
    return json.dumps(response)


def handle_dialog(req, res):
    user_id = req['session']['user_id']
    if req['session']['new']:
        res['response']['text'] = 'Привет, мы тут играем в игру, назови своё имя'
        session_state[user_id] = {
            'state': 1
        }
        return
    states[session_state[user_id]['state']](user_id, req, res)


states = {
    1: offer_class,
    2: offer_adventure,
    3: offer_fight,
    4: end_game
}

session_state = {}
if __name__ == '__main__':
    app.run()
