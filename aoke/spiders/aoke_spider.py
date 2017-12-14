# -*- coding: utf-8 -*-
# import os
import scrapy
import pdb
import datetime, time
# 初步 31.5 457 16555
# 特殊注意：
# 1 若看好方向《20分钟内进球，要赶快卖出
# 2 看好方向应该是针对初盘的，请尽量购买初盘盘口

# 要查询赔率的公司
info_days = 365  # 收集多少天的信息

bookmakerID = 84
# 50 pinnacle, 250 皇冠 84 澳门 19 必发交易所
# 算法思想
# 1.以澳门升降两个盘口的方向为support    √
# 2.20分钟内看好方向进球，要及时卖出   √
# 3 初盘，终盘赔率其一小于1.80的反方向不能选取
# result 3.5 12 1284
# 都小于
# result 4.5 13 1284 (得出都小于更优) √ （在没有4的情况）
# 其一小于1.80反方向不能选取，若都小于直接选取该场
# result 6 265 1284 不合理
# 4 若看好方向有》2.00的赔率出现，放弃该场比赛 √
# result 4.5 7 1284
# 可能的优化方向
# 1

# 算法判断参数
super_low_price = 1.80  # 超低水，＜
limit_max_price = 1.99  # 超高水, ＞

# 盘口字典
handicap_dict = {
    '平手': 0.0,
    '平手/半球': 0.25,
    '半球': 0.5,
    '半球/一球': 0.75,
    '一球': 1.0,
    '一球/球半': 1.25,
    '球半': 1.5,
    '球半/两球': 1.75,
    '两球': 2.0,
    '两球/两球半': 2.25,
    '两球半': 2.5,
    '两球半/三球': 2.75,
    '三球': 3.0,
    '三球/三球半': 3.25,
    '三球半': 3.5,
    '三球半/四球': 3.75,
    '四球': 4.0,
    '四球/四球半': 4.25,
    '四球半': 4.5,
    '四球半/五球': 4.75,
    '五球': 5.0
}


# 转换盘口到数字
def handicap2num(handicap_name):
    if handicap_name[0] == '受':
        result = -handicap_dict[handicap_name[1:]]
    else:
        result = handicap_dict[handicap_name]
    return result


# 根据净胜球和盘口计算盘口赛果 返回值：0 0.5 1 -0.5 -1
def score_my_algorithm(net_score, handicap):
    net_handicap = net_score - handicap
    if net_handicap >= 1.0:
        net_handicap = 1.0
    elif net_handicap <= -1.0:
        net_handicap = -1.0
    else:
        net_handicap = net_handicap * 2
    # 有时候会超过边界
    if net_handicap < -1:
        net_handicap = -1
    if net_handicap > 1:
        net_handicap = 1
    return net_handicap


# 升降盘判断函数
def compare_handicap(prev, current):
    result = 0
    if prev != current:
        # 转换 prev 盘口到数字
        if prev[0] == '受':
            prev_handicap = -handicap_dict[prev[1:]]
        else:
            prev_handicap = handicap_dict[prev]
        if current[0] == '受':
            current_handicap = -handicap_dict[current[1:]]
        else:
            current_handicap = handicap_dict[current]
        # 判断升降盘
        change_handicap = current_handicap - prev_handicap
        if abs(change_handicap) <= 0.25:
            if change_handicap > 0:
                result = 1
            elif change_handicap < 0:
                result = -1
    return result


# 处理赔率格式
def get_handicap_odds(price_text):
    if len(price_text) == 4:
        price_float = float(price_text)  # 主队赔率
    else:
        price_float = float(price_text[:-1])  # 主队赔率
    return price_float


# 比赛item
class match_Item(scrapy.Item):
    match_id = scrapy.Field()  # 比赛唯一ID
    host = scrapy.Field()  # 主队名称
    guest = scrapy.Field()  # 客队名称
    league_name = scrapy.Field()  # 联赛名
    start_time = scrapy.Field()  # 开始时间
    host_goal = scrapy.Field()  # 主队进球数
    guest_goal = scrapy.Field()  # 客队进球数
    is_end = scrapy.Field()  # 比赛是否已结束
    # 关于赔率
    macao_handicap = scrapy.Field()  # pinnacle 初始盘口名
    macaoBifa_support_direction = scrapy.Field()  # 该算法支持方向
    algorithm_score = scrapy.Field()  # 根据赛果评判算法，赢全+1，赢半+0.5 输同理


