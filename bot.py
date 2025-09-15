import discord
from discord.ext import commands
import asyncio
import os

from flask import Flask
from threading import Thread

app = Flask('')


@app.route('/')
def home():
    return "봇이 잘 작동 중이에요!"


def run():
    app.run(host='0.0.0.0', port=8080)


def keep_alive():
    t = Thread(target=run)
    t.start()


intents = discord.Intents.all()
bot = commands.Bot(command_prefix=".", intents=intents)


# 닫기 버튼 뷰
class CloseButton(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="티켓 닫기",
                       style=discord.ButtonStyle.gray,  # ButtonStyle.black은 없음
                       emoji="<a:a9:1413823289771561040>")
    async def close_ticket(self, interaction: discord.Interaction,
                           button: discord.ui.Button):
        await interaction.response.send_message("티켓을 닫는 중입니다...", ephemeral=True)
        await asyncio.sleep(2)
        await interaction.channel.delete()


# 티켓 패널 생성 함수
async def create_ticket_panel(ctx,
                              panel_title,
                              options: dict,
                              category,
                              embed_color=0xFFD1DC,
                              author_icon=""):

    class TicketDropdown(discord.ui.Select):

        def __init__(self):
            select_options = [
                discord.SelectOption(label=label,
                                     value=label,
                                     emoji=options[label].get("emoji"))
                for label in options
            ]
            super().__init__(placeholder=" 원하는 항목을 선택해주세요!",
                             options=select_options,
                             min_values=1,
                             max_values=1)

        async def callback(self, interaction: discord.Interaction):
            label = self.values[0]
            data = options[label]

            if not category or not isinstance(category,
                                              discord.CategoryChannel):
                await interaction.response.send_message("❌ 카테고리를 찾을 수 없습니다.",
                                                        ephemeral=True)
                return

            user_name = interaction.user.name.replace(" ", "-").lower()
            topic = label

            # 이모지 및 공백 제거 (필요시)
            for emoji in ["🚨", " ", "🧡", "🩷", "💙", "🩵"]:
                topic = topic.replace(emoji, "")
            topic = topic.strip()

            channel_name = f"{user_name}의-{topic}".replace(" ", "-").lower()

            overwrites = {
                interaction.guild.default_role:
                discord.PermissionOverwrite(view_channel=False),
                interaction.user:
                discord.PermissionOverwrite(view_channel=True,
                                            send_messages=True,
                                            read_message_history=True)
            }

            for role_id in data.get("roles", []):
                role = interaction.guild.get_role(role_id)
                if role:
                    overwrites[role] = discord.PermissionOverwrite(
                        view_channel=True,
                        send_messages=True,
                        read_message_history=True)

            for user_id in data.get("users", []):
                member = interaction.guild.get_member(user_id)
                if member:
                    overwrites[member] = discord.PermissionOverwrite(
                        view_channel=True,
                        send_messages=True,
                        read_message_history=True)

            ticket_channel = await interaction.guild.create_text_channel(
                name=channel_name, overwrites=overwrites, category=category)

            embed = discord.Embed(
                title=" 티켓이 생성되었어요!",
                description=
                f"{interaction.user.mention}님, 잠시만 기다려주세요. 담당자가 곧 도와드릴게요!",
                color=embed_color)
            embed.set_footer(text="문의해주셔서 감사합니다!")

            await ticket_channel.send(embed=embed, view=CloseButton())
            await interaction.response.send_message(
                f"티켓이 생성되었습니다 {ticket_channel.mention}", ephemeral=True)

    class TicketView(discord.ui.View):

        def __init__(self):
            super().__init__(timeout=None)
            self.add_item(TicketDropdown())

    embed = discord.Embed(title=panel_title,
                          description=" 아래 메뉴에서 원하는 항목을 선택하여 티켓을 생성해주세요!",
                          color=embed_color)
    embed.set_author(name="말랑이 티켓봇 ")
    embed.set_footer(text="말랑코튼 전용 티켓함")

    await ctx.send(embed=embed, view=TicketView())


# 각 패널별 역할/유저 ID와 이모지 포함 예시


