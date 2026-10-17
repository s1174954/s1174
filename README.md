Markdown
# INT6164 数据库系统与管理个人作业
## 智能短视频内容创作、发布与审核平台

---

## Part A: 需求分析与设计假设 (15分)

### 1. 核心实体与作用
* **USER**：平台注册用户，发布视频、提交 AI 任务、点赞及评论。
* **VIDEO**：短视频内容资产，记录标题、时长、审核状态及时间戳。
* **CATEGORY**：视频主分类目录（如科技、美食），用于归类与审核权限划分。
* **TAG**：微观特征标签，用于检索与推荐。
* **MODERATOR**：风控审核员，负责视频内容审核。
* **AITASK**：用户提交的 AI 辅助创作任务（如脚本/文案生成）。
* **VIDEO_LIKE**：用户与视频的点赞互动记录。
* **COMMENT**：用户发表的评论内容。

### 2. 实体主要关系
* **USER - VIDEO**: 1:N | **CATEGORY - VIDEO**: 1:N | **USER - AITASK**: 1:N
* **VIDEO - TAG**: M:N | **MODERATOR - CATEGORY**: M:N
* **VIDEO - AITASK**: 0..1:N（未采用的 AI 任务 VideoID 为空）
* **USER - VIDEO - VIDEO_LIKE / COMMENT**: M:N（通过关联表/实体实现）

### 3. 4条关键设计假设
1. **取消点赞**：物理删除 `VIDEO_LIKE` 记录，复合主键确保每人每视频仅一条有效点赞。
2. **下架数据保留**：`Removed` 状态视频的历史点赞/评论在数据库保留以备审计，前端展示屏蔽。
3. **审核状态联动**：`Pending` 视频审核员字段为空；状态更新为 `Approved` 或 `Rejected` 时强制记录审核员与时间。
4. **AI 任务独立性**：生成的 AI 脚本未转化为视频时，`AITASK` 记录依然独立保留。

---

## Part B: 概念数据库设计 - ER Diagram (25分)

### 1. ER 图展示

