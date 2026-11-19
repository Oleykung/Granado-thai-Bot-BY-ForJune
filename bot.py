
# -*- coding: utf-8 -*-
"""
Granado Espada M - Discord Boss Timer Bot
เซิร์ฟไทย | 3 เมือง: Reboldoeux / The Port of Coimbra / City of Auch
เวลาไทย Asia/Bangkok

วิธีรัน:
  pip install -r requirements.txt
  ใส่ DISCORD_TOKEN ในไฟล์ .env
  python bot.py

คำสั่งหลัก (พิมพ์ใน Discord):
  !บอส                - ดูสถานะบอสทั้งหมด + เวลาเกิดถัดไป
  !บอสตาย <ชื่อบอส>   - บันทึกว่าบอสตายตอนนี้ -> คำนวณเวลาเกิดอัตโนมัติ
  !บอสตาย <ชื่อบอส> 21:30 - บันทึกว่าตายตอน 21:30 (วันนี้)
  !บอสเกิด <ชื่อบอส> 22:00 - ตั้งเวลาเกิดเอง (ถ้ารู้เวลาเกิดจากในเกม)
  !บอสรีเซ็ต <ชื่อบอส>  - ล้างตัวจับเวลา
  !บอสตั้งเวลา <ชื่อบอส> <ชม.> - เปลี่ยน respawn ของบอสตัวนั้น เช่น !บอสตั้งเวลา hill 4
  !ตั้งช่องแจ้งเตือน    - ตั้งช่องนี้เป็นช่องแจ้งเตือนบอส (ต้องพิมพ์ในช่องนั้น)
  !บอสช่วย            - ดูวิธีใช้ทั้งหมด

Slash Commands ก็ใช้ได้เหมือนกัน: /boss /kill /spawn /reset /helpboss

Respawn ตั้งต้น (อิงแพทช์ SEA - แก้ได้ด้วย !บอสตั้งเวลา):
  Reboldoeux: 3 ชม. (ยังไม่มีแพทช์ทางการยืนยัน - ค่าประมาณ ใช้แก้ได้)
  The Port of Coimbra: 5 ชม. (Patch Notes 12 Aug 2026)
  City of Auch: 11 ชม. (Patch Notes 23 Sep 2026 Gigante II)
"""

import os
import json
import asyncio
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv

load_dotenv()
# 24h keep-alive web server (for Render/Railway)
KEEP_ALIVE = os.getenv("KEEP_ALIVE", "0") == "1"
if KEEP_ALIVE:
    try:
        from keep_alive import keep_alive
        keep_alive()
        print("🌐 Keep-alive web server started (for 24h hosting)")
    except Exception as e:
        print(f"Keep-alive failed: {e}")

TOKEN = os.getenv("DISCORD_TOKEN", "")
NOTIFY_ROLE_ID = os.getenv("NOTIFY_ROLE_ID", "")  # ใส่ Role ID ถ้าอยากให้ ping role แทน @everyone
PREFIX = os.getenv("PREFIX", "!")

BKK = ZoneInfo("Asia/Bangkok")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BOSSES_FILE = os.path.join(BASE_DIR, "bosses.json")
TIMERS_FILE = os.path.join(BASE_DIR, "boss_timers.json")
SETTINGS_FILE = os.path.join(BASE_DIR, "settings.json")

# ---------- Load bosses ----------
with open(BOSSES_FILE, encoding="utf-8") as f:
    BOSSES = json.load(f)
BOSS_BY_KEY = {b["key"]: b for b in BOSSES}

# ---------- Storage ----------
def load_json(path, default):
    if os.path.exists(path):
        try:
            with open(path, encoding="utf-8") as f:
                return json.load(f)
        except:
            return default
    return default

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

timers = load_json(TIMERS_FILE, {})  # key -> {last_kill_iso, next_spawn_iso, killed_by, notified: {10min, 5min, 1min, spawn}}
settings = load_json(SETTINGS_FILE, {"notify_channel_id": None})

