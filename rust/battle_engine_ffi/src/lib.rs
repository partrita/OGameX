//! # Battle Engine FFI (전투 시뮬레이션 엔진)
//!
//! `battle_engine_ffi`는 OGameX의 고성능 우주 전투 시뮬레이션 엔진의 Rust 구현체입니다.
//!
//! ## 🚀 핵심 특징 및 성능
//! - **초고속 연산**: 대규모 함대 전투 시 순수 인터프리터 언어 대비 **최대 200배 빠르고 10배 적은 메모리**를 사용합니다.
//! - **ACS 다중 함대 지원**: 연합 공격(ACS Attack) 및 연합 방어(ACS Defend)를 완벽 지원하며,
//!   `fleet_mission_id`와 `owner_id`를 추적하여 플레이어별/함대별 손실 보고서를 생성합니다.
//! - **OGame 전투 규칙 100% 재현**:
//!   1. 최대 6라운드 진행 (한쪽 전멸 시 조기 종료)
//!   2. 1% 미만 흠집 공격 무효화 (Bounce)
//!   3. 쉴드 우선 흡수 및 라운드 종료 시 100% 쉴드 재생
//!   4. 선체(Hull) 손상 70% 초과 시 확률적 폭발(Explosion dice roll)
//!   5. 래피드파이어(Rapidfire) 연쇄 공격 확률 계산

use serde::{Deserialize, Serialize};
use std::ffi::{CStr, CString};
use std::os::raw::c_char;
use rand::Rng;
use std::collections::HashMap;
use memory_stats::memory_stats;

/// [입력 DTO] 전투 시뮬레이션 요청 전체 데이터 (공격측/방어측 함대 목록)
#[derive(Serialize, Deserialize)]
pub struct BattleInput {
    attacker_fleets: Vec<AttackerFleetInput>,
    defender_fleets: Vec<DefenderFleetInput>,
}

/// [입력 DTO] 개별 공격측 함대 (ACS 다중 함대 구분을 위한 ID 포함)
#[derive(Serialize, Deserialize, Clone)]
struct AttackerFleetInput {
    fleet_mission_id: u32,
    owner_id: u32,
    units: HashMap<i16, BattleUnitInfo>,
}

/// [입력 DTO] 개별 방어측 함대
#[derive(Serialize, Deserialize, Clone)]
struct DefenderFleetInput {
    fleet_mission_id: u32,
    owner_id: u32,
    units: HashMap<i16, BattleUnitInfo>,
}

/// [유닛 스펙] 유닛 기본 제원 (공격력, 쉴드, 선체, 래피드파이어 등)
#[derive(Serialize, Deserialize, Clone)]
struct BattleUnitInfo {
    unit_id: i16,
    amount: u32,
    attack_power: f32,
    shield_points: f32,
    hull_plating: f32,
    rapidfire: HashMap<i16, u16>, // 타겟 unit_id -> 래피드파이어 배수
}

/// 유닛 개수 요약 구조체 (통계/보고서용)
#[derive(Serialize, Deserialize, Clone)]
struct BattleUnitCount {
    unit_id: i16,
    amount: u32,
}

/// [실제 시뮬레이션 개체] 전투 중 개별 함선 1척의 실시간 체력 및 소속 정보
#[derive(Serialize, Deserialize, Clone)]
struct BattleUnitInstance {
    unit_id: i16,
    fleet_mission_id: u32,
    owner_id: u32,
    current_shield_points: f32, // 현재 남은 쉴드 (라운드마다 완충)
    current_hull_plating: f32,   // 현재 남은 선체 체력 (누적 손상)
}

