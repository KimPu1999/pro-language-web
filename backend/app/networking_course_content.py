"""Authored Networking Fundamentals vertical slice for the idempotent catalog seed."""
import json
import re

from sqlalchemy import select

from .models import CodingExercise, CodeExample, CourseModule, Lesson, LessonQuiz, QuizQuestion

PLANNED_MODULES = [
    "Introduction to Computer Networking", "Types of Computer Networks", "Network Topologies", "Network Hardware & Devices",
    "OSI Reference Model", "TCP/IP Model", "Network Cables & Media", "Ethernet Fundamentals", "IPv4 Addressing",
    "Subnet Masks & CIDR", "Subnetting Fundamentals", "Advanced Subnetting & VLSM", "IPv6 Fundamentals",
    "ARP & Neighbor Discovery", "TCP & UDP", "Common Network Protocols", "DNS Fundamentals", "DHCP Fundamentals",
    "Switching Fundamentals", "VLANs & Trunking", "Spanning Tree Protocol", "Routing Fundamentals",
    "Static & Default Routing", "Dynamic Routing Fundamentals", "NAT & PAT", "Wireless Networking",
    "Wireless Security", "Firewalls & Access Control Lists", "VPN & Secure Remote Access", "Network Security Fundamentals",
    "Linux Networking Commands", "Windows Networking Tools", "Packet Analysis with Wireshark", "Network Troubleshooting",
    "Network Monitoring & Observability", "Cloud Networking Fundamentals", "Network Automation with Python",
    "Network Design & High Availability", "Professional Networking Projects", "Final Network Engineering Capstone",
]

