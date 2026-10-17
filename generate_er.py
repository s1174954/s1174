import matplotlib.pyplot as plt
import networkx as nx

# 解决中文/字体显示问题
plt.rcParams['font.sans-serif'] = ['SimHei']  
plt.rcParams['axes.unicode_minus'] = False

# 1. 创建图结构
G = nx.DiGraph()

# 2. 定义实体节点
entities = [
    "User\n(用户)", 
    "Video\n(短视频)", 
    "Category\n(分类)", 
    "Tag\n(标签)", 
    "Moderator\n(审核员)", 
    "AITask\n(AI任务)", 
    "Video_Like\n(点赞)", 
    "Comment\n(评论)"
]
G.add_nodes_from(entities)

# 3. 定义实体间的关联关系
edges = [
    ("User\n(用户)", "Video\n(短视频)"),
    ("Category\n(分类)", "Video\n(短视频)"),
    ("Video\n(短视频)", "Tag\n(标签)"),
    ("Moderator\n(审核员)", "Category\n(分类)"),
    ("User\n(用户)", "AITask\n(AI任务)"),
    ("Video\n(短视频)", "AITask\n(AI任务)"),
    ("User\n(用户)", "Video_Like\n(点赞)"),
    ("Video\n(短视频)", "Video_Like\n(点赞)"),
    ("User\n(用户)", "Comment\n(评论)"),
    ("Video\n(短视频)", "Comment\n(评论)")
]
G.add_edges_from(edges)

# 4. 绘制 ER 图
fig, ax = plt.subplots(figsize=(12, 8))
pos = nx.spring_layout(G, seed=42)

nx.draw_networkx_nodes(G, pos, node_size=3500, node_color='lightblue', edgecolors='black')
nx.draw_networkx_labels(G, pos, font_size=10, font_family='sans-serif')
nx.draw_networkx_edges(G, pos, width=2, alpha=0.6, edge_color='gray', arrowsize=20)

plt.title("平台 ER 图概念结构图 (ER Diagram)", fontsize=14)
plt.axis('off')

# 5. 强制保存图片并展示
plt.savefig("er_diagram.png", dpi=300, bbox_inches='tight')
print("--- 图片已强制写入磁盘！---")
plt.show()  # 运行后会直接弹出一个图片窗口