# ---------- Helpers ----------
def now_bkk():
    return datetime.now(BKK)

def parse_time_today(hhmm: str):
    """รับ '21:30' -> datetime วันนี้ เวลาไทย, ถ้าเลยไปแล้วถือว่าเป็นเมื่อวาน? ไม่ - ถ้าเป็นเวลาตาย ให้ถือว่าเป็นวันนี้ ถ้าเกินตอนนี้ให้ถือว่าเมื่อวาน"""
    try:
        h, m = hhmm.strip().split(":")
        h, m = int(h), int(m)
        if not (0 <= h <= 23 and 0 <= m <= 59):
            return None
        now = now_bkk()
        dt = now.replace(hour=h, minute=m, second=0, microsecond=0)
        # ถ้าเวลาที่ใส่ มากกว่าเวลาปัจจุบันเกิน 5 นาที แปลว่าน่าจะเป็นของเมื่อวาน (เช่น ตีตอน 23:50 แล้วมาบันทึกตอน 00:10)
        if dt > now + timedelta(minutes=5):
            dt = dt - timedelta(days=1)
        return dt
    except:
        return None

def fmt_dt(dt: datetime):
    return dt.strftime("%d/%m %H:%M")

def fmt_countdown(delta: timedelta):
    total = int(delta.total_seconds())
    if total < 0:
        return "เกิดแล้ว!"
    h = total // 3600
    m = (total % 3600) // 60
    s = total % 60
    if h > 0:
        return f"{h} ชม. {m} นาที"
    if m > 0:
        return f"{m} นาที {s} วิ"
    return f"{s} วิ"

def find_boss(query: str):
    if not query:
        return None
    q = query.strip().lower()
    # 1. ตรง key
    if q in BOSS_BY_KEY:
        return BOSS_BY_KEY[q]
    # 2. alias / ชื่อตรง
    for b in BOSSES:
        if q == b["name_th"].lower() or q == b["name_en"].lower():
            return b
        if q in [a.lower() for a in b.get("aliases", [])]:
            return b
    # 3. มีคำอยู่ในชื่อ (fuzzy แบบง่าย)
    candidates = []
    for b in BOSSES:
        if q in b["name_th"].lower() or q in b["name_en"].lower():
            candidates.append(b)
        elif any(q in a.lower() for a in b.get("aliases", [])):
            candidates.append(b)
    if len(candidates) == 1:
        return candidates[0]
    if len(candidates) > 1:
        # ถ้าเจอหลายตัว เช่น "cockatrice" เจอ 2 ตัว ให้คืนตัวแรกแล้วให้ผู้ใช้เลือกใหม่ แต่เราจะคืน None พร้อมรายชื่อใน caller
        return ("multiple", candidates)
    return None

def boss_display(b):
    return f"{b['name_th']} / {b['name_en']}"

def boss_line(b, timer=None):
    now = now_bkk()
    base = f"**{boss_display(b)}** | {b['city_th']} ({b['city_en']}) | {b['map_th']} / {b['map_en']} | {b['type_th']} | รี {b['respawn_hours']} ชม."
    if not timer or not timer.get("next_spawn_iso"):
        return base + " | ⏳ ยังไม่มีเวลา"
    nxt = datetime.fromisoformat(timer["next_spawn_iso"])
    delta = nxt - now
    if delta.total_seconds() <= 0:
        return base + f" | 🟢 **เกิดแล้ว!** (เกิดเมื่อ {fmt_dt(nxt)})"
    else:
        return base + f" | 🕐 เกิด {fmt_dt(nxt)} (อีก {fmt_countdown(delta)})"

