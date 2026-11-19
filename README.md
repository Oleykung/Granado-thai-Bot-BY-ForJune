# 🤖 Granado Espada M - Discord Boss Timer Bot (เซิร์ฟไทย)

บอทแจ้งเวลาบอสตาย / เกิด สำหรับ 3 เมือง
**เรโบลโด (Reboldoeux) / ท่าเรือโคอิมบรา (The Port of Coimbra) / เมืองโอช (City of Auch)**
เวลาไทย Asia/Bangkok

## ✅ บอสที่มีในบอท (13 ตัว)

### เรโบลโด - Respawn 3 ชม. (ค่าประมาณ - แก้ได้)
- ฮิลล์ไจแอนท์ / Hill Giant - สามแยกเฟอร์รุชชิโอ / Ferruccio Junction
- ยักษ์หัวรังนก / Bird's Nest Giant - เขตเรโบลโด

### ท่าเรือโคอิมบรา - Respawn 5 ชม. (Patch Notes 12 Aug 2026)
- พอลลักซ์ / Pollux - สุสานใต้ดินเททรา / Tetra Catacomb
- แคสเตอร์ / Castor - ถนนทองเททรา / Tetra Golden Road
- โกเลมสมบัติ / Treasure Golem - ห้องโบราณวัตถุเททรา / Tetra Antiquities Room
- หัวหน้าเผ่าเมอร์แมน / Merman Chieftain Lv.63 - ดาดฟ้าปอร์โตเบลโล / Porto Bello Deck
- กัปตันชาร์ฟเฟนเบอร์เกอร์ / Captain Scharffenberger Lv.69 - หน้าผาร้างปอร์โตเบลโล / Porto Bello Desolate Cliff
- วานลันเช่ / Wanlanshe - ท่าเรือร้างปอร์โตเบลโล / Porto Bello Deserted Quay

### เมืองโอช - Respawn 11 ชม. (Patch Notes 23 Sep 2026 Gigante II)
- บิ๊กค็อกคาทริซ / Big Cockatrice Lv.69 - แม่น้ำโบนาวิสตา / Bonavista River
- ค็อกคาทริซยักษ์ / Giant Cockatrice - ทุ่งริออน / Rion Prairie
- วิกเตอร์ / Victor (Mighty Victor) - ห้องสมุดใหญ่คฤหาสน์ทอร์เช่ / Torsche Mansion Grand Library
- เกรทฮิลล์ไจแอนท์ / Great Hill Giant - เวกัสฮาเวียร์ / Vegas Javier
- กริฟฟอน / Griffon - เวกัสฮาเวียร์ / Vegas Javier

> หมายเหตุ: Respawn เรโบลโด ยังไม่มีแพทช์ทางการยืนยัน ใช้ 3 ชม. เป็นค่าเริ่มต้น แก้ได้ด้วย `!บอสตั้งเวลา`

## 🚀 วิธีติดตั้ง (5 นาที)

### 1. สร้างบอทใน Discord Developer Portal
1. เข้า https://discord.com/developers/applications > New Application > ตั้งชื่อ เช่น `GEM Boss Timer`
2. เมนูซ้าย Bot > Reset Token > Copy Token เก็บไว้ (ห้ามส่งให้ใคร)
3. ในหน้า Bot เปิดสวิตช์:
   - MESSAGE CONTENT INTENT = ON
   - SERVER MEMBERS INTENT = ON (ถ้ามี)
4. เมนูซ้าย OAuth2 > URL Generator
   - Scopes: ติ๊ก `bot` + `applications.commands`
   - Bot Permissions: ติ๊ก `Send Messages`, `Embed Links`, `Mention Everyone`, `Read Message History`, `Use Slash Commands`
   - Copy URL ด้านล่าง เอาไปเปิดในเบราว์เซอร์เพื่อเชิญบอทเข้าเซิร์ฟเวอร์