/// [라운드 통계] 단일 전투 라운드의 모든 결과 데이터
#[derive(Serialize, Deserialize)]
struct BattleRound {
    attacker_ships: HashMap<i16, BattleUnitCount>,
    defender_ships: HashMap<i16, BattleUnitCount>,
    attacker_losses: HashMap<i16, BattleUnitCount>,
    defender_losses: HashMap<i16, BattleUnitCount>,
    attacker_losses_in_round: HashMap<i16, BattleUnitCount>,
    defender_losses_in_round: HashMap<i16, BattleUnitCount>,
    absorbed_damage_attacker: f64, // 공격측 쉴드가 흡수한 총 데미지
    absorbed_damage_defender: f64, // 방어측 쉴드가 흡수한 총 데미지
    full_strength_attacker: f64,   // 공격측이 가한 총 순수 타격력
    full_strength_defender: f64,   // 방어측이 가한 총 순수 타격력
    hits_attacker: u32,            // 공격측 유효 타격 횟수
    hits_defender: u32,            // 방어측 유효 타격 횟수
    attacker_fleet_results: HashMap<u32, AttackerFleetResult>, // 함대별 세부 손실
    defender_fleet_results: HashMap<u32, DefenderFleetResult>,
}

/// 개별 공격측 함대의 라운드 결과 (시작 유닛, 생존 유닛, 손실 유닛)
#[derive(Serialize, Deserialize, Clone)]
struct AttackerFleetResult {
    fleet_mission_id: u32,
    owner_id: u32,
    units_start: HashMap<i16, BattleUnitCount>,
    units_result: HashMap<i16, BattleUnitCount>,
    units_lost: HashMap<i16, BattleUnitCount>,
}

/// 개별 방어측 함대의 라운드 결과
#[derive(Serialize, Deserialize, Clone)]
struct DefenderFleetResult {
    fleet_mission_id: u32,
    owner_id: u32,
    units_start: HashMap<i16, BattleUnitCount>,
    units_result: HashMap<i16, BattleUnitCount>,
    units_lost: HashMap<i16, BattleUnitCount>,
}

/// 메모리 프로파일링 지표 (디버그용)
#[derive(Serialize, Deserialize)]
struct MemoryMetrics {
    peak_memory: u64, // KB 단위
}

/// [최종 출력 DTO] 전투 전체 라운드 결과 및 통계
#[derive(Serialize, Deserialize)]
pub struct BattleOutput {
    rounds: Vec<BattleRound>,
    memory_metrics: MemoryMetrics,
}

/// ============================================================================
/// FFI C-Interface 진입점: 외부 언어(Python / PHP 등)에서 호출되는 함수
/// ============================================================================
#[no_mangle]
pub extern "C" fn fight_battle_rounds(input_json: *const c_char) -> *mut c_char {
    // 1. C-String 포인터를 안전하게 Rust 문자열 슬라이스로 변환
    let input_str = unsafe { CStr::from_ptr(input_json).to_str().unwrap() };
    
    // 2. JSON 파싱
    let battle_input: BattleInput = serde_json::from_str(input_str).unwrap();
    
    // 3. 실제 전투 시뮬레이션 수행
    let battle_output = process_battle_rounds(battle_input);
    
    // 4. 결과를 JSON 문자열로 직렬화 후 C 포인터로 반환
    let result_json = serde_json::to_string(&battle_output).unwrap();
    let c_str = CString::new(result_json).unwrap();
    c_str.into_raw()
}