def make_embed(b, timer=None, title=None):
    color = b.get("color", 0x3498db)
    embed = discord.Embed(
        title=title or boss_display(b),
        description=f"**เมือง:** {b['city_th']} / {b['city_en']}\n**แผนที่:** {b['map_th']} / {b['map_en']}\n**ประเภท:** {b['type_th']} / {b['type_en']}\n**Respawn:** {b['respawn_hours']} ชม.",
        color=color,
        timestamp=now_bkk()
    )
    if timer and timer.get("next_spawn_iso"):
        nxt = datetime.fromisoformat(timer["next_spawn_iso"])
        delta = nxt - now_bkk()
        if delta.total_seconds() <= 0:
            embed.add_field(name="สถานะ", value=f"🟢 เกิดแล้ว! เกิดเมื่อ {fmt_dt(nxt)}", inline=False)
        else:
            embed.add_field(name="เกิดถัดไป", value=f"{fmt_dt(nxt)} (อีก {fmt_countdown(delta)})", inline=False)
        if timer.get("last_kill_iso"):
            last = datetime.fromisoformat(timer["last_kill_iso"])
            embed.add_field(name="ตายล่าสุด", value=f"{fmt_dt(last)} โดย {timer.get('killed_by','-')}", inline=False)
    else:
        embed.add_field(name="สถานะ", value="⏳ ยังไม่มีเวลาตาย/เกิด", inline=False)
    embed.set_footer(text="Granado Espada M • Boss Timer • เวลาไทย (Asia/Bangkok)")
    return embed

def get_notify_channel(bot):
    cid = settings.get("notify_channel_id")
    if cid:
        ch = bot.get_channel(int(cid))
        if ch:
            return ch
    return None

def ping_text():
    if NOTIFY_ROLE_ID:
        return f"<@&{NOTIFY_ROLE_ID}>"
    return "@everyone"

# ---------- Bot ----------
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.guild_messages = True

bot = commands.Bot(command_prefix=PREFIX, intents=intents, help_command=None)

@bot.event
async def on_ready():
    print(f"✅ ล็อกอินแล้ว: {bot.user} (ID: {bot.user.id})")
    print(f"📋 บอสที่โหลด: {len(BOSSES)} ตัว")
    try:
        synced = await bot.tree.sync()
        print(f"✅ Sync slash commands: {len(synced)} คำสั่ง")
    except Exception as e:
        print(f"⚠️ Sync slash ไม่ได้: {e}")
    check_boss_spawns.start()

# ---------- Core logic (ใช้ร่วมกันทั้ง prefix + slash) ----------
async def do_show_all(ctx_or_interaction, is_interaction=False):
    # จัดกลุ่มตามเมือง
    groups = {}
    for b in BOSSES:
        groups.setdefault(b["city_en"], []).append(b)
    order = ["Reboldoeux", "The Port of Coimbra", "City of Auch"]
    embeds = []
    for city in order:
        if city not in groups:
            continue
        city_th = groups[city][0]["city_th"]
        color = groups[city][0].get("color", 0x3498db)
        embed = discord.Embed(title=f"📍 {city_th} / {city}", color=color, timestamp=now_bkk())
        lines = []
        for b in groups[city]:
            timer = timers.get(b["key"])
            lines.append(boss_line(b, timer))
        embed.description = "\n\n".join(lines)
        embed.set_footer(text="พิมพ์ !บอสตาย <ชื่อบอส> เมื่อบอสตาย เพื่อเริ่มจับเวลา")
        embeds.append(embed)
    if is_interaction:
        await ctx_or_interaction.response.send_message(embeds=embeds[:10])
    else:
        for e in embeds:
            await ctx_or_interaction.send(embed=e)

