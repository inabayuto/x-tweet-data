# %% ライブラリのインポート
import time
import urllib.parse
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException


import urllib.request
import os
from datetime import datetime
import nest_asyncio
import asyncio
from twikit import Client
from dotenv import load_dotenv
import pandas as pd
import sys

sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '..')))
from utils import parameter
from utils.utils import create_folder

# %%　driverのの初期設定
# Chrome オプションの設定（ヘッドレスモード）
options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

# %% システムにインストールされている chromedriver のパスを指定
# webdriver_managerでchromedriverを自動取得
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

# %% パラメータの指定
keyword = parameter.keyword
max_user = parameter.max_user
sub_keyword_list = parameter.sub_keyword_list
query = urllib.parse.quote(keyword)
url = f"https://search.yahoo.co.jp/realtime/search?p={query}&gm=w" 
driver.get(url)

# %% スクロール関数の定義
def scroll_to_elem(driver, elem):
    """
    指定された要素までスクロールする関数
    """
    try:
        actions = ActionChains(driver)
        actions.move_to_element(elem)
        actions.perform()
        time.sleep(0.1)
        return True
    except (NoSuchElementException, StaleElementReferenceException):
        return False

# %% もっと見るボタンを取得する関数
def find_show_more_button(driver):
    """
    もっと見るボタンを取得する関数
    """
    try:
        return driver.find_element(By.CLASS_NAME, 'More_More___s3p1')
    except NoSuchElementException:
        return None

# %% もっと見るボタンをクリックする関数
def click_show_more_button(driver):
    """
    もっと見るボタンをクリックする関数
    """
    try:
        find_show_more_button(driver).click()
        time.sleep(0.1)
        return True
    except NoSuchElementException:
        return False

# %% ツイート要素を取得する関数
def extract_tweet_elements(driver, max_user):
    """
    ツイート要素を取得する関数
    
    Args:
        driver (WebDriver): SeleniumのWebDriverインスタンス
        max_tweets (int): 取得するツイート要素の最大数

    Returns:
        list: 取得したツイート要素のリスト

    Notes:
        - 「もっと見る」ボタンが存在しないか、既に十分なツイートが取得された場合、追加読み込みを終了
    """
    # "もっと見る"ボタンをクリックして追加のツイートを取得
    while True:
        # ツイートコンテナ要素を取得
        tweet_elements = driver.find_elements(By.CLASS_NAME, 'Tweet_bodyContainer__ud_57')
        
        # 取得ツイート数が指定された数に達するか、もっと見るボタンがない場合は終了
        if len(tweet_elements) >= max_user or not find_show_more_button(driver):
            break
        
        # もっと見るボタンをクリック
        click_show_more_button(driver)
        
        # 指定回数スクロール（次のもっと見るボタンが出てくるまで）
        while True:
            # もっと見るボタンを取得
            show_more_button_element = find_show_more_button(driver)
            
            # もっと見るボタンまでスクロール
            scroll_to_elem(driver, show_more_button_element)
            
            # もっと見るボタンがないか、もっと見るボタンまでスクロール出来たら終了
            if not find_show_more_button(driver) or show_more_button_element == find_show_more_button(driver):
                break
    
    return tweet_elements[:max_user]


# メイン処理
if __name__ == "__main__":
    tweet_container_element = extract_tweet_elements(driver, max_user=100)

# %% ツイートのテキストを取得する関数
def extract_tweet_text(tweet_container_element):
    """
    ツイートのテキストを取得する関数
    """    
    try:
        # ツイートのテキスト要素を取得
        tweet_elements = tweet_container_element.find_element(By.CLASS_NAME, 'Tweet_bodyWrap__lhoVN')
        return tweet_elements.text
    except NoSuchElementException:
        return None