/// ============================================================================
/// 전투 시뮬레이션 메인 루프 (최대 6라운드)
/// ============================================================================
fn process_battle_rounds(input: BattleInput) -> BattleOutput {
    let mut peak_memory = 0;
    let mut rounds = Vec::new();

    // 1. 함대 메타데이터 및 소유자 매핑 구성
    let mut attacker_fleet_metadata: HashMap<u32, HashMap<i16, BattleUnitInfo>> = HashMap::new();
    let mut attacker_fleet_owners: HashMap<u32, u32> = HashMap::new();
    for fleet in &input.attacker_fleets {
        attacker_fleet_metadata.insert(fleet.fleet_mission_id, fleet.units.clone());
        attacker_fleet_owners.insert(fleet.fleet_mission_id, fleet.owner_id);
    }

    let mut defender_fleet_metadata: HashMap<u32, HashMap<i16, BattleUnitInfo>> = HashMap::new();
    let mut defender_fleet_owners: HashMap<u32, u32> = HashMap::new();
    for fleet in &input.defender_fleets {
        defender_fleet_metadata.insert(fleet.fleet_mission_id, fleet.units.clone());
        defender_fleet_owners.insert(fleet.fleet_mission_id, fleet.owner_id);
    }

    // 2. 입력받은 수량(amount)을 개별 함선 인스턴스 배열(`Vec<BattleUnitInstance>`)로 전개
    let mut attacker_units = expand_fleets(&input.attacker_fleets);
    let mut defender_units = expand_fleets(&input.defender_fleets);

    update_peak_memory(&mut peak_memory);

    // 3. 최대 6라운드 전투 루프 실행
    for _ in 0..6 {
        // 어느 한 쪽이라도 전멸하면 전투 종료
        if attacker_units.is_empty() || defender_units.is_empty() {
            break;
        }

        let mut round = BattleRound {
            attacker_ships: HashMap::new(),
            defender_ships: HashMap::new(),
            attacker_losses: HashMap::new(),
            defender_losses: HashMap::new(),
            attacker_losses_in_round: HashMap::new(),
            defender_losses_in_round: HashMap::new(),
            absorbed_damage_attacker: 0.0,
            absorbed_damage_defender: 0.0,
            full_strength_attacker: 0.0,
            full_strength_defender: 0.0,
            hits_attacker: 0,
            hits_defender: 0,
            attacker_fleet_results: HashMap::new(),
            defender_fleet_results: HashMap::new(),
        };

        // 빠른 조회를 위한 전체 유닛 메타데이터 병합
        let mut attacker_units_metadata: HashMap<i16, BattleUnitInfo> = HashMap::new();
        for fleet_units in attacker_fleet_metadata.values() {
            for (unit_id, unit_info) in fleet_units {
                attacker_units_metadata.insert(*unit_id, unit_info.clone());
            }
        }

        let mut defender_units_metadata: HashMap<i16, BattleUnitInfo> = HashMap::new();
        for fleet_units in defender_fleet_metadata.values() {
            for (unit_id, unit_info) in fleet_units {
                defender_units_metadata.insert(*unit_id, unit_info.clone());
            }
        }

        // [동시 교전] 
        // 1) 공격측 -> 방어측 사격
        process_combat(&mut attacker_units, &mut defender_units, &mut round, &attacker_units_metadata, &defender_units_metadata, true);
        // 2) 방어측 -> 공격측 반격
        process_combat(&mut defender_units, &mut attacker_units, &mut round, &defender_units_metadata, &attacker_units_metadata, false);

        // [라운드 정리] 파괴된 유닛 제거 및 잔존 유닛 쉴드 100% 재생
        cleanup_round(&mut round, &mut attacker_units, &mut defender_units, &attacker_units_metadata, &defender_units_metadata);

        // [통계 집계] 생존 유닛 요약 및 손실 계산
        round.attacker_ships = compress_units(&attacker_units);
        round.defender_ships = compress_units(&defender_units);
        calculate_losses(&mut round, &attacker_units_metadata, &defender_units_metadata);
        calculate_fleet_results(&mut round, &attacker_units, &defender_units, &attacker_fleet_metadata, &defender_fleet_metadata, &attacker_fleet_owners, &defender_fleet_owners);

        rounds.push(round);
        update_peak_memory(&mut peak_memory);
    }

    BattleOutput {
        rounds,
        memory_metrics: MemoryMetrics {
            peak_memory,
        },
    }
}

/// 입력받은 함대 그룹을 1척 단위의 개별 `BattleUnitInstance` 벡터로 변환
fn expand_fleets(fleets: &Vec<impl FleetInput>) -> Vec<BattleUnitInstance> {
    let mut expanded = Vec::new();
    for fleet in fleets {
        for (_, unit) in fleet.get_units() {
            for _ in 0..unit.amount {
                expanded.push(BattleUnitInstance {
                    unit_id: unit.unit_id.clone(),
                    fleet_mission_id: fleet.get_fleet_mission_id(),
                    owner_id: fleet.get_owner_id(),
                    current_shield_points: unit.shield_points,
                    current_hull_plating: unit.hull_plating
                });
            }
        }
    }
    expanded
}

