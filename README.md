请复制以下所有内容：
Markdown
# INT6164 数据库系统与管理个人作业

## 智能短视频内容创作、发布与审核平台

---

## Part A: 需求分析与设计假设 (15分)

### 1. 主要实体及其作用
* **USER (用户)**：平台的注册使用者，可创作/发布短视频、提交 AI 生成任务、对视频进行点赞和发表评论。
* **VIDEO (短视频)**：平台核心内容资产，记录标题、时长、当前审核/发布状态及提交/审核时间。
* **CATEGORY (内容分类)**：短视频的主分类目录（如科技、美食、娱乐等），用于内容归类与审核权限划分。
* **TAG (标签)**：贴在短视频上的微观特征标签，用于检索与推荐。
* **MODERATOR (审核员)**：平台风控人员，负责审核提交的短视频。
* **AITASK (AI创作任务)**：用户向 AI 创作工具提交的辅助生成任务（如生成脚本、标题、文案或标签建议）。
* **VIDEO_LIKE (点赞)**：记录用户对视频的赞同互动。
* **COMMENT (评论)**：记录用户对视频发表的文字评论。

### 2. 核心属性说明
* **USER**: UserID (PK), Username, Email, RegistrationTime, AccountStatus
* **VIDEO**: VideoID (PK), Title, Duration, Status, SubmitTime, ReviewTime, ReviewRemark, CreatorID (FK), CategoryID (FK), ReviewerID (FK)
* **CATEGORY**: CategoryID (PK), CategoryName, Description
* **TAG**: TagID (PK), TagName
* **MODERATOR**: ModeratorID (PK), ModeratorName, Email
* **AITASK**: TaskID (PK), TaskType, GeneratedContent, IsAdopted, UserID (FK), VideoID (FK)
* **VIDEO_LIKE**: UserID (PK, FK), VideoID (PK, FK), LikeTime
* **COMMENT**: CommentID (PK), CommentText, CommentTime, CommentStatus, UserID (FK), VideoID (FK)

### 3. 实体间主要关系
* **USER - VIDEO**: 1:N（一名用户可创建多条短视频，每条短视频仅由一名用户创建）。
* **CATEGORY - VIDEO**: 1:N（一个分类包含多条短视频，每条短视频仅属于一个主分类）。
* **VIDEO - TAG**: M:N（一条短视频可有多个标签，一个标签可被多条短视频使用）。
* **MODERATOR - CATEGORY**: M:N（审核员可拥有多个分类的审核资质，一个分类可有多名审核员）。
* **USER - AITASK**: 1:N（一名用户可提交多个 AI 任务）。
* **VIDEO - AITASK**: 0..1:N（一条视频可以使用零个或多个 AI 任务；一个被采用的 AI 任务最多关联一条视频）。
* **USER - VIDEO - VIDEO_LIKE**: M:N（通过关系表实现，记录点赞历史）。
* **USER - VIDEO - COMMENT**: M:N（通过实体表实现 1:N 延伸，记录评论内容）。

### 4. 4条合理的设计假设
1. **取消点赞处理**：用户取消点赞时，系统采用物理删除（直接删除 VIDEO_LIKE 记录），确保复合主键约束能精准保证每位用户对同一视频最多保留一条有效点赞。
2. **下架视频历史数据保留**：状态变为 Removed 的视频，其历史点赞与评论记录在数据库中予以保留，但前端展示层进行屏蔽，以备审计分析。
3. **审核流程触发规则**：新上传视频状态初始为 Pending，ReviewerID 和 ReviewTime 默认为 NULL；仅当状态改变为 Approved 或 Rejected 时才强制要求更新审核员与审核时间。
4. **AI 任务独立性**：用户可随时使用 AI 工具生成内容，即便生成的脚本未最终转化为发布的视频，AI 任务记录依然独立保留（VideoID 可为空）。

---

## Part B: 概念数据库设计 - ER Diagram (25分)

### 1. ER 图展示