```mermaid
erDiagram
    USER ||--o{ VIDEO : "creates"
    CATEGORY ||--o{ VIDEO : "belongs_to"
    VIDEO }|--|{ TAG : "has_tag"
    MODERATOR }|--|{ CATEGORY : "qualifies_for"
    USER ||--o{ AITASK : "submits"
    VIDEO ||--o{ AITASK : "adopts"
    USER ||--o{ VIDEO_LIKE : "likes"
    VIDEO ||--o{ VIDEO_LIKE : "liked_by"
    USER ||--o{ COMMENT : "posts"
    VIDEO ||--o{ COMMENT : "has_comment"

    USER {
        int UserID PK
        string Username
        string Email
        datetime RegistrationTime
        string AccountStatus
    }
    VIDEO {
        int VideoID PK
        string Title
        int Duration
        string Status
        datetime SubmitTime
        datetime ReviewTime
        string ReviewRemark
        int CreatorID FK
        int CategoryID FK
        int ReviewerID FK
    }
    CATEGORY {
        int CategoryID PK
        string CategoryName
        string Description
    }
    TAG {
        int TagID PK
        string TagName
    }
    MODERATOR {
        int ModeratorID PK
        string ModeratorName
        string Email
    }
    AITASK {
        int TaskID PK
        string TaskType
        string GeneratedContent
        boolean IsAdopted
        int UserID FK
        int VideoID FK
    }
    VIDEO_LIKE {
        int UserID PK_FK
        int VideoID PK_FK
        datetime LikeTime
    }
    COMMENT {
        int CommentID PK
        string CommentText
        datetime CommentTime
        string CommentStatus
        int UserID FK
        int VideoID FK
    }
2. 重要设计决策说明
M:N 拆分：VIDEO-TAG 与 MODERATOR-CATEGORY 多对多关系在物理表转为关联表 VIDEO_TAG 和 MODERATOR_CATEGORY。

点赞实体化：使用复合主键 (UserID, VideoID) 建模，避免在 VIDEO 表增加高并发更新计数器的性能瓶颈。

Part C: Relational Schema, Keys 与完整性约束 (20分)
1. 关系模式 (Relational Schema)
USER (UserID, Username, Email, RegistrationTime, AccountStatus)

CATEGORY (CategoryID, CategoryName, Description)

TAG (TagID, TagName)

MODERATOR (ModeratorID, ModeratorName, Email)

VIDEO (VideoID, Title, Duration, Status, SubmitTime, ReviewTime, ReviewRemark, CreatorID, CategoryID, ReviewerID)

AITASK (TaskID, TaskType, GeneratedContent, IsAdopted, UserID, VideoID)

COMMENT (CommentID, CommentText, CommentTime, CommentStatus, UserID, VideoID)

VIDEO_LIKE (UserID, VideoID, LikeTime)

VIDEO_TAG (VideoID, TagID)

MODERATOR_CATEGORY (ModeratorID, CategoryID)

2. DDL 核心建表语句
SQL
CREATE TABLE MODERATOR_CATEGORY (
    ModeratorID INT NOT NULL,
    CategoryID INT NOT NULL,
    PRIMARY KEY (ModeratorID, CategoryID),
    FOREIGN KEY (ModeratorID) REFERENCES MODERATOR(ModeratorID) ON DELETE CASCADE,
    FOREIGN KEY (CategoryID) REFERENCES CATEGORY(CategoryID) ON DELETE CASCADE
);

CREATE TABLE VIDEO (
    VideoID INT AUTO_INCREMENT PRIMARY KEY,
    Title VARCHAR(255) NOT NULL,
    Duration INT NOT NULL CHECK (Duration > 0),
    Status VARCHAR(20) NOT NULL CHECK (Status IN ('Draft', 'Pending', 'Approved', 'Rejected', 'Removed')),
    SubmitTime DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ReviewTime DATETIME NULL,
    ReviewRemark VARCHAR(500) NULL,
    CreatorID INT NOT NULL,
    CategoryID INT NOT NULL,
    ReviewerID INT NULL,
    FOREIGN KEY (CreatorID) REFERENCES USER(UserID),
    FOREIGN KEY (CategoryID) REFERENCES CATEGORY(CategoryID),
    FOREIGN KEY (ReviewerID) REFERENCES MODERATOR(ModeratorID)
);
3. 约束保障
唯一点赞：VIDEO_LIKE 的复合主键 (UserID, VideoID) 从物理层强制防重。

跨表资质校验：审核员跨分类权限控制通过应用层事务/存储过程在提交审核时校验 MODERATOR_CATEGORY 关系。

Part D: 面向业务的 SQL 查询设计 (20分)
1. 业务 SQL 查询
SQL
-- Q1 (多表连接): 查询已审核通过视频的详细信息
SELECT v.VideoID, v.Title, u.Username AS Creator, c.CategoryName, v.SubmitTime
FROM VIDEO v
JOIN USER u ON v.CreatorID = u.UserID
JOIN CATEGORY c ON v.CategoryID = c.CategoryID
WHERE v.Status = 'Approved';

-- Q2 (聚合统计): 按分类统计已发布视频数量及平均时长
SELECT c.CategoryName, COUNT(v.VideoID) AS TotalVideos, AVG(v.Duration) AS AvgDuration
FROM CATEGORY c
JOIN VIDEO v ON c.CategoryID = v.CategoryID
WHERE v.Status = 'Approved'
GROUP BY c.CategoryID, c.CategoryName;

-- Q3 (否定查询): 查找从未提交过任何 AI 任务的用户
SELECT u.UserID, u.Username, u.Email
FROM USER u
LEFT JOIN AITASK a ON u.UserID = a.UserID
WHERE a.TaskID IS NULL;

-- Q4 (运营管理): 查询具备分类资质但从未审核过该分类视频的审核员
SELECT m.ModeratorID, m.ModeratorName, mc.CategoryID
FROM MODERATOR m
JOIN MODERATOR_CATEGORY mc ON m.ModeratorID = mc.ModeratorID
WHERE NOT EXISTS (
    SELECT 1 FROM VIDEO v 
    WHERE v.ReviewerID = m.ModeratorID AND v.CategoryID = mc.CategoryID
);
2. 关系代数表达式 (RA)
RA1 (Q1): π VideoID, Title, Username, CategoryName, SubmitTime ( σ Status='Approved' (VIDEO) ⋈ USER ⋈ CATEGORY )

RA3 (Q3): π UserID, Username, Email ( USER ) - π UserID, Username, Email ( USER ⋈ AITASK )

3. 查询优化表达式 (Selection Push Down)
表达式: π VideoID, Title, Username, CategoryName, SubmitTime ( ( σ Status='Approved' (VIDEO) ) ⋈ USER ⋈ CATEGORY )

优化说明: 将谓词下推到 Join 之前，先过滤非 Approved 数据，大幅减少中间结果集行数，降低内存及 I/O 消耗。

Part E: 索引与物理设计建议 (20分)
1. 索引建议
idx_video_status_cat 在 VIDEO(Status, CategoryID)：优化 Q1 与 Q2 过滤。

idx_video_reviewer_cat 在 VIDEO(ReviewerID, CategoryID)：优化 Q4 跨表比对。

idx_video_submittime 在 VIDEO(SubmitTime)：加速时间排序与范围检索。

2. B+Tree 检索机制说明
在按时间范围查询（如 WHERE SubmitTime BETWEEN ...）或降序分页时，B+Tree 叶子节点构成的双向有序链表允许直接进行顺序扫描（Sequential Scan），避免随机磁盘 I/O。