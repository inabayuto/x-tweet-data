import os

def create_folder(folder_name):
    """
    指定したフォルダ名のフォルダを作成する関数
    """
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)