"""
Data management for bot persistence (in-memory storage)
"""
from typing import Dict, List, Tuple, Optional
import threading

class DataManager:
    """Manage bot data storage across guilds"""
    
    def __init__(self):
        self._lock = threading.Lock()
        self._data = {
            'guilds': {},  # guild_id -> guild_data
        }
    
    def _ensure_guild(self, guild_id: int):
        """Ensure guild data structure exists"""
        if guild_id not in self._data['guilds']:
            self._data['guilds'][guild_id] = {
                'characters': {},  # name -> character_data
                'initiative': [],  # [(name, roll), ...]
                'notes': [],      # campaign notes
                'quests': [],     # quest log
                'inventory': [],  # party inventory
                'location': None, # current location
                'session': None,  # current session
            }
    
    # Initiative tracking methods
    def add_initiative(self, guild_id: int, name: str, roll: int):
        """Add character to initiative tracker"""
        with self._lock:
            self._ensure_guild(guild_id)
            guild_data = self._data['guilds'][guild_id]
            
            # Remove existing entry for this character
            guild_data['initiative'] = [
                (char_name, init_roll) for char_name, init_roll in guild_data['initiative']
                if char_name.lower() != name.lower()
            ]
            
            # Add new entry
            guild_data['initiative'].append((name, roll))
            
            # Sort by initiative (highest first)
            guild_data['initiative'].sort(key=lambda x: x[1], reverse=True)
    
    def get_initiative_order(self, guild_id: int) -> List[Tuple[str, int]]:
        """Get sorted initiative order"""
        with self._lock:
            self._ensure_guild(guild_id)
            return self._data['guilds'][guild_id]['initiative'].copy()
    
    def clear_initiative(self, guild_id: int):
        """Clear initiative tracker"""
        with self._lock:
            self._ensure_guild(guild_id)
            self._data['guilds'][guild_id]['initiative'] = []
    
    # Character management methods
    def add_character(self, guild_id: int, owner_id: int, name: str, hp: int):
        """Add character to database"""
        with self._lock:
            self._ensure_guild(guild_id)
            guild_data = self._data['guilds'][guild_id]
            
            guild_data['characters'][name.lower()] = {
                'name': name,
                'hp': hp,
                'max_hp': hp,
                'owner_id': owner_id,
                'created_at': self._get_timestamp()
            }
    
    def get_character(self, guild_id: int, name: str) -> Optional[Dict]:
        """Get character by name"""
        with self._lock:
            self._ensure_guild(guild_id)
            guild_data = self._data['guilds'][guild_id]
            return guild_data['characters'].get(name.lower())
    
    def update_character_hp(self, guild_id: int, name: str, new_hp: int) -> bool:
        """Update character HP"""
        with self._lock:
            self._ensure_guild(guild_id)
            guild_data = self._data['guilds'][guild_id]
            
            if name.lower() in guild_data['characters']:
                guild_data['characters'][name.lower()]['hp'] = new_hp
                return True
            return False
    
    def delete_character(self, guild_id: int, name: str) -> bool:
        """Delete character"""
        with self._lock:
            self._ensure_guild(guild_id)
            guild_data = self._data['guilds'][guild_id]
            
            if name.lower() in guild_data['characters']:
                del guild_data['characters'][name.lower()]
                return True
            return False
    
    def get_user_characters(self, guild_id: int, user_id: int) -> List[Dict]:
        """Get all characters owned by a user"""
        with self._lock:
            self._ensure_guild(guild_id)
            guild_data = self._data['guilds'][guild_id]
            
            return [
                char_data for char_data in guild_data['characters'].values()
                if char_data['owner_id'] == user_id
            ]
    
    def get_all_characters(self, guild_id: int) -> List[Dict]:
        """Get all characters in guild"""
        with self._lock:
            self._ensure_guild(guild_id)
            guild_data = self._data['guilds'][guild_id]
            return list(guild_data['characters'].values())
    
    # Utility methods
    def _get_timestamp(self) -> str:
        """Get current timestamp as string"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def get_guild_stats(self, guild_id: int) -> Dict:
        """Get guild statistics"""
        with self._lock:
            self._ensure_guild(guild_id)
            guild_data = self._data['guilds'][guild_id]
            
            return {
                'character_count': len(guild_data['characters']),
                'initiative_count': len(guild_data['initiative']),
                'active_initiative': len(guild_data['initiative']) > 0
            }
    
    def clear_guild_data(self, guild_id: int):
        """Clear all data for a guild"""
        with self._lock:
            if guild_id in self._data['guilds']:
                del self._data['guilds'][guild_id]
    
    # Note-taking methods
    def add_note(self, guild_id: int, author_id: int, title: str, content: str):
        """Add campaign note"""
        with self._lock:
            self._ensure_guild(guild_id)
            guild_data = self._data['guilds'][guild_id]
            
            note = {
                'id': len(guild_data['notes']) + 1,
                'title': title,
                'content': content,
                'author_id': author_id,
                'created_at': self._get_timestamp()
            }
            guild_data['notes'].append(note)
    
    def get_all_notes(self, guild_id: int) -> List[Dict]:
        """Get all campaign notes"""
        with self._lock:
            self._ensure_guild(guild_id)
            return self._data['guilds'][guild_id]['notes'].copy()
    
    # Quest management methods
    def add_quest(self, guild_id: int, author_id: int, title: str, description: str, status: str):
        """Add or update quest"""
        with self._lock:
            self._ensure_guild(guild_id)
            guild_data = self._data['guilds'][guild_id]
            
            # Check if quest exists (by title)
            for quest in guild_data['quests']:
                if quest['title'].lower() == title.lower():
                    quest['description'] = description
                    quest['status'] = status
                    quest['updated_at'] = self._get_timestamp()
                    return
            
            # Add new quest
            quest = {
                'id': len(guild_data['quests']) + 1,
                'title': title,
                'description': description,
                'status': status,
                'author_id': author_id,
                'created_at': self._get_timestamp(),
                'updated_at': self._get_timestamp()
            }
            guild_data['quests'].append(quest)
    
    def get_all_quests(self, guild_id: int) -> List[Dict]:
        """Get all quests"""
        with self._lock:
            self._ensure_guild(guild_id)
            return self._data['guilds'][guild_id]['quests'].copy()
    
    # Location management
    def set_location(self, guild_id: int, location: str, updater_id: int):
        """Set party location"""
        with self._lock:
            self._ensure_guild(guild_id)
            guild_data = self._data['guilds'][guild_id]
            
            guild_data['location'] = {
                'name': location,
                'updated_by': updater_id,
                'updated_at': self._get_timestamp()
            }
    
    def get_location(self, guild_id: int) -> Optional[Dict]:
        """Get current location"""
        with self._lock:
            self._ensure_guild(guild_id)
            return self._data['guilds'][guild_id]['location']
    
    # Session management
    def start_session(self, guild_id: int, dm_id: int, session_name: str):
        """Start new session"""
        with self._lock:
            self._ensure_guild(guild_id)
            guild_data = self._data['guilds'][guild_id]
            
            guild_data['session'] = {
                'name': session_name,
                'dm_id': dm_id,
                'started_at': self._get_timestamp(),
                'notes': []
            }
    
    def get_current_session(self, guild_id: int) -> Optional[Dict]:
        """Get current session"""
        with self._lock:
            self._ensure_guild(guild_id)
            return self._data['guilds'][guild_id]['session']
    
    # Inventory management
    def add_inventory_item(self, guild_id: int, added_by: int, name: str, quantity: int, description: str = None):
        """Add item to inventory"""
        with self._lock:
            self._ensure_guild(guild_id)
            guild_data = self._data['guilds'][guild_id]
            
            # Check if item exists
            for item in guild_data['inventory']:
                if item['name'].lower() == name.lower():
                    item['quantity'] += quantity
                    return
            
            # Add new item
            item = {
                'name': name,
                'quantity': quantity,
                'description': description,
                'added_by': added_by,
                'added_at': self._get_timestamp()
            }
            guild_data['inventory'].append(item)
    
    def get_inventory(self, guild_id: int) -> List[Dict]:
        """Get party inventory"""
        with self._lock:
            self._ensure_guild(guild_id)
            return self._data['guilds'][guild_id]['inventory'].copy()
    
    def remove_inventory_item(self, guild_id: int, name: str, quantity: int = 1) -> bool:
        """Remove item from inventory"""
        with self._lock:
            self._ensure_guild(guild_id)
            guild_data = self._data['guilds'][guild_id]
            
            for item in guild_data['inventory']:
                if item['name'].lower() == name.lower():
                    if item['quantity'] <= quantity:
                        guild_data['inventory'].remove(item)
                    else:
                        item['quantity'] -= quantity
                    return True
            return False

# Example usage
if __name__ == "__main__":
    dm = DataManager()
    
    # Test character management
    dm.add_character(123456789, 987654321, "Aragorn", 50)
    dm.add_character(123456789, 987654321, "Legolas", 40)
    
    char = dm.get_character(123456789, "aragorn")
    print(f"Character: {char}")
    
    # Test initiative tracking
    dm.add_initiative(123456789, "Aragorn", 15)
    dm.add_initiative(123456789, "Orc", 10)
    dm.add_initiative(123456789, "Legolas", 18)
    
    initiative = dm.get_initiative_order(123456789)
    print(f"Initiative: {initiative}")
    
    stats = dm.get_guild_stats(123456789)
    print(f"Stats: {stats}")
