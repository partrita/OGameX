use battle_engine_ffi;
use serde_json::Result;
use libc;

/// ============================================================================
/// 전투 엔진 독립 실행 및 벤치마크/디버깅용 메인 함수
/// ============================================================================
fn main() -> Result<()> {
    // 테스트용 10만 vs 10만 대규모 함대 JSON 입력 예제
    let json_input = r#"
    {
        "attacker_fleets": [
            {
                "fleet_mission_id": 1,
                "owner_id": 100,
                "units": {
                    "204": {
                        "unit_id": 204,
                        "amount": 100000,
                        "shield_points": 10.0,
                        "attack_power": 50.0,
                        "hull_plating": 400.0,
                        "rapidfire": {"210": 5, "212": 5}
                    }
                }
            }
        ],
        "defender_fleets": [
            {
                "fleet_mission_id": 2,
                "owner_id": 200,
                "units": {
                    "401": {
                        "unit_id": 401,
                        "amount": 100000,
                        "shield_points": 20.0,
                        "attack_power": 80.0,
                        "hull_plating": 200.0,
                        "rapidfire": {}
                    }
                }
            }
        ]
    }
    "#;

    // 1. JSON 문자열을 C-String 형태로 변환
    let c_input = std::ffi::CString::new(json_input).unwrap();

    // 2. FFI 함수 직접 호출 (Rust 전투 엔진 실행)
    let output_ptr = battle_engine_ffi::fight_battle_rounds(c_input.as_ptr());

    // 3. 반환된 C 포인터로부터 Rust String 복원 및 C 메모리 해제
    let output = unsafe {
        let output_str = std::ffi::CStr::from_ptr(output_ptr).to_string_lossy().into_owned();
        libc::free(output_ptr as *mut libc::c_void);
        output_str
    };

    // 4. 결과 JSON 예쁘게 콘솔 출력
    let json: serde_json::Value = serde_json::from_str(&output)?;
    println!("{}", serde_json::to_string_pretty(&json).unwrap());

    Ok(())
}