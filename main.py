import os
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import aiohttp
import discord
from discord.ext import commands
from discord import app_commands

from alive import server_on

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

GUILD_ID = 1275651444669681685  # เปลี่ยนเป็น ID ของเซิร์ฟเวอร์
CHANNEL_ID = 1275870288277405749  # เปลี่ยนเป็น ID ของช่องข้อความ

async def fetch_image(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.read()

async def create_welcome_image(profile_image_bytes, username, text, background_url, additional_text=None):
    # โหลดภาพพื้นหลังจาก URL
    background_bytes = await fetch_image(background_url)
    background = Image.open(BytesIO(background_bytes)).convert('RGBA')
    
    width, height = background.size
    draw = ImageDraw.Draw(background)

    # เปิดรูปโปรไฟล์
    profile_image = Image.open(BytesIO(profile_image_bytes)).convert('RGBA')
    
    # ขนาดใหม่ของรูปโปรไฟล์
    profile_image_size = (400, 400)  # ขนาดใหม่ที่ต้องการ
    profile_image = profile_image.resize(profile_image_size, Image.LANCZOS)

    # สร้างมาสก์วงกลมสำหรับรูปโปรไฟล์
    mask = Image.new('L', profile_image_size, 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.ellipse((0, 0, profile_image_size[0], profile_image_size[1]), fill=255)
    profile_image.putalpha(mask)

    # วางรูปโปรไฟล์ลงบนพื้นหลัง
    profile_position = ((width - profile_image_size[0]) // 2, (height - profile_image_size[1]) // 2 - 50)
    background.paste(profile_image, profile_position, profile_image)

   # เพิ่มกรอบรูปโปรไฟล์
    border_color = (25, 25, 112)  
    border_width = 10
    border_draw = ImageDraw.Draw(background)
    border_draw.ellipse(
        [profile_position[0] - border_width, profile_position[1] - border_width,
         profile_position[0] + profile_image_size[0] + border_width,
         profile_position[1] + profile_image_size[1] + border_width],
        outline=border_color, width=border_width
    )

    # เพิ่มข้อความ
    try:
        font = ImageFont.truetype("font.otf", 100)  # ขนาดฟอนต์หลัก
        small_font = ImageFont.truetype("font.otf", 60)  # ขนาดฟอนต์สำหรับชื่อ
       
    except IOError:
        font = ImageFont.load_default()
        small_font = ImageFont.load_default()
     

    # ข้อความหลัก
    text_position = (width // 2, height // 2 + 220)
    draw.text(text_position, text, font=font, fill=(255, 255, 255, 255), anchor='mm')

    # ชื่อผู้ใช้
    username_position = (width // 2, height // 2 + 300)
    draw.text(username_position, username, font=small_font, fill=(255, 255, 255, 255), anchor='mm')


    return background


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')


@bot.event
async def on_member_join(member):
    if member.guild.id == GUILD_ID:
        channel = bot.get_channel(CHANNEL_ID)
        if channel:
            profile_image_url = member.avatar.url
            profile_image_bytes = await fetch_image(profile_image_url)
            background_url = "https://cdn.discordapp.com/attachments/1276433865375879199/1276433907394547724/954407-1280x720.png?ex=66c98336&is=66c831b6&hm=70b5ab475db8c7605a8c386a583932c1a244ee1a7cd8fc24faf6ec56c601c6ad&"  # URL ของภาพพื้นหลังรูป welcome
            welcome_image = await create_welcome_image(
                profile_image_bytes, 
                member.name, 
                "Welcome", 
                background_url,
               
            )
            with BytesIO() as buf:
                welcome_image.save(buf, format='PNG')
                buf.seek(0)
                file = discord.File(fp=buf, filename='welcome.png')
                await channel.send(f'{member.mention} has joined the server! You are our  {len(member.guild.members)} Member!', file=file)

@bot.event
async def on_member_remove(member):
    if member.guild.id == GUILD_ID:
        channel = bot.get_channel(CHANNEL_ID)
        if channel:
            profile_image_url = member.avatar.url
            profile_image_bytes = await fetch_image(profile_image_url)
            background_url = "https://i.pinimg.com/originals/f9/a6/ee/f9a6ee9b22ee3fcd960760521c64135c.png"  # URL ของภาพพื้นหลัง รูป leave
            leave_image = await create_welcome_image(
                profile_image_bytes, 
                member.name, 
                "Sayanara", 
                background_url,
                
            )
            with BytesIO() as buf:
                leave_image.save(buf, format='PNG')
                buf.seek(0)
                file = discord.File(fp=buf, filename='sayanara.png')
                await channel.send(f'sayanara {member.mention} We have {len(member.guild.members) - 1} member left.', file=file)


@bot.tree.command(name="say", description="Send a text image")
async def say(interaction: discord.Interaction, message: str):
    text_image = create_image_from_text(message)
    with BytesIO() as buf:
        text_image.save(buf, format='PNG')
        buf.seek(0)
        file = discord.File(fp=buf, filename='text_image.png')
        await interaction.response.send_message(file=file)

 
@bot.event    # สถานะสตรีม
async def on_ready():
    streaming_activity = discord.Streaming(
        name="Dev by Nattapat2871",
        url="https://www.twitch.tv/nattapat2871_"
    )
    await bot.change_presence(activity=streaming_activity)

server_on()


bot.run(os.getenv('TOKEN'))