async def do_kill(ctx_or_interaction, boss_query, time_str=None, author_name="ไม่ระบุ", is_interaction=False, channel=None):
    found = find_boss(boss_query)
    if found is None:
        msg = f"❌ หาบอสชื่อ `{boss_query}` ไม่เจอ ลองพิมพ์ `!บอส` เพื่อดูรายชื่อ\nตัวอย่าง: `!บอสตาย hill` / `!บอสตาย ค็อกคาทริซ`"
        if is_interaction:
            await ctx_or_interaction.response.send_message(msg)
        else:
            await channel.send(msg)
        return
    if isinstance(found, tuple) and found[0] == "multiple":
        cands = found[1]
        lst = "\n".join([f"- {boss_display(c)} ({c['city_th']} / {c['map_th']})" for c in cands])
        msg = f"⚠️ เจอหลายตัวที่ตรงกับ `{boss_query}` เลือกให้ชัดกว่านี้:\n{lst}"
        if is_interaction:
            await ctx_or_interaction.response.send_message(msg)
        else:
            await channel.send(msg)
        return
    b = found
    # เวลาตาย
    if time_str:
        kill_dt = parse_time_today(time_str)
        if kill_dt is None:
            msg = "❌ เวลาผิด ใช้แบบ `21:30` เช่น `!บอสตาย hill 21:30`"
            if is_interaction:
                await ctx_or_interaction.response.send_message(msg)
            else:
                await channel.send(msg)
            return
    else:
        kill_dt = now_bkk()
    respawn = float(b["respawn_hours"])
    next_dt = kill_dt + timedelta(hours=respawn)
    timers[b["key"]] = {
        "last_kill_iso": kill_dt.isoformat(),
        "next_spawn_iso": next_dt.isoformat(),
        "killed_by": author_name,
        "notified": {"10min": False, "5min": False, "1min": False, "spawn": False},
        "notify_channel_id": channel.id if channel else (settings.get("notify_channel_id") or None)
    }
    save_json(TIMERS_FILE, timers)
    # ถ้ายังไม่มีช่องแจ้งเตือนหลัก ให้ใช้ช่องนี้เป็นหลักไปก่อน
    if not settings.get("notify_channel_id") and channel:
        settings["notify_channel_id"] = channel.id
        save_json(SETTINGS_FILE, settings)
    embed = make_embed(b, timers[b["key"]], title=f"💀 บอสตายแล้ว: {boss_display(b)}")
    embed.add_field(name="⏰ จะเกิดอีกครั้ง", value=f"{fmt_dt(next_dt)} (อีก {fmt_countdown(next_dt - now_bkk())})", inline=False)
    if is_interaction:
        await ctx_or_interaction.response.send_message(embed=embed)
    else:
        await channel.send(embed=embed)

async def do_set_spawn(ctx_or_interaction, boss_query, time_str, author_name="ไม่ระบุ", is_interaction=False, channel=None):
    found = find_boss(boss_query)
    if found is None or (isinstance(found, tuple)):
        msg = f"❌ หาบอส `{boss_query}` ไม่เจอ / เจอหลายตัว ลองพิมพ์ให้ชัดกว่านี้"
        if is_interaction:
            await ctx_or_interaction.response.send_message(msg)
        else:
            await channel.send(msg)
        return
    b = found
    spawn_dt = parse_time_today(time_str)
    if spawn_dt is None:
        msg = "❌ เวลาผิด ใช้แบบ `22:00` เช่น `!บอสเกิด hill 22:00`"
        if is_interaction:
            await ctx_or_interaction.response.send_message(msg)
        else:
            await channel.send(msg)
        return
    # ถ้าเวลาที่ใส่เลยไปแล้ว ให้ถือว่าเป็นพรุ่งนี้
    if spawn_dt < now_bkk():
        spawn_dt = spawn_dt + timedelta(days=1)
    timers[b["key"]] = {
        "last_kill_iso": None,
        "next_spawn_iso": spawn_dt.isoformat(),
        "killed_by": author_name,
        "notified": {"10min": False, "5min": False, "1min": False, "spawn": False},
        "notify_channel_id": channel.id if channel else (settings.get("notify_channel_id") or None)
    }
    save_json(TIMERS_FILE, timers)
    embed = make_embed(b, timers[b["key"]], title=f"📅 ตั้งเวลาเกิด: {boss_display(b)}")
    if is_interaction:
        await ctx_or_interaction.response.send_message(embed=embed)
    else:
        await channel.send(embed=embed)

