
class AchievmentEarnedEvent:
    i = 0

class BattleRankUpEvent:
    i = 0

class DeathEvent:
    attacker_character_id = "" #ID of attacker
    attacker_fire_mode_id = ""
    attacker_loadout_id = ""
    attacker_vehicle_id = ""
    attacker_weapon_id = ""
    character_id = ""  #ID of killed player
    character_loadout_id = ""
    event_name = "Death"
    is_headshot = ""
    timestamp = ""
    world_id = ""
    zone_id = ""

class ItemAddedEvent:
	i = 0

class SkillAddedEvent:
    i = 0

class VehicleDestroyEvent:
    i = 0

class GainExperienceEvent:
    amount = ""
    character_id = ""
    event_name = "GainExperience"
    experience_id = ""
    loadout_id = ""
    other_id = ""
    timestamp = ""
    world_id = ""
    zone_id = ""

class PlayerFacilityCaptureEvent:
    i = 0

class PlayerFacilityDefendEvent:
    i = 0

class PlayerLoginEvent:
    i = 0

class PlayerLogoutEvent:
    i = 0
