import subprocess
import json
dirs = subprocess.check_output(["ls", "data"]).decode("utf-8").split()
result = {}
for d in dirs:
    hostname = d.split("_")[0]

    with open("data/" + d + "/results.json", "r") as f:
        json_string = f.read()

    result[hostname] = json.loads(json_string) 

print(json.dumps(result))
