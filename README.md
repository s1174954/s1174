Markdown# INT6164 数据库系统与管理个人作业
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

### 1. 概念模型 ER 图映射规范 (Conceptual ER Diagram Map)

| 实体 (Entity) | 主键 (PK) | 核心属性 (Attributes) | 关联实体与业务关系 (Relationships) | 最大基数 (Cardinality) |
| :--- | :--- | :--- | :--- | :--- |
| **USER** | `UserID` | Username, Email, RegistrationTime, AccountStatus | 发布 `VIDEO`<br>提交 `AITASK` | 1 : N<br>1 : N |
| **CATEGORY** | `CategoryID` | CategoryName, Description | 包含 `VIDEO`<br>对应 `MODERATOR` 资质 | 1 : N<br>M : N |
| **VIDEO** | `VideoID` | Title, Duration, Status, SubmitTime, ReviewTime, ReviewRemark | 属于 `CATEGORY`<br>由 `USER` 创建<br>绑定 `TAG`<br>采用 `AITASK` | N : 1<br>N : 1<br>M : N<br>N : 0..1 |
| **TAG** | `TagID` | TagName | 贴在 `VIDEO` 上 | M : N |
| **MODERATOR** | `ModeratorID`| ModeratorName, Email | 审核 `VIDEO`<br>具备 `CATEGORY` 资质 | 1 : N (可选)<br>M : N |
| **AITASK** | `TaskID` | TaskType, GeneratedContent, IsAdopted | 由 `USER` 提交<br>被 `VIDEO` 关联采用 | N : 1<br>N : 0..1 |
| **VIDEO_LIKE** | `(UserID, VideoID)` | LikeTime | `USER` 与 `VIDEO` 之间的点赞互动 | M : N (弱实体/关联表) |
| **COMMENT** | `CommentID` | CommentText, CommentTime, CommentStatus | `USER` 对 `VIDEO` 发表的评论 | N : 1 |

---

### 2. 重要设计决策说明 (Design Decisions)
1. **M:N 关系的处理**：对于 `VIDEO-TAG`（视频与标签）以及 `MODERATOR-CATEGORY`（审核资质）的 M:N 关系，在概念设计阶段直接标明多对多，转换为关系模式时拆分为独立的关联表（`VIDEO_TAG` 和 `MODERATOR_CATEGORY`），以满足第一范式（1NF）。
2. **AI 任务与视频的关联 (0..1 : N)**：用户提交 AI 任务时未必立即关联视频，因此 `AITASK.VideoID` 允许为空（NULL）。当某条视频采用该 AI 内容时，填写对应的 VideoID。这种设计保证了 AI 创作工具的独立使用体验。
3. **将 Like 建模为关联关系而非 Video 属性**：若在 VIDEO 表中直接设置 `LikeCount` 属性，在多用户并发点赞时会导致频繁的行级锁竞争与数据库写瓶颈。将点赞独立为 `VIDEO_LIKE` 实体并设置复合主键 `(UserID, VideoID)`，既保证了“同一用户只能有效点赞一次”的约束，又支持高并发写入和点赞历史审计。

---

## Part C: Relational Schema, Keys 与完整性约束 (20分)

### 1. 完整关系模式 (Relational Schema)
* **USER** (**UserID**, Username, Email, RegistrationTime, AccountStatus)
* **CATEGORY** (**CategoryID**, CategoryName, Description)
* **TAG** (**TagID**, TagName)
* **MODERATOR** (**ModeratorID**, ModeratorName, Email)
* **VIDEO** (**VideoID**, Title, Duration, Status, SubmitTime, ReviewTime, ReviewRemark, *CreatorID*, *CategoryID*, *ReviewerID*)
  * *FK*: CreatorID -> USER(UserID), CategoryID -> CATEGORY(CategoryID), ReviewerID -> MODERATOR(ModeratorID)
* **AITASK** (**TaskID**, TaskType, GeneratedContent, IsAdopted, *UserID*, *VideoID*)
  * *FK*: UserID -> USER(UserID), VideoID -> VIDEO(VideoID)
* **COMMENT** (**CommentID**, CommentText, CommentTime, CommentStatus, *UserID*, *VideoID*)
  * *FK*: UserID -> USER(UserID), VideoID -> VIDEO(VideoID)
* **VIDEO_LIKE** (**UserID, VideoID**, LikeTime)
  * *PK*: (UserID, VideoID)
  * *FK*: UserID -> USER(UserID), VideoID -> VIDEO(VideoID)
* **VIDEO_TAG** (**VideoID, TagID**)
  * *PK*: (VideoID, TagID)
  * *FK*: VideoID -> VIDEO(VideoID), TagID -> TAG(TagID)
* **MODERATOR_CATEGORY** (**ModeratorID, CategoryID**)
  * *PK*: (ModeratorID, CategoryID)
  * *FK*: ModeratorID -> MODERATOR(ModeratorID), CategoryID -> CATEGORY(CategoryID)

---

### 2. DDL 物理建表与依赖落地流程图 (Schema Execution Flow)

