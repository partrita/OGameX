export const translations = {
  en: {
    // Header & Resources
    planetName: "Homeworld",
    metal: "Metal",
    crystal: "Crystal",
    deuterium: "Deuterium",
    energy: "Energy",
    liveSync: "Live Sync",
    offline: "Offline",

    // Navigation Menu
    navOverview: "Overview",
    navResources: "Resources",
    navFacilities: "Facilities",
    navShipyard: "Shipyard",
    navFleet: "Fleet Dispatch",
    navGalaxy: "Galaxy Map",

    // Overview Panel
    commandTitle: "Planetary Command",
    commandSubtitle: "Real-time status calculated via FastAPI asynchronous core",
    statDiameter: "Diameter",
    statFields: "Fields Used",
    statTemp: "Temperature",

    // Buildings & Facilities
    resourcesTitle: "Resource Buildings",
    resourcesSubtitle: "Construct and upgrade planetary mines to boost raw income",
    facilitiesTitle: "Planetary Facilities",
    facilitiesSubtitle: "Infrastructure required for high-tech research and armada production",
    lvl: "Lv.",
    prodPerHour: "Prod / Hr",
    upgradeToLvl: "Upgrade to Lv.",
    buildingCost: "Cost:",
    btnUpgrade: "Upgrade",
    btnBuildingUnavailable: "Insufficient Resources",

    // Shipyard
    shipyardTitle: "Orbital Shipyard",
    shipyardSubtitle: "Construct military armadas and transport fleets",
    hangarCount: "In Hangar:",
    shipSpecs: "Specs: ATK / DEF / SPD / CARGO",
    btnBuild: "Construct",

    // Fleet Dispatch
    fleetTitle: "Fleet Dispatch Command",
    fleetSubtitle: "Deploy exploration, tactical strikes, or transport fleets across galaxies",
    availableShips: "Available Fleet",
    fleetMission: "Select Mission",
    missionTransport: "Transport",
    missionDeploy: "Station / Deploy",
    missionAttack: "Attack / Raid",
    missionHarvest: "Debris Harvest",
    btnSendFleet: "🚀 Dispatch Fleet",

    // Galaxy
    galaxyTitle: "Galactic Cartography",
    galaxySubtitle: "Scan planetary systems, locate debris fields and neighboring empires",
    btnScanSystem: "Scan System",
    colPos: "Pos",
    colPlanet: "Planet",
    colPlayer: "Commander",
    colAlliance: "Alliance",
    colDebris: "Debris Field",
    colAction: "Action",
    emptySlot: "Empty Space",
    btnSendMission: "Target",

    // Fleet Dispatch Simulator
    fleetSimTitle: "Fast Fleet Dispatch Simulator",
    targetCoordsLabel: "Target Galaxy : System : Pos",
    fleetSelectionLabel: "Fleet Selection",
    shipSmallCargo: "Small Cargo (202)",
    shipLightFighter: "Light Fighter (204)",
    shipCruiser: "Cruiser (206)",
    btnCalculateFlight: "⚡ Calculate Mission Flight",

    // Results & Messages
    resDistance: "Distance:",
    resFlightTime: "Flight Time:",
    resFuel: "Fuel Consumption:",
    resCargo: "Total Cargo:",
    alertSelectShip: "Please select at least 1 ship.",
    alertCalcError: "Error calculating fleet flight.",
    activeMissionsTitle: "Active Fleet Movements & Missions",
    noActiveMissions: "No fleets currently in flight.",
    colMissionType: "Mission",
    colDestination: "Target",
    colFleetShips: "Ships",
    colRemainingTime: "ETA",
    colStatus: "Status",
    // Auth & User System
    loginTitle: "Commander Login",
    registerTitle: "New Commander Registration",
    usernameLabel: "Commander Name",
    passwordLabel: "Access Code (Password)",
    planetNameLabel: "Homeworld Name",
    btnLogin: "Login",
    btnRegister: "Register Account",
    btnLogout: "Logout",
    welcomeCommander: "Commander",
    loginSuccess: "Login successful!",
    registerSuccess: "Registration complete! Homeworld settled.",
    authError: "Authentication failed. Please check credentials.",
    loginPrompt: "Already have an account? Login",
    registerPrompt: "Need an account? Register now",
  },

  ko: {
    // 상단 리소스 바
    planetName: "모행성 (Homeworld)",
    metal: "메탈",
    crystal: "크리스탈",
    deuterium: "듀테륨",
    energy: "에너지",
    liveSync: "실시간 동기화 중",
    offline: "오프라인",

    // Auth & User System
    loginTitle: "사령관 로그인",
    registerTitle: "신규 사령관 계정 생성",
    usernameLabel: "사령관 이름",
    passwordLabel: "접속 암호",
    planetNameLabel: "모행성 이름",
    btnLogin: "로그인",
    btnRegister: "신규 행성 개척 (가입)",
    btnLogout: "로그아웃",
    welcomeCommander: "사령관",
    loginSuccess: "로그인되었습니다!",
    registerSuccess: "회원가입 및 모행성 개척이 완료되었습니다!",
    authError: "인증에 실패했습니다. 입력 정보를 확인해 주세요.",
    loginPrompt: "이미 계정이 있으신가요? 로그인",
    registerPrompt: "계정이 없으신가요? 신규 사령관 등록",

    // 내비게이션 메뉴
    navOverview: "행성 개요",
    navResources: "자원 생산",
    navFacilities: "시설 관리",
    navShipyard: "조선소",
    navFleet: "함대 발송",
    navGalaxy: "은하계 성도",

    // 개요 패널
    commandTitle: "행성 사령부",
    commandSubtitle: "FastAPI 비동기 초고속 코어로 실시간 상태 연산 중",
    statDiameter: "행성 지름",
    statFields: "개발 구역",
    statTemp: "행성 기온",
    activeMissionsTitle: "실시간 함대 기동 및 미션 현황",
    noActiveMissions: "현재 비행 중인 함대 미션이 없습니다.",
    colMissionType: "임무 유형",
    colDestination: "목표 좌표",
    colFleetShips: "함선 규모",
    colRemainingTime: "도착까지",
    colStatus: "상태",

    // 자원 및 시설 건물
    resourcesTitle: "자원 생산 시설",
    resourcesSubtitle: "행성 광산 및 발전소를 업그레이드하여 자원 채굴량을 극대화합니다",
    facilitiesTitle: "행성 인프라 시설",
    facilitiesSubtitle: "고급 연구 및 함선 건조를 위한 기반 시설을 건설합니다",
    lvl: "레벨",
    prodPerHour: "시간당 생산량",
    upgradeToLvl: "다음 레벨 업그레이드: Lv.",
    buildingCost: "소모 자원:",
    btnUpgrade: "업그레이드",
    btnBuildingUnavailable: "자원 부족",

    // 조선소
    shipyardTitle: "궤도 조선소",
    shipyardSubtitle: "전투 함대 및 화물 수송선을 대량 건조합니다",
    hangarCount: "보유 격납고:",
    shipSpecs: "스펙: 공 / 방 / 속도 / 적재량",
    btnBuild: "건조",

    // 함대 발송
    fleetTitle: "함대 사령부 발송",
    fleetSubtitle: "은하계 전역으로 탐사, 수송, 정거, 공격 임무를 지시합니다",
    availableShips: "보유 함선 편성",
    fleetMission: "임무(Mission) 선택",
    missionTransport: "자원 수송 (Transport)",
    missionDeploy: "함대 배치 (Deploy)",
    missionAttack: "공격 작전 (Attack)",
    missionHarvest: "잔해 수거 (Harvest)",
    btnSendFleet: "🚀 함대 발송",

    // 은하계 성도
    galaxyTitle: "은하계 성도 탐색",
    galaxySubtitle: "태양계 내 행성 좌표, 플레이어 식별 및 잔해 필드를 스캔합니다",
    btnScanSystem: "태양계 스캔",
    colPos: "위치",
    colPlanet: "행성명",
    colPlayer: "사령관",
    colAlliance: "동맹",
    colDebris: "우주 잔해",
    colAction: "작전",
    emptySlot: "비어 있는 우주 구역",
    btnSendMission: "목표 설정",

    // 함대 발송 시뮬레이터
    fleetSimTitle: "고속 함대 발송 시뮬레이터",
    targetCoordsLabel: "목표 좌표 (은하 : 태양계 : 위치)",
    fleetSelectionLabel: "함대 편성",
    shipSmallCargo: "소형 수송선 (202)",
    shipLightFighter: "경전투기 (204)",
    shipCruiser: "순양함 (206)",
    btnCalculateFlight: "⚡ 비행 및 연료 시뮬레이션",

    // 결과 및 메시지
    resDistance: "비행 거리:",
    resFlightTime: "비행 소요 시간:",
    resFuel: "듀테륨 연료 소모:",
    resCargo: "총 화물 적재량:",
    alertSelectShip: "최소 1척 이상의 함선을 선택해 주세요.",
    alertCalcError: "함대 비행 계산 중 오류가 발생했습니다.",
    upgradeSuccess: "건물 업그레이드가 완료되었습니다!",
    shipBuildSuccess: "함선 건조가 완료되었습니다!",
  }
};


