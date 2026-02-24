def register(ron):
    def install_tool(tool_name):
        """Install ANY pentest tool automatically"""
        tools = {
            "sqlmap": "apt install sqlmap -y",
            "metasploit": "curl https://raw.githubusercontent.com/rapid7/metasploit-omnibus/master/config/templates/metasploit-framework-wrappers/msfupdate.erb > msfinstall && chmod 755 msfinstall && ./msfinstall",
            "dirsearch": "pip install dirsearch",
            "gobuster": "apt install gobuster -y",
            "nikto": "apt install nikto -y"
        }
        
        if tool_name in tools:
            ron.execute_task(tools[tool_name])
            ron.log(f"✅ INSTALLED: {tool_name}")
        else:
            ron.log(f"❓ Tool '{tool_name}' not in list. Add to installer.py")
    
    return {"install": install_tool}
