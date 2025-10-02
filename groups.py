import asyncio
import json
import os

from config import password, username
from spond_auth_helpers import create_spond_session

if not os.path.exists("./exports"):
    os.makedirs("./exports")


async def main():
    s = create_spond_session(username=username, password=password)
    
    if s is None:
        return  # User aborted
    groups = await s.get_groups()
    for group in groups:
        name = group["name"]
        data = json.dumps(group, indent=4, sort_keys=True)
        keepcharacters = (" ", ".", "_")
        filename = os.path.join(
            "./exports",
            "".join(c for c in name if c.isalnum() or c in keepcharacters).rstrip()
            + ".json",
        )
        print(filename)
        with open(filename, "w") as out_file:
            out_file.write(data)

    await s.clientsession.close()


loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
asyncio.run(main())