### 2. รันบอทบนคอม / VPS
```bash
pip install -r requirements.txt
# สร้างไฟล์ .env จาก .env.example แล้วใส่ Token
cp .env.example .env
# เปิด .env แล้วใส่ DISCORD_TOKEN=Token_ที่ได้มา
python bot.py
```
ถ้ารันแล้วขึ้น `✅ ล็อกอินแล้ว` = สำเร็จ

### 3. ตั้งช่องแจ้งเตือน
ใน Discord พิมพ์ในช่องที่อยากให้บอทแจ้งเตือน:
```
!ตั้งช่องแจ้งเตือน
```

## 🎮 คำสั่งที่ใช้จริง

| คำสั่ง | ตัวอย่าง | ใช้ทำอะไร |
|---|---|---|
| `!บอส` | `!บอส` | ดูบอสทั้งหมด + เวลาเกิดถัดไป |
| `!บอสตาย <ชื่อบอส>` | `!บอสตาย hill` | บอสตายตอนนี้ เริ่มนับเวลาเกิดใหม่ |
| `!บอสตาย <ชื่อบอส> <เวลา>` | `!บอสตาย ค็อกคาทริซ 21:30` | บอสตายตอน 21:30 |
| `!บอสเกิด <ชื่อบอส> <เวลา>` | `!บอสเกิด hill 22:00` | รู้เวลาเกิดจากในเกม ตั้งเอง |
| `!บอสรีเซ็ต <ชื่อบอส>` | `!บอสรีเซ็ต hill` | ล้างเวลา |
| `!บอสตั้งเวลา <ชื่อบอส> <ชม.>` | `!บอสตั้งเวลา hill 4` | เปลี่ยน Respawn |
| `!บอสช่วย` | `!บอสช่วย` | ดูวิธีใช้ |

**ค้นหาบอสพิมพ์ไทยหรืออังกฤษก็ได้:** `hill`, `ฮิลล์`, `ค็อกคาทริซ`, `cockatrice`, `โกเลม`, `วิกเตอร์`, `กัปตัน`

**Slash Commands ก็ใช้ได้:** `/boss`, `/kill`, `/spawn`, `/reset`, `/helpboss`

## 🔔 การแจ้งเตือนอัตโนมัติ
บอทเช็กทุก 60 วินาที จะแจ้งในช่องที่ตั้งไว้:
- อีก 10 นาทีจะเกิด
- อีก 5 นาทีจะเกิด
- อีก 1 นาทีจะเกิด
- เกิดแล้ว! + ping @everyone (หรือ Role ที่ตั้งใน .env)

## 📁 ไฟล์ในโฟลเดอร์นี้
- `bot.py` - ตัวบอทหลัก
- `bosses.json` - รายชื่อบอส 13 ตัว + เมือง + แมป + Respawn (แก้ไฟล์นี้ได้)
- `boss_timers.json` - เวลาตาย/เกิดที่บันทึกไว้ (บอทสร้าง/อัปเดตเอง)
- `settings.json` - ช่องแจ้งเตือน
- `requirements.txt`
- `.env.example` - ตัวอย่างไฟล์ Token

## ⚠️ ข้อควรระวัง
- อย่าส่ง Token ให้ใคร - ใครได้ Token ไปจะคุมบอทได้
- ถ้าบอทไม่ตอบ: เช็กว่าเปิด MESSAGE CONTENT INTENT แล้วหรือยัง + บอทมีสิทธิ์ส่งข้อความในช่องนั้นไหม
- ถ้าเวลาผิด: บอทใช้เวลาเครื่องที่รัน ให้ตั้งเครื่องเป็นเวลาไทย Asia/Bangkok
- ข้อมูล Respawn: โคอิมบรา 5 ชม. / โอช 11 ชม. อิงจาก Patch Notes SEA ถ้าเซิร์ฟไทยเปลี่ยน ให้แก้ด้วย `!บอสตั้งเวลา`

