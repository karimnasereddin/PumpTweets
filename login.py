import httpx
import asyncio
from twikit import Client

original_client=httpx.Client()
def patched_client(*args,**kwargs):
    kwargs.pop('proxy',None)
    return original_client(*args,**kwargs)

httpx.Client=patched_client

username="TWITTERUSERNAME"
email="TWITTEREMAIL"
password="PASSWORD"
client= Client(user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36')

async def login_and_save_cookies():
    await client.login(auth_info_1=username, auth_info_2=email, password=password)
    
    client.save_cookies("cookies.json")


asyncio.run(login_and_save_cookies())