# %% data-cl-params属性を取得する関数
def extract_client_params(tweet_container_element):
    """
    data-cl-params属性を取得する関数
    """
    try:
        # ツイートのフッター要素を取得
        tweet_footer = tweet_container_element.find_element(By.CLASS_NAME, 'Tweet_footer__gF4gH')

        # tweet_footer内にあるdata-cl-params属性を持つ全てのリンク要素を取得
        cl_elements = tweet_footer.find_elements(By.XPATH, ".//a[@data-cl-params]")

        # 各リンク要素からクライアントパラメータの情報を抽出
        for cl_element in cl_elements:
            cl_params_str = cl_element.get_attribute("data-cl-params")
            
            # 条件：例として、"_cl_link:twtm;" が含まれているものを対象にする
            if "_cl_link:twtm;" in cl_params_str:
                # セミコロン区切りでパラメータを分解して辞書に変換
                pairs = cl_params_str.split(';')
                cl_params_dict = {}
                for pair in pairs:
                    if ':' in pair:
                        key, value = pair.split(':', 1)
                        cl_params_dict[key] = value
                return cl_params_dict
    except NoSuchElementException:
        return None

# %% ユーザーリンクを取得する関数
def extract_user_link(tweet_container_element):
    '''
    ユーザーリンクを取得する関数
    '''
    try:
        tweet_user_link_element = tweet_container_element.find_element(By.CLASS_NAME, 'Tweet_authorID__JKhEb')
        return tweet_user_link_element.get_attribute('href')
    except NoSuchElementException:
        return None

# %% スクリーンネームを取得する関数
def extract_screen_name(tweet_container_element):
    '''
    スクリーンネームを取得する関数
    '''
    try:
        tweet_screen_name_element = tweet_container_element.find_element(By.CLASS_NAME, 'Tweet_info__bBT3t')
        lines = tweet_screen_name_element.text.splitlines()
        if lines:
            screen_name = lines[0]
            return screen_name
    except NoSuchElementException:
        return None

# %% アカウント名を取得する関数
def extract_account_name(tweet_container_element):
    '''
    アカウント名を取得する関数
    '''
    try:
        tweet_account_name_element = tweet_container_element.find_element(By.CLASS_NAME, 'Tweet_info__bBT3t')
        lines = tweet_account_name_element.text.splitlines()
        if lines:
            account_name = lines[1]
            return account_name
    except NoSuchElementException:
        return None

# %% ツイート要素からユーザーIDとツイート本文を抽出する関数
def extract_tweet_records(tweet_elements: list, max_user: int, sub_keyword_list: list) -> list:
    """
    ツイート要素からユーザーID（twuid）とツイート本文を抽出する関数
    
    Args:
        tweet_elements (list): SeleniumのWebElementのリスト。
        sub_keyword_list (list): ツイート本文に含まれるべきサブキーワードのリスト。

    Returns:
        list: 条件を満たす各ツイートから抽出された{'user_id', 'tweet_text'}のレコードのリスト。最大20件。 
    """
    tweet_records = []
    
    for tweet_element in tweet_elements:
        # クライアントパラメータからユーザーIDを取得
        cl_params = extract_client_params(tweet_element)
        user_id = cl_params.get('twuid') if cl_params else None
        
        # ツイート本文の抽出
        tweet_text = extract_tweet_text(tweet_element)
        
        # サブキーワードリストのいずれかがツイート本文に含まれているかをチェック
        if tweet_text and any(sub in tweet_text for sub in sub_keyword_list):
            tweet_record = {
                    'user_id': user_id, # ユーザーid
                    'screen_name': extract_screen_name(tweet_element), # ユーザー名
                    'account_name': extract_account_name(tweet_element), # アカウント名
                    'tweet_text': tweet_text, 
            }
            tweet_records.append(tweet_record)
                
            # 20件に達したらループを終了
            if len(tweet_records) >= max_user:
                    break
    return tweet_records


# メイン処理
if __name__ == "__main__":
    extract_tweet_records = extract_tweet_records(tweet_container_element, max_user, sub_keyword_list)
    print(f"取得した関連ブログのリンク件数: {len(extract_tweet_records)}")
    for link in extract_tweet_records:
        print(link)
    driver.quit()

# %% .envファイルの内容を読み込む
load_dotenv('.env')