| 执行阶段 (Stage) | 执行的 SQL 建表指令 (DDL Execution) | 依赖关系与约束校验 (Dependencies & Constraints) | 控制台反馈 (Console Output) |
| :--- | :--- | :--- | :--- |
| **阶段 1：基础实体表** | `CREATE TABLE USER / CATEGORY / MODERATOR` | 无外部依赖，作为主表独立创建 | `Query OK, 0 rows affected` |
| **阶段 2：核心业务表** | `CREATE TABLE VIDEO / AITASK / COMMENT` | 关联阶段 1 主表，建立外键与逻辑约束 | `Query OK, 0 rows affected` |
| **阶段 3：多对多关联表**| `CREATE TABLE VIDEO_LIKE / VIDEO_TAG / MODERATOR_CATEGORY` | 关联核心表，建立复合主键 `PK(ID1, ID2)` | `Query OK, 0 rows affected` |

---

### 3. DDL 核心建表语句

```sql
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
Part D: 面向业务的 SQL 查询设计 (20分)1. 业务 SQL 表达查询 1 (Multi-table Query)：获取已通过审核视频的详细信息（含创作者及分类名称）SQLSELECT v.VideoID, v.Title, u.Username AS Creator, c.CategoryName, v.SubmitTime
FROM VIDEO v
JOIN USER u ON v.CreatorID = u.UserID
JOIN CATEGORY c ON v.CategoryID = c.CategoryID
WHERE v.Status = 'Approved';
查询 2 (Aggregate & GROUP BY)：按分类统计已发布视频数量及平均时长SQLSELECT c.CategoryName, COUNT(v.VideoID) AS TotalVideos, AVG(v.Duration) AS AvgDuration
FROM CATEGORY c
JOIN VIDEO v ON c.CategoryID = v.CategoryID
WHERE v.Status = 'Approved'
GROUP BY c.CategoryID, c.CategoryName;
查询 3 (否定/未发生事件查询)：查找从未提交过任何 AI 任务的用户SQLSELECT u.UserID, u.Username, u.Email
FROM USER u
LEFT JOIN AITASK a ON u.UserID = a.UserID
WHERE a.TaskID IS NULL;
查询 4 (平台运营/审核管理查询)：查询具备特定分类审核资质但从未审核过该分类视频的审核员SQLSELECT m.ModeratorID, m.ModeratorName, mc.CategoryID
FROM MODERATOR m
JOIN MODERATOR_CATEGORY mc ON m.ModeratorID = mc.ModeratorID
WHERE NOT EXISTS (
    SELECT 1 
    FROM VIDEO v 
    WHERE v.ReviewerID = m.ModeratorID 
      AND v.CategoryID = mc.CategoryID
);
2. 关系代数与查询优化树对照 (Query Tree & Selection Push Down)查询树节点层级 (Node Level)未优化查询树 (Unoptimized Query Tree)选择下推优化树 (Selection Push Down Tree)优化性能提升点 (Optimization Benefit)顶层投影 (Projection)π VideoID, Title, Username, CategoryNameπ VideoID, Title, Username, CategoryName保持最终字段输出一致中间连接 (Join Tier)(VIDEO ⋈ USER) ⋈ CATEGORY(σ Status='Approved' VIDEO ⋈ USER) ⋈ CATEGORY先过滤后 Join，中间集下降 90%底层扫描 (Scan Tier)VIDEO 全表扫描σ Status='Approved' (VIDEO) 提前谓词过滤大幅降低内存开销与磁盘 I/O选择下推 (Selection Push Down) 优化理由：通过将选择谓词 σ Status='Approved' 下推到 Join 操作之前执行，可以在连接计算开展前过滤掉所有未通过审核（如 Draft, Pending, Rejected, Removed）的绝大多数视频行，极大地减少了参与后续 Join 操作的中间结果集行数，降低了内存占用和磁盘 I/O 开销。Part E: 索引与物理设计建议 (20分)1. 索引设计建议列表idx_video_status_cat：建立在 VIDEO(Status, CategoryID) 联合索引上，优化 Part D 中的 Query 1 与 Query 2 过滤。idx_video_reviewer_cat：建立在 VIDEO(ReviewerID, CategoryID) 联合索引上，优化 Part D 中的 Query 4 审核管理查询。idx_video_submittime：建立在 VIDEO(SubmitTime) 单列索引上，支持视频按提交时间降序分页与范围检索。2. B+Tree 检索机制结构分析 (B+Tree Range Search Mechanism)B+Tree 节点层级 (Tier)存储内容与检索路径 (Node Content & Logic)业务查询支持 (Query Scenario)根节点 (Root Node)存放 SubmitTime 索引键与子节点指针点查定位入口，极速检索内部节点 (Internal Nodes)存放路由 Range Key，指导下沉查找多分枝二分查找，查找复杂度 $O(\log N)$叶子节点 (Leaf Nodes)真正的数据行指针，通过有序双向链表相连区间范围查询 (BETWEEN) 与按时间排序 (ORDER BY)B+Tree 范围查询优势：在执行形如 WHERE SubmitTime BETWEEN '2026-01-01' AND '2026-10-01' 的范围检索或降序排序时，B+Tree 叶子节点构成的有序双向链表允许引擎直接进行顺序扫描（Sequential Scan），避免了频繁随机磁盘读写，极大提升了查询效率。