## 💡 ทิปใช้งานกับเพื่อนในกิลด์
1. ให้คนเดียวเป็นคนพิมพ์ `!บอสตาย` ตอนบอสตาย จะได้ไม่นับซ้ำ
2. ตั้งช่อง `#boss-timer` แยกไว้เลย จะได้ไม่รกช่องคุยหลัก
3. ถ้าเล่นหลายแชแนล / หลายเซิร์ฟเวอร์ ให้ระบุชื่อบอส + เวลาให้ชัด


---

## 🌙 ทำยังไงให้บอทรัน 24 ชม.

### วิธีที่ 1: Render.com (ฟรี - แนะนำสุด ง่ายที่สุด)

1. เอาโฟลเดอร์นี้อัปขึ้น GitHub (สร้าง repo ใหม่ แล้ว upload ไฟล์ทั้งหมด)
2. เข้า https://dashboard.render.com > New > Web Service > Connect repo ที่อัปไป
3. ตั้งค่า:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python bot.py`
   - Region: Singapore
4. ในหน้า Environment เพิ่ม:
   - `DISCORD_TOKEN` = Token บอท
   - `KEEP_ALIVE` = `1`
5. กด Create Web Service - รอ 2-3 นาที บอทจะออนไลน์ 24 ชม.
   - Render ฟรีจะ sleep ถ้าไม่มีคนเรียก 15 นาที แต่ไฟล์ `keep_alive.py` จะเปิดเว็บให้ UptimeRobot มา ping ได้
   - แนะนำเพิ่ม UptimeRobot: https://uptimerobot.com สร้าง Monitor แบบ HTTP(s) ใส่ URL ของ Render (เช่น https://gem-boss-bot.onrender.com) ตั้งทุก 5 นาที = บอทจะไม่หลับเลย

### วิธีที่ 2: Railway.app (ฟรี $5 เครดิต/เดือน - ไม่หลับ)

1. เข้า https://railway.app > New Project > Deploy from GitHub
2. เลือก repo บอท
3. เพิ่ม Variable: `DISCORD_TOKEN` และ `KEEP_ALIVE=1`
4. Deploy อัตโนมัติ บอทจะรัน 24 ชม. ไม่ต้องตั้ง UptimeRobot

### วิธีที่ 3: VPS / คอมตัวเอง (ดีที่สุด เสถียรที่สุด)

ถ้ามี VPS Ubuntu หรือคอมเปิดทิ้งไว้:

```bash
# ติดตั้ง
sudo apt update && sudo apt install python3 python3-pip git -y
git clone <repo-url> gem_discord_bot
cd gem_discord_bot
pip3 install -r requirements.txt
cp .env.example .env
nano .env # ใส่ DISCORD_TOKEN

# รันด้วย Docker (แนะนำ)
docker-compose up -d

# หรือรันแบบ systemd (เปิดเครื่องใหม่ก็รันเอง)
sudo cp gem-boss-bot.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable gem-boss-bot
sudo systemctl start gem-boss-bot
sudo systemctl status gem-boss-bot
```

### วิธีที่ 4: รันบนมือถือ Android (ด้วย Termux - สำหรับคนไม่มีคอม)

1. โหลด Termux จาก F-Droid
2. ใน Termux พิมพ์:
```
pkg update && pkg install python git -y
pip install discord.py python-dotenv flask
```
3. ก๊อปไฟล์ bot.py ไปไว้ใน Termux แล้วรัน `python bot.py` (ต้องเปิด Termux ทิ้งไว้)

---

### 🔧 ไฟล์ใหม่ที่เพิ่มมาเพื่อรัน 24 ชม.
- `Dockerfile` + `docker-compose.yml` - สำหรับ Docker / VPS
- `keep_alive.py` - เปิดเว็บเล็กๆ ให้ Render / UptimeRobot ping
- `render.yaml` - ตั้งค่า Render แบบอัตโนมัติ
- `Procfile` - สำหรับ Railway / Heroku
- `gem-boss-bot.service` - สำหรับ Linux systemd

ถ้าใช้ Render อย่าลืมเปิด KEEP_ALIVE=1 ใน Environment ไม่งั้นบอทจะหลับ