# 環境変数からユーザー名、メールアドレス、パスワードを取得
USERNAME = os.environ.get('USERNAME')
EMAIL = os.environ.get('EMAIL')
PASSWORD = os.environ.get('PASSWORD')

# イベントループの再利用を許可
nest_asyncio.apply()

# 古いcookies.json を削除
cookies_file = 'cookies.json'
if os.path.exists(cookies_file):
    os.remove(cookies_file)
    print("cookies.jsonを削除しました")

# Initialize client
client = Client('ja')

# %% ユーザーのツイートを取得する関数
async def get_user_tweets_by_id(extract_tweet_records: list) -> None:
    """
    指定したユーザーの最新20件のツイート情報を取得し、各ユーザー毎にCSVファイルに保存する関数

    引数として与えられたユーザーIDのリスト（extract_tweet_records）に対して、
    各ユーザーの最新20件のツイート情報を取得し、取得したツイート情報を個別のCSVファイルに保存

    Args:
        extract_tweet_records (list): ツイート情報を取得する対象ユーザーのIDリスト

    Returns:
        None

    Notes:
        - 保存先のフォルダ "./data/blog_data" が存在しない場合、自動的に作成される
        - 事前にクッキーのロードまたはログイン処理が実施され、取得後はログアウトされる
        - 取得処理において、タイムアウト（60秒）や認証エラーなどの例外はキャッチされ、該当ユーザーはスキップされる
    """
    current_date = datetime.today().strftime("%Y%m%d")

    # データを格納するフォルダ
    folder = "./tweets_data"
    create_folder(folder)

    # ループの外でログインまたはクッキーのロードを行う
    if os.path.exists(cookies_file):
        client.load_cookies(cookies_file)
    else:
        await client.login(
            auth_info_1=USERNAME,
            auth_info_2=EMAIL,
            password=PASSWORD,
        )
        client.save_cookies(cookies_file)
        
    user_ids = [record['user_id'] for record in extract_tweet_records]

    # 各ユーザーのツイートを取得し、個別のCSVファイルに保存
    for user_id in user_ids:
                
        try:
            tweets = await asyncio.wait_for(
                client.get_user_tweets(user_id, 'Tweets', count=20),
                timeout=300
            )
            
            # print(f"Retrieved tweets for user {user_id}: {tweets}")
            
            # ユーザーごとのツイート情報を格納するリスト
            user_tweet_records = []
            for tweet in tweets:
                tweet_record = {
                    'tweet_id': tweet.id,
                    'user_id': tweet.user.id,
                    'screen_name': tweet.user.screen_name,
                    'account_name': tweet.user.name,
                    'tweet_text': tweet.text,
                    'tweet_date': tweet.created_at,
                    'like': tweet.favorite_count,
                    'quote': tweet.quote_count,
                    'reply': tweet.reply_count,
                    'retweet': tweet.retweet_count,
                }
                user_tweet_records.append(tweet_record)
                
            # ツイートが存在すれば、ユーザーごとにCSVファイルへ保存
            if user_tweet_records:
                df = pd.DataFrame(user_tweet_records)
                csv_filename = f"tweets_{user_id}_{keyword}_{current_date}.csv"
                filepath = os.path.join(folder, csv_filename)
                
                with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                    df.to_csv(csvfile, index=False)
            
            return print("熱量ユーザーのデータソースの取得が完了しました")
                                                               
        except asyncio.TimeoutError:
            print(f'ユーザー {user_id} の取得がタイムアウトした場合はスキップ')
            continue 
        except Exception as e:
            if "Could not authenticate you" in str(e):
                print(f'ユーザー {user_id} の処理中にエラーが発生: {e}')
                continue
            else:
                print(f"Unexpected error for user {user_id}: {e}")
                continue

    # すべてのユーザー処理終了後にログアウト
    try:
        await client.logout()
    except Exception:
        pass

# メイン処理
if __name__ == "__main__":
    asyncio.run(get_user_tweets_by_id(extract_tweet_records))
# %%
