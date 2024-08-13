from collections import deque
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
import pandas as pd
import requests
import time

class GraphSearcher:
    def __init__(self):
        self.visited = set()
        self.order = []

    def visit_and_get_children(self, node):
        """ Record the node value in self.order, and return its children
        param: node
        return: children of the given node
        """
        raise Exception("must be overridden in sub classes -- don't change me here!")

    def dfs_search(self, node):
        self.visited = set()
        self.order = []
        self.dfs_visit(node)
    def dfs_visit(self, node):
        if node in self.visited:
            return
        self.visited.add(node)
        children = self.visit_and_get_children(node)
        for child in children:
            self.dfs_visit(child)

    def bfs_search(self, node):
        to_visit = deque([node])
        added = {node}
        while len(to_visit) > 0:
            curr_node = to_visit.popleft()
            children = self.visit_and_get_children(curr_node)
            for child in children:
                if child not in added:
                    to_visit.append(child)
                    added.add(child)


class MatrixSearcher(GraphSearcher):
    def __init__(self, df):
        super().__init__()
        self.df = df

    def visit_and_get_children(self, node):
        self.order.append(node)
        children = []
        for node, has_edge in self.df.loc[node].items():
            if has_edge:
                children.append(node)
        return children

class FileSearcher(GraphSearcher):
    def __init__(self):
        super().__init__()

    def visit_and_get_children(self, txt):
        lines = []
        with open("file_nodes/" + str(txt)) as file:
            for line in file:
                lines.append(line)
        self.order.append(lines[0].replace("\n", ""))
        return lines[1].replace("\n", "").split(",")
    
    def concat_order(self):
        return "".join(self.order)

class WebSearcher(GraphSearcher):
    def __init__(self, driver):
        super().__init__()
        self.driver = driver
        self.htmlList = []
        
    def visit_and_get_children(self, url):
        self.order.append(url)
        self.htmlList.append(pd.read_html(url)[0])
        self.driver.get(url)
        children = []
        for a_element in self.driver.find_elements("tag name", "a"):
            children.append(a_element.get_attribute("href"))
        return children
    
    def table(self):
        return pd.concat(self.htmlList, ignore_index=True)

def reveal_secrets(driver, url, travellog):
    password = "".join(map(str, travellog["clue"].values.tolist()))
    driver.get(url)
    text = driver.find_element("id", "password-textbox")
    button = driver.find_element("id", "submit-button")
    text.send_keys(password)
    button.click()
    time.sleep(2)
    locationButton = driver.find_element("id", "location-button")
    locationButton.click()
    time.sleep(2)
    imageURL = driver.find_element("id", "image").get_attribute("src")
    response = requests.get(imageURL)
    with open("Current_Location.jpg", "wb") as file:
        file.write(response.content)
    return driver.find_element("id", "location").text