class SoccerSpider(scrapy.Spider):
    name = 'aoke'
    allowed_domains = ['www.okooo.com']
    nowadays = datetime.datetime.now().strftime("%Y-%m-%d")  # 获取当前日期
    # tomorrow = (datetime.datetime.now()+datetime.timedelta(days = +1)).strftime("%Y-%m-%d")     # 获取明天日期
    # 生成遍历的日期列表
    calendar_list = []
    # 遍历一年的数据
    for i in range(info_days):
        add_day = (datetime.datetime.now() + datetime.timedelta(days=-(i + 1))).strftime("%Y-%m-%d")
        add_url = "http://www.okooo.com/livecenter/football/?date=" + add_day
        calendar_list.append(add_url)
    start_urls = calendar_list

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url)

    def parse(self, response):
        # 获取进球数据
        # response.xpath('//script')[9].xpath('text()').extract()[0].replace('var initData = ', '').replace(' ','').strip().replace(
        #     "var controller = 'football';", '').replace("var LotteryType = 'IndexPage';", '').replace(
        #     "var MatchIDs = '1000344,1000806,999733';",'').replace("",'')

        for tr in response.css('div[id=livescore_table]').css('tr'):
            if len(tr.xpath('@id')) > 0:
                # 唯一比赛ID
                match_id = tr.xpath('@id').extract()[0].split('_')[-1]
                league_name = tr.xpath('@type').extract()[0]
                host_name = tr.xpath('td/a[@class="ctrl_homename"]/text()').extract()[0]
                guest_name = tr.xpath('td/a[@class="ctrl_awayname"]/text()').extract()[0]
                start_time = response.css('td[class=match_date]').xpath('text()').extract()[0].split('-')[0] + '-' + \
                             tr.xpath('td')[2].xpath('text()').extract()[0]
                # 主进球
                host_goal_text = tr.xpath('td[@class="show_score"]/a/b')[0].xpath('text()').extract()
                if len(host_goal_text) == 0:
                    host_goal = 0
                else:
                    host_goal = int(host_goal_text[0])
                # 客进球
                guest_goal_text = tr.xpath('td[@class="show_score"]/a/b')[2].xpath('text()').extract()
                if len(guest_goal_text) == 0:
                    guest_goal = 0
                else:
                    guest_goal = int(guest_goal_text[0])
                # 判断是否完场
                get_if_end = tr.xpath('td')[3].xpath('span/text()').extract()
                if len(get_if_end) > 0 and get_if_end[0] == '完':
                    is_end = True
                else:
                    is_end = False
                # 想要爬取赔率的公司ID
                bookmaker_id = bookmakerID
                match_url = 'http://www.okooo.com/soccer/match/' + match_id + '/ah/change/' + str(bookmaker_id)
                yield scrapy.Request(match_url, meta={'match_id': match_id, 'host': host_name, 'guest': guest_name,
                                                      'start_time': start_time, 'host_goal': host_goal,
                                                      'guest_goal': guest_goal, 'is_end': is_end,
                                                      'league_name': league_name}, callback=self.match_macao_parse)

    # 需要当前查询到的tr，还有host / guest
    def find_odds(self, tr, hg):
        # 根据主客不同，赔率所在td位置不同
        if hg == 'host':
            td_index = 2
        else:
            td_index = 4
        # 有时候赔率会在td下又一个span内,或者又一个span
        # 先查看tr 下有无赔率
        price_text = tr.xpath('td')[td_index].xpath('text()')
        # 如果=0则继续查找 tr span 下
        if len(price_text) == 0:
            price_text = tr.xpath('td')[td_index].xpath('span/text()')
            # 如果还是等于0 那继续查找 tr span span 下
            if len(price_text) == 0:
                price_text = tr.xpath('td')[td_index].xpath('span/span/text()')
        price = price_text.extract()[0][:4]
        return float(price)
    # 将赛前时间转化为赛前多少分钟
    def preTime2num(self, pre_time):
        try:
            hour = int(pre_time[2:5])
        except:
            hour = int(pre_time[2:4])
        # 分钟时间有的在5:7，有的在6:8
        try:
            min = int(pre_time[5:7])
        except:
            min = int(pre_time[6:8])
        pre_time_num = hour*60 + min
        return pre_time_num
    # 将多个support统一化
    # 若不一致则取0
    def unification_support(self,support_direction,last_change_support,begin_to_ultimate_handicap_change):
        # 最重要的是support_direction，last_change_support
        # begin_to_ultimate_handicap_change 起参考作用
        if support_direction == last_change_support:
            result = support_direction
        else:
            result = support_direction + last_change_support
        if (result != begin_to_ultimate_handicap_change) and result != 0:
            result = result + begin_to_ultimate_handicap_change
        return result

    # 先获取澳门赔率
    def match_macao_parse(self, response):
        handle_httpstatus_list = [404]
        if response.status in handle_httpstatus_list:
            print('访问404')
            return False
        odds_tr_len = len(response.xpath('//tbody')[0].xpath('tr')) - 2
        if odds_tr_len <= 0:
            return False

        # 声明match对象，保存当前比赛数据
        single_match_Item = match_Item()
        single_match_Item['match_id'] = response.meta['match_id']
        single_match_Item['host'] = response.meta['host']
        single_match_Item['guest'] = response.meta['guest']
        single_match_Item['start_time'] = response.meta['start_time']
        single_match_Item['host_goal'] = response.meta['host_goal']
        single_match_Item['guest_goal'] = response.meta['guest_goal']
        single_match_Item['is_end'] = response.meta['is_end']
        single_match_Item['league_name'] = response.meta['league_name']

        # 思想：找到澳门初盘到终盘升降两个盘口方向为support
        handicap_change_num = 0 # 记录盘口变化，升盘+1，降盘-1
        pre_handicap = '' # 保存前面查找的盘口
        # 终盘
        ultimate_handicap = ''
        ultimate_host = 0
        ultimate_guest = 0
        # 初盘
        begin_handicap = ''
        begin_host = 0
        begin_guest = 0

        count = 0
        tr_len = len(response.xpath('//tbody')[0].xpath('tr[@class=""]'))
        special_price = False   # 若出现特殊赔率就跳过该场
        support_deny_1_host = 0  # 用来deny support direction
        support_deny_1_guest = 0  # 用来deny support direction
        for tr in response.xpath('//tbody')[0].xpath('tr[@class=""]'):
            current_handicap = tr.xpath('td')[3].xpath('text()').extract()[0]
            current_host_price = float(self.find_odds(tr, 'host'))
            current_guest_price = float(self.find_odds(tr, 'guest'))
            # 有时候澳门赔率会出现特殊情况，特别大的情况要排除
            if current_host_price > 2.15 or current_guest_price > 2.15:
                special_price = True
                break
            # 若出现大于超高水的方向则不能support该方向
            if current_host_price > limit_max_price:
                support_deny_1_host = 1
            if current_guest_price > limit_max_price:
                support_deny_1_guest = 1
            # 终盘
            if count == 0:
                ultimate_handicap = current_handicap
                ultimate_host = current_host_price
                ultimate_guest = current_guest_price
            # 初盘
            if count == tr_len - 1:
                begin_handicap = current_handicap
                begin_host = current_host_price
                begin_guest = current_guest_price
            if pre_handicap != '':
                if current_handicap != pre_handicap:
                    # 因为是倒向遍历，所以pre - current
                    handicap_change_num += handicap2num(pre_handicap) - handicap2num(current_handicap)

            pre_handicap = current_handicap
            count += 1
        # 出现特殊赔率提前结束
        if special_price:
            return False
        # 判断初终盘水位：
        support_deny_2 = 0    # 用来deny support direction
        if (ultimate_host < super_low_price) and (begin_host < super_low_price):
            support_deny_2 = -1
        if (ultimate_guest < super_low_price) and (begin_guest < super_low_price):
            support_deny_2 = 1

        # 判断支持方向
        support_direction = 0
        if handicap_change_num >= 0.5:
            if (1 - support_deny_2) > 0:
                support_direction = 1
        elif handicap_change_num < -0.5:
            if (-1 - support_deny_2) < 0:
                support_direction = -1

        if support_direction != 0:
            # support_deny_1_host 和 support_deny_1_guest可能都取1
            if (support_direction == support_deny_1_host) or (-support_direction == support_deny_1_guest):
                support_direction = 0

        # 初步评分
        ultimate_handicap_num = handicap2num(ultimate_handicap)
        host_net_goal = single_match_Item['host_goal'] - single_match_Item['guest_goal']  # 主队净胜球
        net_handicap = score_my_algorithm(float(host_net_goal), ultimate_handicap_num)
        # mid = single_match_Item['match_id']
        # if mid == 945076 or mid == '945076':
        #     a = 1
        #     pdb.set_trace()
        # 根据判断方向给出本轮比赛算法最终得分
        match_algorithm_score = 0
        # 比赛结束才能评分
        if single_match_Item['is_end']:
            if support_direction == 1:
                match_algorithm_score = net_handicap
            elif support_direction == -1:
                match_algorithm_score = -net_handicap
        single_match_Item['macao_handicap'] = ultimate_handicap
        single_match_Item['macaoBifa_support_direction'] = support_direction  # 该算法支持方向
        single_match_Item['algorithm_score'] = match_algorithm_score  # 该算法本场比赛评分
        yield single_match_Item