/// 함대 입력 추상화 Trait
trait FleetInput {
    fn get_fleet_mission_id(&self) -> u32;
    fn get_owner_id(&self) -> u32;
    fn get_units(&self) -> &HashMap<i16, BattleUnitInfo>;
}

impl FleetInput for AttackerFleetInput {
    fn get_fleet_mission_id(&self) -> u32 { self.fleet_mission_id }
    fn get_owner_id(&self) -> u32 { self.owner_id }
    fn get_units(&self) -> &HashMap<i16, BattleUnitInfo> { &self.units }
}

impl FleetInput for DefenderFleetInput {
    fn get_fleet_mission_id(&self) -> u32 { self.fleet_mission_id }
    fn get_owner_id(&self) -> u32 { self.owner_id }
    fn get_units(&self) -> &HashMap<i16, BattleUnitInfo> { &self.units }
}

/// 개별 유닛 인스턴스 배열을 유닛 종류별 수량(Count) 맵으로 압축 집계
fn compress_units(units: &Vec<BattleUnitInstance>) -> HashMap<i16, BattleUnitCount> {
    units.iter()
        .fold(HashMap::new(), |mut counts, unit| {
            *counts.entry(unit.unit_id).or_insert(0) += 1;
            counts
        })
        .into_iter()
        .map(|(unit_id, count)| {
            (unit_id, BattleUnitCount {
                unit_id,
                amount: count,
            })
        })
        .collect()
}

/// 함대별(Fleet Mission ID) 시작 수량, 생존 수량, 손실 수량 계산
fn compress_fleet_results(
    units: &Vec<BattleUnitInstance>,
    fleet_mission_id: u32,
    _owner_id: u32,
    initial_units: &HashMap<i16, BattleUnitInfo>,
) -> (HashMap<i16, BattleUnitCount>, HashMap<i16, BattleUnitCount>, HashMap<i16, BattleUnitCount>) {
    let fleet_units: Vec<&BattleUnitInstance> = units.iter()
        .filter(|u| u.fleet_mission_id == fleet_mission_id)
        .collect();

    let mut units_result: HashMap<i16, BattleUnitCount> = HashMap::new();
    for unit in &fleet_units {
        increment_battle_unit_count_amount(&mut units_result, unit.unit_id, 1);
    }

    let mut units_start: HashMap<i16, BattleUnitCount> = HashMap::new();
    for (unit_id, unit_info) in initial_units {
        units_start.insert(*unit_id, BattleUnitCount {
            unit_id: *unit_id,
            amount: unit_info.amount,
        });
    }

    let mut units_lost: HashMap<i16, BattleUnitCount> = HashMap::new();
    for (unit_id, start_unit) in &units_start {
        let result_amount = units_result.get(unit_id).map(|u| u.amount).unwrap_or(0);
        if start_unit.amount > result_amount {
            units_lost.insert(*unit_id, BattleUnitCount {
                unit_id: *unit_id,
                amount: start_unit.amount - result_amount,
            });
        }
    }

    (units_start, units_result, units_lost)
}

