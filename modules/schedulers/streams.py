import re
import pendulum
import aiohttp

from modules.schedulers.base import Scheduler, ReminderEvent
from modules.utils import timediff
from constants import STOVE_API

class LiveStreamScheduler(Scheduler):
    """Event reminders for official live streams"""
    type = 'livestream'

    async def _fetch_stove_articles (self, count = 1):
        url = f'{STOVE_API}/ArticleSearchList'
        args = {"cafe_key":"epicseven","channel_key":"global","board_key":"all","query":"livestream","page":1,"size":count,"search_type":"TITLE","display_opt":"usertag_on,html_remove","direction":"latest","headline_nos":[],"not_headline_nos":[],"view_type":"list","version":2}
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=args) as r:
                return await r.json()

    def _parse_schedule (self, article) -> pendulum.DateTime:
        try:
            s = article['content'].split('Schedule: ')[1].split(' 2.')[0]
        except IndexError:
            return None
        dt_matcher = re.compile(r'(\d+\.\d+\.\d+) \(.*\) (\d+:\d+) (.*)')
        matched = dt_matcher.match(s)
        if matched is None or len(matched.groups()) == 0:
            return None
        date, time, tz = matched.groups()
        dt = f'{date} {time}'
        return pendulum.from_format(dt, 'YYYY.MM.DD HH:mm', tz=tz)

    def _parse_details (self, article):
        try:
            d = list(map(str.strip, article['content'].split('2. Details ')[1].split(' 3.')[0].split('-')))
            while '' in d:
                d.remove('')
            return {
                'title': article['title'],
                'details': d
            }
        except:
            return {
                'title': article['title'],
                'details': ''
            }

    async def next_datetime (self) -> pendulum.DateTime:
        a = await self._fetch_stove_articles()
        dt = self._parse_schedule(a['context']['article_list'][0])
        if dt is None:
            return None
        else:
            return dt.add(seconds=self.priority)

    async def next (self):
        a = await self._fetch_stove_articles()
        article = a['context']['article_list'][0]
        dt = self._parse_schedule(article)
        if dt is None or dt < pendulum.now(dt.timezone):
            return None
        dta = dt.add(seconds=self.priority)
        details = self._parse_details(article)
        return ReminderEvent(
            self.type,
            dta,
            timediff(dta),
            details['title'],
            '\n'.join([f'- {i}' for i in details['details']]),
            f'Hello! There should be a live stream starting: {details["title"]}. Check out the E7 Twitch or YouTube to watch and look out for surveys with rewards!'
        )