async def do_reset(ctx_or_interaction, boss_query, is_interaction=False, channel=None):
    found = find_boss(boss_query)
    if found is None or (isinstance(found, tuple)):
        msg = f"❌ หาบอส `{boss_query}` ไม่เจอ"
        if is_interaction:
            await ctx_or_interaction.response.send_message(msg)
        else:
            await channel.send(msg)
        return
    b = found
    if b["key"] in timers:
        del timers[b["key"]]
        save_json(TIMERS_FILE, timers)
    msg = f"✅ ล้างตัวจับเวลา **{boss_display(b)}** แล้ว"
    if is_interaction:
        await ctx_or_interaction.response.send_message(msg)
    else:
        await channel.send(msg)

async def do_set_respawn(ctx_or_interaction, boss_query, hours_str, is_interaction=False, channel=None):
    found = find_boss(boss_query)
    if found is None or (isinstance(found, tuple)):
        msg = f"❌ หาบอส `{boss_query}` ไม่เจอ"
        if is_interaction:
            await ctx_or_interaction.response.send_message(msg)
        else:
            await channel.send(msg)
        return
    try:
        h = float(hours_str)
        if h <= 0 or h > 48:
            raise ValueError
    except:
        msg = "❌ ชั่วโมงผิด ใส่ 0.5 - 48 เช่น `!บอสตั้งเวลา hill 4`"
        if is_interaction:
            await ctx_or_interaction.response.send_message(msg)
        else:
            await channel.send(msg)
        return
    b = found
    b["respawn_hours"] = h
    # บันทึกกลับเข้า bosses.json
    save_json(BOSSES_FILE, BOSSES)
    msg = f"✅ ตั้ง Respawn **{boss_display(b)}** = {h} ชม. แล้ว (ใช้กับครั้งถัดไปที่บันทึกตาย)"
    if is_interaction:
        await ctx_or_interaction.response.send_message(msg)
    else:
        await channel.send(msg)

# ---------- Prefix Commands (ภาษาไทย) ----------
@bot.command(name="บอส", aliases=["boss", "บอสทั้งหมด", "bosslist"])
async def cmd_boss_th(ctx):
    await do_show_all(ctx, is_interaction=False)

@bot.command(name="บอสตาย", aliases=["kill", "ตาย"])
async def cmd_kill_th(ctx, *, args: str = ""):
    # args = "hill" หรือ "hill 21:30"
    parts = args.strip().rsplit(" ", 1)
    if len(parts) == 2 and ":" in parts[1]:
        boss_q, t = parts[0], parts[1]
    else:
        boss_q, t = args.strip(), None
    if not boss_q:
        await ctx.send("ใช้แบบ: `!บอสตาย <ชื่อบอส>` เช่น `!บอสตาย hill` หรือ `!บอสตาย ค็อกคาทริซ 21:30`")
        return
    await do_kill(ctx, boss_q, t, author_name=str(ctx.author), is_interaction=False, channel=ctx.channel)

@bot.command(name="บอสเกิด", aliases=["spawn", "เกิด"])
async def cmd_spawn_th(ctx, *, args: str = ""):
    parts = args.strip().rsplit(" ", 1)
    if len(parts) != 2 or ":" not in parts[1]:
        await ctx.send("ใช้แบบ: `!บอสเกิด <ชื่อบอส> <HH:MM>` เช่น `!บอสเกิด hill 22:00`")
        return
    await do_set_spawn(ctx, parts[0], parts[1], author_name=str(ctx.author), is_interaction=False, channel=ctx.channel)

@bot.command(name="บอสรีเซ็ต", aliases=["reset", "ล้าง"])
async def cmd_reset_th(ctx, *, boss_q: str = ""):
    if not boss_q:
        await ctx.send("ใช้แบบ: `!บอสรีเซ็ต <ชื่อบอส>`")
        return
    await do_reset(ctx, boss_q, is_interaction=False, channel=ctx.channel)

