#!/bin/bash
# ⚡️ R.O.N v9.0 - PERPLEXITY DB + MISSION STATUS ⚡️🤖
# https://github.com/YOURUSERNAME/RON

CONFIG_DIR="$HOME/ron"
LOGS="$CONFIG_DIR/logs"
HARVEST="$CONFIG_DIR/harvest"
DB="$CONFIG_DIR/perplexity.db"
MISSION_DB="$CONFIG_DIR/missions.db"
mkdir -p "$LOGS" "$HARVEST"

# 🌈 ULTRA COLORS
RED='\u001B[0;31m'; GREEN='\u001B[0;32m'; YELLOW='\u001B[1;33m'; BLUE='\u001B[0;34m'
PURPLE='\u001B[0;35m'; CYAN='\u001B[0;36m'; BOLD='\u001B[1m'; NC='\u001B[0m'
ORANGE='\u001B[38;5;208m'; MAGENTA='\u001B[0;95m'

# 🔥 PERPLEXITY DB BANNER 🔥
banner() {
    clear
    echo -e "${BOLD}${RED}╔═══════════════════════════════════════════════════════╗${NC}"
    echo -e "${BOLD}${RED}║${BOLD}${CYAN}  ⚡️ R.O.N v9.0 - PERPLEXITY DB + MISSIONS ⚡️ ${RED}║${NC}"
    echo -e "${BOLD}${RED}╠═══════════════════════════════════════════════════════╣${NC}"
    echo -e "${GREEN}║${BOLD}${YELLOW} ______    _____    __   _     [DB ACTIVE]     ${GREEN}║${NC}"
    echo -e "${GREEN}║ |_____/   |        |   | \\    |               ${GREEN}║${NC}"
    echo -e "${BLUE}║ ██╗  ██╗ █████╗ ██╗    ██╗██╗  ██╗███████╗ ⚡️║${NC}"
    echo -e "${CYAN}║╚═╝  ╚═╝╚═╝  ╚═╝ ╚══╝╚═╝╚═╝  ╚═╝╚══════╝ 🔥║${NC}"
    echo -e "${BOLD}${RED}╚═══════════════════════════════════════════════════════╝${NC}"
    echo -e "${ORANGE}Perplexity Database + Mission Tracking = ONLINE${NC}"
}

# 🗄️ PERPLEXITY DATABASE (w3m scraping)
perplexity_db() {
    banner
    echo -e "${BOLD}${GREEN}🧠 PERPLEXITY DB UPDATE${NC}"
    
    # Scrape Perplexity-like sources
    w3m -dump "https://www.perplexity.ai/search?q=linux+automation" > "$DB/search_linux.txt" 2>/dev/null &
    w3m -dump "https://news.ycombinator.com" > "$DB/hackernews.txt" 2>/dev/null &
    w3m -dump "https://duckduckgo.com/?q=pentesting+tools" > "$DB/pentest_tools.txt" 2>/dev/null &
    
    wait
    echo -e "${GREEN}✅ DB UPDATED: $(ls -la $DB/ | wc -l) files${NC}"
}

# 🎯 MISSION DATABASE + STATUS
mission_status() {
    local mission_id="$1"
    local status="$2"  # complete|incomplete
    
    sqlite3 "$MISSION_DB" "CREATE TABLE IF NOT EXISTS missions (
        id INTEGER PRIMARY KEY, 
        time TEXT, 
        command TEXT, 
        status TEXT, 
        log TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    );"
    
    if [[ "$status" == "complete" ]]; then
        sqlite3 "$MISSION_DB" "UPDATE missions SET status='✅ COMPLETE' WHERE id=$mission_id;"
        echo -e "${BOLD}${GREEN}🎯 MISSION $mission_id ✅ COMPLETE${NC}"
    else
        sqlite3 "$MISSION_DB" "UPDATE missions SET status='❌ INCOMPLETE' WHERE id=$mission_id;"
        echo -e "${BOLD}${RED}🎯 MISSION $mission_id ❌ INCOMPLETE${NC}"
    fi
}

