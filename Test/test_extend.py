import unittest
import re


class A:
    @classmethod
    def print(cls):
        print("A")


class B:
    @classmethod
    def print(cls):
        print("B")


class C(A):
    @classmethod
    def saw(cls):
        cls.print()


class D(B, C):
    @classmethod
    def saw(cls):
        cls.print()


class E(C, B):
    @classmethod
    def saw(cls):
        cls.print()


class TestExtend(unittest.TestCase):
    def test_extend(self):
        D.saw()  # B
        E.saw()  # A

    def test_re(self):
        ori = """\u200b21312313123​![image](https://3x.2xxxxx.com/siyuan/未命名_image_20240807134945_n4ues_1_2_1.png "@#@#!#"){: style='width: 765px;' parent-style='width: 775px;'}\u200b"""
        # 匹配整个资源文本 ![](https://xxx.xxx.com/siyuan/Nginx_image_20220512101137719.png)
        resource_pattern = r'!\[.*?\]\(.*?\)\s?'
        # 匹配markdown资源文本中的链接 https://xxx.xxx.com/siyuan/Nginx_image_20220512101137719.png
        resource_link_pattern = r'!\[.*?\]\((.*?)(?=\)| )\s?'
        resource = re.search(resource_pattern, ori).group()
        resource_link = re.search(resource_link_pattern, resource).group(1)
        print(resource, type(resource))
        print(resource_link, type(resource_link))