MODULE_ONE = [
    ("What a Computer Network Is", "hosts, links, protocols, addressing, and communication goals",
     "printf 'host -> link -> switch/router -> service\\n' # Educational output only",
     "bash", "A computer network connects hosts so they can exchange data using agreed protocols. Reliable networking requires addressing, forwarding, naming, transport behavior, security boundaries, and observability. A packet path is a system of decisions, not just a cable.",
     "Computer network သည် host များကို link နှင့် protocol များဖြင့်ချိတ်ဆက်ပြီး data လဲလှယ်စေသည်။ Addressing၊ forwarding၊ naming နှင့် security boundary များလိုအပ်သည်။",
     "Draw a path from a laptop to a web service and label host, link, gateway, DNS, and transport roles.",
     ("Network တစ်ခု၏ အဓိကရည်ရွယ်ချက်က ဘာလဲ?", ["Enable hosts to exchange data using agreed protocols", "Only provide Wi-Fi passwords", "Replace every application"], "Enable hosts to exchange data using agreed protocols", "Networks provide communication paths and rules.")),
    ("LAN, WAN, and Network Scope", "local, wide-area, campus, internet, and administrative boundaries",
     "ip addr show # Read-only example for an authorized lab",
     "bash", "A LAN is a local administrative and physical scope, while WANs connect broader sites through provider or private links. Scope affects latency, ownership, routing, failure domains, and security policy. Never assume a private address is reachable from every network.",
     "LAN သည် local scope ဖြစ်ပြီး WAN သည် site များကို ချိတ်ဆက်သည်။ Scope က latency၊ ownership၊ routing နှင့် failure domain ကိုသက်ရောက်သည်။",
     "Classify a home network, school campus, and cloud region connection as LAN, WAN, or a combination.",
     ("LAN နှင့် WAN ကွာခြားချက်ကို ဘာကဖော်ပြသနည်း?", ["Their scope, ownership, and connectivity boundaries", "Only cable color", "Only the application language"], "Their scope, ownership, and connectivity boundaries", "Scope changes design and troubleshooting assumptions.")),
    ("Protocols and Encapsulation", "layers, headers, payloads, and packet movement",
     "printf 'application data -> TCP segment -> IP packet -> Ethernet frame\\n'",
     "bash", "Protocols divide responsibilities into layers. Application data is wrapped by transport, network, and link headers as it travels, then unwrapped at the destination. Each layer has addresses and failure modes that should be observed separately.",
     "Protocol များသည် responsibility ကို layer များခွဲပေးသည်။ Data သည် transport၊ network နှင့် link header များဖြင့် encapsulate လုပ်ပြီး destination တွင် ပြန်ဖြည်သည်။",
     "Label application, transport, network, and link headers in a simulated request.",
     ("Encapsulation ဆိုသည်မှာ ဘာလဲ?", ["Wrapping data with layer-specific headers", "Deleting all headers", "Changing a password"], "Wrapping data with layer-specific headers", "Layered headers let each protocol perform its role.")),
    ("Network Devices and Roles", "switches, routers, firewalls, access points, and servers",
     "ip route show # Inspect the local routing table in an authorized lab",
     "bash", "Switches forward frames within a local network using MAC addresses. Routers forward packets between IP networks. Firewalls enforce policy, access points bridge wireless clients, and servers provide services. A device can combine roles, but the security and failure boundaries still matter.",
     "Switch သည် MAC address ဖြင့် local frame forward လုပ်ပြီး router သည် IP network ကြား packet forward လုပ်သည်။ Firewall သည် policy ကို enforce လုပ်သည်။",
     "Create a device-role table for a small office network and identify each trust boundary.",
     ("Router ၏ အဓိကတာဝန်က ဘာလဲ?", ["Forward packets between IP networks", "Store every web page", "Replace DNS records"], "Forward packets between IP networks", "Routing connects distinct network prefixes.")),
    ("OSI Reference Model", "seven layers, responsibilities, and troubleshooting boundaries",
     "printf '7 Application | 6 Presentation | 5 Session | 4 Transport | 3 Network | 2 Data Link | 1 Physical\\n'",
     "bash", "The OSI model is a reasoning and troubleshooting framework. Physical problems, framing, addressing, routing, transport reliability, session behavior, and application protocols can be investigated separately. Real implementations do not always map one-to-one to seven layers.",
     "OSI model သည် troubleshooting အတွက် reasoning framework ဖြစ်သည်။ Physical၊ data link၊ network၊ transport နှင့် application ပြဿနာများကို layer အလိုက်စစ်နိုင်သည်။",
     "Map DNS, TCP, IP, Ethernet, and a copper cable to their primary OSI layers.",
     ("OSI model ကို ဘာအတွက်အသုံးများသနည်း?", ["Separate responsibilities and narrow troubleshooting", "Guarantee every vendor uses seven protocols", "Encrypt all traffic"], "Separate responsibilities and narrow troubleshooting", "Layer reasoning reduces a large problem into testable boundaries.")),
    ("TCP/IP Model", "link, internet, transport, application layers and practical mapping",
     "printf 'application -> transport -> internet -> network access\\n'",
     "bash", "The TCP/IP model groups practical protocols into network access, internet, transport, and application layers. IPv4/IPv6 provide addressing, TCP/UDP provide transport behavior, and DNS/HTTP/SSH live at the application layer.",
     "TCP/IP model တွင် network access၊ internet၊ transport နှင့် application layer များပါဝင်သည်။ IPv4/IPv6၊ TCP/UDP နှင့် DNS/HTTP/SSH တို့၏ role များကို ခွဲခြားပါ။",
     "Compare the OSI and TCP/IP models for a DNS lookup over UDP.",
     ("TCP/IP model တွင် IP သည် ဘယ် layer တွင်ရှိသနည်း?", ["Internet layer", "Application layer only", "Physical layer only"], "Internet layer", "IP provides internetwork addressing and forwarding.")),
    ("Addresses, Ports, and Names", "MAC addresses, IP addresses, ports, DNS names, and scope",
     "printf 'MAC: local link | IP: routed address | port: service endpoint | name: human label\\n'",
     "bash", "A MAC address identifies a link-layer interface in a local segment, an IP address identifies a routed interface, a port identifies a transport service endpoint, and a DNS name maps human-friendly labels to records. These identifiers are related but not interchangeable.",
     "MAC သည် local link interface၊ IP သည် routed interface၊ port သည် service endpoint နှင့် DNS name သည် human label ဖြစ်သည်။",
     "Annotate a browser request with its DNS name, destination IP, TCP port, and local interface.",
     ("Port number သည် ဘာကိုဖော်ပြသနည်း?", ["A transport service endpoint", "A physical cable length", "A DNS zone owner"], "A transport service endpoint", "Ports let multiple services share an IP address.")),
    ("First Network Troubleshooting Workflow", "scope, evidence, layered tests, and safe remediation",
     "ping 192.0.2.1 # Documentation address; simulator only\\nnslookup academy.invalid",
     "bash", "Troubleshooting starts by defining scope and symptoms, collecting evidence, testing from lower to higher layers, comparing a known-good path, and recording changes. Use authorized lab networks and documentation addresses; do not scan or probe public or private infrastructure without permission.",
     "Troubleshooting တွင် scope သတ်မှတ်ပြီး evidence စုကာ lower layer မှ higher layer သို့ စစ်ရသည်။ ခွင့်ပြုချက်မရှိသော network ကို မစမ်းသပ်ပါနှင့်။",
     "Complete the playground guided challenge: inspect interface, route, DNS, and simulated reachability, then record the likely failing layer.",
     ("Network troubleshooting ၏ ပထမအဆင့်က ဘာလဲ?", ["Define scope, symptoms, and authorized evidence collection", "Scan every address", "Change firewall rules randomly"], "Define scope, symptoms, and authorized evidence collection", "Scope and evidence make troubleshooting safe and repeatable.")),
]

