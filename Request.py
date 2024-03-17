import asyncio
import aiohttp
import time

async def make_request(session, url, semaphore, proxy, success_counter):
    async with semaphore:
        try:
            async with session.get(url, proxy=f"http://{proxy}") as response:
                if response.status == 200:
                    print(f"Request successful with proxy: {proxy}")
                    success_counter.increment()
                elif response.status == 429:
                    print(f"Proxy {proxy} is rate limited. Switching to the next one.")
                else:
                    print(f"Request failed with status code {response.status} for proxy: {proxy}")
        except aiohttp.ClientError as e:
            print(f"Request failed: {e} for proxy: {proxy}")

class SuccessCounter:
    def __init__(self):
        self.count = 0

    def increment(self):
        self.count += 1

    def get_count(self):
        return self.count

async def main():
    url = "your-link"    # URL to which requests will be made. Set up view count @ https://visitor-badge.laobi.icu/
    num_requests = 100000     # Number of requests to be made before the script stops
    concurrency_limit = 100    # Limit on the number of concurrent requests. I highly advise that you use the concurrency limit of you're proxies it's normally stated in the section were you see you're proxy information but putting it higher doesn't affect anything.
    start_time = time.time()    # Start time to calculate execution duration
    semaphore = asyncio.Semaphore(concurrency_limit)    # Semaphore to limit the concurrency of requests
    success_counter = SuccessCounter()   # Counter to track the number of successful requests 


    with open("proxies.txt", "r") as file:
        proxies = file.readlines()

    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=None)) as session:
        tasks = []
        proxy_index = 0
        for _ in range(num_requests):
            proxy = proxies[proxy_index].strip()
            task = asyncio.create_task(make_request(session, url, semaphore, proxy, success_counter))
            tasks.append(task)
            print(f"Attempting proxy: {proxy}")
            proxy_index = (proxy_index + 1) % len(proxies)

        await asyncio.gather(*tasks)

    end_time = time.time()
    total_time = end_time - start_time
    print(f"Finished in {total_time} seconds")
    print(f"Number of successful requests: {success_counter.get_count()}")

if __name__ == "__main__":
    asyncio.run(main())
