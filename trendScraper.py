from selenium import webdriver
import time
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from queue import Queue
import pandas as pd 
import os
import csv

#this is the node class that we will create the tree from 
class Node(object):
    def __init__(self, data):
        self.data = data
        self.children = []

    def add_child(self, obj):
        self.children.append(obj)
    def has_children(self):
        return len(self.children) > 0

        

PATH = "chromedriver.exe"
options = webdriver.ChromeOptions()
options.enable_downloads
service = Service(executable_path=PATH)
driver = webdriver.Chrome(service=service, options=options)
wait = WebDriverWait(driver=driver, timeout=10, poll_frequency=1)

def call_trends (keyword): #method call takes the browser back to trends main page
    driver.get("https://trends.google.com")
    driver.maximize_window()
    driver.implicitly_wait(1)
    element = driver.find_element(By.ID, 'i7')
    time.sleep(3)
    element.clear()
    element.send_keys(keyword)
    element.send_keys(Keys.ENTER)
    

def fetch_related_queries(keyword):
    call_trends(keyword)
    wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "widget-template")))
    time.sleep(3)
    widgets = driver.find_elements(By.CLASS_NAME, "widget-template")[4]
    btn = widgets.find_element(By.XPATH, "/html/body/div[2]/div[2]/div/md-content/div/div/div[4]/trends-widget/ng-include/widget/div/div/div/widget-actions/div/button[1]")
    btn.click()
    time.sleep(3)
    file_path = "C:/Users/eric0/Downloads/relatedQueries.csv" #replace with whatever your default download directory is
    related_queries = pd.read_csv(file_path, delimiter="^", encoding='utf-8') 
    rq_list = related_queries.values.tolist()[1:]
    for i in range(len(rq_list)):
        rq_list[i] = rq_list[i][0]
    x = 0
    y = 0
    new_list = []
    for i, j in enumerate(rq_list):
        if j == 'TOP':
            x = i
        if j == 'RISING':
            y = i
    for i in range(x + 1, y):
        if ',' in rq_list[i]:
            new_list.append(rq_list[i].split(',')[0])
            
            
    if os.path.exists(file_path):
    # Delete the file
        os.remove(file_path)
        print("File deleted successfully.")
    else:
        print("The file does not exist.")

    return new_list

    
    
def build_tree(keyword, depth=3):
    if depth == 0:
        return Node(keyword)

    # Fetch related queries for the keyword
    print(keyword)
    related_queries = fetch_related_queries(keyword)

    # Create a new node for the keyword
    node = Node(keyword)

    # Recursively build children nodes
    for query in related_queries:
        child_node = build_tree(query, depth - 1)
        node.add_child(child_node)

    return node

#prints out the tree in a breadth first manner
def breadth_first_traversal(root):
    keyword_list = [root.data]
    if not root:
        return
    queue = Queue()
    queue.put(root)
    while not queue.empty():
        node = queue.get()
        keyword_list.append(node.data)
        for child in node.children:
            queue.put(child)
            
    with open("keywords.csv", "w") as out:
        writer = csv.writer(out)
        writer.writerow(keyword_list)
            
            
            
root = build_tree("flu", depth=2)
breadth_first_traversal(root)

driver.close()