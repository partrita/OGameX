import ctypes
import json
import os
from typing import Dict, Any, Optional

class RustBattleEngineWrapper:
    """Wrapper around rust/battle_engine_ffi shared library for maximum performance."""

    def __init__(self, lib_path: Optional[str] = None):
        self.lib = None
        if lib_path is None:
            # Common paths for compiled rust library
            candidates = [
                os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../rust/battle_engine_ffi/target/release/libbattle_engine_ffi.so")),
                os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../rust/battle_engine_ffi/target/debug/libbattle_engine_ffi.so")),
            ]
            for path in candidates:
                if os.path.exists(path):
                    lib_path = path
                    break

        if lib_path and os.path.exists(lib_path):
            try:
                self.lib = ctypes.CDLL(lib_path)
                # Rust exposes fight_battle_rounds; keep battle_engine alias for compat
                fn = getattr(self.lib, "fight_battle_rounds", None) or getattr(self.lib, "battle_engine", None)
                if fn is not None:
                    fn.argtypes = [ctypes.c_char_p]
                    fn.restype = ctypes.c_char_p
                    self._fn = fn
                else:
                    self.lib = None
            except Exception:
                self.lib = None
                self._fn = None
        else:
            self._fn = None

    def is_available(self) -> bool:
        return self.lib is not None and getattr(self, "_fn", None) is not None

    def execute_battle(self, battle_input: Dict[str, Any]) -> Dict[str, Any]:
        """Runs the combat simulation via Rust FFI or fallback python simulation."""
        if self.is_available():
            try:
                input_json = json.dumps(battle_input).encode("utf-8")
                result_ptr = self._fn(input_json)
                if result_ptr:
                    result_str = ctypes.c_char_p(result_ptr).value.decode("utf-8")
                    return json.loads(result_str)
            except Exception:
                pass
        
        # Fallback simulation if Rust FFI is not compiled yet
        return self._fallback_simple_battle(battle_input)

    def _fallback_simple_battle(self, battle_input: Dict[str, Any]) -> Dict[str, Any]:
        """Deterministic fallback: compare total attack vs hull."""
        try:
            atk_units = []
            for fleet in battle_input.get("attacker_fleets", []):
                atk_units.extend(fleet.get("units", {}).values())
            def_units = []
            for fleet in battle_input.get("defender_fleets", []):
                def_units.extend(fleet.get("units", {}).values())
            atk_power = sum(u.get("attack_power", 0) * u.get("amount", 0) for u in atk_units)
            def_power = sum(u.get("attack_power", 0) * u.get("amount", 0) for u in def_units)
            atk_hull = sum(u.get("hull_plating", 0) * u.get("amount", 0) for u in atk_units)
            def_hull = sum(u.get("hull_plating", 0) * u.get("amount", 0) for u in def_units)
            if atk_power == 0 and def_power == 0:
                winner = "draw"
            elif atk_power + atk_hull > def_power + def_hull:
                winner = "attacker"
            elif def_power + def_hull > atk_power + atk_hull:
                winner = "defender"
            else:
                winner = "draw"
        except Exception:
            winner = "attacker"
        return {
            "winner": winner,
            "rounds": 1,
            "attacker_losses": {"metal": 0, "crystal": 0, "deuterium": 0},
            "defender_losses": {"metal": 0, "crystal": 0, "deuterium": 0},
            "debris": {"metal": 0, "crystal": 0},
            "rounds_data": []
        }