```mermaid
erDiagram
    USER ||--o{ VIDEO : "creates (1:N)"
    CATEGORY ||--o{ VIDEO : "belongs_to (1:N)"
    VIDEO }|--|{ TAG : "has_tag (M:N)"
    MODERATOR }|--|{ CATEGORY : "qualifies_for (M:N)"
    USER ||--o{ AITASK : "submits (1:N)"
    VIDEO ||--o{ AITASK : "adopts (0..1:N)"
    USER ||--o{ VIDEO_LIKE : "likes"
    VIDEO ||--o{ VIDEO_LIKE : "liked_by"
    USER ||--o{ COMMENT : "posts (1:N)"
    VIDEO ||--o{ COMMENT : "has_comment (1:N)"

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
M:N 关系的处理：对于 VIDEO 与 TAG、MODERATOR 与 CATEGORY 的多对多关系，在概念设计中直接标明 M:N，后续转为关系模式（Relational Schema）时拆分为独立的中间关联表（如 VIDEO_TAG 和 MODERATOR_CATEGORY）。

AI 任务与视频的关系 (0..1 : N)：用户提交 AI 任务时未必立即关联视频，因此 VideoID 允许为空（NULL）。当某条视频采用了生成的脚本/文案时，该 AI 任务最多与一条视频绑定，满足实际业务弹性需求。

点赞（Like）建模为关联实体：由于点赞涉及 UserID、VideoID 两个维度且需要记录 LikeTime，通过复合主键 (UserID, VideoID) 建模，既方便精准控制“每位用户对同一视频只能有效点赞一次”，又能避免给 VIDEO 表添加过多计数器的并发性能瓶颈。

Part C: Relational Schema, Keys 与完整性约束 (20分)
1. 完整关系模式 (Relational Schema)
USER (UserID, Username, Email, RegistrationTime, AccountStatus)

CATEGORY (CategoryID, CategoryName, Description)

TAG (TagID, TagName)

MODERATOR (ModeratorID, ModeratorName, Email)

VIDEO (VideoID, Title, Duration, Status, SubmitTime, ReviewTime, ReviewRemark, CreatorID, CategoryID, ReviewerID)

FK: CreatorID -> USER(UserID), CategoryID -> CATEGORY(CategoryID), ReviewerID -> MODERATOR(ModeratorID)

AITASK (TaskID, TaskType, GeneratedContent, IsAdopted, UserID, VideoID)

FK: UserID -> USER(UserID), VideoID -> VIDEO(VideoID)

COMMENT (CommentID, CommentText, CommentTime, CommentStatus, UserID, VideoID)

FK: UserID -> USER(UserID), VideoID -> VIDEO(VideoID)

VIDEO_LIKE (UserID, VideoID, LikeTime)

PK: (UserID, VideoID)

FK: UserID -> USER(UserID), VideoID -> VIDEO(VideoID)

VIDEO_TAG (VideoID, TagID)

PK: (VideoID, TagID)

FK: VideoID -> VIDEO(VideoID), TagID -> TAG(TagID)

MODERATOR_CATEGORY (ModeratorID, CategoryID)

PK: (ModeratorID, CategoryID)

FK: ModeratorID -> MODERATOR(ModeratorID), CategoryID -> CATEGORY(CategoryID)

2. 重要完整性约束说明
Referential Integrity (参照完整性)：VIDEO.CategoryID 必须引用 CATEGORY.CategoryID 中存在的值。当删除某个分类时，应采用 ON DELETE RESTRICT 阻止删除，防止产生孤立视频。

Domain Constraint (域约束)：VIDEO.Duration 必须限制为大于 0 的正整数（秒数），VIDEO.Status 仅允许在列表 ('Draft', 'Pending', 'Approved', 'Rejected', 'Removed') 中取值。

Business Integrity Constraint (业务逻辑约束)：当视频状态更改为 'Approved' 或 'Rejected' 时，ReviewerID 和 ReviewTime 绝不能为空（NOT NULL）。

3. DDL 语句实现 (DDL SQL)
SQL
-- 1. MODERATOR_CATEGORY 关系表 (审核资质关联表)
CREATE TABLE MODERATOR_CATEGORY (
    ModeratorID INT NOT NULL,
    CategoryID INT NOT NULL,
    PRIMARY KEY (ModeratorID, CategoryID),
    FOREIGN KEY (ModeratorID) REFERENCES MODERATOR(ModeratorID) ON DELETE CASCADE,
    FOREIGN KEY (CategoryID) REFERENCES CATEGORY(CategoryID) ON DELETE CASCADE
);

-- 2. VIDEO 关系表
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
    FOREIGN KEY (ReviewerID) REFERENCES MODERATOR(ModeratorID),
    CONSTRAINT CHK_Review_Info CHECK (
        (Status IN ('Approved', 'Rejected') AND ReviewerID IS NOT NULL AND ReviewTime IS NOT NULL) OR
        (Status NOT IN ('Approved', 'Rejected'))
    )
);
4. 关键业务约束保障说明
同一用户对同一视频唯一有效点赞：通过将 VIDEO_LIKE 表的主键设计为复合主键 PRIMARY KEY (UserID, VideoID)，在数据库引擎物理层保证数据唯一性，重复插入时将直接触发主键冲突报错。

跨表业务规则保障（审核员需具备对应分类资质）：此类规则无法单凭基础 CHECK 约束实现。在实际应用中，通过事务逻辑（Transaction Logic）或存储过程/应用层保障。在审核提交接口中先查询 MODERATOR_CATEGORY 表验证是否存在 (ReviewerID, CategoryID) 匹配项，验证通过后方可更新 VIDEO 表状态。

Part D: 面向业务的 SQL 查询设计 (20分)
1. 业务 SQL 表达
查询 1 (Multi-table Query)：获取已通过审核视频的详细信息（含创作者及分类名称）
SQL
SELECT v.VideoID, v.Title, u.Username AS Creator, c.CategoryName, v.SubmitTime
FROM VIDEO v
JOIN USER u ON v.CreatorID = u.UserID
JOIN CATEGORY c ON v.CategoryID = c.CategoryID
WHERE v.Status = 'Approved';
查询 2 (Aggregate & GROUP BY)：按分类统计已发布视频数量及平均时长
SQL
SELECT c.CategoryName, COUNT(v.VideoID) AS TotalVideos, AVG(v.Duration) AS AvgDuration
FROM CATEGORY c
JOIN VIDEO v ON c.CategoryID = v.CategoryID
WHERE v.Status = 'Approved'
GROUP BY c.CategoryID, c.CategoryName;
查询 3 (否定/未发生事件查询)：查找从未提交过任何 AI 任务的用户
SQL
SELECT u.UserID, u.Username, u.Email
FROM USER u
LEFT JOIN AITASK a ON u.UserID = a.UserID
WHERE a.TaskID IS NULL;
查询 4 (平台运营/审核管理查询)：查询具备特定分类审核资质但从未审核过该分类视频的审核员
SQL
SELECT m.ModeratorID, m.ModeratorName, mc.CategoryID
FROM MODERATOR m
JOIN MODERATOR_CATEGORY mc ON m.ModeratorID = mc.ModeratorID
WHERE NOT EXISTS (
    SELECT 1 
    FROM VIDEO v 
    WHERE v.ReviewerID = m.ModeratorID 
      AND v.CategoryID = mc.CategoryID
);
2. 关系代数表达式 (Relational Algebra)
查询 1 的关系代数 (RA1):
π VideoID, Title, Username, CategoryName, SubmitTime ( σ Status='Approved' (VIDEO) ⋈ USER ⋈ CATEGORY )

查询 3 的关系代数 (RA3):
π UserID, Username, Email ( USER ) - π UserID, Username, Email ( USER ⋈ AITASK )

3. 查询优化表达式 (Push Down Optimization)
对 查询 1 运用 Selection Push Down（选择下推）的优化表达式：

π VideoID, Title, Username, CategoryName, SubmitTime ( ( σ Status='Approved' (VIDEO) ) ⋈ USER ⋈ CATEGORY )

优化理由说明：通过将选择条件 σ Status='Approved' 下推到连接操作（Join）之前执行，提前过滤掉所有非 Approved 状态的视频数据，大大减少了参与后续与 USER 和 CATEGORY 表 Join 的中间结果集规模（Intermediate Result），显著降低磁盘 I/O 开销与 CPU 内存消耗。

Part E: 索引与物理设计建议 (20分)
1. 索引设计建议列表
idx_video_status_cat：建立在 VIDEO(Status, CategoryID) 联合索引上。

支持查询：支持 Part D 中的 Query 1 和 Query 2。

idx_video_reviewer_cat：建立在 VIDEO(ReviewerID, CategoryID) 联合索引上。

支持查询：支持 Part D 中的 Query 4 审核管理查询。

idx_video_submittime：建立在 VIDEO(SubmitTime) 索引上。

支持查询：支持首页或分类列表按视频提交/发布时间进行降序分页展示。

2. 索引选择与 B+Tree 机制分析
B+Tree 在范围查询（Range Search）与排序中的优势：
在短视频平台中，用户常常按发布时间调取最新视频（如 ORDER BY SubmitTime DESC），或查询指定时间段内的视频（WHERE SubmitTime BETWEEN ...）。由于 B+Tree 的所有叶子节点（Leaf Nodes）形成了双向链表结构，一旦通过树结构查找到起始节点，后续的数据读取只需在叶子节点链表上做顺序扫描（Sequential Scan），避免了大量的磁盘随机 I/O，极其高效。

联合索引键顺序设计（Key Order Selection）：
对于联合索引 idx_video_status_cat(Status, CategoryID)，将高选择性（High Selectivity）且常作为等值筛选条件（Equality Condition）的 Status 放在首位，能够快速跳过占大部分的非展示态视频，极大提升 B+Tree 的检索效率。