import re, string
import emoji
import cn2an


def num2char_simple(text):
    text = re.sub('1','一',text)
    text = re.sub('2','二',text)
    text = re.sub('3','三',text)
    text = re.sub('4','四',text)
    text = re.sub('5','五',text)
    text = re.sub('6','六',text)
    text = re.sub('7','七',text)
    text = re.sub('8','八',text)
    text = re.sub('9','九',text)
    text = re.sub('0','零',text)
    return text

def product2char(text):
    # HTC A74型號
    # F1.8 的望遠鏡頭
    pos = [(m.start(0), m.end(0)) for m in re.finditer(r'(\d+)([a-z|A-Z]+)(\d?)', text)]
    pos += [(m.start(0), m.end(0)-1) for m in re.finditer(r'([a-z|A-Z]+)(\d+)([^\.])', text)]
    text_split = list(text)
    for s, e in pos:
        text_split[s:e] = num2char_simple(text[s:e])
    text = ''.join(text_split)
    return text

def date2char(text):
    text = re.sub(r'([^\d\.])?(\d{1,2})(/)(\d{1,2})([^\.\d])', r'\1\2月\4\5', text)
    pos = [(m.start(0), m.end(0)) for m in re.finditer(r'20\d\d', text)]
    text_split = list(text)
    for s, e in pos:
        text_split[s:e] = num2char_simple(text[s:e])
    text = ''.join(text_split)
    return text

def unit2char(text):
    text = re.sub(r'([\d\s]+)(cm)',r'\1公分', text)
    text = re.sub(r'([\d\s]+)(m)',r'\1公尺', text)
    text = re.sub(r'mAh',r'毫安培', text)
    text = re.sub(r'Hz', r'赫茲', text)
    text = re.sub(r'\+', r'加', text)
    text = re.sub(r'([\d\s])(×)([\d\s])', r'\1乘\3', text)
    return text

def num2char(text):
    text = re.sub(r'(\d)(,)(\d)',r'\1\3', text)
    text = re.sub(r'(\d)([:|：])(\d)',r'\1比\3',text)
    text = re.sub(r'(\d)(\.)([一二三四五六七八九零])([a-zA-Z])',r'\1點\3\4', text)
    text = re.sub(r'([^\d\.])(2)(號)',r'\1二\3',text)
    text = re.sub(r'第(2)([^\d\.])',r'第二\2',text)
    text = re.sub(r'([^\d\.\s])(2)([^\d\.\s])',r'\1兩\3',text)
    text = cn2an.transform(text, "an2cn")
    text = re.sub(r'二([百千萬億兆])',r'兩\1',text)
    text = re.sub(r'点',r'點',text)
    text = re.sub(r'负',r'負',text)
    text = re.sub(r'万',r'萬',text)
    text = re.sub(r'亿',r'億',text)
    return text

def rm_spaces(text):
    text = re.sub(r'([a-z|A-Z])(\s+)([a-z|A-Z])', r'\1|\3',text)
    text = re.sub(r'\s+|\n+|\t+',r'|',text)
    text = re.sub(r'[|]+',r'|',text)
    return text

def rm_punctuation(text):
    text = re.sub(r'[/‘’“”【】『』「」（）《》<>＂\[\]\(\)\{\}]','',text)
    text = re.sub(r'[\.；～！，、？。]+','|',text)
    text = re.sub(r'[;~!,?]+','|',text)
    text = re.sub(r'[^\u4e00-\u9fff\|\sa-zA-Z\u3105-\u3129\u02c7\u02cb\u02ca]',r'',text)
    return text

def rm_speaker(text):
    text = re.sub(r'^[a-zA-Z\u4e00-\u9fff]+[:：︰]',r'',text)
    text = re.sub(r'(滴妹|菜喳|DODO|林辰|劉沛|羅伊|胖茲|店員|蹲蹲|聖結石|瓜瓜)(︰|：|:)',r'|', text)
    return text
 