MODULE_LESSON_TOPICS = {
    "Types of Computer Networks": ["LAN, WAN, and MAN", "PAN, CAN, and data-center networks", "Internet and private network boundaries", "Network ownership and failure domains", "Network scope design lab"],
    "Network Topologies": ["Bus, star, ring, and mesh", "Physical and logical topology", "Hierarchical campus design", "Redundancy and single points of failure", "Topology review lab"],
    "Network Hardware & Devices": ["Switches and MAC learning", "Routers and forwarding tables", "Firewalls and policy enforcement", "Wireless access points", "Device role selection lab"],
    "OSI Reference Model": ["Physical and data-link layers", "Network and transport layers", "Session, presentation, and application layers", "Layer-to-protocol mapping", "OSI troubleshooting lab"],
    "TCP/IP Model": ["Network access layer", "Internet layer and IP", "Transport layer behavior", "Application layer protocols", "TCP/IP mapping lab"],
    "Network Cables & Media": ["Copper Ethernet media", "Fiber optic links", "Wireless radio media", "Connectors, transceivers, and standards", "Media troubleshooting lab"],
    "Ethernet Fundamentals": ["Ethernet frames", "MAC addresses and unicast", "Broadcast and multicast", "Duplex, speed, and negotiation", "Ethernet verification lab"],
    "IPv4 Addressing": ["IPv4 address structure", "Public and private address ranges", "Network, host, and broadcast addresses", "Loopback, link-local, and documentation ranges", "IPv4 planning lab"],
    "Subnet Masks & CIDR": ["Dotted-decimal subnet masks", "CIDR prefixes", "Network and host bits", "Address capacity calculations", "CIDR planning lab"],
    "Subnetting Fundamentals": ["Binary subnet calculations", "Equal-size subnetting", "Subnet boundaries", "Address allocation", "Subnetting practice lab"],
    "Advanced Subnetting & VLSM": ["Variable-length subnet masks", "Route summarization", "Address planning constraints", "VLSM verification", "VLSM design lab"],
    "IPv6 Fundamentals": ["IPv6 address notation", "Global, link-local, and unique-local addresses", "IPv6 prefixes", "Neighbor discovery", "IPv6 planning lab"],
    "ARP & Neighbor Discovery": ["ARP requests and replies", "ARP cache behavior", "IPv6 neighbor discovery", "Spoofing risks and protections", "Neighbor troubleshooting lab"],
    "TCP & UDP": ["TCP connection establishment", "TCP reliability and flow control", "UDP datagrams", "Ports and ephemeral ports", "Transport troubleshooting lab"],
    "Common Network Protocols": ["HTTP and HTTPS", "SSH and secure administration", "SMTP and email delivery", "FTP, SFTP, and file transfer", "Protocol identification lab"],
    "DNS Fundamentals": ["DNS names and records", "Recursive and authoritative resolution", "Caching and TTL", "DNS security and split-horizon", "DNS troubleshooting lab"],
    "DHCP Fundamentals": ["DHCP discovery and leases", "DHCP options", "Reservations and scopes", "DHCP relay", "DHCP troubleshooting lab"],
    "Switching Fundamentals": ["MAC address tables", "Forwarding and flooding", "Collision and broadcast domains", "Port security", "Switch verification lab"],
    "VLANs & Trunking": ["VLAN segmentation", "Access ports", "802.1Q trunks", "Native VLAN risks", "VLAN configuration lab"],
    "Spanning Tree Protocol": ["Layer-two loops", "STP roles and states", "Root bridge selection", "Rapid STP", "STP troubleshooting lab"],
    "Routing Fundamentals": ["Routing table entries", "Longest-prefix match", "Next hops and interfaces", "Administrative distance", "Routing verification lab"],
    "Static & Default Routing": ["Static route syntax", "Default routes", "Floating static routes", "Route failure behavior", "Static routing lab"],
    "Dynamic Routing Fundamentals": ["Routing protocol concepts", "Distance-vector behavior", "Link-state behavior", "Convergence and metrics", "Dynamic routing lab"],
    "NAT & PAT": ["Private address translation", "Port address translation", "Static NAT", "NAT limitations and logging", "NAT verification lab"],
    "Wireless Networking": ["Wireless bands and channels", "802.11 association", "Roaming and coverage", "Wireless performance", "Wireless planning lab"],
    "Wireless Security": ["WPA2 and WPA3", "Enterprise authentication", "Guest network isolation", "Wireless monitoring", "Wireless security review lab"],
    "Firewalls & Access Control Lists": ["Stateful firewall behavior", "ACL order and matching", "Ingress and egress policy", "Logging denied traffic", "Firewall policy lab"],
    "VPN & Secure Remote Access": ["VPN tunnel concepts", "Site-to-site VPN", "Remote-access VPN", "Authentication and key exchange", "VPN troubleshooting lab"],
    "Network Security Fundamentals": ["Network threat models", "Segmentation and zero trust", "Secure management", "Network security monitoring", "Security architecture lab"],
    "Linux Networking Commands": ["ip and ss commands", "ping, tracepath, and mtr", "dig and resolvectl", "tcpdump for authorized captures", "Linux troubleshooting lab"],
    "Windows Networking Tools": ["ipconfig and route", "ping and tracert", "nslookup and Resolve-DnsName", "Test-NetConnection", "Windows troubleshooting lab"],
    "Packet Analysis with Wireshark": ["Capture scope and filters", "Ethernet and ARP packets", "TCP handshake analysis", "DNS and HTTP inspection", "Packet analysis lab"],
    "Network Troubleshooting": ["Troubleshooting methodology", "Physical and link failures", "Addressing and routing failures", "DNS and transport failures", "Incident troubleshooting lab"],
    "Network Monitoring & Observability": ["Metrics, logs, and traces", "Availability and latency", "SNMP and telemetry", "Alert design", "Monitoring review lab"],
    "Cloud Networking Fundamentals": ["Virtual networks and subnets", "Cloud route tables", "Security groups and network ACLs", "Private endpoints and gateways", "Cloud network lab"],
    "Network Automation with Python": ["Python ipaddress module", "Parsing command output safely", "Network API clients", "Automation idempotency", "Automation lab"],
    "Network Design & High Availability": ["Requirements and capacity", "Redundant links and devices", "Load balancing", "Disaster recovery", "High-availability design lab"],
    "Professional Networking Projects": ["Network assessment project", "Campus network project", "Secure branch-office project", "Cloud hybrid network project", "Professional project review"],
    "Final Network Engineering Capstone": ["Capstone scope and requirements", "Addressing and routing design", "Security and observability design", "Implementation and validation", "Capstone assessment"],
}

