# import time, requests, concurrent.futures

# URL = "http://ec2-13-239-254-120.ap-southeast-2.compute.amazonaws.com:5000/v1/generate"
# payload = {"prompt":"Long Brisbane noir.","genre":"mystery","style":"noir","length":1200}

# TARGET_CONCURRENCY = 150
# DURATION_SEC = 10*60

# def hit():
#     try:
#         return requests.post(URL, json=payload, timeout=120).status_code
#     except Exception:
#         return 0

# if __name__ == "__main__":
#     end = time.time() + DURATION_SEC
#     total = 0
#     with concurrent.futures.ThreadPoolExecutor(max_workers=TARGET_CONCURRENCY) as ex:
#         inflight = set()
#         def submit_one():
#             fut = ex.submit(hit)
#             inflight.add(fut)
#             fut.add_done_callback(lambda f: inflight.discard(f))
#         # fill the pipe
#         for _ in range(TARGET_CONCURRENCY):
#             submit_one()
#         # keep it full
#         while time.time() < end:
#             while len(inflight) < TARGET_CONCURRENCY:
#                 submit_one()
#             time.sleep(0.01)
#         # drain remaining
#         for f in concurrent.futures.as_completed(list(inflight)):
#             pass
#     print("Done")

import concurrent.futures, requests

URL = "https://storygen.cab432.com/v1/stories/generate"

payload = {
    "prompt": "Long Brisbane noir with a lot of details, twists, and inner monologue. " * 5,
    "genre": "mystery",
    "style": "noir",
    "length": 300,          
    "use_random_character": False,
    "user_id": 8 
}

TOTAL_REQUESTS =  150
CONCURRENCY = 40             

def hit(i):
    try:
        r = requests.post(URL, json=payload, timeout=40)
        return r.status_code
    except:
        return 0

with concurrent.futures.ThreadPoolExecutor(max_workers=CONCURRENCY) as ex:
    futures = [ex.submit(hit, i) for i in range(TOTAL_REQUESTS)]
    for f in futures:
        f.result()

print("done")

