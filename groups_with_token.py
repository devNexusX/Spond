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
    
    try:
        groups = await s.get_groups()
        
        print(f"\n🎉 Successfully retrieved {len(groups)} groups!")
        
        for group in groups:
            name = group["name"]
            data = json.dumps(group, indent=4, sort_keys=True)
            keepcharacters = (" ", ".", "_")
            filename = os.path.join(
                "./exports",
                "".join(c for c in name if c.isalnum() or c in keepcharacters).rstrip()
                + ".json",
            )
            print(f"📄 Saving: {filename}")
            with open(filename, "w") as out_file:
                out_file.write(data)
    
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await s.clientsession.close()


if __name__ == "__main__":
    asyncio.run(main())