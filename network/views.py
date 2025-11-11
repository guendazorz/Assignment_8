import re, time, json
from datetime import datetime
from django.shortcuts import render, redirect
from django.conf import settings
from .forms import DhcpForm
from pymongo import MongoClient

# Store current DHCP leases temporarily in memory
LEASES = {}
LEASE_SECONDS = getattr(settings, 'LEASE_SECONDS', 3600)
MAC_RE = re.compile(r"^[0-9A-Fa-f]{2}(:[0-9A-Fa-f]{2}){5}$")

def mongo_collection():
    host = settings.MONGO["HOST"]; port = settings.MONGO["PORT"]
    dbn  = settings.MONGO["DB"];  user = (settings.MONGO["USER"] or "").strip()
    pwd  = (settings.MONGO["PASS"] or "").strip()

    if user and pwd:
        uri = f"mongodb://{user}:{pwd}@{host}:{port}/{dbn}?authSource={dbn}"
    else:
        uri = f"mongodb://{host}:{port}/{dbn}"

    client = MongoClient(uri, serverSelectionTimeoutMS=3000)
    return client[dbn]["leases"]


def mac_valid(mac):
    return MAC_RE.match(mac) is not None

def mac_bytes(mac):
    return [int(x, 16) for x in mac.split(":")]

def mac_sum_is_even(mac):
    return (sum(mac_bytes(mac)) & 1) == 0

def ipv4_from_pool(mac):
    last = mac_bytes(mac)[-1]
    ip_last = 10 + (last % (254 - 10))
    return f"192.168.1.{ip_last}"

def eui64_from_mac(mac, prefix="2001:db8::/64"):
    b = mac_bytes(mac)
    b[0] ^= 0x02  # toggle u/l bit
    eui = b[:3] + [0xFF, 0xFE] + b[3:]
    iid = f"{eui[0]:02x}{eui[1]:02x}:{eui[2]:02x}{eui[3]:02x}:{eui[4]:02x}{eui[5]:02x}:{eui[6]:02x}{eui[7]:02x}"
    return f"2001:db8::{iid}"

def lease_key(mac, dhcp):
    return f"{mac.upper()}_{dhcp}"

def get_or_assign_ip(mac, dhcp):
    now = time.time()
    key = lease_key(mac, dhcp)
    if key in LEASES and LEASES[key]["expires_at"] > now:
        return LEASES[key]["ip"]
    ip = ipv4_from_pool(mac) if dhcp == "DHCPv4" else eui64_from_mac(mac)
    LEASES[key] = {"ip": ip, "expires_at": now + LEASE_SECONDS}
    return ip

def home(request):
    return render(request, "network/home.html", {"form": DhcpForm()})

def submit_request(request):
    if request.method != "POST":
        return redirect("home")

    form = DhcpForm(request.POST)
    if not form.is_valid():
        return render(request, "network/home.html", {"form": form, "result": "Invalid form."})

    mac = form.cleaned_data["mac_address"].strip()
    dhcp = form.cleaned_data["dhcp_version"]

    if not mac_valid(mac):
        return render(request, "network/home.html", {"form": form, "result": "Invalid MAC format."})

    if dhcp not in ("DHCPv4", "DHCPv6"):
        return render(request, "network/home.html", {"form": form, "result": "Invalid DHCP version."})

    assigned_ip = get_or_assign_ip(mac, dhcp)
    even = mac_sum_is_even(mac)

    doc = {
        "mac_address": mac.upper(),
        "dhcp_version": dhcp,
        "assigned_ip": assigned_ip,
        "lease_time": f"{LEASE_SECONDS} seconds",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "mac_sum_even": even,
    }

    try:
        # Insert a COPY so PyMongo adding _id doesn't mutate our original dict
        res = mongo_collection().insert_one(doc.copy())
        # Build a JSON-safe response including the inserted_id as a string
        result_doc = {**doc, "_id": str(res.inserted_id)}
        result = json.dumps(result_doc, indent=2)
    except Exception as e:
        result = json.dumps({"error": str(e), **doc}, indent=2)

    return render(request, "network/home.html", {"form": DhcpForm(), "result": result})

def view_leases(request):
    col = mongo_collection()
    items = list(col.find({}, {"_id": 0}).sort("timestamp", -1))
    return render(request, "network/leases.html", {"data": items})