def _generated_code(title: str) -> tuple[str, str]:
    lower = title.lower()
    if "python" in lower or "automation" in lower:
        return ("from ipaddress import ip_network\n\nnetwork = ip_network('192.0.2.0/24')\nprint(network.num_addresses)", "python")
    if "ipv6" in lower or "neighbor" in lower:
        return ("printf '2001:db8:1::/64 -> link-local neighbor discovery\\n'", "bash")
    if "dns" in lower:
        return ("nslookup academy.invalid # Authorized documentation example", "bash")
    if "windows" in lower:
        return ("Test-NetConnection 192.0.2.1 -Port 443", "powershell")
    if "wireshark" in lower or "packet" in lower or "tcpdump" in lower:
        return ("tcpdump -ni eth0 'tcp port 443' # Authorized capture only", "bash")
    if "subnet" in lower or "cidr" in lower or "vlsm" in lower:
        return ("python -c \"from ipaddress import ip_network; print(list(ip_network('192.0.2.0/28').hosts()))\"", "bash")
    if "route" in lower or "routing" in lower:
        return ("ip route show # Read-only inspection in an authorized lab", "bash")
    if "vlan" in lower or "switch" in lower or "ethernet" in lower:
        return ("printf 'access-port -> VLAN 10 -> trunk -> routed gateway\\n'", "bash")
    if "firewall" in lower or "acl" in lower or "security" in lower:
        return ("printf 'allow documented service -> log decision -> deny everything else\\n'", "bash")
    if "wireless" in lower or "wifi" in lower:
        return ("printf 'client -> WPA3 access point -> isolated guest VLAN\\n'", "bash")
    return ("printf 'scope -> evidence -> layered test -> documented result\\n'", "bash")

def _generated_content(module_title: str, title: str, previous: str, next_title: str) -> str:
    code, language = _generated_code(title)
    return f"""Introduction
{title} is part of the {module_title} module and develops a professional network-engineering skill.

Learning objectives
- Explain the purpose, scope, and failure modes of {title}.
- Map the topic to devices, layers, addresses, protocols, and observable evidence.
- Perform a safe read-only analysis in an isolated or explicitly authorized lab.
- Document a verified result, a failure path, and a remediation decision.

Prerequisites
{previous}

Network architecture explanation
client -> access/link -> switch or access point -> gateway/router -> routed network -> service

Detailed theory
{title} is useful only when its boundary is clear. Identify which hosts, interfaces, prefixes, ports, names, devices, and administrative owners are involved. Separate physical connectivity, link-layer forwarding, IP routing, transport behavior, application protocol behavior, and security policy. A symptom at one layer does not prove that every higher layer is broken.

For a professional workflow, define the authorized scope first, establish the expected packet path, collect the smallest amount of read-only evidence, compare it with a known-good path, and record the change and verification result. Address plans, route tables, DNS records, firewall rules, logs, captures, and monitoring data should agree with the documented design.

Syntax and progressive examples
Example 1 — inspect or model the smallest boundary:
{code}

Example 2 — identify the relevant address or prefix:
from ipaddress import ip_network
network = ip_network("192.0.2.0/28")
print(network.network_address, network.broadcast_address)

Example 3 — describe the packet path:
client -> gateway -> routed prefix -> service

Example 4 — record a safe verification:
expected = "authorized scope, expected route, expected response"
print(expected)

Example 5 — preserve the security boundary:
print("read-only evidence; no unauthorized scan or configuration change")

Use documentation ranges such as 192.0.2.0/24 and 2001:db8::/32 in examples. Run executable commands only in a disposable lab or network where you have explicit authorization. Real output varies by operating system, device vendor, route, policy, and current state.

Expected output
The expected result is predefined simulator evidence or a documented local observation: an interface, prefix, route, protocol exchange, policy decision, or captured field. Record the command, scope, timestamp, result, and interpretation. Do not treat an absent ping reply as proof that the service is unavailable.

Step-by-step explanation
1. Define the authorized network, user impact, and symptom.
2. Draw the expected path and identify the relevant layer.
3. Run the smallest read-only test from a known location.
4. Compare the result with the address plan, route table, policy, DNS, or capture.
5. Change only a documented lab configuration and verify the change.

Practical lab
Build a disposable scenario for {title}. Create a diagram, choose documentation addresses, define the expected packet path, collect evidence from two layers, explain one failure case, and write a cleanup note. Add a test or repeatable verification checklist.

Common errors
- Confusing MAC addresses, IP addresses, ports, prefixes, and DNS names.
- Testing from the wrong interface, namespace, VLAN, route, or resolver.
- Changing a firewall, switch, or router before collecting evidence.
- Scanning public or private systems without authorization.

Troubleshooting
Check link state, interface configuration, VLAN or wireless association, default route, longest-prefix match, DNS response, transport port, firewall decision, service logs, and monitoring history. Preserve evidence and redact credentials, private addresses, tokens, and customer data before sharing.

Security best practices
Use least privilege, segmentation, secure management protocols, MFA, key rotation, documented change control, rate limits, logging, safe capture filters, and explicit authorization. Keep management interfaces private, avoid hardcoded secrets, and verify that automation is idempotent before it changes network state.

Exercises
- Easy: label the devices, layer, identifiers, and expected result in Example 1.
- Medium: introduce one controlled fault in a disposable lab and identify it with two read-only tests.
- Advanced: write a verification plan that distinguishes a physical, addressing, routing, transport, DNS, and policy failure.

Homework
Prepare a network-engineering note for {title} containing the diagram, assumptions, address plan, commands, expected output, observed output, failure analysis, security considerations, test evidence, and cleanup steps.

Quiz
1. What should be defined before collecting network evidence? The authorized scope, symptom, and expected path.
2. True or false: a failed ping always proves that an application is down. False.
3. Which evidence helps distinguish routing from DNS failure? Route/path evidence and a resolver response checked separately.
4. What should a network automation script do before changing state? Validate scope, inputs, authorization, and idempotent behavior.

Summary
You can now reason about {title} with layered models, explicit scope, correct identifiers, repeatable evidence, and safe network-engineering practice.

Next lesson
{next_title}

Safety note
The Academy simulator uses predefined local state. It does not execute arbitrary commands, scan public targets, access host networking, or connect to private infrastructure.
"""

