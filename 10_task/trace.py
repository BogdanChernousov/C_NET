#!/usr/bin/env python3
import subprocess
import csv
import socket

DOMAINS = ["google.com", "yandex.ru", "github.com", "stackoverflow.com"]
CSV_FILE = "traceroute_results.csv"


def get_ip(domain: str):
    try:
        return socket.gethostbyname(domain)
    except socket.gaierror:
        return "N/A"


def get_traceroute(ip: str):
    if ip == "N/A":
        return "N/A"
    try:
        result = subprocess.check_output(
            ["traceroute", "-n", ip],
            timeout=30,
            text=True
        )
        return result.strip()
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError):
        return "N/A"


def process_domains(domains: list):
    results = []
    print("DNS и Traceroute для списка доменов\n")
    
    for domain in domains:
        print(f"Обработка: {domain}")
        
        ip = get_ip(domain)
        print(f"  IP: {ip}")
        
        trace = get_traceroute(ip)
        if trace != "N/A":
            print("  Traceroute: выполнено")
        else:
            print("err")
        
        results.append([domain, ip, trace])
        print()
    
    return results


def save_to_csv(filename: str, data: list):
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Domain", "IP", "Traceroute"])
        writer.writerows(data)
    print(f"Результаты сохранены в {filename}")


def main():
    results = process_domains(DOMAINS)
    save_to_csv(CSV_FILE, results)


if __name__ == "__main__":
    main()