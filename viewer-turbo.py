import asyncio
import aiohttp
import random
import time

class ViewBot:
    def __init__(self, target_views):
        self.target_views = target_views
        self.success = 0
        self.failed = 0
        self.lock = asyncio.Lock()

    async def send_view(self, session, url):
        """
        Send a single view with retries and tiny delay to avoid overload.
        """
        for _ in range(3):   # retry up to 3 times
            try:
                await asyncio.sleep(random.uniform(0.001, 0.01))  # tiny delay
                async with session.get(url, timeout=5) as r:
                    if r.status == 200:
                        async with self.lock:
                            self.success += 1
                        return True
            except:
                await asyncio.sleep(0.02)  # wait before retry

        # Final failure
        async with self.lock:
            self.failed += 1
        return False

    async def run_batch(self, url, concurrency):
        """
        Runs ONE batch of requests with limited concurrency.
        """
        connector = aiohttp.TCPConnector(limit=0)
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept": "*/*",
            "Connection": "close"
        }

        async with aiohttp.ClientSession(connector=connector, headers=headers) as session:
            sem = asyncio.Semaphore(concurrency)

            async def worker():
                async with sem:
                    await self.send_view(session, url)

            # Run a batch equal to concurrency
            tasks = [asyncio.create_task(worker()) for _ in range(concurrency)]
            await asyncio.gather(*tasks)

    async def run_until_done(self, url, concurrency):
        """
        Keeps running batches until success == desired views
        """
        print(f"Starting view generation...\n")
        
        while self.success < self.target_views:
            remaining = self.target_views - self.success
            batch_size = min(concurrency, remaining)

            await self.run_batch(url, batch_size)

            print(
                f"\rProgress: {self.success}/{self.target_views} "
                f"(failed: {self.failed})",
                end=""
            )

        print("\n\n✔ Completed!")
        print(f"Successful views: {self.success}")
        print(f"Failed attempts : {self.failed}")



async def main():
    print("🚀 VIEW BOT — SAFE LOAD TESTER\n")

    url = input("Enter video URL: ").strip()
    if not url:
        print("❌ Invalid URL.")
        return

    try:
        target = int(input("Enter desired number of views: "))
    except:
        print("❌ Invalid number.")
        return

    try:
        concurrency = int(input("Concurrency (recommended 50–150): "))
    except:
        concurrency = 100

    print("\nStarting in 2 seconds...\n")
    await asyncio.sleep(2)

    bot = ViewBot(target)
    await bot.run_until_done(url, concurrency)


if __name__ == "__main__":
    asyncio.run(main())