def _generated_content_mm(module_title: str, title: str, code: str, previous: str, next_title: str) -> str:
    return f"""သင်ခန်းစာခေါင်းစဉ် — {title}

နိဒါန်း
{title} သည် {module_title} module အတွင်းရှိ network engineering အကြောင်းအရာတစ်ခုဖြစ်ပြီး network ကို layer၊ address၊ protocol နှင့် evidence များဖြင့် စနစ်တကျ နားလည်စေရန် လေ့လာခြင်းဖြစ်သည်။

သင်ယူရမည့်ရည်ရွယ်ချက်များ
- {title} ၏ ရည်ရွယ်ချက်၊ scope နှင့် failure mode များကို ရှင်းပြနိုင်ရန်။
- Device၊ layer၊ address၊ protocol နှင့် စောင့်ကြည့်နိုင်သော evidence တို့၏ ဆက်နွယ်မှုကို ခွဲခြားနိုင်ရန်။
- Isolated သို့မဟုတ် ခွင့်ပြုချက်ရှိသော lab ထဲတွင် read-only analysis ပြုလုပ်နိုင်ရန်။
- Result၊ failure path နှင့် ပြန်လည်ပြင်ဆင်မည့် ဆုံးဖြတ်ချက်ကို document လုပ်နိုင်ရန်။

လိုအပ်သောအခြေခံများ
{previous}
Computer၊ IP address၊ HTTP နှင့် command line အခြေခံကို သိထားပါ။ Command တစ်ခုကို လက်တွေ့ run မလုပ်မီ target network သည် ကိုယ်ပိုင် သို့မဟုတ် ခွင့်ပြုချက်ရထားသော lab ဖြစ်ကြောင်း စစ်ပါ။

Network architecture အကြောင်း
client -> access/link -> switch သို့မဟုတ် access point -> gateway/router -> routed network -> service

အသေးစိတ်သီအိုရီ
{title} ကို မှန်ကန်စွာအသုံးချရန် boundary ကို အရင်သတ်မှတ်ရသည်။ ပါဝင်သော host၊ interface၊ prefix၊ port၊ name၊ device နှင့် network owner ကို ခွဲခြားပါ။ Physical connection၊ link-layer forwarding၊ IP routing၊ transport behavior၊ application protocol နှင့် security policy တို့ကို သီးခြားစဉ်းစားပါ။ Layer တစ်ခုတွင် symptom ဖြစ်ခြင်းသည် အခြား layer အားလုံးပျက်နေသည်ဟု မဆိုလိုပါ။

Professional workflow တွင် authorized scope ကို အရင်သတ်မှတ်ပါ။ မျှော်မှန်းထားသော packet path ကို ရေးပါ။ Read-only evidence အနည်းဆုံးကို စုပါ။ Known-good path နှင့် နှိုင်းယှဉ်ပါ။ ပြောင်းလဲမှုနှင့် verification result ကို မှတ်တမ်းတင်ပါ။ Address plan၊ route table၊ DNS record၊ firewall rule၊ log၊ capture နှင့် monitoring data တို့သည် documented design နှင့် ကိုက်ညီရမည်။

Syntax နှင့် အဆင့်လိုက်ဥပမာများ
ဥပမာ ၁ — အနည်းဆုံး boundary ကို စစ်ခြင်း
{code}

ဥပမာ ၂ — Address သို့မဟုတ် prefix ကို ခွဲခြားခြင်း
from ipaddress import ip_network
network = ip_network("192.0.2.0/28")
print(network.network_address, network.broadcast_address)

ဥပမာ ၃ — Packet path ကို ရေးခြင်း
client -> gateway -> routed prefix -> service

ဥပမာ ၄ — Safe verification ကို မှတ်တမ်းတင်ခြင်း
expected = "authorized scope, expected route, expected response"
print(expected)

ဥပမာ ၅ — Security boundary ကို ထိန်းသိမ်းခြင်း
print("read-only evidence; no unauthorized scan or configuration change")

ဥပမာများတွင် 192.0.2.0/24 နှင့် 2001:db8::/32 ကဲ့သို့ documentation range များကို သုံးပါ။ Executable command များကို ကိုယ်ပိုင် disposable lab သို့မဟုတ် ခွင့်ပြုချက်ရှိသော network ထဲတွင်သာ run ပါ။ OS၊ device vendor၊ route၊ policy နှင့် လက်ရှိ state ပေါ်မူတည်၍ real output ကွာနိုင်သည်။

မျှော်မှန်းရလဒ်
Simulator evidence သို့မဟုတ် local observation တစ်ခု ရရမည်။ Interface၊ prefix၊ route၊ protocol exchange၊ policy decision သို့မဟုတ် captured field ကို command၊ scope၊ timestamp၊ result နှင့် interpretation နှင့်အတူ မှတ်တမ်းတင်ပါ။ Ping reply မရခြင်းတစ်ခုတည်းဖြင့် service မရကြောင်း မဆုံးဖြတ်ပါနှင့်။

အဆင့်လိုက်ရှင်းလင်းချက်
၁။ Authorized network၊ user impact နှင့် symptom ကို သတ်မှတ်ပါ။
၂။ မျှော်မှန်း packet path ကို ရေးပြီး သက်ဆိုင်ရာ layer ကို ရွေးပါ။
၃။ Known location မှ read-only test အနည်းဆုံးကို run ပါ။
၄။ Result ကို address plan၊ route table၊ policy၊ DNS သို့မဟုတ် capture နှင့် နှိုင်းယှဉ်ပါ။
၅။ Documented lab configuration ကိုသာ ပြောင်းပြီး ပြောင်းလဲမှုကို ပြန်စစ်ပါ။

လက်တွေ့လေ့ကျင့်ခန်း
{title} အတွက် disposable scenario တစ်ခု တည်ဆောက်ပါ။ Diagram ရေးပါ။ Documentation address များ ရွေးပါ။ မျှော်မှန်း packet path သတ်မှတ်ပါ။ Layer နှစ်ခုမှ evidence စုပါ။ Failure case တစ်ခုကို ရှင်းပြပြီး cleanup note နှင့် repeatable verification checklist ထည့်ပါ။

အဖြစ်များသောအမှားများ
- MAC address၊ IP address၊ port၊ prefix နှင့် DNS name ကို ရောထွေးခြင်း။
- Interface၊ namespace၊ VLAN၊ route သို့မဟုတ် resolver မှားနေရာမှ test လုပ်ခြင်း။
- Evidence မစုမီ firewall၊ switch သို့မဟုတ် router configuration ကို ပြောင်းခြင်း။
- ခွင့်ပြုချက်မရှိဘဲ public သို့မဟုတ် private system များကို scan လုပ်ခြင်း။

Troubleshooting လမ်းညွှန်
Link state၊ interface configuration၊ VLAN သို့မဟုတ် wireless association၊ default route၊ longest-prefix match၊ DNS response၊ transport port၊ firewall decision၊ service log နှင့် monitoring history ကို အစဉ်လိုက်စစ်ပါ။ Evidence များကို ထိန်းသိမ်းပြီး credential၊ private address၊ token နှင့် customer data များကို ဖုံးကွယ်ပြီးမှ share လုပ်ပါ။

လုံခြုံရေးအကောင်းဆုံးနည်းလမ်းများ
Least privilege၊ segmentation၊ secure management protocol၊ MFA၊ key rotation၊ documented change control၊ rate limit၊ logging၊ safe capture filter နှင့် explicit authorization ကို သုံးပါ။ Management interface များကို private ထားပါ။ Secret ကို code ထဲမထည့်ပါနှင့်။ Automation သည် state ကို ပြောင်းမီ idempotent ဖြစ်ကြောင်း စစ်ပါ။

လေ့ကျင့်ခန်းများ
- လွယ်ကူသောအဆင့်: ဥပမာ ၁ ထဲမှ device၊ layer၊ identifier နှင့် expected result ကို သတ်မှတ်ပါ။
- အလယ်အလတ်အဆင့်: Disposable lab ထဲတွင် fault တစ်ခုကို ထည့်ပြီး read-only test နှစ်ခုဖြင့် ရှာပါ။
- အဆင့်မြင့်: Physical၊ addressing၊ routing၊ transport၊ DNS နှင့် policy failure များကို ခွဲခြားနိုင်သော verification plan ရေးပါ။

အိမ်စာ
{title} အတွက် diagram၊ assumptions၊ address plan၊ commands၊ expected output၊ observed output၊ failure analysis၊ security consideration၊ test evidence နှင့် cleanup step ပါသော network-engineering note တစ်ခု ပြင်ဆင်ပါ။

Quiz
၁။ Network evidence မစုမီ ဘာကို သတ်မှတ်ရမည်နည်း။ Authorized scope၊ symptom နှင့် expected path ဖြစ်သည်။
၂။ Ping မအောင်မြင်ခြင်းသည် application down ဖြစ်ကြောင်း အမြဲသက်သေပြသလား။ မပြပါ။
၃။ Routing failure နှင့် DNS failure ကို ခွဲခြားရန် ဘာ evidence လိုသနည်း။ Route/path evidence နှင့် resolver response ကို သီးခြားစစ်ရမည်။
၄။ Network automation script သည် state မပြောင်းမီ ဘာကိုစစ်ရမည်နည်း။ Scope၊ input၊ authorization နှင့် idempotent behavior ဖြစ်သည်။

အနှစ်ချုပ်
ယခု {title} ကို layered model၊ explicit scope၊ မှန်ကန်သော identifier၊ repeatable evidence နှင့် safe network-engineering practice များဖြင့် လေ့လာနိုင်ပြီဖြစ်သည်။

နောက်သင်ခန်းစာ
{next_title}

လုံခြုံရေးမှတ်ချက်
Academy simulator သည် predefined local state ကိုသာ အသုံးပြုသည်။ Arbitrary command execute မလုပ်ပါ၊ public target scan မလုပ်ပါ၊ host networking မသုံးပါ၊ private infrastructure နှင့် မချိတ်ဆက်ပါ။
"""

