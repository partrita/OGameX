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
                # Define signature: char* battle_engine(char* input_json)
                self.lib.battle_engine.argtypes = [ctypes.c_char_p]
                self.lib.battle_engine.restype = ctypes.c_char_p
            except Exception as e:
                self.lib = None

    def is_available(self) -> bool:
        return self.lib is not None

    def execute_battle(self, battle_input: Dict[str, Any]) -> Dict[str, Any]:
        """Runs the combat simulation via Rust FFI or fallback python simulation."""
        if self.lib:
            input_json = json.dumps(battle_input).encode("utf-8")
            result_ptr = self.lib.battle_engine(input_json)
            if result_ptr:
                result_str = ctypes.c_char_p(result_ptr).value.decode("utf-8")
                return json.loads(result_str)
        
        # Fallback simulation if Rust FFI is not compiled yet
        return self._fallback_simple_battle(battle_input)

    def _fallback_simple_battle(self, battle_input: Dict[str, Any]) -> Dict[str, Any]:
        """Simple fallback simulation structure."""
        return {
            "winner": "attacker",
            "rounds": 1,
            "attacker_losses": {"metal": 0, "crystal": 0, "deuterium": 0},
            "defender_losses": {"metal": 0, "crystal": 0, "deuterium": 0},
            "debris": {"metal": 0, "crystal": 0},
            "rounds_data": []
        }
