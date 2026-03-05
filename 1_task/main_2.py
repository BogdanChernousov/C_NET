import subprocess
import re

def pars(file, dom):
    with open(file, "w") as f:
        f.write("domain,rtt(ms),loss(%),ttl,packets\n")

        for domain in dom:
            output = subprocess.run(
                ["ping", "-c", "3", domain], capture_output=True, text=True
            ).stdout


            rtt_match = re.search(r"/([\d\.]+)/", output)
            rtt = float(rtt_match.group(1)) if rtt_match else 0
            loss_match = re.search(r"(\d+)% packet loss", output)
            loss = int(loss_match.group(1)) if loss_match else 100
            ttl_match = re.search(r"ttl=(\d+)", output)
            ttl = int(ttl_match.group(1)) if ttl_match else 0

            f.write(f"{domain},{rtt:.2f},{loss},{ttl},3\n")
    return 0

def main():
    domains = [
        "google.com",
        "googleapis.com",
        "gstatic.com",
        "cloudflare.com",
        "apple.com",
        "microsoft.com",
        "github.com",
        "googlevideo.com",
        "amazonaws.com",
        "stackoverflow.com",
    ]

    file = "output.csv"
    pars(file, domains)
    print("Done")
    return 0