def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")

def _content(position: int, item: tuple) -> str:
    title, topic, commands, language, theory, mm, exercise, question_data = item
    question, options, answer, explanation = question_data
    prerequisite = "No networking experience is required; basic computer use helps." if position == 1 else f"Complete Module 1 lesson {position - 1} first."
    next_lesson = "Continue to the next Module 1 lesson." if position < len(MODULE_ONE) else "Next: open the simulator and complete the first networking fundamentals lab."
    return f"""Introduction
{title} introduces {topic} through safe network reasoning and authorized simulations.

Learning objectives
- Explain {topic} and its place in network communication.
- Identify layers, addresses, devices, protocols, and evidence.
- Troubleshoot only within an isolated or explicitly authorized environment.

Prerequisites
{prerequisite}

Network architecture explanation
application -> transport -> network -> link -> physical medium -> forwarding and service response

Detailed theory
{theory}

Commands and configuration examples
{commands}

Expected output
The simulator returns predefined interface, route, DNS, or protocol evidence. Real command output varies by operating system; verify scope, interface, address, route, and permission before changing anything.

Step-by-step explanation
1. Define the authorized network and symptom.
2. Identify the relevant layer and identifiers.
3. Run the smallest read-only test.
4. Compare evidence with the expected path.
5. Change only a documented lab configuration and verify.

Network diagram
client -> access point/switch -> gateway/router -> routed network -> service

Common errors
- Confusing MAC, IP, port, and DNS name.
- Testing the wrong interface, route, or namespace.
- Treating ping failure as proof that an application is down.
- Running scans or configuration changes without authorization.

Troubleshooting
Check link state, interface address, default route, DNS response, transport port, firewall policy, service logs, and the smallest known-good comparison. Preserve timestamps and redact sensitive network details before sharing.

Best practices
- Use least privilege, read-only inspection first, segmentation, secure management, and documented change control.
- Keep diagrams, address plans, route tables, and expected results current.
- Use monitoring and packet evidence to validate hypotheses.

Security considerations
The Academy simulator is local and predefined. It does not execute arbitrary commands, access host networking, scan public targets, or connect to private infrastructure. Use executable labs only in isolated authorized networks.

Hands-on exercise
{exercise}

Quiz
{question}
Options: {" | ".join(options)}
Correct answer: {answer}
Explanation: {explanation}

Mini project
Design a small isolated network diagram with devices, layers, address roles, a route path, a DNS record, troubleshooting evidence, and a cleanup note.

Summary
You can now reason about {topic} with layered models, identifiers, protocol boundaries, and safe troubleshooting.

Next lesson
{next_lesson}

Myanmar explanation
{mm}

Safety note
Commands are displayed for authorized learning only. No host networking or unauthorized scanning is available.
"""

