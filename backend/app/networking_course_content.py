"""Authored Networking Fundamentals vertical slice for the idempotent catalog seed."""
import json
import re

from sqlalchemy import select

from .models import CodeExample, CourseModule, Lesson, LessonQuiz, QuizQuestion

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
    course.level, course.status, course.published = "beginner", "published", True
    course.duration_minutes = len(MODULE_ONE) * 45
    course.outcomes = "Explain OSI and TCP/IP layers, protocols, devices, addresses, and packet flow|Calculate and reason about IPv4 prefixes, routes, DNS, DHCP, switching, and transport behavior|Troubleshoot authorized networks using layered evidence and safe command workflows|Design secure, observable, resilient network foundations for local and cloud environments"
    course.requirements = "Basic computer use is helpful; no networking experience is required."
    module = db.scalar(select(CourseModule).where(CourseModule.course_id == course.id, CourseModule.order_index == 1))
    if not module:
        module = CourseModule(course_id=course.id, title=PLANNED_MODULES[0], order_index=1)
        db.add(module)
        db.flush()
    module.title = PLANNED_MODULES[0]
    for position, item in enumerate(MODULE_ONE, 1):
        title = item[0]
        slug = f"01-{_slug(title)}"
        lesson = db.scalar(select(Lesson).where(Lesson.module_id == module.id, Lesson.order_index == position))
        if not lesson:
            lesson = Lesson(module_id=module.id, title=title, slug=slug, order_index=position, content_en="", content_mm="")
            db.add(lesson)
            db.flush()
        lesson.title, lesson.slug = title, slug
        lesson.description = item[1]
        lesson.content_en = _content(position, item)
        lesson.content_mm = f"{title}\n\n{item[5]}\n\nလေ့ကျင့်ခန်း\n{item[6]}"
        lesson.duration_minutes, lesson.status, lesson.published = 45, "published", True
        example = db.scalar(select(CodeExample).where(CodeExample.lesson_id == lesson.id).order_by(CodeExample.position, CodeExample.created_at, CodeExample.id))
        values = {"title": f"{title} example", "language": item[3], "filename": item[3], "code": item[2], "description": "Safe networking example for an isolated or authorized lab; the Academy does not execute it.", "position": 1}
        if not example:
            db.add(CodeExample(lesson_id=lesson.id, **values))
        else:
            for key, value in values.items():
                setattr(example, key, value)
        quiz = db.scalar(select(LessonQuiz).where(LessonQuiz.lesson_id == lesson.id))
        if not quiz:
            quiz = LessonQuiz(lesson_id=lesson.id, title=f"{title} knowledge check", explanation="Review layers, scope, evidence, and safe network boundaries before retrying.", status="published")
            db.add(quiz)
            db.flush()
        questions = [
            (item[7][0], item[7][1], item[7][2], item[7][3]),
            ("True or false: the Academy simulator executes arbitrary network commands on the host.", ["True", "False"], "False", "The simulator uses predefined local state and outputs."),
            ("Which practice makes network troubleshooting safer?", ["Define scope and collect read-only evidence first", "Scan every address", "Change firewall rules randomly"], "Define scope and collect read-only evidence first", "Authorized scope and evidence reduce harm and confusion.")
        ]
        for q_position, (prompt, choices, answer, explanation) in enumerate(questions, 1):
            row = db.scalar(select(QuizQuestion).where(QuizQuestion.quiz_id == quiz.id, QuizQuestion.position == q_position))
            values = {"prompt": prompt, "question_type": "true_false" if choices == ["True", "False"] else "multiple_choice", "options_json": json.dumps(choices), "correct_answer": answer, "explanation": explanation}
            if not row:
                db.add(QuizQuestion(quiz_id=quiz.id, position=q_position, **values))
            else:
                for key, value in values.items():
                    setattr(row, key, value)
    db.flush()

