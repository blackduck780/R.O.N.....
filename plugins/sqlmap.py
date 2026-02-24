def register(ron):
    def sql_inject(url):
        cmd = f"sqlmap -u '{url}' --batch --risk=3 --level=5 --dbs"
        ron.anon.anon_command(cmd)
        ron.log(f"🗄️ SQLMap: {url}")
    
    return {"sqlmap": sql_inject}