def seed_networking_course(db, course):
    course.title = "Computer Networking Fundamentals — From Zero to Professional Network Engineer"
    course.short_description = "A free, practical path from networking concepts and protocols to routing, security, cloud networking, and automation."
    course.description = "Learn network models, devices, Ethernet, IPv4, subnetting, IPv6, TCP/UDP, DNS, DHCP, switching, VLANs, routing, NAT, wireless, security, troubleshooting, Wireshark concepts, cloud networking, and Python automation."
    course.level, course.status, course.published = "beginner", "draft", False
    course.duration_minutes = 0
    course.outcomes = "Explain OSI and TCP/IP layers, protocols, devices, addresses, and packet flow|Calculate and reason about IPv4 prefixes, routes, DNS, DHCP, switching, and transport behavior|Troubleshoot authorized networks using layered evidence and safe command workflows|Design secure, observable, resilient network foundations for local and cloud environments"
    course.requirements = "Basic computer use is helpful; no networking experience is required."
    for module_index, module_title in enumerate(PLANNED_MODULES, 1):
        module = db.scalar(select(CourseModule).where(CourseModule.course_id == course.id, CourseModule.order_index == module_index))
        if not module:
            module = CourseModule(course_id=course.id, title=module_title, order_index=module_index)
            db.add(module)
            db.flush()
        module.title = module_title
        specs = MODULE_ONE if module_index == 1 else [
            (lesson_title, lesson_title.lower(), *_generated_code(lesson_title), "", "", "", None)
            for lesson_title in MODULE_LESSON_TOPICS[module_title]
        ]
        for position, item in enumerate(specs, 1):
            title = item[0]
            slug = f"{module_index:02d}-{_slug(title)}"
            lesson = db.scalar(select(Lesson).where(Lesson.module_id == module.id, Lesson.order_index == position))
            if not lesson:
                lesson = Lesson(module_id=module.id, title=title, slug=slug, order_index=position, content_en="", content_mm="")
                db.add(lesson)
                db.flush()
            previous = "No networking experience is required; basic computer use helps." if module_index == 1 and position == 1 else f"Complete the previous lesson before starting {title}."
            next_title = "Continue to the next lesson." if position < len(specs) else (f"Continue to Module {module_index + 1}." if module_index < len(PLANNED_MODULES) else "Complete the final network-engineering capstone.")
            lesson.title, lesson.slug = title, slug
            lesson.description = item[1]
            lesson.content_en = _content(position, item) if module_index == 1 else _generated_content(module_title, title, previous, next_title)
            lesson.content_mm = _generated_content_mm(
                module_title,
                title,
                item[2],
                "Networking အတွေ့အကြုံ မလိုအပ်ပါ။ Basic computer use ကို သိထားပါက အထောက်အကူဖြစ်သည်။" if module_index == 1 and position == 1 else f"{title} မစတင်မီ ယခင်သင်ခန်းစာကို ပြီးအောင်လေ့လာပါ။",
                next_title,
            )
            lesson.duration_minutes, lesson.status, lesson.published = 45, "draft", False
            course.duration_minutes += lesson.duration_minutes
            example = db.scalar(select(CodeExample).where(CodeExample.lesson_id == lesson.id).order_by(CodeExample.position, CodeExample.created_at, CodeExample.id))
            values = {"title": f"{title} example", "language": item[3], "filename": item[3], "code": item[2], "description": "Safe networking example for an isolated or authorized lab; the Academy does not execute it.", "position": 1}
            if not example:
                db.add(CodeExample(lesson_id=lesson.id, **values))
            else:
                for key, value in values.items():
                    setattr(example, key, value)
            quiz = db.scalar(select(LessonQuiz).where(LessonQuiz.lesson_id == lesson.id))
            if not quiz:
                quiz = LessonQuiz(lesson_id=lesson.id, title=f"{title} knowledge check", explanation="Review layers, scope, evidence, and safe network boundaries before retrying.", status="draft")
                db.add(quiz)
                db.flush()
            first_question = (item[7][0], item[7][1], item[7][2], item[7][3]) if module_index == 1 else ("Network evidence မစုမီ ဘာကို သတ်မှတ်ရမည်နည်း?", ["Authorized scope and expected path", "Every public address", "A random firewall change"], "Authorized scope and expected path", "Scope and evidence make troubleshooting safe and repeatable.")
            questions = [
                first_question,
                ("True or false: the Academy simulator executes arbitrary network commands on the host.", ["True", "False"], "False", "The simulator uses predefined local state and outputs."),
                ("Which practice makes network troubleshooting safer?", ["Define scope and collect read-only evidence first", "Scan every address", "Change firewall rules randomly"], "Define scope and collect read-only evidence first", "Authorized scope and evidence reduce harm and confusion."),
                ("Which evidence should be checked separately when diagnosing a web request?", ["Route/path evidence, DNS response, and transport response", "Only the browser color", "Only a Wi-Fi password"], "Route/path evidence, DNS response, and transport response", "Separate evidence narrows the failing layer.")
            ]
            for q_position, (prompt, choices, answer, explanation) in enumerate(questions, 1):
                row = db.scalar(select(QuizQuestion).where(QuizQuestion.quiz_id == quiz.id, QuizQuestion.position == q_position))
                values = {"prompt": prompt, "question_type": "true_false" if choices == ["True", "False"] else "multiple_choice", "options_json": json.dumps(choices), "correct_answer": answer, "explanation": explanation}
                if not row:
                    db.add(QuizQuestion(quiz_id=quiz.id, position=q_position, **values))
                else:
                    for key, value in values.items():
                        setattr(row, key, value)
            for difficulty, label in (("beginner", "Easy"), ("intermediate", "Medium"), ("advanced", "Advanced")):
                exercise_slug = f"{slug}-{difficulty}"
                exercise = db.scalar(select(CodingExercise).where(CodingExercise.slug == exercise_slug))
                values = {"lesson_id": lesson.id, "title": f"{title} — {label} exercise", "slug": exercise_slug, "description_en": f"{label} exercise: analyze {title} in an isolated or authorized network lab and document the evidence.", "description_mm": f"{title} ကို ခွင့်ပြုချက်ရှိသော isolated network lab ထဲတွင် {label} အဆင့်ဖြင့် လေ့လာပြီး evidence ကို မှတ်တမ်းတင်ပါ။", "difficulty": difficulty, "language": "networking", "starter_code": "# Record scope, command, expected output, observed output, and cleanup\n", "status": "draft"}
                if not exercise:
                    db.add(CodingExercise(**values))
                else:
                    for key, value in values.items():
                        setattr(exercise, key, value)
    db.flush()

