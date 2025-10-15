from deprecated import deprecated
from pydantic import BaseModel, Field

from wt_resource_tool.schema._common import Country, NameI18N


class VehicleDesc(BaseModel):
    vehicle_id: str
    """Unique vehicle ID"""

    name_shop_i18n: NameI18N | None
    name_0_i18n: NameI18N | None
    name_1_i18n: NameI18N | None
    name_2_i18n: NameI18N | None

    rank: int
    """Vehicle rank, from 1 to 10+"""

    economic_rank: int
    """Vehicle economic rank"""

    economic_rank_arcade: int
    """Vehicle economic rank in arcade mode"""

    economic_rank_historical: int
    """Vehicle economic rank in historical mode"""

    economic_rank_simulation: int
    """Vehicle economic rank in simulation mode"""

    economic_rank_tank_historical: int | None = Field(default=None)
    """Vehicle economic rank in historical tank mode"""

    economic_rank_tank_simulation: int | None = Field(default=None)
    """Vehicle economic rank in simulation tank mode"""

    does_it_give_nation_bonus: bool | None = Field(default=None)
    """Whether the vehicle gives nation bonus"""

    country: Country
    """Country of vehicle"""

    unit_class: str
    """Class of vehicle.
    
    For example, exp_fighter, etc...
    """

    spawn_type: str | None = Field(
        default=None,
    )
    """Spawn type of vehicle in battles.
    
    For example, bomber, etc..."""

    unit_move_type: str
    """Movement type of vehicle.
    
    For example, air, tank, etc...
    """

    speed: float | None = Field(default=None)
    """Base speed in km/h"""

    value: int
    """Cost value in sliver lions"""

    req_exp: int | None = Field(
        default=None,
    )
    """Research cost in experience points"""

    train_cost: int
    """Crew training cost in experience points"""

    train2_cost: int
    """Crew training cost in experience points for the phase 2"""

    train3_cost_gold: int
    """Crew training cost in golden eagles for the phase 3"""

    train3_cost_exp: int
    """Crew training cost in experience points for the phase 3"""

    repair_time_hrs_arcade: float
    """Repair time in hours in arcade"""

    repair_time_hrs_historical: float
    """Repair time in hours in historical"""

    repair_time_hrs_simulation: float
    """Repair time in hours in simulation"""

    repair_time_hrs_no_crew_arcade: float
    """Repair time in hours in arcade without crew"""

    repair_time_hrs_no_crew_historical: float
    """Repair time in hours in historical without crew"""

    repair_time_hrs_no_crew_simulation: float
    """Repair time in hours in simulation without crew"""

    repair_cost_arcade: int
    """Repair cost in sliver lions in arcade"""

    repair_cost_historical: int
    """Repair cost in sliver lions in historical"""

    repair_cost_simulation: int
    """Repair cost in sliver lions in simulation"""

    repair_cost_per_min_arcade: int
    """Repair cost per minute in sliver lions in arcade"""

    repair_cost_per_min_historical: int
    """Repair cost per minute in sliver lions in historical"""

    repair_cost_per_min_simulation: int
    """Repair cost per minute in sliver lions in simulation"""

    repair_cost_full_upgraded_arcade: int | None = Field(
        default=None,
    )
    """Repair cost in sliver lions when vehicle is fully upgraded in arcade"""

    repair_cost_full_upgraded_historical: int | None = Field(
        default=None,
    )
    """Repair cost in sliver lions when vehicle is fully upgraded in historical"""

    repair_cost_full_upgraded_simulation: int | None = Field(
        default=None,
    )
    """Repair cost in sliver lions when vehicle is fully upgraded in simulation"""

    battle_time_award_arcade: int
    battle_time_award_historical: int
    battle_time_award_simulation: int

    timed_award_simulation: int | None = Field(default=None)

    avg_award_arcade: int
    avg_award_historical: int
    avg_award_simulation: int

    reward_mul_arcade: float
    """Reward multiplier in arcade"""

    reward_mul_historical: float
    """Reward multiplier in historical"""

    reward_mul_simulation: float
    """Reward multiplier in simulation"""

    exp_mul: float
    """Base experience multiplier"""

    ground_kill_mul: float | None = Field(default=None)
    """Ground kill exp multiplier"""

    battle_time_arcade: float
    battle_time_historical: float
    battle_time_simulation: float

    req_air: str | None = Field(
        default=None,
    )
    """Pre required vehicle ID"""

    reload_time_cannon: float | None = Field(
        default=None,
    )
    """Reload time of the main cannon in seconds"""

    reload_time_mgun: float | None = Field(default=None)
    """Reload time of the machine gun in seconds"""

    max_ammo: int | None = Field(default=None)
    """Maximum ammunition count"""

    max_flight_time_minutes: int | None = Field(default=None)

    crew_total_count: int | None = Field(default=None)
    """Total crew count"""

    primary_weapon_auto_loader: bool | None = Field(default=None)
    """Whether the primary weapon is an auto-loader"""

    cost_gold: int | None = Field(default=None)

    turret_speed: tuple[float, float] | None = Field(default=None)
    """Turret rotation speed in horizontal and vertical axis in degrees per second"""

    need_buy_to_open_next_in_tier1: int
    """Number of upgrades needed to unlock from tier 1 to next research"""

    need_buy_to_open_next_in_tier2: int
    """Number of upgrades needed to unlock from tier 2 to next research"""

    need_buy_to_open_next_in_tier3: int
    """Number of upgrades needed to unlock from tier 3 to next research"""

    need_buy_to_open_next_in_tier4: int
    """Number of upgrades needed to unlock from tier 4 to next research"""

    max_dm_part_repair_time_sec: int | None = Field(default=None)
    """Maximum damage part repair time in seconds"""

    gift: str | None = Field(default=None)

    research_type: str | None = Field(default=None)
    """Research type of vehicle. For now only clanVehicle is known"""

    game_version: str
    """Game version when the vehicle data is parsed"""

    @deprecated(reason="use get_icon_cdn_url instead")
    def get_icon_url(
        self,
    ) -> str:
        return self.get_icon_cdn_url()

    def get_icon_cdn_url(self) -> str:
        """Get the vehicle icon CDN URL.

        CDN is loaded from jsdelivr, which is a free CDN for GitHub repositories.
        """
        return f"https://cdn.jsdelivr.net/gh/gszabi99/War-Thunder-Datamine@refs/heads/master/atlases.vromfs.bin_u/units/{self.vehicle_id}.png"


class ParsedVehicleData(BaseModel):
    vehicles: list[VehicleDesc]
    max_economic_rank: int