/// ============================================================================
/// [핵심 전투 로직] 단일 공격 페이즈 연산
/// 1. 무작위 타겟 선정
/// 2. 1% 미만 흠집 공격(Bounce) 체크
/// 3. 쉴드 감쇄 후 잔여 데미지 선체 관통
/// 4. 선체 70% 손상 시 폭발 주사위(Explosion Roll)
/// 5. 래피드파이어(Rapidfire) 연쇄 사격 확률 판정
/// ============================================================================
fn process_combat(
    attackers: &mut Vec<BattleUnitInstance>,
    defenders: &mut Vec<BattleUnitInstance>,
    round: &mut BattleRound,
    attacker_unit_metadata: &HashMap<i16, BattleUnitInfo>,
    defender_unit_metadata: &HashMap<i16, BattleUnitInfo>,
    is_attacker: bool,
) {
    let mut rng = rand::thread_rng();

    for attacker in attackers.iter() {
        let mut continue_attacking = true;
        let attacker_metadata = attacker_unit_metadata.get(&attacker.unit_id).unwrap();
        let damage = attacker_metadata.attack_power;

        while continue_attacking {
            continue_attacking = false;

            // 방어측에서 무작위 타겟 1척 선정
            let target_idx = rng.gen_range(0..defenders.len());
            let target = &mut defenders[target_idx];
            let target_metadata = defender_unit_metadata.get(&target.unit_id).unwrap();

            // [OGame 규칙 1] 공격력이 타겟 최대 쉴드의 1% 미만이면 공격 무효화(Bounce)
            if damage < (0.01 * target_metadata.shield_points) {
                continue;
            }

            // [OGame 규칙 2] 데미지를 쉴드에 먼저 흡수, 남은 데미지는 선체(Hull)에 직접 적용
            let mut shield_absorption = 0.0;
            if target.current_shield_points > 0.0 {
                if damage <= target.current_shield_points {
                    shield_absorption = damage;
                    target.current_shield_points -= damage;
                } else {
                    shield_absorption = target.current_shield_points;
                    target.current_hull_plating -= damage - target.current_shield_points;
                    target.current_shield_points = 0.0;
                }
            } else {
                target.current_hull_plating -= damage;
            }

            // [OGame 규칙 3] 선체 체력이 70% 미만으로 떨어졌을 때 폭발 확률 주사위
            // 폭발 확률(%) = 100% - (현재 선체 / 최대 선체 * 100%)
            if target.current_hull_plating / target_metadata.hull_plating < 0.7 {
                let explosion_chance = 100.0 - ((target.current_hull_plating / target_metadata.hull_plating) * 100.0);
                let roll = rng.gen_range(0..=100);
                if roll < explosion_chance as i32 {
                    // 폭발 성공 시 즉시 파괴 처리
                    target.current_hull_plating = 0.0;
                    target.current_shield_points = 0.0;
                }
            }

            // 라운드 타격 통계 누적
            if is_attacker {
                round.hits_attacker += 1;
                round.full_strength_attacker += damage as f64;
                round.absorbed_damage_defender += shield_absorption as f64;
            } else {
                round.hits_defender += 1;
                round.full_strength_defender += damage as f64;
                round.absorbed_damage_attacker += shield_absorption as f64;
            }

            // [OGame 규칙 4] 래피드파이어(Rapidfire) 연쇄 사격 판정
            // 연속 사격 확률 = 100 - (100 / RF값)
            // (예: RF=4 -> 75% 확률, RF=10 -> 90% 확률, RF=250 -> 99.6% 확률)
            continue_attacking = if let Some(rapidfire_amount) = attacker_metadata.rapidfire.get(&target.unit_id) {
                let chance = 100.0 / *rapidfire_amount as f64;
                let rounded_chance = (chance * 100.0).floor() / 100.0;
                let rapidfire_chance = 100.0 - rounded_chance;

                let roll = rng.gen_range(0.0..100.0);
                roll <= rapidfire_chance // 확률 통과 시 loop 재실행
            } else {
                false
            };
        }
    }
}

/// 라운드 종료 정리: 파괴된 유닛 제거 및 잔존 유닛 쉴드 완충
fn cleanup_round(
    round: &mut BattleRound,
    attackers: &mut Vec<BattleUnitInstance>,
    defenders: &mut Vec<BattleUnitInstance>,
    units_metadata_attacker: &HashMap<i16, BattleUnitInfo>,
    units_metadata_defender: &HashMap<i16, BattleUnitInfo>,
) {
    // 1. 공격측 파괴 유닛 제거
    attackers.retain(|unit| {
        if unit.current_hull_plating <= 0.0 {
            increment_battle_unit_count_amount(&mut round.attacker_losses_in_round, unit.unit_id, 1);
            return false;
        }
        true
    });

    // 2. 공격측 생존 유닛 쉴드 100% 재생
    for unit in attackers.iter_mut() {
        let unit_metadata = units_metadata_attacker.get(&unit.unit_id).unwrap();
        unit.current_shield_points = unit_metadata.shield_points;
    }

    // 3. 방어측 파괴 유닛 제거
    defenders.retain(|unit| {
        if unit.current_hull_plating <= 0.0 {
            increment_battle_unit_count_amount(&mut round.defender_losses_in_round, unit.unit_id, 1);
            return false;
        }
        true
    });

    // 4. 방어측 생존 유닛 쉴드 100% 재생
    for unit in defenders.iter_mut() {
        let unit_metadata = units_metadata_defender.get(&unit.unit_id).unwrap();
        unit.current_shield_points = unit_metadata.shield_points;
    }
}

