Markdown
# INT6164 数据库系统与管理个人作业
## 智能短视频内容创作、发布与审核平台

---

## Part A: 需求分析与设计假设 (15分)

### 1. 主要实体及其作用
* **USER (用户)**：平台的注册使用者，可创作/发布短视频、提交 AI 生成任务、对视频进行点赞和发表评论。
* **VIDEO (短视频)**：平台核心内容资产，记录标题、时长、当前审核/发布状态及提交/审核时间。
* **CATEGORY (内容分类)**：短视频的主分类目录（如科技、美食等），用于内容归类与审核权限划分。
* **TAG (标签)**：贴在短视频上的微观特征标签，用于检索与推荐。
* **MODERATOR (审核员)**：平台风控人员，负责审核提交的短视频。
* **AITASK (AI创作任务)**：用户向 AI 创作工具提交的辅助生成任务（如生成脚本、标题、文案或标签建议）。
* **VIDEO_LIKE (点赞)**：记录用户对视频的赞同互动。
* **COMMENT (评论)**：记录用户对视频发表的文字评论。

### 2. 实体间主要关系
* **USER - VIDEO**: 1:N（一名用户可创建多条短视频，每条短视频仅由一名用户创建）。
* **CATEGORY - VIDEO**: 1:N（一个分类包含多条短视频，每条短视频仅属于一个主分类）。
* **VIDEO - TAG**: M:N（一条短视频可有多个标签，一个标签可被多条短视频使用）。
* **MODERATOR - CATEGORY**: M:N（审核员可具备多个分类的审核资质，一个分类可有多名审核员）。
* **USER - AITASK**: 1:N（一名用户可提交多个 AI 任务）。
* **VIDEO - AITASK**: 0..1:N（未被采用的 AI 任务 VideoID 为空；一条视频可以使用零个或多个 AI 任务）。
* **USER - VIDEO - VIDEO_LIKE**: M:N（通过关联实体表实现，记录点赞历史）。
* **USER - VIDEO - COMMENT**: M:N（通过实体表实现 1:N 延伸，记录评论内容）。

### 3. 4条合理的设计假设
1. **取消点赞处理**：用户取消点赞时，系统采用物理删除（直接删除 VIDEO_LIKE 记录），确保复合主键约束能精准保证每位用户对同一视频最多保留一条有效点赞。
2. **下架视频历史数据保留**：状态变为 Removed 的视频，其历史点赞与评论记录在数据库中予以保留，但前端展示层进行屏蔽，以备审计分析。
3. **审核流程触发规则**：新上传视频状态初始为 Pending，ReviewerID 和 ReviewTime 默认为 NULL；仅当状态改变为 Approved 或 Rejected 时才强制要求更新审核员与审核时间。
4. **AI 任务独立性**：用户可随时使用 AI 工具生成内容，即便生成的脚本未最终转化为发布的视频，AI 任务记录依然独立保留（VideoID 可为空）。

---

## Part B: 概念数据库设计 - ER Diagram (25分)

### 1. 概念模型 ER 图 (Conceptual ER Diagram)

