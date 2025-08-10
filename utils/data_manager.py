# utils/data_manager.py
import threading
from collections import defaultdict
import datetime

LOCK = threading.Lock()
DATA = {}

def default_guild_data():
    return {
        'characters': {},
        'initiative': [],
        'notes': [],
        'quests': defaultdict(list),
        'location': None,
        'inventory': {},
        'session_voice': None,
    }

def add_character(guild_id, name, max_hp):
    with LOCK:
        data = DATA.setdefault(guild_id, default_guild_data())
        if name in data['characters']:
            raise ValueError("Character already exists")
        data['characters'][name] = {'hp': max_hp, 'max_hp': max_hp}

def get_character(guild_id, name):
    with LOCK:
        data = DATA.get(guild_id, default_guild_data())
        return data['characters'].get(name)

def get_all_characters(guild_id):
    with LOCK:
        data = DATA.get(guild_id, default_guild_data())
        return data['characters'].copy()

def update_hp(guild_id, name, new_hp):
    with LOCK:
        data = DATA.get(guild_id, default_guild_data())
        if name in data['characters']:
            data['characters'][name]['hp'] = min(new_hp, data['characters'][name]['max_hp'])
            if data['characters'][name]['hp'] < 0:
                data['characters'][name]['hp'] = 0

def damage_character(guild_id, name, amount):
    with LOCK:
        data = DATA.get(guild_id, default_guild_data())
        if name in data['characters']:
            data['characters'][name]['hp'] -= amount
            if data['characters'][name]['hp'] < 0:
                data['characters'][name]['hp'] = 0

def heal_character(guild_id, name, amount):
    with LOCK:
        data = DATA.get(guild_id, default_guild_data())
        if name in data['characters']:
            data['characters'][name]['hp'] += amount
            if data['characters'][name]['hp'] > data['characters'][name]['max_hp']:
                data['characters'][name]['hp'] = data['characters'][name]['max_hp']

def add_initiative(guild_id, name, roll):
    with LOCK:
        data = DATA.get(guild_id, default_guild_data())
        data['initiative'].append({'name': name, 'roll': roll})
        data['initiative'].sort(key=lambda x: x['roll'], reverse=True)

def get_initiative(guild_id):
    with LOCK:
        data = DATA.get(guild_id, default_guild_data())
        return data['initiative'].copy()

def clear_initiative(guild_id):
    with LOCK:
        data = DATA.get(guild_id, default_guild_data())
        data['initiative'] = []

def add_note(guild_id, note):
    with LOCK:
        data = DATA.get(guild_id, default_guild_data())
        time = datetime.datetime.now().isoformat()
        data['notes'].append({'time': time, 'note': note})

def get_notes(guild_id):
    with LOCK:
        data = DATA.get(guild_id, default_guild_data())
        return data['notes'].copy()

def add_or_update_quest(guild_id, name, desc, status):
    with LOCK:
        data = DATA.get(guild_id, default_guild_data())
        for st, qlist in data['quests'].items():
            qlist[:] = [q for q in qlist if q['name'] != name]
        data['quests'][status].append({'name': name, 'desc': desc})

def get_quests(guild_id):
    with LOCK:
        data = DATA.get(guild_id, default_guild_data())
        return {k: v.copy() for k, v in data['quests'].items()}

def set_location(guild_id, loc):
    with LOCK:
        data = DATA.get(guild_id, default_guild_data())
        data['location'] = loc

def get_location(guild_id):
    with LOCK:
        data = DATA.get(guild_id, default_guild_data())
        return data['location']

def add_inventory(guild_id, item, qty, desc):
    with LOCK:
        data = DATA.get(guild_id, default_guild_data())
        if item in data['inventory']:
            data['inventory'][item]['qty'] += qty
        else:
            data['inventory'][item] = {'qty': qty, 'desc': desc}

def get_inventory(guild_id):
    with LOCK:
        data = DATA.get(guild_id, default_guild_data())
        return data['inventory'].copy()

def set_session_voice(guild_id, channel_id):
    with LOCK:
        data = DATA.get(guild_id, default_guild_data())
        data['session_voice'] = channel_id

def get_session_voice(guild_id):
    with LOCK:
        data = DATA.get(guild_id, default_guild_data())
        return data['session_voice']