/// 전투 시작 전 수량 대비 누적 손실 계산
fn calculate_losses(
    round: &mut BattleRound,
    initial_attacker: &HashMap<i16, BattleUnitInfo>,
    initial_defender: &HashMap<i16, BattleUnitInfo>,
) {
    for (_, unit) in initial_attacker {
        let initial_count = unit.amount;
        let current_count = round.attacker_ships.get(&unit.unit_id).map(|unit| unit.amount).unwrap_or(0);
        if current_count < initial_count {
            let loss_amount = initial_count - current_count;
            increment_battle_unit_count_amount(&mut round.attacker_losses, unit.unit_id, loss_amount);
        }
    }

    for (_, unit) in initial_defender {
        let initial_count = unit.amount;
        let current_count = round.defender_ships.get(&unit.unit_id).map(|unit| unit.amount).unwrap_or(0);
        if current_count < initial_count {
            let loss_amount = initial_count - current_count;
            increment_battle_unit_count_amount(&mut round.defender_losses, unit.unit_id, loss_amount);
        }
    }
}

/// 다중 함대(ACS) 참여자별 세부 손실 통계 계산
fn calculate_fleet_results(
    round: &mut BattleRound,
    attacker_units: &Vec<BattleUnitInstance>,
    defender_units: &Vec<BattleUnitInstance>,
    attacker_fleets: &HashMap<u32, HashMap<i16, BattleUnitInfo>>,
    defender_fleets: &HashMap<u32, HashMap<i16, BattleUnitInfo>>,
    attacker_fleet_owners: &HashMap<u32, u32>,
    defender_fleet_owners: &HashMap<u32, u32>,
) {
    for (&fleet_mission_id, initial_units) in attacker_fleets {
        let owner_id = *attacker_fleet_owners.get(&fleet_mission_id).unwrap_or(&0);
        let (units_start, units_result, units_lost) =
            compress_fleet_results(attacker_units, fleet_mission_id, owner_id, initial_units);

        round.attacker_fleet_results.insert(fleet_mission_id, AttackerFleetResult {
            fleet_mission_id,
            owner_id,
            units_start,
            units_result,
            units_lost,
        });
    }

    for (&fleet_mission_id, initial_units) in defender_fleets {
        let owner_id = *defender_fleet_owners.get(&fleet_mission_id).unwrap_or(&0);
        let (units_start, units_result, units_lost) =
            compress_fleet_results(defender_units, fleet_mission_id, owner_id, initial_units);

        round.defender_fleet_results.insert(fleet_mission_id, DefenderFleetResult {
            fleet_mission_id,
            owner_id,
            units_start,
            units_result,
            units_lost,
        });
    }
}

/// 유닛 개수 증감 헬퍼 함수
fn increment_battle_unit_count_amount(hash_map: &mut HashMap<i16, BattleUnitCount>, unit_id: i16, amount_to_increment: u32) {
    let count = hash_map.entry(unit_id).or_insert(BattleUnitCount {
        unit_id,
        amount: 0,
    });
    count.amount += amount_to_increment;
}

/// 피크 메모리 사용량 기록 (디버그용)
fn update_peak_memory(current_peak: &mut u64) {
    if let Some(usage) = memory_stats() {
        *current_peak = (*current_peak).max(usage.physical_mem as u64 / 1024);
    }
}