def rm_emoji(text):
    text = emoji.get_emoji_regexp().sub(r'|', text)
    text = re.sub(r'(XD|ww|QQ|OwOb|O.O|Q.Q)', r'|', text)
    return text

def rm_special(text):
    text = re.sub(r'&quot;', r'', text)
    text = re.sub(r'\(.+?\)', r'', text)
    text = re.sub(r'（.+?）', r'', text)
    text = re.sub(r'([A-Za-z0-9])(\.)(![0-9])', r'\3', text)
    # text = re.sub(r'(\.)', r'點', text)
    return text

def find_engWord(text):
    text = rm_speaker(text)
    text = rm_emoji(text)
    text = rm_special(text)
    head = re.match(r'[A-Z][a-z]{1,}', text)
    middle = re.search(r'[a-z]{2,}|[A-Z]{4,}', text)
    return head or middle

def clean(text):
    text = rm_speaker(text)
    text = rm_emoji(text)
    text = rm_special(text)
    text = date2char(text)
    text = unit2char(text)
    text = product2char(text)
    text = num2char(text)
    text = rm_punctuation(text)
    text = rm_spaces(text)
    if text == '|' or text == '':
        return ''
    text = text[1:] if text[0] == '|' else text
    text = text[:-1] if text[-1] == '|' else text
    return text

if __name__ == '__main__':
    # text = '2018年5月22號第2天深夜2點22分多花了2元買2.12個漢堡'
    # text = '傳出將會HTC A74型號搭載更大的 6.59 吋螢幕及15:3的比例'
    # text = '#而在台灣所上市的 A52 5G'
    # text = 'Ｃ：其他做法	'
    # text = '3. 大腦情緒：腸道菌會影響一些神經傳導物質'
    # text = '不對..應該是說回到&quot;乳牛繁殖牧場&quot;'
    # text = '( ˘•ω•˘ )'
    # text = 'Hello出發～'
    # text = '專用card(卡)10枚！還有保護膜所以外面那個是保護膜'
    # text = '那雖然 WHO 還沒有宣告這次的疫情屬於'
    # text = '呵呵w你在說什麼XD不是我在講什麼	'
    # text = '另外自從 A8 2018 之後'
    # text = '包含32、64、128以及256GB'
    # text = '雖然內建3300mAh電池'
    # text = 'Hi，出門！'
    # text = '同樣都是正面 2.5D 結合上背面 3D 的康寧玻璃'
    # text = '可以看到兩款手機分別搭載 6.5 吋以及 6.39 吋螢幕'
    # text = '對、很寬闊滴妹：感覺很孤寂的冷捏'
    # text = '想繼續看可以按訂閱哦蹲蹲:(ﾟДﾟ;)(ﾟДﾟ;)(ﾟДﾟ;)(ﾟДﾟ;)(ﾟДﾟ;)'
    # text = '啦啦啦啦啦啦ヽ(ﾟ∀。)ノ'
    # text = '欸 &quot;ㄅㄧㄤˋ&quot;*5'
    # text = '(黑夜暗潮洶湧)'
    # text = '還有...牙線、棉花棒、跟一些髮夾'
    # text = '就是…'
    # text = '就有 1000×100 × 100×3'
    # text = '菜喳︰紅鯉魚與綠鯉魚與你與驢'
    # text = '中文的怎麼了嗎||（怒）'
    # text = '對啊|真的欸瓜瓜:剛好一題就三個人不一樣'
    # text = '菜喳:LOVE IS ALWAYS FRESH 並不是'
    # text = '所以你要讓外面的人看到那個(LP數字)'
    # text = '往右滑的IPHONE欸'
    # text = 'A. 我想到就買、喜歡就刷，下手毫不猶豫'
    # text = '淦我被胡椒粒嗆到QwQ'
    # text = '單像素面積則有55m'
    # text = '好，那以上就是今天 577,771,234 訂閱的'
    # text = '此外每週一晚上 21:31~22:48'
    # text = "以及 F1.8 的望遠鏡頭"
    print(not find_engWord(text))
    print(clean(text))
    
