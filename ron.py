#!/usr/bin/env python3
"""
{COLOR_YELLOW}  ______    _____    __   _        
               |_____/   |     |   | \  |        
               |    \_ . |_____| . |  \_| . . . . 
{COLOR_YELLOW}  
{COLOR_YELLOW}  
{COLOR_YELLOW}  
"""

import subprocess, json, time, os, sys, re, schedule, threading, sqlite3
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass
import importlib.util

@dataclass
class Mission:
    id: int = 0
    date_time: str = ""
    command: str = ""
    status: str = "pending"
    output: str = ""
    auto_close: bool = False

class AnonymousMode:
    def __init__(self, ron):
        self.ron = ron
        self.tor_running = False
        self.proxychains_ready = False
    
    def setup_tor(self):
        self.ron.log("🌀 Setting up Tor...")
        self.ron.execute_task("apt update && apt install -y tor")
        
        torrc = "/etc/tor/torrc"
        with open(torrc, "a") as f:
            f.write("""
SocksPort 9050
SocksPort 9051
ControlPort 9051
HashedControlPassword 16:872860B76453A77D60CA2BB8C1A7042072093276A3D701AD684053EC4C
VirtualAddrNetwork 10.192.0.0/10
AutomapHostsOnResolve 1
TransPort 9040
DNSPort 5353
""")
        
        self.ron.execute_task("systemctl restart tor")
        self.tor_running = True
        self.ron.log("✅ Tor ready: 127.0.0.1:9050/9051")
    
    def setup_proxychains(self):
        self.ron.log("🔗 Setting up Proxychains...")
        self.ron.execute_task("apt install -y proxychains")
        
        conf = "/etc/proxychains.conf"
        config_lines = [
            "quiet_mode",
            "proxy_dns",
            "tcp_read_time_out 15000",
            "tcp_connect_time_out 8000",
            "localnet 127.0.0.0/255.0.0.0",
            "localnet 192.168.0.0/255.255.0.0",
            "",
            "[ProxyList]",
            "socks5 127.0.0.1 9050",
            "socks5 127.0.0.1 9051"
        ]
        
        with open(conf, "w") as f:
            f.write("
".join(config_lines))
        
        self.proxychains_ready = True
        self.ron.log("✅ Proxychains → Tor ready!")
    
    def anon_command(self, cmd):
        if not self.tor_running: self.setup_tor()
        if not self.proxychains_ready: self.setup_proxychains()
        
        self.ron.log(f"🕵️ ANON: {cmd}")
        full_cmd = f"timeout 300 proxychains -q {cmd}"
        return self.ron.execute_task(full_cmd)
    
    def renew_tor_ip(self):
        self.ron.execute_task("echo -e 'AUTHENTICATE "mypass"\
SIGNAL NEWNYM\
QUIT' | nc 127.0.0.1 9051")
        self.ron.log("🔄 NEW TOR IP ACTIVE")
    
    def check_ip(self):
        ip = self.ron.execute_task("curl -s https://icanhazip.com")
        anon_ip = self.ron.execute_task("proxychains -q curl -s https://icanhazip.com")
        self.ron.log(f"🌐 Real IP: {ip.strip()} | TOR IP: {anon_ip.strip()}")

class RON:
    def __init__(self):
        self.home = Path("/root/R.O.N")
        self.home.mkdir(exist_ok=True)
        self.db = self.init_db()
        self.history = []
        self.missions = []
        self.config = self.load_config()
        self.anon = AnonymousMode(self)  # Anonymous mode
        self.plugins = self.load_plugins()
        self.log("🖥️ R.O.N.... v2.1 ANONYMOUS - /root/R.O.N - PATHS FIXED!")

    def init_db(self):
        db_path = self.home / "ron.db"
        conn = sqlite3.connect(db_path, check_same_thread=False)
        conn.execute('''CREATE TABLE IF NOT EXISTS missions 
            (id INTEGER PRIMARY KEY, date_time TEXT, command TEXT, status TEXT, 
            output TEXT, auto_close INTEGER)''')
        conn.execute('''CREATE TABLE IF NOT EXISTS credentials 
            (id INTEGER PRIMARY KEY, tool TEXT, username TEXT, password TEXT, timestamp TEXT)''')
        return conn

    def load_config(self):
        config_path = self.home / "config.json"
        default = {"auto_close": False, "plugins": []}
        try:
            with open(config_path) as f:
                return json.load(f)
        except:
            with open(config_path, "w") as f:
                json.dump(default, f, indent=2)
            return default

    def load_plugins(self):
        plugins = {}
        plugin_dir = self.home / "plugins"
        plugin_dir.mkdir(exist_ok=True)
        for py_file in plugin_dir.glob("*.py"):
            if py_file.stem != "__init__":
                try:
                    spec = importlib.util.spec_from_file_location(py_file.stem, py_file)
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    if hasattr(module, "register"):
                        plugins.update(module.register(self))
                except Exception as e:
                    self.log(f"Plugin error: {e}")
        return plugins

    def log(self, msg):
        timestamp = datetime.now().strftime("%H:%M:%S")
        entry = f"[{timestamp}] {msg}"
        print(f"\u001B[1;36m{entry}\u001B[0m")
        self.history.append(entry)
        with open(self.home / "ron.log", "a") as f:
            f.write(entry + "
")

    def execute_task(self, cmd):
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=300)
            if result.returncode == 0:
                self.log(f"✅ SUCCESS: {cmd[:50]}...")
                return result.stdout
            else:
                self.log(f"❌ ERROR: {result.stderr[:100]}")
                if "permission" in result.stderr.lower():
                    return self.execute_task(f"sudo {cmd}")
                elif "not found" in result.stderr.lower():
                    pkg = re.search(r"'([a-z0-9-]+)'", result.stderr)
                    if pkg:
                        self.execute_task(f"sudo apt install -y {pkg.group(1)}")
        except:
            self.log(f"⏰ TIMEOUT: {cmd[:30]}")
        return ""

    def add_mission(self, date_time, command, auto_close=False):
        mission = Mission(0, date_time, command, "pending", "", auto_close)
        mission.id = self.db.execute(
            "INSERT INTO missions (date_time, command, status, auto_close) VALUES (?, ?, ?, ?)",
            (date_time, command, "pending", auto_close)
        ).lastrowid
        self.missions.append(mission)

        def run_mission():
            output = self.execute_task(command)
            self.db.execute("UPDATE missions SET status='completed', output=? WHERE id=?", (output, mission.id))
            self.db.commit()
            self.log(f"🎯 MISSION #{mission.id} COMPLETE")
            if auto_close: sys.exit(0)

        if " " in date_time:
            time_part = date_time.split()[-1]
            schedule.every().day.at(time_part).do(run_mission)
        self.log(f"📋 Mission #{mission.id}: {date_time} -> {command}")

    def dashboard(self):
        os.system('clear')
        print("
" + "═" * 70)
        print("🖥️  R.O.N.... v2.1 DASHBOARD - /root/R.O.N")
        print("═" * 70)
        print("📁 Files: ron.py | ron.db | ron.log | config.json")
        print("🕵️  Anonymous: Tor+Proxychains ready")
        print("📜 History:", len(self.history))
        print("📋 Missions:", len(self.missions))
        print("═" * 70)

    def run(self):
        def scheduler():
            while True:
                schedule.run_pending()
                time.sleep(1)
        threading.Thread(target=scheduler, daemon=True).start()

        self.log("🚀 R.O.N.... ACTIVE! Type 'help'")
        while True:
            try:
                cmd = input("
$ ").strip()
                if cmd in ['quit', 'exit']: break
                elif cmd == 'dashboard': self.dashboard()
                elif cmd == 'help':
                    print('''🛠️ COMMANDS:
task "nmap 192.168.1.1"           → Normal execution
anon "nmap target"               → TOR Anonymous  
newip                           → Change TOR IP
checkip                         → Verify anonymity
mission "15:30 anon hydra..."    → Schedule anonymous
mission "24.2.26 14:30 cmd"      → One-time mission
create toolname "code"          → Make tools''')
                elif cmd == 'anon': 
                    self.anon.setup_tor()
                    self.anon.setup_proxychains()
                elif cmd.startswith('anon '): 
                    self.anon.anon_command(cmd[5:])
                elif cmd == 'newip': 
                    self.anon.renew_tor_ip()
                elif cmd == 'checkip': 
                    self.anon.check_ip()
                elif cmd.startswith('task '): 
                    self.execute_task(cmd[5:])
                elif cmd.startswith('mission '):
                    parts = cmd[8:].split(maxsplit=2)
                    self.add_mission(parts[0], ' '.join(parts[1:]))
                else: self.log("❓ Unknown: 'help'")
            except KeyboardInterrupt: break
        self.log("👋 R.O.N.... shutdown")

if __name__ == "__main__":
    RON().run()
