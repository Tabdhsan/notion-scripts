from pprint import pprint
from notion.client import NotionClient
from notion_cookie import cookie

client = NotionClient(token_v2=cookie)
test_url = "https://www.notion.so/notion-test-page-016e708bebed482a97dcfab33d83a435"

media_url = "https://www.notion.so/8352e1aaf48944bbb6d5f341eb4eb9f6?v=0d38dbd28c944bb0bc7cd30b2c82f71e"

# Replace this URL with the URL of the page you want to edit
page = client.get_block(media_url)
# print("The old title is:", page.title)

collectionViewPageBlock = page
db = page.collection
print(db.get_rows())