# 📊 ULTIMATE DASHBOARD WITH MISSION STATUS
ultimate_dashboard() {
    banner
    echo -e "${BOLD}${CYAN}📊 RON DASHBOARD + MISSION STATUS${NC}"
    echo -e "${MAGENTA}═══════════════════════════════════${NC}"
    
    sys=$(detect_system)
    echo -e "${GREEN}🔥 SYSTEM:${NC} ${BOLD}$sys${NC}"
    echo -e "${GREEN}🕐 TIME:${NC} ${BOLD}$(date +'%H:%M')${NC}"
    
    echo -e "
${YELLOW}🎯 MISSION STATUS:${NC}"
    sqlite3 "$MISSION_DB" "SELECT id, time, status FROM missions ORDER BY timestamp DESC LIMIT 10;" 2>/dev/null | \
    while read -r id time status; do
        if [[ "$status" == *"COMPLETE"* ]]; then
            echo -e "  ${GREEN}ID:$id ${CYAN}$time${NC} ${BOLD}${GREEN}$status${NC}"
        else
            echo -e "  ${RED}ID:$id ${CYAN}$time${NC} ${BOLD}${RED}$status${NC}"
        fi
    done || echo "No missions tracked"
    
    echo -e "
${ORANGE}🧠 PERPLEXITY DB:${NC} $(find $DB/ -type f | wc -l) entries"
    echo -e "${PURPLE}📁 HARVEST:${NC} $(du -sh $HARVEST/ 2>/dev/null | cut -f1 || echo "0")"
}

# 🔥 ENHANCED MISSION EXECUTOR
execute_mission() {
    local mission_id="$1"
    local time="$2" 
    local cmd="$3"
    
    # Log mission start
    sqlite3 "$MISSION_DB" "INSERT INTO missions (id, time, command, status) VALUES ($mission_id, '$time', '$cmd', '⏳ RUNNING');"
    
    if timeout 120s bash -c "$cmd" 2>&1; then
        mission_status "$mission_id" "complete"
        return 0
    else
        mission_status "$mission_id" "incomplete"
        ca_hyper_fix "Mission $mission_id failed"
        return 1
    fi
}

detect_system() {
    if [ -n "$PREFIX" ] && echo "$PREFIX" | grep -q "com.termux"; then echo "TERMUX"
    elif command -v lsb_release >/dev/null 2>&1 && lsb_release -rs 2>/dev/null | grep -q "12"; then echo "DEBIAN12"
    elif grep -q "Debian" /etc/os-release 2>/dev/null; then echo "DEBIAN"
    elif grep -q "parrot" /etc/os-release 2>/dev/null; then echo "PARROT"
    else echo "LINUX"; fi
}

ca_hyper_fix() {
    local sys=$(detect_system)
    banner
    echo -e "${RED}🔧 HYPER-FIX ${sys}${NC}"
    case "$sys" in "TERMUX") pkg update -y && pkg install sqlite w3m nmap -y ;;
                      "DEBIAN12"|"DEBIAN") sudo apt update && sudo apt install -y sqlite3 w3m nmap ;; esac
}

# 🎮 MAIN CONTROL CENTER
case "$1" in
  "install")
    echo "* * * * * cd $CONFIG_DIR && ./ron.sh check" | crontab -
    sqlite3 "$MISSION_DB" "CREATE TABLE IF NOT EXISTS missions (id INTEGER PRIMARY KEY, time TEXT, command TEXT, status TEXT, log TEXT, timestamp DATETIME);"
    banner && echo -e "${BOLD}${GREEN}🚀 RON v9.0 + DB DEPLOYED${NC}"
    ;;
    
  "check")
    mission_id=$$  # Unique ID
    current_time=$(date +%H:%M)
    while IFS='|' read -r time cmd || [ -n "$time" ]; do
      [[ "$time" =~ ^[0-2][0-9]:[0-5][0-9]$ ]] || continue
      [[ "$time" == "$current_time" ]] || continue
      execute_mission "$mission_id" "$time" "$cmd"
    done < "$CONFIG_DIR/alarms.conf" 2>/dev/null
    ;;
    
  "db"|"perplexity")
    perplexity_db
    ;;
    
  "dashboard"|"status")
    ultimate_dashboard
    ;;
    
  "harvest")
    hyper_harvest "${2:-127.0.0.1}"
    ;;
    
  "missions"|"alarm")
    case "$2" in
      "add") echo "$3|$4" >> "$CONFIG_DIR/alarms.conf" && banner && echo -e "${GREEN}✅ MISSION DEPLOYED${NC}" ;;
      "list") banner; echo -e "${YELLOW}🎯 QUEUE:${NC}"; cat -n "$CONFIG_DIR/alarms.conf" ;;
      "nuke") > "$CONFIG_DIR/alarms.conf" && echo -e "${RED}💥 MISSIONS CLEARED${NC}" ;;
    esac
    ;;
    
  *)
    banner
    echo -e "${BOLD}${CYAN}🎮 R.O.N v9.0 - PERPLEXITY + MISSIONS${NC}"
    echo -e "  ${YELLOW}install${NC}           → Deploy + DB setup"
    echo -e "  ${YELLOW}dashboard${NC}       → Mission status"
    echo -e "  ${YELLOW}db${NC}             → Perplexity update"
    echo -e "  ${YELLOW}harvest 192.168.1.1${NC} → Recon"
    echo -e "  ${YELLOW}missions add "07:00" "harvest target"${NC}"
    ;;
esac
