# 导入py2neo和其他需要的相关包
from py2neo import Graph, Node, Relationship
import spacy
import jieba.posseg as pseg
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

import json
# 导入flask和相关的扩展
from flask import Flask, render_template, request

# 创建一个flask应用对象
app = Flask(__name__, static_folder='templates')

# 连接到图数据库，根据实际情况修改参数
graph = Graph("bolt://localhost:7687", auth=("neo4j", "15985527670"))

# 加载 spaCy 模型
nlp = spacy.load("en_core_web_sm")


# 定义一个路由，用于处理首页的请求
@app.route("/")
def index():
    # 从图数据库中获取product类型的节点信息，同时包括关系sold_by和相关商家节点的信息
    query = """
    MATCH (p:product)-[:sold_by]->(s:Shop)
    RETURN p, s.name AS seller_name limit 50
    """
    result = graph.run(query)

    # 处理查询结果，将节点信息转换为字典列表
    products = [{'product': record['p'], 'seller_name': record['seller_name']} for record in result]

    # 渲染模板，并将产品信息传递给模板
    return render_template('index.html', products=products, recommandation_product=[])


# 导入数学模块
import math

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
    if norm1 == 0 or norm2 == 0:
        return 0
    cos = dot / (norm1 * norm2)
    # 返回余弦值
    return cos

global query_list
global query_text


