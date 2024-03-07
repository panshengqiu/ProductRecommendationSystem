# 导入所需的库
import pandas as pd
from py2neo import Graph, Node, Relationship
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# 连接neo4j数据库
graph = Graph('bolt://localhost:7687', auth=('neo4j', '15985527670'))

# 导入数学模块
import math
graph.run("MATCH (p:product)-[r:similar_to]->() DELETE r")
# 定义一个函数，用于计算两个向量的点积
def dot_product(vec1, vec2):
    # 初始化结果为0
    result = 0
    # 遍历两个向量的元素
    for i in range(len(vec1)):
        # 累加两个向量对应元素的乘积
        result += vec1[i] * vec2[i]
    # 返回结果
    return result

# 定义一个函数，用于计算一个向量的模长
def norm(vec):
    # 初始化结果为0
    result = 0
    # 遍历向量的元素
    for i in range(len(vec)):
        # 累加向量元素的平方
        result += vec[i] ** 2
    # 对结果开根号
    result = math.sqrt(result)
    # 返回结果
    return result

import jieba.posseg as pseg
# 定义一个函数，用于计算两个文本的余弦相似度
def cosine_similarity(str1, str2):
    # 使用jieba进行中文分词，并获取词性
    words1 = pseg.cut(str1)
    words2 = pseg.cut(str2)
    # 创建一个空集合，用于存放词汇表
    word_set = set()
    # 遍历两个文本的词语
    for word, flag in words1:
        # 将词语添加到集合中
        word_set.add(word)
    for word, flag in words2:
        # 将词语添加到集合中
        word_set.add(word)
    # 将集合转换为列表
    word_list = list(word_set)
    # 创建两个空列表，用于存放向量
    vec1 = []
    vec2 = []
    # 遍历词汇表中的词语
    for word in word_list:
        # 计算词语在第一个文本中的出现次数
        count1 = str1.count(word)
        # 将次数添加到第一个向量中
        vec1.append(count1)
        # 计算词语在第二个文本中的出现次数
        count2 = str2.count(word)
        # 将次数添加到第二个向量中
        vec2.append(count2)
    # 计算两个向量的点积
    dot = dot_product(vec1, vec2)
    # 计算两个向量的模长
    norm1 = norm(vec1)
    norm2 = norm(vec2)
    # 计算两个向量的余弦值
    cos = dot / (norm1 * norm2)
    # 返回余弦值
    return cos


# 从数据库中获取所有的product节点
products = graph.run("MATCH (p:product) RETURN p").data()
# 创建一个空的列表，用于存储产品的id和name
data = []
# 遍历所有的product节点，将id和name添加到列表中
for product in products:
    node_name = product['p']['name']
    data.append(node_name)

# 导入itertools模块
import itertools
# 获取字符串列表中的所有组合
combinations = itertools.combinations(data, 2)

# 遍历所有的组合
for pair in combinations:
    # 获取两个字符串
    str1 = pair[0]
    str2 = pair[1]
    # 计算两个字符串的相似度
    similarity = cosine_similarity(str1, str2)
    # 打印结果
    print(f"相似度({str1}, {str2}) = {similarity}")
    if similarity > 0.62:
        # 查询两个产品的节点
        product1 = graph.run(f"MATCH (p:product) WHERE p.name = '{str1}' RETURN p").data()[0]['p']
        product2 = graph.run(f"MATCH (p:product) WHERE p.name = '{str2}' RETURN p").data()[0]['p']

        # 创建相似关系，并将相似度作为属性
        relation = Relationship(product1, 'similar_to', product2, similarity=float(similarity))

        # 将相似关系添加到图谱中
        graph.create(relation)