@bot.command(name="บอสตั้งเวลา", aliases=["setrespawn", "ตั้งเวลา"])
async def cmd_setrespawn_th(ctx, boss_q: str = "", hours: str = ""):
    if not boss_q or not hours:
        await ctx.send("ใช้แบบ: `!บอสตั้งเวลา <ชื่อบอส> <ชม.>` เช่น `!บอสตั้งเวลา hill 4`")
        return
    await do_set_respawn(ctx, boss_q, hours, is_interaction=False, channel=ctx.channel)

@bot.command(name="ตั้งช่องแจ้งเตือน", aliases=["setchannel", "setnotify"])
async def cmd_setchannel(ctx):
    settings["notify_channel_id"] = ctx.channel.id
    save_json(SETTINGS_FILE, settings)
    await ctx.send(f"✅ ตั้งช่องนี้ <#{ctx.channel.id}> เป็นช่องแจ้งเตือนบอสแล้ว")

@bot.command(name="บอสช่วย", aliases=["helpboss", "ช่วย"])
async def cmd_help_th(ctx):
    text = (
        "**🤖 บอทแจ้งเวลาบอส Granado Espada M - เซิร์ฟไทย**\n"
        "เมืองที่รองรับ: เรโบลโด / ท่าเรือโคอิมบรา / เมืองโอช\n\n"
        "**คำสั่งหลัก:**\n"
        "`!บอส` - ดูบอสทั้งหมด + เวลาเกิดถัดไป\n"
        "`!บอสตาย <ชื่อบอส>` - บอสตายตอนนี้ เช่น `!บอสตาย hill`\n"
        "`!บอสตาย <ชื่อบอส> 21:30` - บอสตายตอน 21:30\n"
        "`!บอสเกิด <ชื่อบอส> 22:00` - ตั้งเวลาเกิดเอง\n"
        "`!บอสรีเซ็ต <ชื่อบอส>` - ล้างเวลา\n"
        "`!บอสตั้งเวลา <ชื่อบอส> <ชม.>` - เปลี่ยน respawn เช่น `!บอสตั้งเวลา hill 4`\n"
        "`!ตั้งช่องแจ้งเตือน` - ตั้งช่องนี้เป็นช่องแจ้งเตือน\n\n"
        "**Respawn ตั้งต้น:** เรโบลโด 3 ชม. / โคอิมบรา 5 ชม. / โอช 11 ชม.\n"
        "บอทจะแจ้งล่วงหน้า 10 นาที, 5 นาที, 1 นาที และตอนเกิด\n"
        "ค้นหาบอสพิมพ์ไทยหรืออังกฤษก็ได้ เช่น `hill`, `ค็อกคาทริซ`, `โกเลม`, `วิกเตอร์`"
    )
    await ctx.send(text)

# ---------- Slash Commands (English names - Discord บังคับ) ----------
@bot.tree.command(name="boss", description="ดูสถานะบอสทั้งหมด Granado Espada M")
async def slash_boss(interaction: discord.Interaction):
    await do_show_all(interaction, is_interaction=True)

@bot.tree.command(name="kill", description="บันทึกว่าบอสตายตอนนี้")
@discord.app_commands.describe(boss="ชื่อบอส เช่น hill, cockatrice, golem", time="เวลาที่ตาย เช่น 21:30 (ถ้าไม่ใส่ = ตอนนี้)")
async def slash_kill(interaction: discord.Interaction, boss: str, time: str = None):
    await do_kill(interaction, boss, time, author_name=str(interaction.user), is_interaction=True, channel=interaction.channel)

@bot.tree.command(name="spawn", description="ตั้งเวลาเกิดบอสเอง")
@discord.app_commands.describe(boss="ชื่อบอส", time="เวลาเกิด เช่น 22:00")
async def slash_spawn(interaction: discord.Interaction, boss: str, time: str):
    await do_set_spawn(interaction, boss, time, author_name=str(interaction.user), is_interaction=True, channel=interaction.channel)

