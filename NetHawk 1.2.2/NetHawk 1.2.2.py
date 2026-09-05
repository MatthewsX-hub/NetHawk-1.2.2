"""
NetHawk 1.2.2 - Network Connection Monitor for Windows
Tracks active TCP/UDP connections, detects new/closed connections,
logs changes, and displays protocol statistics.
"""

import subprocess
import time
import os
import sys
from datetime import datetime

LOG_FILE = "nethawk_log.txt"

def clear_screen():
    os.system("cls")

def log_event(event):
    """Append a timestamped message to the log file."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as log_file:
        log_file.write(f"[{timestamp}] {event}\n")
        #Creates or appends to nethawk.log.txt for later review
        

def get_connections():
    """Get current network connections using netstat."""
    #Uses netstat -ano to list connections with PIDs
    #Returns a set of formatted strings for easy comparison
    try:
        result = subprocess.run(
            ["netstat", "-ano"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="ignore",
            timeout=10
        )
        lines = result.stdout.splitlines()
        connections = set()

        for line in lines:
            line = line.strip()
            if line.startswith("TCP") or line.startswith("UDP"):
                parts = line.split()
                if len(parts) >= 4:
                    proto = parts[0]
                    local = parts[1]
                    remote = parts[2] if len(parts) > 2 else "-"
                    state = parts[3] if proto == "TCP" and len(parts) > 3 else "-"
                    pid = parts[-1]
                    conn_str = f"{proto} {local} -> {remote} | {state} | PID: {pid}"
                    connections.add(conn_str)

        return connections

    except subprocess.TimeoutExpired:
        return {"Error: netstat timeout"}
    except Exception as e:
        return {f"Error: {str(e)}"}

def get_protocol_stats(connections):
    """Return counts of TCP and UDP connections."""
    #Skips error messages and counts only valid protocol entries
    tcp_count = 0
    udp_count = 0

    for conn in connections:
        if conn.startswith("Error"):
            continue
        if conn.startswith("TCP"):
            tcp_count += 1
        elif conn.startswith("UDP"):
            udp_count += 1

    return tcp_count, udp_count

def show_connections(connections):
    """Display connections in a clean table."""
    #Parses each connection string back into columns for display
    #Falls back to raw output if parsing fails
    print(f"{'Proto':<7} {'Local Address':<25} {'Remote Address':<25} {'State':<16} {'PID'}")
    print("-" * 95)

    count = 0
    for conn in sorted(connections):
        if conn.startswith("Error"):
            print(conn)
            continue

        try:
            parts = conn.split(" | ")
            main_part = parts[0]
            state = parts[1] if len(parts) > 1 else "-"
            pid = parts[2].replace("PID: ", "") if len(parts) > 2 else "-"

            proto_local, remote = main_part.split(" -> ")
            proto, local = proto_local.split(" ", 1)

            print(f"{proto:<7} {local:<25} {remote:<25} {state:<16} {pid}")
            count += 1
        except Exception:
            print(conn)
            count += 1

    if count == 0:
        print("No active connections found.")

    return count

def main():
    print("NetHawk 1.2.2 starting...")
    log_event("NetHawk 1.2.2 started")

    #Establish proper baseline (no NEW detections on first run)
    previous_connections = get_connections()
    baseline_set = True

    try:
        while True:
            clear_screen()
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            print("=" * 95)
            print(f" NetHawk 1.2.2  |  Network Connection Monitor  |  {current_time}")
            print("=" * 95)
            print("Press Ctrl + C to exit cleanly\n")

            current_connections = get_connections()

            #Checks for errors first
            if any(conn.startswith("Error") for conn in current_connections):
                print("[!] Error retrieving connections:")
                for conn in current_connections:
                    print(f"    {conn}")
                log_event(f"Error retrieving connections: {current_connections}")
                time.sleep(2)
                continue

            #Compares current snapshot against previous snapshot
            new_connections = current_connections - previous_connections
            closed_connections = previous_connections - current_connections

            if baseline_set:
                #Skip change reporting on the very first cycle after baseline
                baseline_set = False
            else:
                if new_connections:
                    print("[+] NEW CONNECTIONS DETECTED:")
                    for conn in sorted(new_connections):
                        print(f"    {conn}")
                        log_event(f"NEW: {conn}")
                    print()

                if closed_connections:
                    print("[-] CONNECTIONS CLOSED:")
                    for conn in sorted(closed_connections):
                        print(f"    {conn}")
                        log_event(f"CLOSED: {conn}")
                    print()

                if not new_connections and not closed_connections:
                    print("No connection changes detected.\n")

            # Show current full list
            print("Current Connections:")
            print("-" * 95)
            count = show_connections(current_connections)

            # TCP / UDP Statistics
            tcp_count, udp_count = get_protocol_stats(current_connections)

            print("\n" + "-" * 95)
            print(f"Total Connections: {count}  |  TCP: {tcp_count}  |  UDP: {udp_count}")
            print("-" * 95)

            previous_connections = current_connections
            time.sleep(2)

    except KeyboardInterrupt:
        clear_screen()
        print("\n[NetHawk] Monitor stopped cleanly.")
        log_event("NetHawk stopped by user")
        print("Goodbye.\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n[NetHawk] Unexpected error: {e}")
        log_event(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