@bot.command()
async def 신고함(ctx):
    category = ctx.channel.category
    if not category:
        await ctx.send("❌ 이 채널은 카테고리 안에 있어야 합니다!")
        return

    options = {
        "신고함": {
            "emoji": "🚨",
            "roles": [1413530966340927640],
            "users": []
        }
    }
    await create_ticket_panel(ctx,
                              "말랑포켓 문의센터",
                              options,
                              category,
                              embed_color=0xFFD1DC)


@bot.command()
async def 하류(ctx):
    category = ctx.channel.category
    if not category:
        await ctx.send("❌ 이 채널은 카테고리 안에 있어야 합니다!")
        return

    options = {
        "하류 문의사항": {
            "emoji": "<:b4:1413825908594315364>",
            "roles": [],
            "users": [1409169549819121839]
        },
        "하류 구매하기": {
            "emoji": "<:b4:1413825908594315364>",
            "roles": [],
            "users": [1409169549819121839]
        }
    }
    await create_ticket_panel(ctx,
                              "<a:a2:1413823326689693737> 하류 티켓함",
                              options,
                              category,
                              embed_color=0xC6E2FF)


@bot.command()
async def 유메(ctx):
    category = ctx.channel.category
    if not category:
        await ctx.send("❌ 이 채널은 카테고리 안에 있어야 합니다!")
        return

    options = {
        "유메 문의사항": {
            "emoji": "<:b2:1413825915900657664>",
            "roles": [],
            "users": [1016659263055216661]
        },
        "유메 구매하기": {
            "emoji": "<:b2:1413825915900657664>",
            "roles": [],
            "users": [1016659263055216661]
        }
    }
    await create_ticket_panel(ctx,
                              "<a:a6:1413823303717617735> 유메 티켓함",
                              options,
                              category,
                              embed_color=0xE0BBE4)


@bot.command()
async def 토끼(ctx):
    category = ctx.channel.category
    if not category:
        await ctx.send("❌ 이 채널은 카테고리 안에 있어야 합니다!")
        return

    options = {
        "토끼 문의사항": {
            "emoji": "<:01:1413855049179992194>",
            "roles": [],
            "users": [965997368975712356]
        },
        "토끼 구매하기": {
            "emoji": "<:01:1413855049179992194>",
            "roles": [],
            "users": [965997368975712356]
        }
    }
    await create_ticket_panel(ctx,
                              "<a:a8:1413823294104408134> 토끼 티켓함",
                              options,
                              category,
                              embed_color=0xFFDAC1)


@bot.command()
async def 몽글몽글(ctx):
    category = ctx.channel.category
    if not category:
        await ctx.send("❌ 이 채널은 카테고리 안에 있어야 합니다!")
        return

    options = {
        "몽글몽글 문의사항": {
            "emoji": "<:b3:1413825911312355388>",
            "roles": [],
            "users": [672060781289799702]
        },
        "몽글몽글 구매하기": {
            "emoji": "<:b3:1413825911312355388>",
            "roles": [],
            "users": [672060781289799702]
        }
    }
    await create_ticket_panel(ctx,
                              "<a:a5:1413823308373295114> 몽글몽글 티켓함",
                              options,
                              category,
                              embed_color=0xB5EAEA)

@bot.command()
async def 역지(ctx, member: discord.Member):
    role_id = 1413577757409153155  # 부여할 역할 ID
    role = ctx.guild.get_role(role_id)
    if not role:
        await ctx.send("❌ 역할을 찾을 수 없습니다.")
        return

    # 허용 역할 ID (명령어 사용 가능 역할)
    allowed_role_ids = [1413547785902620844]  # 여기에 허용할 역할 ID 넣기

    # 권한 체크
    author_roles = [r.id for r in ctx.author.roles]
    if (not ctx.author.guild_permissions.manage_roles and 
        not any(rid in allowed_role_ids for rid in author_roles)):
        await ctx.send("❌ 이 명령어를 사용할 권한이 없습니다.")
        return

    try:
        await member.add_roles(role)
        await ctx.send(f"{member.mention}님 `{role.name}`지급 완료! ")
    except discord.Forbidden:
        await ctx.send("❌ 권한이 부족해서 역할을 부여할 수 없습니다.")
    except Exception as e:
        await ctx.send(f"오류가 발생했습니다: {e}")


# 환경변수에서 토큰 불러오기
TOKEN = os.getenv("TOKEN__")

keep_alive()
bot.run(TOKEN)