@bot.tree.command(name="reset", description="ล้างตัวจับเวลาบอส")
@discord.app_commands.describe(boss="ชื่อบอส")
async def slash_reset(interaction: discord.Interaction, boss: str):
    await do_reset(interaction, boss, is_interaction=True, channel=interaction.channel)

@bot.tree.command(name="helpboss", description="วิธีใช้บอทบอส")
async def slash_help(interaction: discord.Interaction):
    await interaction.response.send_message(
        "พิมพ์ `!บอสช่วย` ในช่องแชทเพื่อดูวิธีใช้ทั้งหมด\n"
        "หลักๆ: `!บอส` ดูเวลา / `!บอสตาย <ชื่อบอส>` บันทึกตาย / `!บอสเกิด <ชื่อบอส> 22:00` ตั้งเวลาเกิด"
    )

# ---------- Background checker ----------
@tasks.loop(seconds=60)
async def check_boss_spawns():
    if not bot.is_ready():
        return
    now = now_bkk()
    for b in BOSSES:
        timer = timers.get(b["key"])
        if not timer or not timer.get("next_spawn_iso"):
            continue
        nxt = datetime.fromisoformat(timer["next_spawn_iso"])
        delta = (nxt - now).total_seconds()
        notified = timer.get("notified", {"10min": False, "5min": False, "1min": False, "spawn": False})
        # หาช่องที่จะแจ้ง: ช่องที่บันทึกไว้ตอน kill หรือช่องหลัก
        ch_id = timer.get("notify_channel_id") or settings.get("notify_channel_id")
        ch = bot.get_channel(int(ch_id)) if ch_id else None
        if not ch:
            # ถ้าไม่มีช่อง ให้ข้าม (รอผู้ใช้ตั้งช่อง)
            continue
        try:
            if 0 < delta <= 60 and not notified.get("1min"):
                await ch.send(f"{ping_text()} ⏰ **อีก 1 นาที** `{boss_display(b)}` จะเกิด! | {b['city_th']} - {b['map_th']} / {b['map_en']}")
                notified["1min"] = True
            elif 0 < delta <= 300 and not notified.get("5min"):
                await ch.send(f"{ping_text()} ⏰ **อีก 5 นาที** `{boss_display(b)}` จะเกิด! | {b['city_th']} - {b['map_th']} / {b['map_en']} | เกิด {fmt_dt(nxt)}")
                notified["5min"] = True
            elif 0 < delta <= 600 and not notified.get("10min"):
                await ch.send(f"{ping_text()} ⏰ **อีก 10 นาที** `{boss_display(b)}` จะเกิด! | {b['city_th']} - {b['map_th']} / {b['map_en']} | เกิด {fmt_dt(nxt)}")
                notified["10min"] = True
            elif delta <= 0 and not notified.get("spawn"):
                embed = make_embed(b, timer, title=f"🟢 บอสเกิดแล้ว! {boss_display(b)}")
                await ch.send(content=f"{ping_text()} บอสเกิดแล้ว ไปตีกัน!", embed=embed)
                notified["spawn"] = True
            if notified != timer.get("notified"):
                timer["notified"] = notified
                save_json(TIMERS_FILE, timers)
        except Exception as e:
            print(f"แจ้งเตือน {b['key']} ไม่ได้: {e}")

@check_boss_spawns.before_loop
async def before_check():
    await bot.wait_until_ready()

# ---------- Run ----------
if __name__ == "__main__":
    if not TOKEN:
        print("❌ ยังไม่มี DISCORD_TOKEN - สร้างไฟล์ .env แล้วใส่ DISCORD_TOKEN=xxx")
        print("ดูวิธีสร้าง Token ใน README.md")
    else:
        bot.run(TOKEN)