```mermaid
graph TD
    USER[USER<br>+UserID PK] -->|1:N Publishes| VIDEO[VIDEO<br>+VideoID PK]
    CATEGORY[CATEGORY<br>+CategoryID PK] -->|1:N Belongs to| VIDEO
    USER -->|1:N Submits| AITASK[AITASK<br>+TaskID PK]
    VIDEO -.->|0..1:N Adopts| AITASK
    
    VIDEO <-->|M:N Has Tag| TAG[TAG<br>+TagID PK]
    MODERATOR[MODERATOR<br>+ModeratorID PK] <-->|M:N Has Qualification| CATEGORY
    MODERATOR -->|1:N Audits| VIDEO
    
    USER <-->|M:N Likes| VIDEO_LIKE[VIDEO_LIKE<br>+(UserID, VideoID) PK]
    VIDEO <-->|M:N Liked By| VIDEO_LIKE
    USER -->|1:N Writes| COMMENT[COMMENT<br>+CommentID PK]
    VIDEO -->|1:N Has Comment| COMMENT

    style USER fill:#e3f2fd,stroke:#2196f3
    style VIDEO fill:#e8f5e9,stroke:#4caf50
    style CATEGORY fill:#fff3e0,stroke:#ff9800
    style MODERATOR fill:#f3e5f5,stroke:#9c27b0
    style AITASK fill:#e0f2f1,stroke:#009688
2. 重要设计决策说明 (Design Decisions)
M:N 关系的处理：对于 VIDEO-TAG（视频与标签）以及 MODERATOR-CATEGORY（审核资质）的 M:N 关系，在概念设计阶段直接标明多对多，转换为关系模式时拆分为独立的关联表（VIDEO_TAG 和 MODERATOR_CATEGORY），以满足第一范式（1NF）。

AI 任务与视频的关联 (0..1 : N)：用户提交 AI 任务时未必立即关联视频，因此 AITASK.VideoID 允许为空（NULL）。当某条视频采用该 AI 内容时，填写对应的 VideoID。这种设计保证了 AI 创作工具的独立使用体验。

将 Like 建模为关联关系而非 Video 属性：若在 VIDEO 表中直接设置 LikeCount 属性，在多用户并发点赞时会导致频繁的行级锁竞争与数据库写瓶颈。将点赞独立为 VIDEO_LIKE 实体并设置复合主键 (UserID, VideoID)，既保证了“同一用户只能有效点赞一次”的约束，又支持高并发写入和点赞历史审计。

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

2. DDL 物理建表与数据落地图 (Schema Execution Diagram)
代码段
graph LR
    subgraph 核心建表与物理落地控制台
    A[CREATE TABLE USER / CATEGORY / MODERATOR] -->|物理生成| B[Query OK, 0 rows affected]
    B --> C[CREATE TABLE VIDEO / AITASK / COMMENT]
    C -->|外键约束生效| D[Query OK, 0 rows affected]
    D --> E[CREATE TABLE VIDEO_LIKE / VIDEO_TAG]
    E -->|复合主键校验通过| F[Query OK, 0 rows affected]
    end

    style A fill:#e1f5fe,stroke:#0288d1
    style C fill:#e1f5fe,stroke:#0288d1
    style E fill:#e1f5fe,stroke:#0288d1
    style B fill:#f1f8e9,stroke:#558b2f
    style D fill:#f1f8e9,stroke:#558b2f
    style F fill:#f1f8e9,stroke:#558b2f
3. DDL 核心建表语句
SQL
-- 1. MODERATOR_CATEGORY 关系表 (审核资质关联表)
CREATE TABLE MODERATOR_CATEGORY (
    ModeratorID INT NOT NULL,
    CategoryID INT NOT NULL,
    PRIMARY KEY (ModeratorID, CategoryID),
    FOREIGN KEY (ModeratorID) REFERENCES MODERATOR(ModeratorID) ON DELETE CASCADE,
    FOREIGN KEY (CategoryID) REFERENCES CATEGORY(CategoryID) ON DELETE CASCADE
);

-- 2. VIDEO 关系表 (包含主键、外键及完整约束)
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
2. 关系代数与查询优化树 (Query Execution Tree / Selection Push Down)
代码段
graph TD
    subgraph 优化前查询树 (Unoptimized Tree)
    T1[π VideoID, Title, Username, CategoryName] --- J1[Join ⋈]
    J1 --- J2[Join ⋈]
    J1 --- C1[CATEGORY]
    J2 --- U1[USER]
    J2 --- S1[σ Status='Approved']
    S1 --- V1[VIDEO 全表扫描]
    end

    subgraph 优化后推导树 (Selection Push Down Tree)
    T2[π VideoID, Title, Username, CategoryName] --- J3[Join ⋈]
    J3 --- J4[Join ⋈]
    J3 --- C2[CATEGORY]
    J4 --- U2[USER]
    J4 --- Filter[σ Status='Approved' VIDEO 提前过滤]
    end
    
    style Filter fill:#ffe0b2,stroke:#f57c00
    style S1 fill:#fff9c4,stroke:#fbc02d
选择下推 (Selection Push Down) 优化理由：通过将选择谓词 σ Status='Approved' 下推到 Join 操作之前执行，先过滤掉非 Approved 状态的大量视频，极大地减少了连接计算时的中间结果集规模，降低了内存占用和磁盘 I/O 消耗。

Part E: 索引与物理设计建议 (20分)
1. 索引设计建议列表
idx_video_status_cat：建立在 VIDEO(Status, CategoryID) 联合索引上，优化 Part D 中的 Query 1 与 Query 2 过滤。

idx_video_reviewer_cat：建立在 VIDEO(ReviewerID, CategoryID) 联合索引上，优化 Part D 中的 Query 4 审核管理查询。

idx_video_submittime：建立在 VIDEO(SubmitTime) 单列索引上，支持视频按提交时间降序分页与范围检索。

2. B+Tree 检索机制结构图 (B+Tree Range Search Mechanism)
代码段
graph TD
    Root[Root Node: SubmitTime Index Key] --> Internal1[Internal Node 1]
    Root --> Internal2[Internal Node 2]
    
    Internal1 --> Leaf1[Leaf Node 1: 2026-01-01]
    Internal1 --> Leaf2[Leaf Node 2: 2026-05-01]
    Internal2 --> Leaf3[Leaf Node 3: 2026-10-01]
    
    Leaf1 <--->|有序双向链表 Range Scan| Leaf2
    Leaf2 <--->|顺序磁盘 I/O 扫描| Leaf3

    style Leaf1 fill:#e3f2fd,stroke:#2196f3
    style Leaf2 fill:#e3f2fd,stroke:#2196f3
    style Leaf3 fill:#e3f2fd,stroke:#2196f3
B+Tree 范围查询优势：在执行形如 WHERE SubmitTime BETWEEN '2026-01-01' AND '2026-10-01' 的范围检索或降序排序时，B+Tree 叶子节点构成的有序双向链表允许引擎直接进行顺序扫描（Sequential Scan），避免了频繁随机磁盘读写，极大提升了查询效率。