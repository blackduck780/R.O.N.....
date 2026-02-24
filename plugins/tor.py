def register(ron):
    def anon_nmap(target):
        ron.anon.anon_command(f"nmap -sS -T4 {target}")
        ron.log(f"🗺️ Anonymous Nmap: {target}")
    
    def anon_nikto(target):
        ron.anon.anon_command(f"nikto -h {target}")
        ron.log(f"🔍 Anonymous Nikto: {target}")
    
    def anon_hydra(target, user, passlist):
        ron.anon.anon_command(f"hydra -l {user} -P {passlist} {target} http-post-form")
    
    return {
        "anon_nmap": anon_nmap,
        "anon_nikto": anon_nikto,
        "anon_hydra": anon_hydra,
        "new_identity": ron.anon.renew_tor_ip
  }