@app.route("/result")
def result():
    global query_text
    query_text = request.args.get("query")
    # 从数据库中获取所有的product节点
    # 获取每个产品节点的名称name
    type_list = graph.run("MATCH (p:product) RETURN DISTINCT p.category").data()

    product_type = []
    for item in type_list:
        type_name = item["p.category"]
        product_type.append(type_name)

    global query_list
    query_list = []
    for type_name in product_type:
        if type_name in query_text:
            query_list.append(type_name)

    fruit_key = ["水果","苹果","香蕉","梨","火龙果","葡萄","草莓","桃子","西瓜","李子","柠檬","芒果","菠萝","榴莲","木瓜","橙子","柚子","桑葚","蓝莓",
                 "猕猴桃","柿子","百香果","樱桃","枇杷","石榴","枸杞","山楂","椰子","荔枝","龙眼","山竹","杨梅","桂圆",
                 "橄榄","杨桃","蛋黄果","人心果","诺丽果","榴莲蜜","番石榴","木鳖果","龙功果","柑桔","沙糖桔","蜜桔","沃柑","皇帝柑","椪柑","耙耙柑","爱媛38号柑桔","贡桔",
                 "不知火丑桔","特早蜜桔","青见柑桔","茂谷柑","普早蜜桔","马水桔","南丰蜜桔","红美人柑桔","涌泉蜜桔","澳柑","芦柑","金桔","核桃","板栗","开心果","瓜子","榛子","银杏","松子","果仁","白果","坚果"]
    addKey(fruit_key,"水果")

    fitness_key = ["健身器材","健身", "跑步机", "椭圆机", "动感单车", "健身车", "划船机", "杠铃", "哑铃", "仰卧板", "史密斯架",
                   "自由深蹲架", "大龙门架", "弹力带", "拉力器", "瑜伽垫", "泡沫轴", "健身椅", "健身球", "飞鸟器",
                   "腹肌板", "腿部训练器"]
    addKey(fitness_key, "健身器材")

    cap_key = ["帽子","帽","头盔","头套"]
    addKey(cap_key, "帽子")

    trouser_key = ["裤子", "裤"]
    addKey(trouser_key,"裤子")

    man_wear_key = ["羽绒服","冬季","保暖","厚","衣服","衣","服装"]
    addKey(man_wear_key,"羽绒服")

    computer_key = ["笔记本","电脑"]
    addKey(computer_key,"电脑")

    ipad_key = ["ipad","平板"]
    addKey(ipad_key,"平板")

    earphone_key = ["蓝牙","耳机","蓝牙耳机"]
    addKey(earphone_key, "耳机")

    key_board = ["键盘","机械键盘"]
    addKey(key_board, "键盘")

    camera_key = ["相机","照相","照相机","拍照"]
    addKey(camera_key,"相机")

    subwoofer_key = ["低音炮","音响"]
    addKey(subwoofer_key, "低音炮")

    noodles_key = ["面","面条","泡面","康师傅","白象","兰州拉面","火鸡面"]
    addKey(noodles_key, "泡面")

    food_key = ["吃","食品"]
    addKey(food_key,"食品")

    office_key = ["本子","笔","椅子","公司","桌子"]
    addKey(office_key,"办公用品")

    study_key = ["书","学习","本子","本","学生","订书机","便利贴"]
    addKey(study_key, "学习用品")

    furniture_key = ["家具", "桌子", "椅子", "床", "沙发", "衣柜", "书架", "茶几", "电视柜", "餐桌", "梳妆台", "橱柜",
                     "床头柜", "屏风", "花架", "置物架", "挂衣架", "晾衣架", "鞋柜", "酒柜", "办公桌", "电脑桌",
                     "儿童桌椅", "阳台桌椅", "庭院家具", "户外家具", "吧台", "酒架", "餐椅", "电视架", "床垫", "折叠床",
                     "气垫床", "榻榻米", "休闲椅", "摇椅", "躺椅", "晾衣架", "藤椅", "藤床"]
    addKey(furniture_key, "家具")
    kitchenware_key = ["厨具", "锅", "锅具", "炒锅", "汤锅", "煎锅", "蒸锅", "炖锅", "砂锅", "炸锅", "火锅", "炊具",
                       "刀具", "砧板", "瓶子", "碗", "盘", "筷子", "勺子", "刀", "菜板", "砧板", "厨房垃圾桶",
                       "厨房置物架", "厨房小工具", "保鲜盒", "食品罐", "厨房地垫"]
    addKey(kitchenware_key,"厨具")
    vegetable_key = ["蔬菜", "菜", "青菜", "黄瓜", "西红柿", "茄子", "土豆", "白菜", "芹菜", "胡萝卜", "洋葱", "大蒜",
                     "生姜", "红椒", "绿椒", "黄椒", "花菜", "西兰花", "菜花", "南瓜", "丝瓜", "冬瓜", "苦瓜", "芋头",
                     "山药", "空心菜", "菠菜", "苋菜", "秋葵", "生菜", "菜心", "茼蒿", "荠菜", "油菜", "水芹", "白萝卜",
                     "红萝卜", "黄萝卜", "胡椒", "小葱", "大葱", "香葱", "韭菜", "香菜", "芫荽", "莴苣", "娃娃菜"]
    addKey(vegetable_key,"蔬菜")

    # 使用graph.run方法，执行一个Cypher语句，根据category属性的值在query_list中过滤出product节点
    result = graph.run("MATCH (p:product) WHERE p.category IN $query_list RETURN p", query_list=query_list).data()


    min_similarity = 0.55;
    products = []
    while True:
        for record in result:
            node = record['p']
            product_name = node['name']
            words = pseg.cut(query_text)  # 对query_text进行分词和词性标注
            nouns = ""  # 创建一个空字符串，用来存放名词
            for word, flag in words:  # 遍历分词和词性标注的结果
                if flag.startswith("n"):  # 如果词性以n开头，表示是名词
                    nouns += word  # 将名词添加到字符串中
            # 调用函数，使用名词字符串和产品名称计算余弦相似度
            similarity = cosine_similarity(str(nouns), str(product_name))

            # 如果相似度 >= 0.6 ，则将该产品加入到推荐列表中
            if similarity >= min_similarity:
                # 将该产品节点的商家Shop节点的名称查询出来
                query = """
                    MATCH (p:product)-[:sold_by]->(s:Shop)
                    WHERE p.name = $product_name 
                    RETURN p, s.name AS seller_name,s.shop_link AS shop_link
                    """
                # 将该产品加入到推荐列表中
                shop_rs = graph.run(query, product_name=product_name).data()
                print(f'shop_link_one:{shop_rs[0]["shop_link"]}')
                products.append({'product': node, 'seller_name': shop_rs[0]['seller_name'],'shop_link': shop_rs[0]["shop_link"]})
        if len(products) == 0 and min_similarity >= 0.25:
            min_similarity -= 0.067
            continue
        else:
            break


    recommandation_product = []
    for record in products:
        # 获取产品节点
        product_node_name = record['product']['name']
        # 定义查询语句，查找与该产品有similar_to关系的产品
        query = """
                MATCH (p:product)-[:similar_to]->(p1:product)-[:sold_by]->(s:Shop)
                WHERE p.name = $product_node_name and p1.category IN $query_list
                RETURN p1, s.name AS seller_name, s.shop_link AS shop_link
                """
        # 执行查询语句，返回结果
        recommandation_result = graph.run(query, product_node_name=product_node_name,query_list=query_list)
        temp = [{'product': record['p1'], 'seller_name': record['seller_name'],"shop_link":record["shop_link"]} for record in
                recommandation_result]
        # 依次将temp中的产品加入recommandation_product
        for record in recommandation_result:
            print(f'shop_link_two: {record["shop_link"]}')
        for item in temp:
            recommandation_product.append(item)
    # 返回结果
    from collections import OrderedDict
    # 使用OrderedDict进行去重，保留顺序
    unique_list = list(OrderedDict((tuple(d.items()), d) for d in recommandation_product).values())
    return render_template('index.html', products=products, recommandation_product=unique_list)


