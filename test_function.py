
from dotenv import load_dotenv
import os

from src.service.polymarket_bot import PolymarketBot
load_dotenv()

def test_function():
    print("Hello, World!")
    bot = PolymarketBot(
        private_key=os.getenv("PRIVATE_KEY"),
        host=os.getenv("CLOB_API_HOST"),
        relayer_url=os.getenv("RELAYER_URL"),
        chain_id=int(os.getenv("CHAIN_ID", 137)),
        signature_type=int(os.getenv("SIGNATURE_TYPE", 2)),
        funder=os.getenv("FUNDER"),
        builder_api_key=os.getenv("BUILDER_API_KEY"),
        builder_secret=os.getenv("BUILDER_SECRET"),
        builder_passphrase=os.getenv("BUILDER_PASS_PHRASE")
    )

    bot.find_active_market()
    print(bot.poly_client.is_available())
    print(bot.relayer_client.is_available())
    # bot.place_market_order(token_id="101157936694808431608163613512894380362192529161825190715122565290895993245363", side="BUY", size=1)
    bot.place_market_order(token_id="101157936694808431608163613512894380362192529161825190715122565290895993245363", side="SELL",  size=1.5)
    # bot.redeem_positions("0x4e1e88c413e38748176db89e543ae00e1fa6ef2abec8909b62d704bcfba9cec7")



    


test_function()