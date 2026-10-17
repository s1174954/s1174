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

### 1. 概念模型与 ER 图映射 (ER Schema Mapping)

为确保跨平台高可读性，下表完整展示了系统内主要实体、核心属性、主外键及实体间最大基数关系：

| 实体 (Entity) | 主键 (PK) | 关键属性 (Attributes) | 关联实体与业务关系 (Relationships) | 最大基数 (Cardinality) |
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

### 2. 完整性约束说明 (Integrity Constraints)
1. **Referential Integrity (参照完整性)**：`VIDEO.CategoryID` 必须引用 `CATEGORY.CategoryID` 中存在的值。若尝试删除一个包含视频的分类，将因 `ON DELETE RESTRICT` 阻止删除，防止产生孤立数据。
2. **Domain Constraint (域约束)**：`VIDEO.Duration` 必须限制为大于 0 的正整数 (`CHECK (Duration > 0)`)；`VIDEO.Status` 仅允许在 `('Draft', 'Pending', 'Approved', 'Rejected', 'Removed')` 中取值。
3. **Business Integrity Constraint (业务逻辑约束)**：当视频状态改变为 'Approved' 或 'Rejected' 时，必须强制记录 `ReviewerID` 和 `ReviewTime`。

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
4. 关键业务约束保障机制唯一点赞保证：将 VIDEO_LIKE 表的主键设为复合主键 PRIMARY KEY (UserID, VideoID)，在数据库物理层强行保证任何用户对同一视频无法重复插入第二条记录。跨表资质校验说明（审核员必须具备对应分类资质）：由于 SQL 基本 CHECK 约束无法进行跨表子查询，此约束属于应用层或事务级规则。在生产环境中，系统会在提交审核的 API 事务（Transaction）中先执行 SELECT 1 FROM MODERATOR_CATEGORY WHERE ModeratorID = ? AND CategoryID = ?，校验通过后才允许提交更新 VIDEO 表的事务。Part D: 面向业务的 SQL 查询设计 (20分)1. 业务 SQL 表达查询 1 (Multi-table Query)：获取已通过审核视频的详细信息（含创作者及分类名称）SQLSELECT v.VideoID, v.Title, u.Username AS Creator, c.CategoryName, v.SubmitTime
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
2. 关系代数表达式 (Relational Algebra)查询 1 的关系代数 (RA1):$$\pi_{VideoID, Title, Username, CategoryName, SubmitTime} (\sigma_{Status='Approved'} (VIDEO) \bowtie USER \bowtie CATEGORY)$$查询 3 的关系代数 (RA3):$$\pi_{UserID, Username, Email} (USER) - \pi_{UserID, Username, Email} (USER \bowtie AITASK)$$3. 查询优化表达式 (Selection Push Down)针对 查询 1，运用选择下推（Selection Push Down）优化后的等价关系代数表达式为：$$\pi_{VideoID, Title, Username, CategoryName, SubmitTime} ( (\sigma_{Status='Approved'} (VIDEO)) \bowtie USER \bowtie CATEGORY )$$优化理由说明：通过将选择谓词 \sigma_{Status='Approved'} 下推到笛卡尔积/连接（Join）操作之前执行，可以在连接计算开展前过滤掉所有未通过审核（如 Draft, Pending, Rejected, Removed）的绝大多数视频行，极大地减少了参与后续 Join 操作的中间结果集行数，降低了内存占用和磁盘 I/O 开销。Part E: 索引与物理设计建议 (20分)1. 索引设计建议列表idx_video_status_cat：建立在 VIDEO(Status, CategoryID) 联合索引上。支持查询：优化 Part D 中的 Query 1 与 Query 2 的条件过滤与分组。idx_video_reviewer_cat：建立在 VIDEO(ReviewerID, CategoryID) 联合索引上。支持查询：优化 Part D 中的 Query 4 审核管理查询。idx_video_submittime：建立在 VIDEO(SubmitTime) 单列索引上。支持查询：支持平台按视频提交时间降序分页与时间范围检索。2. B+Tree 检索机制与键顺序分析B+Tree 在范围查询（Range Search）与排序中的优势：在执行形如 WHERE SubmitTime BETWEEN '2026-01-01' AND '2026-10-01' 或 ORDER BY SubmitTime DESC 的查询时，B+Tree 的叶子节点通过有序双向链表相连。查询引擎只需通过 B+Tree 索引快速定位到起始边界节点，随后直接沿着叶子节点链表进行顺序扫描，避免了全表随机磁盘读取，极大提升效率。联合索引键顺序选择（Key Order Selection）：在联合索引 (Status, CategoryID) 中，将选择性高且经常作为等值匹配条件（Status = 'Approved'）的 Status 字段放在左侧，使得查询能最快利用 B+Tree 的前缀匹配原则过滤数据。