def addKey(type_list, type_name):
    for item in type_list:
        if item in query_text and type_name not in query_list:
            query_list.append(type_name)


def query_by_shop(query_text):
    # js_url = url_for()
    return ;



#
# @app.route("/result")
# def result():
#     # 从url中获取查询文本
#     query_text = request.args.get("query")
#     # 使用 jieba 进行中文分词，并获取词性
#     words = pseg.cut(query_text)
#
#     # 创建一个空集合，用于存放名词
#     unique_nouns_set = set()
#
#     # 选择保留名词（词性为 'n'）并添加到集合中
#     for word, flag in words:
#         if flag.startswith('n'):
#             unique_nouns_set.add(word)
#
#     # 将集合转换回列表
#     unique_nouns_list = list(unique_nouns_set)
#
#     # 初始化查询语句模板
#     query_template = """
#     MATCH (p:product)-[:sold_by]->(s:Shop)
#     WHERE ALL(entity IN $unique_nouns_list WHERE p.name CONTAINS entity)
#     RETURN p, s.name AS seller_name
#     """
#
#     # 逐步减少unique_nouns_list的元素
#     for i in range(len(unique_nouns_list), 0, -1):
#         # 获取当前循环迭代中的实体子列表
#         current_entities = unique_nouns_list[:i]
#
#         # 使用当前实体子列表填充查询语句模板
#         current_query = query_template.replace("$unique_nouns_list", str(current_entities))
#
#         # 执行查询
#         # 声明result为全局变量
#
#         global result
#         result = graph.run(current_query, unique_nouns_list=current_entities)
#
#         # 如果结果不为空，处理查询结果
#         if result is not None:
#             print("result:\n")
#             print(result)
#             break
#
#     # 将结果转换为列表
#     result_list = list(result)
#     # 处理查询结果，将节点信息转换为字典列表
#     products = [{'product': record['p'], 'seller_name': record['seller_name']} for record in result_list]
#     # 遍历result，获取与result有similar_to关系的产品
#     # 获取与result有similar_to关系的产品
#     recommandation_product = []
#     print("result:\n")
#     print(result)
#     print("result_list:\n")
#     print(result_list)
#     for record in result_list:
#         print("record:\n")
#         print(record)
#         # 获取产品节点
#         product_node_name = record['p']['name']
#         # 定义查询语句，查找与该产品有similar_to关系的产品
#         query = """
#             MATCH (p:product)-[:similar_to]->(p1:product)-[:sold_by]->(s:Shop)
#             WHERE p.name = $product_node_name
#             RETURN p1, s.name AS seller_name
#             """
#         # 执行查询语句，返回结果
#         recommandation_result = graph.run(query, product_node_name=product_node_name)
#         print(recommandation_result)
#         # temp = [{'product': record['p1'], 'seller_name': record['seller_name']} for record in recommandation_result]
#         temp = [{'product': record['p1'], 'seller_name': record['seller_name']} for record in
#                 recommandation_result]
#         # 依次将temp中的产品加入recommandation_product
#         i = 0
#         for item in temp:
#             i += 1
#             print("temp:\n")
#             print("i=" + str(i));
#             print(item)
#             recommandation_product.append(item)
#     # 返回结果
#     return render_template('index.html', products=products, recommandation_product=recommandation_product)
#

# 运行flask应用，开启调试模式
if __name__ == "__main__":
    app.run(debug=True, port=5001)
