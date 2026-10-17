# INT6164 数据库系统与管理个人作业
## 智能短视频内容创作、发布与审核平台

---

## Part A: 需求分析与设计假设 (15分)

### 1. 主要实体及其作用
- **USER (用户)**：平台的注册使用者，可创作/发布短视频、提交 AI 生成任务、对视频进行点赞和发表评论。
- **VIDEO (短视频)**：平台核心内容资产，记录标题、时长、当前审核/发布状态及提交/审核时间。
- **CATEGORY (内容分类)**：短视频的主分类目录（如科技、美食、娱乐等），用于内容归类与审核权限划分。
- **TAG (标签)**：贴在短视频上的微观特征标签，用于检索与推荐。
- **MODERATOR (审核员)**：平台风控人员，负责审核提交的短视频。
- **AITASK (AI创作任务)**：用户向 AI 创作工具提交的辅助生成任务（如生成脚本、标题、文案或标签建议）。
- **VIDEO_LIKE (点赞)**：记录用户对视频的赞同互动。
- **COMMENT (评论)**：记录用户对视频发表的文字评论。

### 2. 核心属性说明
- **USER**: UserID (PK), Username, Email, RegistrationTime, AccountStatus
- **VIDEO**: VideoID (PK), Title, Duration, Status, SubmitTime, ReviewTime, ReviewRemark, CreatorID (FK), CategoryID (FK), ReviewerID (FK)
- **CATEGORY**: CategoryID (PK), CategoryName, Description
- **TAG**: TagID (PK), TagName
- **MODERATOR**: ModeratorID (PK), ModeratorName, Email
- **AITASK**: TaskID (PK), TaskType, GeneratedContent, IsAdopted, UserID (FK), VideoID (FK)
- **VIDEO_LIKE**: UserID (PK, FK), VideoID (PK, FK), LikeTime
- **COMMENT**: CommentID (PK), CommentText, CommentTime, CommentStatus, UserID (FK), VideoID (FK)

### 3. 实体间主要关系
- **USER - VIDEO**: 1:N（一名用户可创建多条短视频，每条短视频仅由一名用户创建）。
- **CATEGORY - VIDEO**: 1:N（一个分类包含多条短视频，每条短视频仅属于一个主分类）。
- **VIDEO - TAG**: M:N（一条短视频可有多个标签，一个标签可被多条短视频使用）。
- **MODERATOR - CATEGORY**: M:N（审核员可拥有多个分类的审核资质，一个分类可有多名审核员）。
- **USER - AITASK**: 1:N（一名用户可提交多个 AI 任务）。
- **VIDEO - AITASK**: 0..1:N（一条视频可使用零个或多个 AI 任务；一个被采用的 AI 任务最多关联一条视频）。
- **USER - VIDEO - VIDEO_LIKE**: M:N（通过关系表实现，记录点赞历史）。
- **USER - VIDEO - COMMENT**: M:N（通过实体表实现 1:N 延伸，记录评论内容）。

### 4. 4条合理的设计假设
1. **取消点赞处理**：用户取消点赞时，系统采用物理删除（直接删除 `VIDEO_LIKE` 记录），确保复合主键约束能精准保证每位用户对同一视频最多保留一条有效点赞。
2. **下架视频历史数据保留**：状态变为 `Removed` 的视频，其历史点赞与评论记录在数据库中予以保留，但前端展示层进行屏蔽，以备审计分析。
3. **审核流程触发规则**：新上传视频状态初始为 `Pending`，`ReviewerID` 和 `ReviewTime` 默认为 NULL；仅当状态改变为 `Approved` 或 `Rejected` 时才强制要求更新审核员与审核时间。
4. **AI 任务独立性**：用户可随时使用 AI 工具生成内容，即便生成的脚本未最终转化为发布的视频，AI 任务记录依然独立保留 (`VideoID` 可为空)。

---

## Part B: 概念数据库设计 - ER Diagram (25分)

### 1. ER 图展示

![Smart Video Platform ER Diagram](./er_diagram.png)

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