import ssl
import certifi

ssl_context = ssl.create_default_context(cafile=certifi.where())
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Gecko/20100101 Firefox/92.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Safari/537.36 Edge/91.0"
]

# 検討するパラメーターの設定
keyword = "ハリーポッター"  # 起点キーワード
max_user = 10  # 取得する熱量ユーザー数
sortfield_no = 0 # （人気順 = 0） or (新着順 = 1)
months = 2 # 過去何ヶ月分のデータを取得するか

search_min_page = 1 
search_max_page = 11 # ページ番号の範囲設定（例：1ページ目から10ページ目まで検索）

max_scrolls = 30 # スクロールの最大回数

# 起点キーワードに関連するサブワードのリスト
sub_keyword_list = [
    "ホグワーツ", "魔法", "魔法使い", "呪文", "ほうき",
    "ダンブルドア", "ハリー・ポッター", "ロン・ウィーズリー", "ハーマイオニー",
    "グリフィンドール", "スリザリン", "レイブンクロー", "ハッフルパフ",
    "クィディッチ", "ダイアゴン横丁", "杖", "ポーション", "禁じられた森",
    "闇の魔術", "不死鳥", "ホグワーツ特急", "舞台", "呪いの子",
]
