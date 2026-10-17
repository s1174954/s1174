```mermaid
erDiagram
    USER ||--o{ VIDEO : "publishes"
    CATEGORY ||--o{ VIDEO : "belongs to"
    VIDEO }|--|{ TAG : "tagged with"
    MODERATOR o|--o{ VIDEO : "reviews"
    MODERATOR }|--|{ CATEGORY : "has qualification"
    USER ||--o{ AI_TASK : "creates"
    AI_TASK }o--o| VIDEO : "adopted by"
    USER ||--o{ VIDEO_LIKE : "likes"
    VIDEO ||--o{ VIDEO_LIKE : "liked by"
    USER ||--o{ COMMENT : "writes"
    VIDEO ||--o{ COMMENT : "has"

    USER {
        int UserID PK
        string Nickname
        string Email
        datetime RegisterTime
        string AccountStatus
    }

    VIDEO {
        int VideoID PK
        string Title
        int Duration
        string Status
        datetime SubmitTime
        datetime ReviewTime
        int UserID FK
        int CategoryID FK
        int ModeratorID FK
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
        string Name
        string Email
        string WorkStatus
    }

    AI_TASK {
        int TaskID PK
        string TaskType
        string PromptText
        string ResultText
        datetime CreateTime
        int UserID FK
        int VideoID FK
    }

    VIDEO_LIKE {
        int UserID PK, FK
        int VideoID PK, FK
        datetime LikeTime
    }

    COMMENT {
        int CommentID PK
        string Content
        datetime CommentTime
        string Status
        int UserID FK
        int VideoID FK
    }