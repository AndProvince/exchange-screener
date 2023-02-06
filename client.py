import asyncio
from dydx3.constants import MARKET_BTC_USD, MARKET_ETH_USD
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.dispatcher.filters.builtin import CommandStart
from aiogram.utils import executor
from config import TOKEN

from utils.scaner_candles import Scaner

bot = Bot(TOKEN)
dsp = Dispatcher(bot)

resolution = "5MINS"
THRESHOLD = 3.0

# Start command handler:
# create scanners for markets and check approaches
@dsp.message_handler(CommandStart())
async def bot_start(message: types.Message):
    await message.answer(f"Connection to exchange... ")
    btc_scaner = Scaner(MARKET_BTC_USD, resolution)
    await asyncio.sleep(1)
    eth_scaner = Scaner(MARKET_ETH_USD, resolution)
    await message.answer(f"Connect successfully!")

    asyncio.create_task(scan_vma(message, btc_scaner))
    # Sleep for defuse call frequency
    await asyncio.sleep(1)
    asyncio.create_task(scan_vma(message, eth_scaner))
    await asyncio.sleep(1)
    asyncio.create_task(scan_pd(message, btc_scaner))
    await asyncio.sleep(1)
    asyncio.create_task(scan_pd(message, eth_scaner))

# Algorithm to check VMA for 8 and 20 window sizes.
# Send messages to buy and sell on markets.
async def scan_vma(message: types.Message, scaner: Scaner):
    # Start vma values in None for take the first loop
    last_vma8 = None
    last_vma20 = None

    await message.answer(f"Start VMA scan for {scaner.market} market")
    # Scan loop
    while True:
        # Take new VMA values
        vma8 = scaner.vma(8)
        vma20 = scaner.vma(20)
        print(scaner.market, vma8, vma20)
        # Condition to buy token
        if vma8 > vma20 and last_vma8:
            if last_vma8 < last_vma20:
                await message.answer(f"{scaner.market} need to buy by VMA")
        # Condition to sell token
        if vma8 < vma20 and last_vma20:
            if last_vma8 > last_vma20:
                await message.answer(f"{scaner.market} need to sell by VMA")
        last_vma8 = vma8
        last_vma20 = vma20
        # Sleep for defuse call frequency
        await asyncio.sleep(150)

# Algorithm to check change volume of trade at marker
async def scan_pd(message: types.Message, scaner: Scaner):

    await message.answer(f"Start pump/dump scan for {scaner.market} market")

    while True:
        # Get volumes
        average = scaner.average_spot(5)
        actual = scaner.get_trade_volume()
        # Check exceeding the threshold
        if actual/average > THRESHOLD:
            print("PD: ", average, " - ", actual)
            await message.answer(f"{scaner.market} need to action by pump/dump")
        # Sleep for defuse call frequency
        await asyncio.sleep(150)

try:
    if __name__ == '__main__':
        executor.start_polling(dsp, skip_updates=True)
except Exception as inst:
        print(type(inst))
        print(inst.args)
        print(inst)
