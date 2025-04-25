from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
from astrbot.api import logger
import requests

# 注册网易云点歌命令
@register("music", "YourName", "网易云点歌命令", "1.0.0.0")
class MusicPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        self.search_results = []

    async def initialize(self):
        logger.info("MusicPlugin initialized")

    @filter.command("music")
    async def handle_music_command(self, event: AstrMessageEvent):
        message = event.message_str
        parts = message.split(" ", 1)
        if len(parts) > 1:
            song_name = parts[1]
            search_results = await self.search_song(song_name)
            if search_results:
                response = "搜索结果:\n"
                for idx, song in enumerate(search_results, 1):
                    response += f"{idx}. {song['name']} - {song['artist']}\n"
                response += "请输入序号选择歌曲，例如: /select 1"
                self.search_results = search_results  # 保存搜索结果以供选择使用
            else:
                response = "未找到相关歌曲，请检查歌曲名称是否正确。"
        else:
            response = "请输入歌曲名称，例如: /music 晴天"

        yield event.plain_result(response)

    @filter.command("select")
    async def handle_select_command(self, event: AstrMessageEvent):
        message = event.message_str
        parts = message.split(" ", 1)
        if len(parts) > 1:
            try:
                selection = int(parts[1])
                if hasattr(self, 'search_results') and self.search_results:
                    if 1 <= selection <= len(self.search_results):
                        selected_song = self.search_results[selection - 1]
                        response = f"已选择: {selected_song['name']} - {selected_song['artist']}\n链接: {selected_song['url']}"
                    else:
                        response = "序号超出范围，请重新选择。"
                else:
                    response = "请先进行歌曲搜索。"
            except ValueError:
                response = "请输入有效的序号，例如: /select 1"
        else:
            response = "请输入序号，例如: /select 1"

        yield event.plain_result(response)

    async def search_song(self, song_name):
        api_url = f"https://api.网易云.com/search/suggest/web?keywords={song_name}"
        response = requests.get(api_url)
        if response.status_code == 200:
            data = response.json()
            if data.get("result", {}).get("songs"):
                self.search_results = []
                for song in data["result"]["songs"][:10]:
                    self.search_results.append({
                        "name": song["name"],
                        "artist": song["artists"][0]["name"],
                        "url": f"https://music.163.com/song/{song['id']}"
                    })
                return self.search_results
        return None

    async def terminate(self):
        logger.info("MusicPlugin terminated")